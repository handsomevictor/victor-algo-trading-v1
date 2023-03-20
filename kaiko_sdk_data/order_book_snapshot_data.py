"""
Currently consider to add Binance orderbook data using REST API

Bid and Ask slippage is already multiplied by 10000
"""

import os
import requests
import pandas as pd
import datetime
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from itertools import repeat
from tqdm import tqdm
import logging
import warnings

from contants import write_api
from availability_check import availability_total

from influxdb_client import InfluxDBClient, Point, WriteOptions, WritePrecision
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

warnings.filterwarnings("ignore")


def time_convert(timestamp):
    if type(timestamp) == datetime.datetime or type(timestamp) == datetime.date:
        start_time_str = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        start_time_dt = timestamp
    else:
        start_time_str = timestamp
        start_time_dt = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
    return start_time_str, start_time_dt


# noinspection SpellCheckingInspection,PyShadowingNames
class GetOhlcv:
    def __init__(self, exches: list, pairs: list, start_time, end_time,
                 interval='1d', aclass='spot', time_label='timestamp'):
        self.exches = exches
        self.pairs = pairs
        self.start_time = start_time
        self.end_time = end_time
        self.interval = interval
        self.aclass = aclass
        self.time_label = time_label

        self.conc_exch = True if len(exches) > 1 else False
        self.conc_exch_num = len(exches) if len(exches) < 40 else 40

        self.conc_pair = True if len(pairs) > 1 else False
        self.conc_pair_num = len(pairs) if len(pairs) < 40 else 40

        if self.conc_pair_num * self.conc_exch_num > 600:  # try to balance the number of concurrent threads
            self.conc_pair_num = 600 // self.conc_exch_num

        self.start_time_str, self.start_time_dt = time_convert(self.start_time)
        self.end_time_str, self.end_time_dt = time_convert(self.end_time)

        # when more than one exch or pair & interval is using minutes or seconds, use multi threads for spliting dates

    @staticmethod
    def get_ohlcv_single(exch, pair, start_time, end_time, interval='1d', aclass='spot', time_label='timestamp'):
        url_ohlcv = f"https://us.market-api.kaiko.io/v2/data/trades.v1/exchanges/{exch}/{aclass}/{pair}/aggregations/" \
                    f"count_ohlcv_vwap?start_time={start_time}&end_time={end_time}&interval={interval}&page_size=100000"

        headers = {
            'Accept': 'application/json',
            'X-Api-Key': os.environ['KAIKO_API_KEY'],
        }

        response = requests.get(url_ohlcv, headers=headers)
        res = response.json()
        res_data = res['data']

        # Loop for pagination, does not retry if there is an error
        while True:
            if (res.get('next_url') is not None) & (res['data'] != []):
                response = requests.get(res['next_url'], headers=headers)
                res = response.json()
                res_data = res_data + res['data']
            else:
                break
        try:
            df_ = pd.DataFrame.from_dict(res_data, dtype='float')
            df_[time_label] = pd.to_datetime(df_[time_label], unit='ms')
            df_.index = df_[time_label]
            df_ = df_.drop(columns=time_label)
            df_['pair'] = pair
            df_['exchange'] = exch
            return df_

        except KeyError:
            df_ = pd.DataFrame(columns=['pair', 'exchange', 'open', 'high', 'low', 'close', 'volume', 'vwap'])
            return df_

    def get_ohlcv_conc_exch(self, exches, pair):
        """
        Getting ohlcv data from multiple exchanges but only one pair
        :return: DataFrame
        """
        res = pd.DataFrame()
        with ThreadPoolExecutor(max_workers=self.conc_exch_num) as pool:
            if len(self.pairs) == 1:
                res_temp = list(tqdm(pool.map(self.get_ohlcv_single, exches, repeat(pair),
                                              repeat(self.start_time_str), repeat(self.end_time_str),
                                              repeat(self.interval),
                                              repeat(self.aclass), repeat(self.time_label)),
                                     total=len(self.pairs)))
            else:
                res_temp = list(pool.map(self.get_ohlcv_single, exches, repeat(pair),
                                         repeat(self.start_time_str), repeat(self.end_time_str),
                                         repeat(self.interval),
                                         repeat(self.aclass), repeat(self.time_label)))

            for df in res_temp:
                res = pd.concat([res, df])
        return res

    def get_ohlcv_conc_pair(self):
        """
        Getting ohlcv data from multiple pairs (each pair all exchanges)
        :return: DataFrame
        """

        res = pd.DataFrame()
        with ProcessPoolExecutor(max_workers=self.conc_pair_num) as pool:
            res_temp = list(tqdm(pool.map(self.get_ohlcv_conc_exch, repeat(self.exches), self.pairs),
                                 total=len(self.pairs)))

            for df in res_temp:
                res = pd.concat([res, df])
        return res

    def get_ohlcv(self):
        return self.get_ohlcv_conc_pair()


def get_orderbook_single(exch, pair, start_time, end_time, interval='1m'):
    ob_url = 'https://us.market-api.kaiko.io/v2/data/order_book_snapshots.v1/exchanges' \
          f'/{exch}/spot' \
          f'/{pair}/' \
          'ob_aggregations/full' \
          '?page_size=100' \
          '&slippage=100000' \
          f'&interval={interval}' \
          f'&start_time={start_time}' \
          f'&end_time={end_time}'

    headers = {
        'Accept': 'application/json',
        'X-Api-Key': os.environ['KAIKO_API_KEY'],
    }

    response = requests.get(ob_url, headers=headers)
    res = response.json()

    try:
        final_res = res['data']
        final_res = pd.DataFrame(final_res)
        while 'next_url' in res:
            ob_url = res['next_url']
            tmp_res = requests.get(ob_url, headers=headers).json()
            tmp_data = tmp_res['data']
            tmp_data = pd.DataFrame(tmp_data)
            final_res = pd.concat([final_res, tmp_data])
            res = tmp_res

        final_res['poll_timestamp'] = pd.to_datetime(final_res['poll_timestamp'], unit='ms')
        final_res['poll_timestamp'] = final_res['poll_timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        final_res['pair'] = pair
        final_res['exchange'] = exch

        availability_total['minute_updates']['kaiko_ob_data'][f'{exch}_{pair}'] = 1

        # change type to float for all columns
        for col in final_res.columns:
            if col not in ['poll_timestamp', 'pair', 'exchange']:
                final_res[col] = final_res[col].astype(float)

        return final_res
    except KeyError:
        logging.error(f'At {datetime.datetime.now()}, kaiko ob data retrival failure for: '
                      f'{exch}, {pair}, {start_time}, {end_time}, {interval}')
        return None
    # 但是还没有完成上传availability！以后再做！


def upload_historical_data(data, measurement_name, bucket_name, product_name):
    if data is None or data.empty:
        logging.error(f'At {datetime.datetime.now()}')
        logging.error(f"Error in upload_orderbook_data: data is None or empty")
        print(f'At {datetime.datetime.now()}, Error in upload_orderbook_data: data is None or empty')
        return None

    points = []

    for index, row in data.iterrows():
        point = Point(measurement_name) \
            .tag('tag', product_name) \
            .time(row['poll_timestamp'])
        for col in data.columns:
            if col not in ['poll_timestamp', 'pair', 'exchange']:
                point = point.field(col, row[col])

        points.append(point)
    write_api.write(bucket=bucket_name, record=points)


def ob_update(exch, pair, interval='1m'):
    # update orderbook data every 1 minute
    params = {
        'exch': exch,
        'pair': pair,
        'start_time': (datetime.datetime.now(datetime.timezone.utc) -
                       datetime.timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:00Z'),
        'end_time': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z'),
        'interval': interval,
    }

    ob_full_data = get_orderbook_single(**params)
    print(ob_full_data)
    upload_historical_data(data=ob_full_data,
                           bucket_name='testing',
                           measurement_name='ob_btcusdt_try1',
                           product_name='btc-usdt Orderbook Full')


if __name__ == '__main__':
    params = {
        'exch': 'binc',
        'pair': 'btc-usdt',
        'start_time': (datetime.datetime.now(datetime.timezone.utc) -
                       datetime.timedelta(minutes=20)).strftime('%Y-%m-%dT%H:%M:00Z'),
        'end_time': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z'),
        'interval': '1m',
    }

    import time
    start = time.time()
    ob_full_data = get_orderbook_single(**params)
    upload_historical_data(data=ob_full_data,
                           bucket_name='testing',
                           measurement_name='ob_btcusdt_try1',
                           product_name='btc-usdt Orderbook Full')
    print(time.time() - start)





