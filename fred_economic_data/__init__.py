from fred_economic_data.daily_updates import FredData
import os
import logging
import datetime

bucket_name = 'fred_data'
availability_measurement_name = 'availability'


def run_daily_interest_rate_updates():
    log_dir = os.path.join(os.getcwd(), 'logging', 'fred_economic.log')
    logging.basicConfig(filename=log_dir, level=logging.DEBUG)

    fred_data = FredData()

    # ----------- US_High_Yield_Index_Option ------------
    US_High_Yield_Index_Option = fred_data.get_ICE_BofA_US_High_Yield_Index_Option_Adjusted_Spread()
    if US_High_Yield_Index_Option is not None:
        fred_data.upload_historical_data(data=US_High_Yield_Index_Option,
                                         bucket_name=bucket_name,
                                         measurement_name='IR_CB',
                                         product_name='IR_CB ICE BofA US High Yield Index Option-Adjusted Spread')
        print(f'US_High_Yield_Index_Option uploaded at {datetime.datetime.now()}')

    # ----------- Moody's Seasoned Aaa and Baa ------------
    data_DAAA, data_DBAA = fred_data.get_Moodys_Seasoned_Aaa_and_Baa_Corporate_Bond_Yield()
    if data_DAAA is not None and data_DBAA is not None:
        fred_data.upload_historical_data(data=data_DAAA,
                                         bucket_name=bucket_name,
                                         measurement_name='IR_CB',
                                         product_name="IR_CB Moody's Seasoned Aaa Corporate Bond Yield")
        fred_data.upload_historical_data(data=data_DBAA,
                                         bucket_name=bucket_name,
                                         measurement_name='IR_CB',
                                         product_name="IR_CB Moody's Seasoned Baa Corporate Bond Yield")
        print(f'Moody\'s Seasoned Aaa and Baa uploaded at {datetime.datetime.now()}')

    # ----------- 30_Year_Jumbo_Mortgage_Index ------------
    data_30_Year_Jumbo_Mortgage_Index = fred_data.get_30_Year_Jumbo_Mortgage_Index()
    if data_30_Year_Jumbo_Mortgage_Index is not None:
        fred_data.upload_historical_data(data=data_30_Year_Jumbo_Mortgage_Index,
                                         bucket_name=bucket_name,
                                         measurement_name='IR_CB',
                                         product_name="IR_CB 30 Year Jumbo Mortgage Index")
        print(f'30_Year_Jumbo_Mortgage_Index uploaded at {datetime.datetime.now()}')

    # ----------- T Bills Market Rate ------------
    t_bill, which_one = fred_data.get_Treasury_Bill_Secondary_Market_Rate()
    name_dict = {1: '1 Year', 3: '3 Months', 4: '4 Weeks', 6: '6 Months'}
    if t_bill is not None:
        for i in range(len(t_bill)):
            fred_data.upload_historical_data(data=t_bill[i],
                                             bucket_name=bucket_name,
                                             measurement_name='T_Bill',
                                             product_name=f"Treasury Bill - {name_dict[which_one[i]]} "
                                                          f"Secondary Market Rate")
        print(f'T Bills Market Rate uploaded at {datetime.datetime.now()}')

    # ----------- Bank Prime Loan Rate ------------
    Bank_Prime_Loan_Rate = fred_data.get_Bank_Prime_Loan_Rate()
    if Bank_Prime_Loan_Rate is not None:
        fred_data.upload_historical_data(data=Bank_Prime_Loan_Rate,
                                         bucket_name=bucket_name,
                                         measurement_name='IR_CB',
                                         product_name='Bank Prime Loan Rate')
        print(f'Bank Prime Loan Rate uploaded at {datetime.datetime.now()}')

    # ----------- Availability ------------
    fred_data.upload_availability(bucket_name=bucket_name,
                                  measurement_name=availability_measurement_name)
    print(f'Availability uploaded at {datetime.datetime.now()} to {bucket_name} bucket and '
          f'{availability_measurement_name} measurement')


def run_every_thursday_interest_rate_updates():
    pass
