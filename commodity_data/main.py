import yfinance as yf
import ssl
import sys
import datetime
import os
import pandas as pd
import logging
import warnings

from influxdb_client import InfluxDBClient, Point, WriteOptions, WritePrecision
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

from contants import write_api

if sys.platform != 'linux':
    ssl._create_default_https_context = ssl._create_unverified_context

warnings.filterwarnings("ignore")


# noinspection DuplicatedCode
class CommodityData:
    """
    Limits on yfinance commodity data:
    # 1m -> 7 day's data
    # 2m -> 60 day's data
    # 5m -> 60 day's data
    # 15m -> 60 day's data
    # 1h -> 730 days day's data
    # 1d -> All data
    """
    def __init__(self):
        self.today = datetime.datetime.now(datetime.timezone.utc).date().strftime('%Y-%m-%d')
        self.data = {}

    def get_commodity_data(self, end_date: str, commodity: str, interval: str):
        """
        每一分钟执行一次
        （注意，外汇只有工作日有价格，具体时间详见readme）

        没有start date因为目前只取7天的数据 -> 可以加上start date，因为最近的数据用1m的，之前的都用1h即可！有730天呢！
        可以加上start date，判断一下是否存在（肯定要最长时间的）
        """
        # yfinance外汇的interval只能在下面取值
        # [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]

        if interval == '1m':
            start_date = (datetime.datetime.strptime(end_date, '%Y-%m-%d') -
                          datetime.timedelta(days=6)).strftime('%Y-%m-%d')
            data = yf.download(commodity, start=start_date, end=end_date, interval=interval)
        elif interval == '1h':
            start_date = (datetime.datetime.strptime(end_date, '%Y-%m-%d') -
                          datetime.timedelta(days=729)).strftime('%Y-%m-%d')
            data = yf.download(commodity, start=start_date, end=end_date, interval=interval)
        elif isinstance(interval, str):
            logging.error(f'interval {interval} is not supported in commodity data now.')
            return None
        else:
            logging.error(f'interval {interval} is not correct at {datetime.datetime.now()}')
            return None

        # verification
        if data is None or data.empty:
            logging.error(f'commodity {commodity} data is None or empty at {datetime.datetime.now()}')
            return None

        # check if the data columns are correct
        if data.columns.tolist() != ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
            logging.error(f'commodity {commodity} data columns are not correct at {datetime.datetime.now()}')
            return None

        data = data.reset_index()

        # 愿数据的Datetime是这样的：
        # 2023-03-12 18:00:00-04:00，即带有时区信息，后面的-4是UTC-4，所以换算成UTC时间是22点
        data['Datetime_UTC'] = data['Datetime'].map(lambda x: x.tz_convert('UTC').strftime('%Y-%m-%d %H:%M:%S'))
        return data

    def upload_data(self, data, measurement_name, bucket_name, product_name):
        if data is None or data.empty:
            logging.error(f'At {datetime.datetime.now()}')
            logging.error(f"Error in upload_historical_data: data is None or empty")
            return None

        data['measurement'] = measurement_name
        data['tag'] = product_name
        points = []
        for index, row in data.iterrows():
            point = Point(row['measurement']).tag('tag', row['tag'])\
                .field('Open', row['Open']) \
                .field('High', row['High']) \
                .field('Low', row['Low']) \
                .field('Close', row['Close']) \
                .field('Volume', row['Volume']) \
                .time(row['Datetime_UTC'])
            points.append(point)
        write_api.write(bucket=bucket_name, record=points)


if __name__ == '__main__':
    """
    各种ticker详见：https://finance.yahoo.com/commodities?ltr=1
    NQ=F is NASDAQ 100
    CL=F is crude oil
    GC=F is gold
    SI=F is Silver
    ES=F	E-Mini S&P 500
    YM=F	Mini Dow Jones Indus
    RTY=F	E-mini Russell 2000 Index Futur	
    ZB=F	U.S. Treasury Bond Futures,Jun
    ZN=F	10-Year T-Note Futures,Jun-2023
    ZF=F	Five-Year US Treasury Note Futu
    ZT=F	2-Year T-Note Futures,Jun-2023
    
    Maybe use multiple threads to get data
    """
    commodity_data = CommodityData()
    Nasdaq_F = commodity_data.get_commodity_data(commodity_data.today, 'NQ=F', interval='1m')
    commodity_data.upload_data(data=Nasdaq_F,
                               bucket_name='testing',
                               measurement_name='commodity_data_try3',
                               product_name='Nasdaq_Futures')

    Nasdaq_F = commodity_data.get_commodity_data(commodity_data.today, 'NQ=F', interval='1h')
    commodity_data.upload_data(data=Nasdaq_F,
                               bucket_name='testing',
                               measurement_name='commodity_data_try4',
                               product_name='Nasdaq_Futures')

