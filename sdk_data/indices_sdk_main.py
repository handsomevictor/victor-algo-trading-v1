from __future__ import print_function
import logging
import os
import json
import datetime
from collections import defaultdict

import grpc
import pandas as pd
from google.protobuf.json_format import MessageToJson

from kaikosdk import sdk_pb2_grpc
from kaikosdk.stream.index_v1 import request_pb2 as pb_index
from influxdb_upload.upload import execute_check_process


def index_request(index_code, measurement_name, bucket_name, verify_ssl=False):
    credentials = grpc.ssl_channel_credentials(root_certificates=None)
    call_credentials = grpc.access_token_call_credentials(os.environ['KAIKO_API_KEY'])
    composite_credentials = grpc.composite_channel_credentials(credentials, call_credentials)
    channel = grpc.secure_channel('gateway-v0-grpc.kaiko.ovh', composite_credentials)

    data = defaultdict(list)
    i = 0

    try:
        with channel:
            stub = sdk_pb2_grpc.StreamIndexServiceV1Stub(channel)
            responses = stub.Subscribe(pb_index.StreamIndexServiceRequestV1(
                index_code=index_code
            ))
            for response in responses:
                # use json format to get the data
                message = json.loads(MessageToJson(response, including_default_value_fields=True))
                # print(message)

                if i >= 3:
                    # upload data to influxdb
                    # print(data)
                    execute_check_process(data, measurement_name, bucket_name, verify_ssl=verify_ssl)
                    print(f'uploaded data to influxdb at {datetime.datetime.now()}')

                    data = defaultdict(list)
                    i = 0
                else:
                    try:
                        # change the time message['interval']['end_time'] to datetime, format is 2021-05-05T00:00:00Z
                        data['current_time'].append(datetime.datetime.strptime(message['interval']['endTime'],
                                                                               '%Y-%m-%dT%H:%M:%SZ'))
                        data['index_code'].append(index_code)
                        data['price'].append(message['percentages'][0]['price'])
                        i += 1
                    # except key error
                    except KeyError as e:
                        # record time
                        logging.error(datetime.datetime.now(), e, message, '\n')

    except grpc.RpcError as e:
        print(e.details(), e.code())


if __name__ == '__main__':
    logging.basicConfig()
    index_request(index_code='KK_RR_BTCUSD', bucket_name='testing', measurement_name='test_index_btcusd_1')
