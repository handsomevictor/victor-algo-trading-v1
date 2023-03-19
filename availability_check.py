"""
This script stores all the available data sources in a dictionary, if available, 1, if not, 0.

上传的时候，在各自的bucket里面添加availability的measurement！（因为更新频率不一样）
"""

availability_total = {
    'daily_updates': {
        'fred_economic_data': {
            'ICE_BofA_US_High_Yield_Index_Option_Adjusted_Spread': 0,
            'Moodys_Seasoned_Aaa_and_Baa_Corporate_Bond_Yield': 0,
            '30_Year_Jumbo_Mortgage_Index': 0,
            'Treasury_Bill_Secondary_Market_Rate': 0,
            'Bank_Prime_Loan_Rate': 0,
            'Job_Posting_on_Indeed': 0,
            'Initial_Jobless_Claims': 0,
            'Job_Openings_and_Labor_Turnover_Survey': 0,
        },
    },
    "minute_updates": {
        'kaiko_ob_data': {
            'binc_btc-usdt': 0,
            # 'binc_ethusdt': 0,
        },
    },
    "live_updates": {
        'kaiko_sdk_data': {
            'index_request': {
                'KK_RR_BTCUSD': 0,
            },
        },
        'fx_data': {
        },
        'commodity_data': {
        },
    },
}
