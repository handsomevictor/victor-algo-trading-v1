from fredapi import Fred
import ssl
import sys
import datetime
import os
import pandas as pd
import logging
import warnings

from availability_check import availability_total
from contants import write_api

from influxdb_client import InfluxDBClient, Point, WriteOptions, WritePrecision
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

if sys.platform != 'linux':
    ssl._create_default_https_context = ssl._create_unverified_context

warnings.filterwarnings("ignore")


# noinspection DuplicatedCode
class FredData:
    """
    逻辑：似乎不能指定时间段，所以每一次执行的时候就获取全部数据，数据量很小，不会有问题
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
        self.availability_total = availability_total['daily_updates']['fred_economic_data']

    @staticmethod
    def process_data(data, self_defined_error_message):
        try:
            data = data.reset_index()
            data.columns = ['time', 'value']
            data['value'] = data['value'].fillna(method='ffill')
            data['time'] = pd.to_datetime(data['time'])
            return data
        except Exception as e:
            logging.error(self_defined_error_message)
            logging.error(e)
            logging.error(datetime.datetime.now())
            return None

    def get_ICE_BofA_US_High_Yield_Index_Option_Adjusted_Spread(self):
        data = self.fred.get_series('BAMLH0A0HYM2EY')
        if data is None or data.empty:
            # 尝试获取数据失败，设置为-1
            self.availability_total['ICE_BofA_US_High_Yield_Index_Option_Adjusted_Spread'] = -1
            return None

        try:
            data = data.reset_index()
            data.columns = ['time', 'value']

            data['value'] = data['value'].fillna(method='ffill')
            data['time'] = pd.to_datetime(data['time'])

            self.availability_total['ICE_BofA_US_High_Yield_Index_Option_Adjusted_Spread'] = 1
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
            self.availability_total['Moodys_Seasoned_Aaa_and_Baa_Corporate_Bond_Yield'] = -1
            return None

        data_DAAA = self.process_data(data_DAAA, self_defined_error_message=f'DAAA has a problem on '
                                                                            f'{datetime.datetime.now()}')
        data_DBAA = self.process_data(data_DBAA, self_defined_error_message=f'DBAA has a problem on '
                                                                            f'{datetime.datetime.now()}')
        self.availability_total['Moodys_Seasoned_Aaa_and_Baa_Corporate_Bond_Yield'] = 1
        return data_DAAA, data_DBAA

    def get_30_Year_Jumbo_Mortgage_Index(self):
        data_15 = self.fred.get_series('OBMMIJUMBO30YF')
        if data_15 is None or data_15.empty or len(data_15) == 0:
            self.availability_total['30_Year_Jumbo_Mortgage_Index'] = -1
            return None

        data_15 = self.process_data(data_15, self_defined_error_message=f'30_Year_Jumbo_Mortgage_Index has a problem'
                                                                        f' on {datetime.datetime.now()}')
        self.availability_total['30_Year_Jumbo_Mortgage_Index'] = 1
        return data_15

    def get_Treasury_Bill_Secondary_Market_Rate(self):
        """
        This is discount basis
        """
        tbill_4_weeks = self.fred.get_series('DTB4WK')
        tbill_3_months = self.fred.get_series('DTB3')
        tbill_6_months = self.fred.get_series('DTB6')
        tbill_1_year = self.fred.get_series('DTB1YR')

        def process(data, which_one):
            if data is None or data.empty:
                return None, which_one
            return data, which_one

        res = [process(tbill_4_weeks, 4),
               process(tbill_3_months, 3),
               process(tbill_6_months, 6),
               process(tbill_1_year, 1)]

        res = [i for i in res if i[0] is not None]
        which_one = [i[1] for i in res if i[0] is not None]
        if len(res) == 0:
            self.availability_total['Treasury_Bill_Secondary_Market_Rate'] = -1
            return None

        res = [self.process_data(i[0], self_defined_error_message=f'{i[1]}_treasury_bill_secondary_market_rate'
                                                                  f'has a problem'
                                                                  f' on {datetime.datetime.now()}') for i in res]

        # reminder: the length of res may (tho not likely) be different from 4, since calling api may fail
        if len(res) != len(which_one):
            logging.error(f'len(res) != len(which_one) in get_treasury_bill_secondary_market_rate at'
                          f'{datetime.datetime.now()}')
            self.availability_total['Treasury_Bill_Secondary_Market_Rate'] = -1
            return None
        self.availability_total['Treasury_Bill_Secondary_Market_Rate'] = 1
        return res, which_one

    def get_Bank_Prime_Loan_Rate(self):
        """
        https://fred.stlouisfed.org/series/DPRIME
        """
        data = self.fred.get_series('DPRIME')
        if data is None or data.empty or len(data) == 0:
            self.availability_total['Bank_Prime_Loan_Rate'] = -1
            return None
        data = self.process_data(data, self_defined_error_message=f'Bank Prime Loan Rate has a problem on '
                                                                  f'{datetime.datetime.now()}')
        self.availability_total['Bank_Prime_Loan_Rate'] = 1
        return data

    def get_Job_Posting_on_Indeed(self):
        """
        https://fred.stlouisfed.org/series/IHLIDXUS
        看清楚frequency！肯定要从这里移出去的！
        """

        # data = self.fred.get_series('IHLIDXUS')
        # if data is None or data.empty:
        #     return None
        # data = self.process_data(data, self_defined_error_message=f'Job Posting on Indeed has a problem on '
        #                                                           f'{datetime.datetime.now()}')
        # return data
        # self.availability_total['Job_Posting_on_Indeed'] = 1
        ...

    def get_Initial_Jobless_Claims(self):
        """
        https://fred.stlouisfed.org/series/ICSA
        看清楚frequency！肯定要从这里移出去的！
        """
        # data = self.fred.get_series('ICSA')
        # if data is None or data.empty:
        #     return None
        # data = self.process_data(data, self_defined_error_message=f'Initial Jobless Claims has a problem on '
        #                                                           f'{datetime.datetime.now()}')
        # return data
        # self.availability_total['Initial_Jobless_Claims'] = 1
        ...

    def get_Job_Openings_and_Labor_Turnover_Survey(self):
        """
        https://fred.stlouisfed.org/categories/32241 contains:
        1. Total Nonfarm
        2. Total Private
        3. Government
        看清楚frequency！肯定要从这里移出去的！
        """
        non_farm = self.fred.get_series('JTSOSL')
        # if data is None or data.empty:
        #     return None
        # data = self.process_data(data, self_defined_error_message=f'Job Openings and Labor Turnover Survey has a problem on '
        #                                                           f'{datetime.datetime.now()}')
        # return data
        # self.availability_total['Job_Openings_and_Labor_Turnover_Survey'] = 1
        ...

    def upload_historical_data(self, data, measurement_name, bucket_name, product_name):
        if data is None or data.empty:
            logging.error(f'At {datetime.datetime.now()}')
            logging.error(f"Error in upload_historical_data: data is None or empty")
            return None

        data['measurement'] = measurement_name
        data['tag'] = product_name
        points = []
        for index, row in data.iterrows():
            point = Point(row['measurement']).tag('tag', row['tag']).field('value', row['value']).time(row['time'])
            points.append(point)
        write_api.write(bucket=bucket_name, org=self.org, record=points)

    def upload_availability(self, bucket_name, measurement_name):
        # write_api: upload self.availability_total all keys and all values
        points = []
        for key, value in self.availability_total.items():
            point = Point(measurement_name)\
                .tag('tag', key) \
                .field('value', value) \
                .time(datetime.datetime.now(datetime.timezone.utc))
            points.append(point)
        write_api.write(bucket=bucket_name, record=points)


if __name__ == '__main__':
    fred_data = FredData()
    # a = fred_data.get_ICE_BofA_US_High_Yield_Index_Option_Adjusted_Spread()
    # if a is not None:再上传
    # fred_data.upload_historical_data(data=a,
    #                                  bucket_name='testing',
    #                                  measurement_name='corp_bond_try1',
    #                                  product_name='Interest Rate - Corporate Bond - '
    #                                               'ICE BofA US High Yield Index Option-Adjusted Spread')

    # data_DAAA, data_DBAA = fred_data.get_Moodys_Seasoned_Aaa_and_Baa_Corporate_Bond_Yield()
    # if data_DAAA is not None and data_DBAA is not None:
    #     fred_data.upload_historical_data(data=data_DAAA,
    #                                      bucket_name='testing',
    #                                      measurement_name='corp_bond_aaa_try1',
    #                                      product_name="Corporate Bond - Moody's Seasoned Aaa "
    #                                                   "Corporate Bond Yield")
    #     fred_data.upload_historical_data(data=data_DBAA,
    #                                      bucket_name='testing',
    #                                      measurement_name='corp_bond_aaa_try1',
    #                                      product_name="Corporate Bond - Moody's Seasoned Baa "
    #                                                   "Corporate Bond Yield")

    # t_bill, which_one = fred_data.get_treasury_bill_secondary_market_rate()
    # name_dict = {1: '1 Year', 3: '3 Months', 4: '4 Weeks', 6: '6 Months'}
    # if t_bill is not None:
    #     for i in range(len(t_bill)):
    #         fred_data.upload_historical_data(data=t_bill[i],
    #                                          bucket_name='testing',
    #                                          measurement_name='t_bill_try1',
    #                                          product_name=f"Treasury Bill - {name_dict[which_one[i]]} "
    #                                                       f"Treasury Bill Secondary Market Rate")

    Bank_Prime_Loan_Rate = fred_data.get_Bank_Prime_Loan_Rate()
    if Bank_Prime_Loan_Rate is not None:
        fred_data.upload_historical_data(data=Bank_Prime_Loan_Rate,
                                         bucket_name='testing',
                                         measurement_name='corp_bond_aaa_try1',
                                         product_name='Bank Prime Loan Rate')
