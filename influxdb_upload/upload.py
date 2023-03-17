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


def execute_check_process(data: dict,
                          measurement_name: str,
                          bucket_name: str,
                          org='victor',
                          influxdb_token=os.environ['INFLUXDB_TOKEN']):

    url = "https://us-central1-1.gcp.cloud2.influxdata.com"

    client = influxdb_client.InfluxDBClient(
        url=url,
        token=influxdb_token,
        org=org,
        verify_ssl=False
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # upload data (dict) to influxdb, each key is a list of values
    # use pandas
    df = pd.DataFrame(data)
    # print(df)
    for index, row in df.iterrows():
        p = influxdb_client.Point(measurement_name) \
            .tag("index_code", row['index_code']) \
            .field("price", row['price']) \
            .time(row['current_time'], WritePrecision.S)

        write_api.write(bucket=bucket_name, org=org, record=p)

