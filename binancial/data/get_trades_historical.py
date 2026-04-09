from typing import Any
import pandas as pd

def get_trades_historical(client: Any, symbol: str = "BTCUSDT", limit: int = 1000) -> pd.DataFrame:
    ...

    '''Returns historical trades for a given symbol
    
    client | init_binance_api | historical client object
    symbol | str | ticker symbol e.g. 'BTCUSDT'
    limit | int | number of trades to fetch (can exceed 1000)
    '''

    import datetime as dt
    import wrangle as wr
    import pandas as pd

    from ..utils.get_colnames import get_colnames

    all_trades = []
    remaining = limit
    
    # Binance API has a limit of 1000 trades per request
    batch_size = min(1000, limit)
    
    # Get first batch
    trades = client.get_historical_trades(symbol=symbol, limit=batch_size)
    all_trades.extend(trades)
    remaining -= len(trades)
    
    # If we need more trades, continue fetching using fromId pagination
    while remaining > 0 and trades:
        # Get oldest trade ID from previous batch (+ 1 to avoid duplicate)
        from_id = trades[-1]['id'] + 1
        batch_size = min(1000, remaining)
        
        # Fetch next batch of trades
        trades = client.get_historical_trades(symbol=symbol, limit=batch_size, fromId=from_id)
        
        # Break if no more trades are returned
        if not trades:
            break
            
        all_trades.extend(trades)
        remaining -= len(trades)
    
    # Process the aggregated trades
    df = pd.DataFrame(all_trades)
    
    df = df.drop(columns='isBestMatch')
    
    df.columns = get_colnames('trades')
    
    df = wr.col_move_place(df, 'time')
    
    df['trade_id'] = df['trade_id'].astype(int)
    df[['price', 'quantity', 'quote_quantity']] = df[['price', 'quantity', 'quote_quantity']].astype(float)

    dt_str_col = [dt.datetime.fromtimestamp(x/1000) for x in df['time']]
    df['time'] = pd.to_datetime(dt_str_col)

    df['buyer_is_maker'] = df['buyer_is_maker'].astype(bool)

    return df
