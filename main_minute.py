from kaiko_sdk_data import run_every_minute_ob_update


def run():
    """
    This function is the main function that runs updates every minute, all of them are already uploaded to InfluxDB.
    """
    # ----------------- Minute Updates -----------------

    # ----------------- Binance OB Snapshot ------------
    run_every_minute_ob_update()
    print('OB snapshot Updates Done')


if __name__ == '__main__':
    run()

