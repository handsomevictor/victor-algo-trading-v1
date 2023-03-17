from forex_python.converter import CurrencyRates
import datetime
from tqdm import tqdm
import pandas as pd
import yfinance as yf
import sys

from concurrent.futures import ProcessPoolExecutor
from itertools import repeat


class FXData:
    """
    分成两部分：
    - 历史数据，每次执行的时候一次性获取到当下时间点，上传到influxdb
    - 实时数据，每一分钟执行一次，上传到influxdb

    grafana上显示用candlestick
    """
    def __init__(self):
        self.org = 'victor'
        self.bucket_name = 'fx_data'
        self.url = "https://us-central1-1.gcp.cloud2.influxdata.com"
        self.verify_ssl = False if sys.platform != 'linux' else True

    def get_single_historical_fx_data(start_date: str, end_date: str, currency_pair: str):
        """
        每一分钟执行一次
        （注意，外汇只有工作日有价格，具体时间详见readme）

        yfinance外汇的interval只能在下面取值
        [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]
        """
        c = CurrencyRates()
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        dates = [start_date + datetime.timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        dates = [date.strftime('%Y-%m-%d') for date in dates]
        fx_data = []
        for date in tqdm(dates):
            fx_data.append(c.get_rate(currency_pair, date))
        return fx_data

    def get_historical_fx_data(self, start_date: str, end_date: str, currency_pairs: list):
        with ProcessPoolExecutor() as executor:
            fx_data = executor.map(self.get_single_historical_fx_data, repeat(start_date), repeat(end_date), currency_pairs)
        return fx_data

    def get_single_current_fx_data(self, currency_pair: str):
        """
        每一分钟执行一次
        """
        c = CurrencyRates()
        fx_data = c.get_rate(currency_pair, datetime.datetime.now())
        return fx_data

    def get_current_fx_data(self, currency_pairs: list):
        with ProcessPoolExecutor() as executor:
            fx_data = executor.map(self.get_single_current_fx_data, currency_pairs)
        return fx_data

    def upload_fx_data(self, fx_data: list, currency_pairs: list):
        """
        上传到influxdb
        """
        pass


class FXStrategy(FXData):
    """
    经典的外汇策略
    """
    def __init__(self):
        super().__init__()

    def JPY_CAD(self):
        """
        1. 买入JPY
        2. 买入CAD
        3. 等待JPY升值，卖出JPY
        4. 等待CAD升值，卖出CAD
        """
        pass


if __name__ == '__main__':
    ...
