from fredapi import Fred
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

if sys.platform != 'linux':
    ssl._create_default_https_context = ssl._create_unverified_context

warnings.filterwarnings("ignore")


class FredData:
    """
    分成两部分，一部分是以往的数据，一部分是on going的数据
    """
    def __init__(self):
        self.fred = Fred(api_key=os.environ['FRED_API_KEY'])
        # utc time
        self.today = datetime.datetime.now(datetime.timezone.utc).date().strftime('%Y-%m-%d')
        self.start_date = '2010-01-01'
        self.data = {}

        self.org = 'victor'
        self.bucket_name = 'fred_data'
        self.url = "https://us-central1-1.gcp.cloud2.influxdata.com"
        self.verify_ssl = False if sys.platform != 'linux' else True

    def get_ICE_BofA_US_High_Yield_Index_Option_Adjusted_Spread(self):
        data = self.fred.get_series('BAMLH0A0HYM2EY')
        if data is None or data.empty:
            return None

        try:
            data = data.reset_index()
            data.columns = ['time', 'value']

            data['value'] = data['value'].fillna(method='ffill')
            data['time'] = pd.to_datetime(data['time'])

            return data
        except Exception as e:
            logging.error(f"Error in get_ICE_BofA_US_High_Yield_Index_Option_Adjusted_Spread:")
            logging.error(e)
            logging.error(datetime.datetime.now())
            return None

    def get_Moodys_Seasoned_Aaa_and_Baa_Corporate_Bond_Yield(self):
        data_DAAA = self.fred.get_series('DAAA')
        data_DBAA = self.fred.get_series('DBAA')
        if data_DAAA is None or data_DAAA.empty or data_DBAA is None or data_DBAA.empty:
            return None

        def process_data(data, name):
            try:
                data = data.reset_index()
                data.columns = ['time', 'value']
                data['value'] = data['value'].fillna(method='ffill')
                data['time'] = pd.to_datetime(data['time'])
                return data
            except Exception as e:
                logging.error(f"Error in get_Moodys_Seasoned_{name}_Corporate_Bond_Yield:")
                logging.error(e)
                logging.error(datetime.datetime.now())
                return None

        data_DAAA = process_data(data_DAAA, 'DAAA')
        data_DBAA = process_data(data_DBAA, 'DBAA')
        return data_DAAA, data_DBAA

    def upload_historical_data(self, data, measurement_name, bucket_name, product_name):
        if data is None or data.empty:
            logging.error(f'At {datetime.datetime.now()}')
            logging.error(f"Error in upload_historical_data: data is None or empty")
            return None

        client = influxdb_client.InfluxDBClient(
            url=self.url,
            token=os.environ['INFLUXDB_TOKEN'],
            org=self.org,
            verify_ssl=self.verify_ssl
        )

        write_api = client.write_api(write_options=SYNCHRONOUS)
        data['measurement'] = measurement_name
        data['tag'] = product_name
        points = []
        for index, row in data.iterrows():
            point = Point(row['measurement']).tag('tag', row['tag']).field('value', row['value']).time(row['time'])
            points.append(point)
        write_api.write(bucket=bucket_name, org=self.org, record=points)


if __name__ == '__main__':
    fred_data = FredData()
    # a = fred_data.get_ICE_BofA_US_High_Yield_Index_Option_Adjusted_Spread()
    # if a is not None:再上传
    # fred_data.upload_historical_data(data=a,
    #                                  bucket_name='testing',
    #                                  measurement_name='corp_bond_try1',
    #                                  product_name='Interest Rate - Corporate Bond - '
    #                                               'ICE BofA US High Yield Index Option-Adjusted Spread')

    data_DAAA, data_DBAA = fred_data.get_Moodys_Seasoned_Aaa_and_Baa_Corporate_Bond_Yield()
    if data_DAAA is not None and data_DBAA is not None:
        fred_data.upload_historical_data(data=data_DAAA,
                                         bucket_name='testing',
                                         measurement_name='corp_bond_aaa_try1',
                                         product_name="Interest Rate - Corporate Bond - Moody's Seasoned Aaa "
                                                      "Corporate Bond Yield")
        fred_data.upload_historical_data(data=data_DBAA,
                                         bucket_name='testing',
                                         measurement_name='corp_bond_aaa_try1',
                                         product_name="Interest Rate - Corporate Bond - Moody's Seasoned Baa "
                                                      "Corporate Bond Yield")
