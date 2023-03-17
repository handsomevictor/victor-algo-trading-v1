from fred_economic_data.daily_updates import FredData
import os
import logging
import datetime


def run_daily_interest_rate_updates():
    log_dir = os.path.join(os.getcwd(), 'logging', 'fred_economic.log')
    logging.basicConfig(filename=log_dir, level=logging.DEBUG)

    fred_data = FredData()

    # ----------- US_High_Yield_Index_Option ------------
    US_High_Yield_Index_Option = fred_data.get_ICE_BofA_US_High_Yield_Index_Option_Adjusted_Spread()
    if US_High_Yield_Index_Option is not None:
        fred_data.upload_historical_data(data=US_High_Yield_Index_Option,
                                         bucket_name='testing',
                                         measurement_name='corp_bond_try1',
                                         product_name='Interest Rate - Corporate Bond - '
                                                      'ICE BofA US High Yield Index Option-Adjusted Spread')
        print(f'US_High_Yield_Index_Option uploaded at {datetime.datetime.now()}')

    # ----------- Moody's Seasoned Aaa and Baa ------------
    data_DAAA, data_DBAA = fred_data.get_Moodys_Seasoned_Aaa_and_Baa_Corporate_Bond_Yield()
    if data_DAAA is not None and data_DBAA is not None:
        fred_data.upload_historical_data(data=data_DAAA,
                                         bucket_name='testing',
                                         measurement_name='corp_bond_aaa_try1',
                                         product_name="Corporate Bond - Moody's Seasoned Aaa "
                                                      "Corporate Bond Yield")
        fred_data.upload_historical_data(data=data_DBAA,
                                         bucket_name='testing',
                                         measurement_name='corp_bond_aaa_try1',
                                         product_name="Corporate Bond - Moody's Seasoned Baa "
                                                      "Corporate Bond Yield")
        print(f'Moody\'s Seasoned Aaa and Baa uploaded at {datetime.datetime.now()}')
