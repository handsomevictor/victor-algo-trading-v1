from fred_economic_data import run_daily_interest_rate_updates


def run():
    """
    This function is the main function that runs all the daily updates, all of them are already uploaded to InfluxDB.
    """
    # ----------------- Daily Updates -----------------

    # ----------------- Fred Economic Data ------------
    # ----------------- Interest Rates ----------------
    run_daily_interest_rate_updates()
    print('Daily Interest Rate Updates Done')


if __name__ == '__main__':
    run()

