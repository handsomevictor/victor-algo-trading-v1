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


# noinspection DuplicatedCode
class FredData:
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

    @staticmethod
    def process_data(data):
        try:
            data = data.reset_index()
            data.columns = ['time', 'value']

            data['value'] = data['value'].fillna(method='ffill')
            data['time'] = pd.to_datetime(data['time'])

            return data
        except Exception as e:
            logging.error(f"Error in get_30_Year_Fixed_Rate_Mortgage_Average_in_US:")
            logging.error(e)
            logging.error(datetime.datetime.now())
            return None

    def get_15_and_30_Year_Fixed_Rate_Mortgage_Average_in_US(self):
        data_15 = self.fred.get_series('MORTGAGE15US')
        data_30 = self.fred.get_series('MORTGAGE30US')
        if data_15 is None or data_15.empty or data_30 is None or data_30.empty:
            return None

        data_15 = self.process_data(data_15)
        data_30 = self.process_data(data_30)
        return data_15, data_30

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

    Fixed_Rate_Mortgage_Average_15, Fixed_Rate_Mortgage_Average_30 = \
        fred_data.get_15_and_30_Year_Fixed_Rate_Mortgage_Average_in_US()
    if Fixed_Rate_Mortgage_Average_15 is not None and Fixed_Rate_Mortgage_Average_30 is not None:
        fred_data.upload_historical_data(data=Fixed_Rate_Mortgage_Average_15,
                                         bucket_name='testing',
                                         measurement_name='corp_bond_aaa_try1',
                                         product_name="Corporate Bond - 15-Year Fixed Rate Mortgage"
                                                      "Average in the United States")
        fred_data.upload_historical_data(data=Fixed_Rate_Mortgage_Average_30,
                                         bucket_name='testing',
                                         measurement_name='corp_bond_aaa_try1',
                                         product_name="Corporate Bond - 30-Year Fixed Rate Mortgage"
                                                      "Average in the United States")

    print(f'15 and 30-Year Fixed Rate Mortgage Average in the United States has been uploaded to influxdb at'
          f'{datetime.datetime.now()}')
