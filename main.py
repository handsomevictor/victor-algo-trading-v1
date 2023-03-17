from sdk_data.indices_sdk_main import index_request
import sys

if __name__ == '__main__':
    # logging.basicConfig()

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
