def get_trades_historical(symbol="BTCUSDT"):

    import datetime as dt
    import wrangle as wr
    import pandas as pd

    from ..utils.init_binance_api import init_binance_api
    from ..utils.get_colnames import get_colnames

    client = init_binance_api(mode='historical')

    trades = client.get_historical_trades(symbol=symbol, limit=1000)

    df = pd.DataFrame(trades)
    
    df = df.drop(columns='isBestMatch')
    
    df.columns = get_colnames('trades')
    
    df = wr.col_move_place(df, 'time')
    
    df = df.astype(float)
    
    df['time'] = pd.to_datetime([dt.datetime.fromtimestamp(x/1000) for x in df['time']])
    
    df['buyer_is_maker'] = df['buyer_is_maker'].astype(bool)

    return df
