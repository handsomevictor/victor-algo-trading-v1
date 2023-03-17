import os
import pandas as pd

if __name__ == '__main__':
    print(os.environ.get('INFLUXDB_TOKEN'))

    a = {'current_time': ['2023-03-17T01:18:55'], 'index_code': ['KK_RR_BTCUSD'], 'price': [25010.0]}
    print(pd.DataFrame(a))