import quandl


if __name__ == '__main__':
    from iexfinance.stocks import Stock
    from iexfinance.stocks import get_historical_data

    # authenticate


    stock = Stock("CAC.PA", output_format='pandas')
    data = stock.get_historical_prices(output_format='pandas', date_from="2022-03-01", date_to="2022-03-02")
    print(data)