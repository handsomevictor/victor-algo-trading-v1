from sdk_data.indices_sdk_main import index_request


if __name__ == '__main__':
    # logging.basicConfig()
    index_request(index_code='KK_RR_BTCUSD', bucket_name='testing', measurement_name='test_index_btcusd_1')
