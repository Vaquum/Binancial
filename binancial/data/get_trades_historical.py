def get_trades_historical(client, symbol="BTCUSDT"):

    '''Returns historical trades for a given symbol
    
    client | init_binance_api | historical client object
    symbol | str | ticker symbol e.g. 'BTCUSDT' 
    '''

    import datetime as dt
    import wrangle as wr
    import pandas as pd

    from ..utils.get_colnames import get_colnames

    trades = client.get_historical_trades(symbol=symbol, limit=1000)

    df = pd.DataFrame(trades)
    
    df = df.drop(columns='isBestMatch')
    
    df.columns = get_colnames('trades')
    
    df = wr.col_move_place(df, 'time')
    
    df = df.astype(float)
    
    dt_str_col = [dt.datetime.fromtimestamp(x/1000) for x in df['time']]
    df['time'] = pd.to_datetime(dt_str_col)
    
    df['buyer_is_maker'] = df['buyer_is_maker'].astype(bool)

    return df
