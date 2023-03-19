from kaiko_sdk_data import run_live_kaiko_indices


def run():
    """
    This function is the main function that runs all day long live, after running the data is already uploaded to
    InfluxDB.
    """

    # ----------------- Kaiko Indices -----------------
    run_live_kaiko_indices()


if __name__ == '__main__':
    run()

