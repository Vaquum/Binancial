from typing import Any

import pandas as pd


def _parse_datetime_ms(value: str) -> int:
    '''Parse a datetime string to milliseconds since epoch.

    Accepts 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'.
    '''
    import datetime as dt

    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            parsed = dt.datetime.strptime(value, fmt).replace(tzinfo=dt.UTC)
            return int(parsed.timestamp() * 1000)
        except ValueError:
            continue
    raise ValueError(f'Invalid datetime format: {value!r}. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS')


def _api_call(fn: Any, **kwargs: Any) -> Any:
    '''Call a Binance API function with rate-limit retry.'''
    import time as _time

    from binance.exceptions import BinanceAPIException

    for attempt in range(5):
        try:
            return fn(**kwargs)
        except BinanceAPIException as e:
            if e.code == -1003 and attempt < 4:
                _time.sleep(15 * (attempt + 1))
            else:
                raise
    return None


def _resolve_start_id(client: Any, symbol: str, start_datetime: str) -> int:
    '''Resolve a datetime string to the first trade ID at or after that time.'''

    start_ms = _parse_datetime_ms(start_datetime)
    agg = _api_call(client.get_aggregate_trades, symbol=symbol, startTime=start_ms, limit=1)

    if not agg:
        raise ValueError(f'No trades found at or after {start_datetime}')

    return agg[0]['f']


def _format_trades(df: pd.DataFrame) -> pd.DataFrame:
    '''Apply standard column names, types, and formatting to raw trades DataFrame.'''
    import wrangle as wr

    from ..utils.get_colnames import get_colnames

    df = df.drop(columns='isBestMatch')
    df.columns = get_colnames('trades')
    df = wr.col_move_place(df, 'time')

    df['trade_id'] = df['trade_id'].astype(int)
    df[['price', 'quantity', 'quote_quantity']] = df[['price', 'quantity', 'quote_quantity']].astype(float)

    df['time'] = pd.to_datetime(df['time'], unit='ms', utc=True)

    df['buyer_is_maker'] = df['buyer_is_maker'].astype(bool)

    return df


def get_trades_historical(client: Any,
                          symbol: str = "BTCUSDT",
                          limit: int = 1000,
                          start_date: str | None = None,
                          end_date: str | None = None) -> pd.DataFrame:

    '''Returns historical trades for a given symbol

    client | init_binance_api | historical client object
    symbol | str | ticker symbol e.g. 'BTCUSDT'
    limit | int | number of trades to fetch (can exceed 1000)
    start_date | str | datetime in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format
    end_date | str | datetime in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format
    '''

    # Resolve the starting trade ID from start_date if provided
    from_id = _resolve_start_id(client, symbol, start_date) if start_date else None

    # Resolve end_date to a millisecond timestamp for filtering
    end_ms = _parse_datetime_ms(end_date) if end_date else None

    all_trades = []
    remaining = limit

    # Binance API has a limit of 1000 trades per request
    batch_size = min(1000, limit)

    # Get first batch
    kwargs = {'symbol': symbol, 'limit': batch_size}
    if from_id is not None:
        kwargs['fromId'] = from_id
    trades = _api_call(client.get_historical_trades, **kwargs)

    # Filter out trades past end_date
    if end_ms and trades:
        trades = [t for t in trades if t['time'] <= end_ms]

    all_trades.extend(trades)
    remaining -= len(trades)

    # If we need more trades, continue fetching using fromId pagination
    while remaining > 0 and trades:
        # Get oldest trade ID from previous batch (+ 1 to avoid duplicate)
        from_id = trades[-1]['id'] + 1
        batch_size = min(1000, remaining)

        # Fetch next batch of trades
        trades = _api_call(client.get_historical_trades, symbol=symbol, limit=batch_size, fromId=from_id)

        # Break if no more trades are returned
        if not trades:
            break

        # Filter out trades past end_date
        if end_ms:
            trades = [t for t in trades if t['time'] <= end_ms]
            if not trades:
                break

        all_trades.extend(trades)
        remaining -= len(trades)

    if not all_trades:
        return pd.DataFrame(columns=pd.Index(['time', 'trade_id', 'price', 'quantity', 'quote_quantity', 'buyer_is_maker']))

    df = pd.DataFrame(all_trades)

    return _format_trades(df)
