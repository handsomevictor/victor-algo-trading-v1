import sys
import logging
import os

from fred_economic_data import run_daily_interest_rate_updates
from sdk_data import run_live_kaiko_indices


def run():
    """
    This function is the main function that runs all the daily updates, all of them are already uploaded to InfluxDB.
    """
    # ----------------- Daily Updates -----------------
    # ----------------- Interest Rates ----------------
    run_daily_interest_rate_updates()

    # ----------------- Kaiko Indices -----------------
    run_live_kaiko_indices()


if __name__ == '__main__':
    run()

