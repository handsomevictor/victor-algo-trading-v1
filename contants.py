import os
import sys

from influxdb_client import InfluxDBClient, Point, WriteOptions, WritePrecision
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# for failure in calling api, try 3 times
retry_times = 3

client = influxdb_client.InfluxDBClient(
    url="https://us-central1-1.gcp.cloud2.influxdata.com",
    token=os.environ['INFLUXDB_TOKEN'],
    org='victor',
    verify_ssl=False if sys.platform != 'linux' else True
)

write_api = client.write_api(write_options=SYNCHRONOUS)

