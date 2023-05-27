import pandas as pd
import requests
import datetime
import os


class FXDataKaiko:
    def __init__(self):
        self.fx_raw_data = None

    def fx_data_kaiko(self, base, quote, start_time, end_time, interval):
        url = 'https://us.market-api.kaiko.io/v2/data/analytics.v2' \
              '/oanda_fx_rates' \
              f'?base={base}' \
              f'&quote={quote}' \
              f'&page_size=1000' \
              f'&sort=desc' \
              f'&interval={interval}' \
              f'&start_time={start_time}' \
              f'&end_time={end_time}'
        headers = {
            "X-Api-Key": os.environ.get('KAIKO_API_KEY'),
            'Accept': 'application/json'
        }

        response = requests.get(url, headers=headers)

        res = pd.DataFrame(response.json()['data'])
        while 'next_url' in response.json().keys():
            response = requests.get(response.json()['next_url'], headers=headers)
            res = pd.concat([res, pd.DataFrame(response.json()['data'])])

        res['timestamp'] = pd.to_datetime(res['timestamp'], unit='ms')

        res['fx_rate'] = res['fx_rate'].astype(float)
        res['pct_change'] = res['fx_rate'].pct_change().fillna(0)
        
        self.fx_raw_data = res
        return res

    def single_basic_analysis(self, timezone, base, quote, start_time, end_time, interval):
        """
        1. Return daily pct_change
        2. Return weekly pct_change
        3. Return monthly pct_change
        4. Compare daily volatility with the past year
        5. Compare daily volatility with the past month
        6. Compare weekly volatility with the past year

        :param timezone: can be 'Asia/Singapore', 'Europe/London', 'America/New_York' etc.

        # 还没处理好时区的问题！！！
        """
        params = {
            'base': base,
            'quote': quote,
            'start_time': start_time,
            'end_time': end_time,
            'interval': interval
        }
        fx = FXDataKaiko()
        df = fx.fx_data_kaiko(**params)

        # save a copy to fx_data_kaiko_database_temp folder - just for better plotting if needed to be plotted
        df.to_csv(os.path.join(os.getcwd(),
                               'fx_data',
                               'fx_data_kaiko_database_temp',
                               f'{base}_{quote}_{interval}.csv'))

        # ------------------- Calculate Volatility Percentile -------------------
        # calculate the volatility of the fx rate, remember on weekends there is no data, so the volatility is Nan,
        # drop them
        df_vol_daily_group = df.groupby(pd.Grouper(key='timestamp', freq='1D'))['fx_rate'].std()
        df_vol_daily_group = df_vol_daily_group.reset_index()
        df_vol_weekly_group = df.groupby(pd.Grouper(key='timestamp', freq='1W'))['fx_rate'].std()
        df_vol_weekly_group = df_vol_weekly_group.reset_index()

        # calculate the last volatility's percentile among the whole period volatility - pct=True will return
        # in ascending order
        daily_percentile = pd.Series(df_vol_daily_group['fx_rate']).rank(pct=True, ascending=True).iloc[-1]
        weekly_percentile = pd.Series(df_vol_weekly_group['fx_rate']).rank(pct=True, ascending=True).iloc[-1]

        # ------------------- Calculate Daily and Weekly Percentage Change -------------------
        # Calculate weekly percentage change
        df.set_index('timestamp', inplace=True)
        df['weekly_pct_change'] = df['fx_rate'].resample('W').last()
        current_week_pct_change = df['fx_rate'].resample('W').last().pct_change().fillna(0).iloc[-1]

        # Calculate monthly percentage change
        df['monthly_pct_change'] = df['fx_rate'].resample('M').last()
        current_month_pct_change = df['fx_rate'].resample('M').last().pct_change().fillna(0).iloc[-1]

        return df['fx_rate'], daily_percentile, weekly_percentile, current_week_pct_change, current_month_pct_change

    def plot_usd_based(self):
        """
        Plot a graph of the fx rate based on usd, all in one
        """
        ...

    def upload_to_grafana(self):
        ...



if __name__ == '__main__':
    start_time = (datetime.datetime.utcnow() - datetime.timedelta(days=70))
    format_time_func = lambda x: "{:%Y-%m-%dT%H:%M:%S.{:03d}Z}".format(x, x.microsecond // 1000)
    start_time = format_time_func(start_time)
    end_time = format_time_func(datetime.datetime.utcnow())

    params = {
        'timezone': 0,
        'base': 'eur',
        'quote': 'usd',
        'start_time': start_time,
        'end_time': end_time,
        'interval': '1h',
    }
    fx = FXDataKaiko()

    res = fx.single_basic_analysis(**params)
    print(res)