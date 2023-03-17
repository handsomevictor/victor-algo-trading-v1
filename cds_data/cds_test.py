from fredapi import Fred
import ssl
import urllib.request
import os
import sys

if sys.platform != 'linux':
    ssl._create_default_https_context = ssl._create_unverified_context


if __name__ == '__main__':
    fred = Fred(api_key=os.environ['FRED_API_KEY'])
    # data = fred.get_series('SP500')
    # print(data)
    #
    # import pandas as pd
    # start_date = '2010-01-01'
    # end_date = '2020-12-31'
    #
    # # ICE BofA US High Yield Index Effective Yield
    # cds_data = fred.get_series('BAMLH0A0HYM2EY', start_date=start_date, end_date=end_date)
    #
    # cds_data = pd.DataFrame(cds_data)
    # cds_data.to_csv('cds_data.csv')
