from fred_economic_data.daily_updates import FredData
import os
import logging
import datetime

bucket_name = 'fred_data'


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

    # ----------- 30_Year_Jumbo_Mortgage_Index ------------
    data_30_Year_Jumbo_Mortgage_Index = fred_data.get_30_Year_Jumbo_Mortgage_Index()
    if data_30_Year_Jumbo_Mortgage_Index is not None:
        fred_data.upload_historical_data(data=data_30_Year_Jumbo_Mortgage_Index,
                                         bucket_name='testing',
                                         measurement_name='corp_bond_aaa_try1',
                                         product_name="30_Year_Jumbo_Mortgage_Index")
        print(f'30_Year_Jumbo_Mortgage_Index uploaded at {datetime.datetime.now()}')

    # ----------- T Bills Market Rate ------------
    t_bill, which_one = fred_data.get_treasury_bill_secondary_market_rate()
    name_dict = {1: '1 Year', 3: '3 Months', 4: '4 Weeks', 6: '6 Months'}
    if t_bill is not None:
        for i in range(len(t_bill)):
            fred_data.upload_historical_data(data=t_bill[i],
                                             bucket_name='testing',
                                             measurement_name='t_bill_try1',
                                             product_name=f"Treasury Bill - {name_dict[which_one[i]]} "
                                                          f"Treasury Bill Secondary Market Rate")
        print(f'T Bills Market Rate uploaded at {datetime.datetime.now()}')

    # ----------- Bank Prime Loan Rate ------------
    Bank_Prime_Loan_Rate = fred_data.get_Bank_Prime_Loan_Rate()
    if Bank_Prime_Loan_Rate is not None:
        fred_data.upload_historical_data(data=Bank_Prime_Loan_Rate,
                                         bucket_name='testing',
                                         measurement_name='corp_bond_aaa_try1',
                                         product_name='Bank Prime Loan Rate')
        print(f'Bank Prime Loan Rate uploaded at {datetime.datetime.now()}')


def run_every_thursday_interest_rate_updates():
    pass
