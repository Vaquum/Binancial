def get_klines_historical(client,
                          symbol="BTCUSDT",
                          interval='1h',
                          start_date=None,
                          end_date=None):
    
    '''Returns historical klines for a given symbol and interval

    client | init_binance_api | historical client object
    symbol | str | ticker symbol e.g. 'BTCUSDT'
    interval | str | time interval e.g. '1h'
    start_date | str | start date in 'YYYY-MM-DD' format
    end_date | str | end date in 'YYYY-MM-DD' format
    
    '''

    import pandas as pd
    import datetime as dt

    from ..utils.get_colnames import get_colnames

    klines = client.get_historical_klines(symbol,
                                          interval,
                                          start_str=start_date,
                                          end_str=end_date)
    
    df = pd.DataFrame(klines)

    df.columns = get_colnames()

    df = df.astype(float)

    dt_str_col = [dt.datetime.fromtimestamp(x/1000) for x in df['open_time']]
    df['open_time'] = pd.to_datetime(dt_str_col)

    return df
