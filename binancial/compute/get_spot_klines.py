from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import numpy as np
import pandas as pd

KLINE_COLUMNS = [
    'datetime', 'open', 'high', 'low', 'close', 'mean', 'std',
    'median', 'iqr', 'volume', 'maker_ratio', 'no_of_trades',
    'open_liquidity', 'high_liquidity', 'low_liquidity',
    'close_liquidity', 'liquidity_sum', 'maker_volume', 'maker_liquidity',
]


def _parse_datetime(value: str):
    '''Parse a datetime string. Accepts YYYY-MM-DD or YYYY-MM-DD HH:MM:SS.'''
    import datetime as dt

    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            return dt.datetime.strptime(value, fmt).replace(tzinfo=dt.UTC)
        except ValueError:
            continue
    raise ValueError(f'Invalid datetime format: {value!r}')


def _fetch_chunk(client: Any, symbol: str, start: str, end: str) -> pd.DataFrame:
    '''Fetch trades for a single time chunk.'''
    from ..data import get_trades_historical

    return get_trades_historical(
        client, symbol=symbol, limit=10_000_000,
        start_date=start, end_date=end,
    )


def _build_chunks(start_date: str, end_date: str, n_chunks: int) -> list[tuple[str, str]]:
    '''Split a datetime range into n equal sub-ranges.'''
    import datetime as dt

    t0 = _parse_datetime(start_date)
    t1 = _parse_datetime(end_date)

    total = (t1 - t0).total_seconds()
    chunk_s = total / n_chunks
    fmt_out = '%Y-%m-%d %H:%M:%S'

    chunks = []
    for i in range(n_chunks):
        cs = t0 + dt.timedelta(seconds=i * chunk_s)
        ce = t0 + dt.timedelta(seconds=(i + 1) * chunk_s)
        chunks.append((cs.strftime(fmt_out), ce.strftime(fmt_out)))

    return chunks


def _aggregate_trades(trades: pd.DataFrame, kline_size: int) -> pd.DataFrame:
    '''Aggregate raw trades into klines.'''

    if trades.empty:
        return pd.DataFrame(columns=pd.Index(KLINE_COLUMNS))

    # Sort by trade_id so first()/last() give open/close (argMin/argMax equivalent)
    trades = trades.sort_values('trade_id')

    # Assign each trade to a kline bucket (floor to kline_size seconds)
    unix_s = trades['time'].astype(np.int64) // 10**9
    trades['bucket'] = pd.to_datetime(
        (unix_s // kline_size * kline_size) * 10**9, utc=True
    )

    trades['is_maker'] = trades['buyer_is_maker'].astype(np.int8)
    trades['liquidity'] = trades['price'] * trades['quantity']
    trades['maker_qty'] = trades['is_maker'] * trades['quantity']
    trades['maker_liq'] = trades['is_maker'] * trades['liquidity']

    grouped = trades.groupby('bucket')

    df = pd.DataFrame({
        'datetime': grouped['bucket'].first(),

        # OHLC via first/last on trade_id-sorted data
        'open': grouped['price'].first(),
        'high': grouped['price'].max(),
        'low': grouped['price'].min(),
        'close': grouped['price'].last(),

        # Statistical measures (all vectorized, no .apply)
        'mean': grouped['price'].mean(),
        'std': grouped['price'].std(ddof=0),
        'median': grouped['price'].median(),
        'iqr': grouped['price'].quantile(0.75) - grouped['price'].quantile(0.25),

        # Volume and trade metrics
        'volume': grouped['quantity'].sum(),
        'maker_ratio': grouped['is_maker'].mean(),
        'no_of_trades': grouped['price'].count(),

        # Liquidity metrics
        'open_liquidity': grouped['liquidity'].first(),
        'high_liquidity': grouped['liquidity'].max(),
        'low_liquidity': grouped['liquidity'].min(),
        'close_liquidity': grouped['liquidity'].last(),
        'liquidity_sum': grouped['liquidity'].sum(),
        'maker_volume': grouped['maker_qty'].sum(),
        'maker_liquidity': grouped['maker_liq'].sum(),
    })

    # Apply rounding to match ClickHouse output
    df['mean'] = df['mean'].round(5)
    df['std'] = df['std'].round(6)
    df['volume'] = df['volume'].round(9)
    df['liquidity_sum'] = df['liquidity_sum'].round(1)
    df['maker_liquidity'] = df['maker_liquidity'].round(1)

    df['no_of_trades'] = df['no_of_trades'].astype(int)

    df = df.sort_values('datetime').reset_index(drop=True)

    return df


def _drop_partial_kline(df: pd.DataFrame) -> pd.DataFrame:
    '''Drop the last kline row which may be partial (trades still arriving).'''
    if len(df) > 0:
        return df.iloc[:-1].reset_index(drop=True)
    return df


def get_spot_klines(client: Any,
                    symbol: str = "BTCUSDT",
                    kline_size: int = 1,
                    start_date: str | None = None,
                    end_date: str | None = None,
                    workers: int = 10) -> pd.DataFrame:

    '''Build klines from raw trades fetched via the Binance API.

    Replicates the 19-column kline structure: OHLC, statistical measures,
    volume, maker metrics, and liquidity metrics — all aggregated from
    individual trades.

    client | init_binance_api | historical client object
    symbol | str | ticker symbol e.g. 'BTCUSDT'
    kline_size | int | kline period size in seconds
    start_date | str | datetime in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format
    end_date | str | datetime in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format
    workers | int | number of parallel threads for fetching trades
    '''

    from ..data import get_trades_historical

    # Without both dates, fall back to single-threaded fetch
    if not start_date or not end_date:
        trades = get_trades_historical(
            client, symbol=symbol, limit=10_000_000,
            start_date=start_date, end_date=end_date,
        )
        return _drop_partial_kline(_aggregate_trades(trades, kline_size))

    chunks = _build_chunks(start_date, end_date, workers)

    # Fetch all chunks in parallel
    frames = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_fetch_chunk, client, symbol, cs, ce): i
            for i, (cs, ce) in enumerate(chunks)
        }
        for future in as_completed(futures):
            df = future.result()
            if not df.empty:
                frames.append(df)

    if not frames:
        return pd.DataFrame(columns=pd.Index(KLINE_COLUMNS))

    trades = pd.concat(frames, ignore_index=True)
    trades = trades.drop_duplicates(subset='trade_id').sort_values('trade_id').reset_index(drop=True)

    return _drop_partial_kline(_aggregate_trades(trades, kline_size))
