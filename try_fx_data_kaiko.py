import datetime
from fx_data.fx_data_kaiko import FXDataKaiko


if __name__ == '__main__':
    start_time = (datetime.datetime.utcnow() - datetime.timedelta(days=70))
    format_time_func = lambda x: "{:%Y-%m-%dT%H:%M:%S.{:03d}Z}".format(x, x.microsecond // 1000)
    start_time = format_time_func(start_time)
    end_time = format_time_func(datetime.datetime.utcnow())

    params = {
        'timezone': 0,
        'base': 'eur',
        'quote': 'usd',
        'start_time': start_time,
        'end_time': end_time,
        'interval': '1h',
    }
    fx = FXDataKaiko()

    res = fx.single_basic_analysis(**params)
    print(res)
