import os
import logging
import sys

from sdk_data.indices_sdk_main import index_request


def run_live_kaiko_indices():
    log_dir = os.path.join(os.getcwd(), 'logging', 'kaiko_indices.log')
    logging.basicConfig(filename=log_dir, level=logging.DEBUG, format='%(asctime)s %(message)s')

    # if on Linux, set verify_ssl to True
    if sys.platform == 'linux':
        index_request(index_code='KK_RR_BTCUSD',
                      bucket_name='testing',
                      measurement_name='test_index_btcusd_1',
                      verify_ssl=True)
    else:
        index_request(index_code='KK_RR_BTCUSD',
                      bucket_name='testing',
                      measurement_name='test_index_btcusd_1')
