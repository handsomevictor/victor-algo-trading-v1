import datetime
import os
import pandas as pd

import rx
from pytz import UTC
from rx import operators as ops

from influxdb_client import InfluxDBClient, Point, WriteOptions, WritePrecision
from influxdb import DataFrameClient
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat


def execute_check_process(data: pd.DataFrame,
                          struct: dict,
                          measurement_name: str,
                          bucket_name: str,
                          org='victor',
                          influxdb_token=os.environ['INFLUXDB_TOKEN']):

    org = "kaiko"
    token = "ecHl9pQoRZ5hTfyM13pZSHR0IAnU0W0e6DsB0rc9T250TNuRh5kM4pqSE3hTn4Ys0zD3DexaOzfyoy6eMbKc3Q=="
    url = "http://34.78.245.234:8086"

    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)
    # ---------------------------------------------------------------

    # if both are None, then it's because calling api failed, upload 0 to a new measurement to note this down.
    tmp = 0 if (res_df is None or tmp_other_info is None) else 1
    p1 = influxdb_client.Point(api_availability_measurement_name) \
        .field("api_call_availability", tmp) \
        .time(datetime.datetime.now(), WritePrecision.S)
    write_api.write(bucket=bucket, org=org, record=p1)

    # Upload data (if not None) to InfluxDB
    res_df['available'] = res_df['available'].astype(int)
    res_df['stay_in_range'] = res_df['stay_in_range'].astype(int)
    # change from str to datetime
    res_df['expiry_date'] = res_df['expiry_date'].apply(
        lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ"))
    res_df['Current_time'] = res_df['Current_time'].apply(
        lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ"))
    res_df['IV_max'] = res_df['IV_max'].apply(lambda x: round(x, 2))
    res_df['IV_min'] = res_df['IV_min'].apply(lambda x: round(x, 2))

    # add a column to change the datetime to unix time integer
    res_df['expiry_date_unix'] = res_df['expiry_date'].apply(lambda x: int(x.timestamp()))
    print(type(res_df['expiry_date_unix'].iloc[0]))
    for index, row in res_df.iterrows():
        # change current time to datetime format from pandas datetime, want an int
        row['current_time'] = int(row['current_time'].to_pydatetime().timestamp())
        row['expiry_date'] = row['expiry_date'].to_pydatetime()
        res_df['expiry_date_unix'] = float(row['expiry_date_unix'])
        p = influxdb_client.Point(measurement_name) \
            .tag("expiry_date_unix", row['expiry_date_unix']) \
            .tag("expiry_date", row['expiry_date']) \
            .field("IV_max", row['IV_max']) \
            .field("IV_min", row['IV_min']) \
            .field('availability', row['available']) \
            .field('stay_in_range', row['stay_in_range']) \
            .field('instrument', row['exchange']) \
            .field('smile_shape', row['smile_shape_judge']) \
            .time(row['current_time'], WritePrecision.S)

        write_api.write(bucket=bucket, org=org, record=p)

