'''Stateful spot kline cache with incremental trade-history pagination.

Maintains a rolling buffer of raw trades and aggregates them into
klines on each `fetch()`. The first call backfills from
`now - n_rows * kline_size`; subsequent calls only pull NEW trades
since the last cached `trade_id`. Collapses per-fetch network cost
from hundreds of paginated `/api/v3/historicalTrades` calls (one per
1000 trades over the full window) to ~1 call per fetch (the few
hundred trades arrived since the previous fetch).
'''

from __future__ import annotations

import datetime as dt
from typing import Any

import pandas as pd

from ..data import get_trades_historical
from .get_spot_klines import _aggregate_trades, _drop_partial_kline

_DATETIME_FMT = '%Y-%m-%d %H:%M:%S'
_PAGINATION_LIMIT = 10_000_000


class SpotKlineCache:

    '''Rolling kline cache backed by an incremental raw-trade buffer.

    client | init_binance_api | historical client object
    symbol | str | ticker symbol e.g. 'BTCUSDT'
    kline_size | int | kline period size in seconds
    n_rows | int | rolling buffer depth in klines (the trade buffer
                   is trimmed so its time span never exceeds
                   `n_rows * kline_size` seconds after each fetch)
    '''

    def __init__(self,
                 client: Any,
                 symbol: str = 'BTCUSDT',
                 kline_size: int = 300,
                 n_rows: int = 1100) -> None:

        if kline_size <= 0:
            raise ValueError(f'kline_size must be positive, got {kline_size}')

        if n_rows <= 0:
            raise ValueError(f'n_rows must be positive, got {n_rows}')

        self._client = client
        self._symbol = symbol
        self._kline_size = kline_size
        self._n_rows = n_rows
        self._trades: pd.DataFrame = pd.DataFrame()

    @property
    def cached_trade_count(self) -> int:
        '''Number of raw trades currently held in the rolling buffer.'''

        return len(self._trades)

    @property
    def last_trade_id(self) -> int | None:
        '''Highest `trade_id` in the rolling buffer, or `None` if empty.'''

        if self._trades.empty:
            return None

        return int(self._trades['trade_id'].max())

    def fetch(self) -> pd.DataFrame:

        '''Pull new trades since the last fetch, aggregate, return klines.

        On the first call, backfills the trade buffer from
        `now - n_rows * kline_size` via `get_trades_historical`'s
        `start_date` path. On every subsequent call, pulls only trades
        with `trade_id > self.last_trade_id` via the new
        `last_trade_id` path. The buffer is trimmed back to the
        `n_rows * kline_size` time window after each append, so memory
        stays bounded.

        Returns:
            pd.DataFrame: 19-column klines aggregated from the current
                buffer, with the trailing partial kline dropped.
        '''

        if self._trades.empty:
            start = (
                dt.datetime.now(tz=dt.UTC)
                - dt.timedelta(seconds=self._n_rows * self._kline_size)
            ).strftime(_DATETIME_FMT)
            self._trades = get_trades_historical(
                self._client,
                symbol=self._symbol,
                limit=_PAGINATION_LIMIT,
                start_date=start,
            )
        else:
            new_trades = get_trades_historical(
                self._client,
                symbol=self._symbol,
                limit=_PAGINATION_LIMIT,
                last_trade_id=int(self._trades['trade_id'].max()),
            )

            if not new_trades.empty:
                self._trades = pd.concat(
                    [self._trades, new_trades], ignore_index=True,
                )
                self._trim_cache()

        return _drop_partial_kline(_aggregate_trades(self._trades, self._kline_size))

    def _trim_cache(self) -> None:

        '''Drop trades older than `n_rows * kline_size` seconds.'''

        if self._trades.empty:
            return

        cutoff = self._trades['time'].max() - pd.Timedelta(
            seconds=self._n_rows * self._kline_size,
        )
        self._trades = self._trades[
            self._trades['time'] >= cutoff
        ].reset_index(drop=True)
