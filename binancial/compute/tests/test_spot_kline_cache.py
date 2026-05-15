"""Tests for SpotKlineCache."""
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from binancial.compute.spot_kline_cache import SpotKlineCache


def _make_trades_df(start_id, count, base_price=50000.0, base_time_ms=1_700_000_000_000):
    """Build a trades DataFrame mimicking get_trades_historical output.

    `time` carries timezone-aware UTC datetime as get_trades_historical
    returns; `trade_id` is monotonic int from `start_id`.
    """
    times = pd.to_datetime(
        [base_time_ms + i * 1000 for i in range(count)],
        unit='ms',
        utc=True,
    )
    return pd.DataFrame({
        'time': times,
        'trade_id': list(range(start_id, start_id + count)),
        'price': [base_price + i * 0.5 for i in range(count)],
        'quantity': [0.001] * count,
        'quote_quantity': [base_price * 0.001] * count,
        'buyer_is_maker': [bool(i % 2) for i in range(count)],
    })


class TestInit:

    def test_rejects_non_positive_kline_size(self):
        with pytest.raises(ValueError, match='kline_size must be positive'):
            SpotKlineCache(client=MagicMock(), kline_size=0)

    def test_rejects_non_positive_n_rows(self):
        with pytest.raises(ValueError, match='n_rows must be positive'):
            SpotKlineCache(client=MagicMock(), kline_size=300, n_rows=0)


class TestFirstFetchBackfills:

    def test_first_fetch_uses_start_date_path(self):
        """Initial fetch must call get_trades_historical with `start_date`,
        not `last_trade_id`, because the buffer is empty."""

        client = MagicMock()
        cache = SpotKlineCache(client, symbol='BTCUSDT', kline_size=300, n_rows=100)

        with patch(
            'binancial.compute.spot_kline_cache.get_trades_historical',
        ) as mock_fetch:
            mock_fetch.return_value = _make_trades_df(start_id=1000, count=10)
            cache.fetch()

        mock_fetch.assert_called_once()
        kwargs = mock_fetch.call_args.kwargs
        assert 'start_date' in kwargs
        assert kwargs.get('last_trade_id') is None
        assert kwargs['symbol'] == 'BTCUSDT'

    def test_first_fetch_populates_buffer_and_last_trade_id(self):
        client = MagicMock()
        cache = SpotKlineCache(client, kline_size=300, n_rows=100)

        with patch(
            'binancial.compute.spot_kline_cache.get_trades_historical',
            return_value=_make_trades_df(start_id=1000, count=10),
        ):
            cache.fetch()

        assert cache.cached_trade_count == 10
        assert cache.last_trade_id == 1009


class TestSubsequentFetchIncremental:

    def test_second_fetch_uses_last_trade_id_not_start_date(self):
        """Pin: after the buffer is populated, fetch() switches to the
        `last_trade_id` path so it pulls only NEW trades, not the
        full window again."""

        client = MagicMock()
        cache = SpotKlineCache(client, kline_size=300, n_rows=100)

        with patch(
            'binancial.compute.spot_kline_cache.get_trades_historical',
        ) as mock_fetch:
            mock_fetch.side_effect = [
                _make_trades_df(start_id=1000, count=10),
                _make_trades_df(start_id=1010, count=5, base_time_ms=1_700_000_010_000),
            ]
            cache.fetch()
            cache.fetch()

        assert mock_fetch.call_count == 2
        second_kwargs = mock_fetch.call_args_list[1].kwargs
        assert second_kwargs.get('last_trade_id') == 1009
        assert second_kwargs.get('start_date') is None

    def test_incremental_fetch_appends_new_trades(self):
        client = MagicMock()
        cache = SpotKlineCache(client, kline_size=300, n_rows=100)

        with patch(
            'binancial.compute.spot_kline_cache.get_trades_historical',
        ) as mock_fetch:
            mock_fetch.side_effect = [
                _make_trades_df(start_id=1000, count=10),
                _make_trades_df(start_id=1010, count=5, base_time_ms=1_700_000_010_000),
            ]
            cache.fetch()
            cache.fetch()

        assert cache.cached_trade_count == 15
        assert cache.last_trade_id == 1014

    def test_empty_incremental_fetch_keeps_buffer(self):
        """A no-new-trades response must not blow away the existing buffer."""

        client = MagicMock()
        cache = SpotKlineCache(client, kline_size=300, n_rows=100)

        with patch(
            'binancial.compute.spot_kline_cache.get_trades_historical',
        ) as mock_fetch:
            mock_fetch.side_effect = [
                _make_trades_df(start_id=1000, count=10),
                pd.DataFrame(),
            ]
            cache.fetch()
            cache.fetch()

        assert cache.cached_trade_count == 10
        assert cache.last_trade_id == 1009


class TestTrimCache:

    def test_trim_drops_trades_outside_window(self):
        """After append, trades older than `n_rows * kline_size` seconds
        from the newest trade must be dropped."""

        client = MagicMock()
        cache = SpotKlineCache(client, kline_size=60, n_rows=2)

        old_trades = _make_trades_df(
            start_id=1000, count=5, base_time_ms=1_700_000_000_000,
        )
        new_trades = _make_trades_df(
            start_id=1005, count=5, base_time_ms=1_700_000_500_000,
        )

        with patch(
            'binancial.compute.spot_kline_cache.get_trades_historical',
        ) as mock_fetch:
            mock_fetch.side_effect = [old_trades, new_trades]
            cache.fetch()
            cache.fetch()

        assert cache.cached_trade_count == 5
        assert cache.last_trade_id == 1009


class TestEmptyState:

    def test_last_trade_id_none_when_buffer_empty(self):
        cache = SpotKlineCache(client=MagicMock(), kline_size=300, n_rows=100)
        assert cache.last_trade_id is None
        assert cache.cached_trade_count == 0

    def test_empty_first_backfill_re_enters_backfill_on_next_fetch(self):
        """Pin: if the initial backfill returns an empty DataFrame, the
        next `fetch()` call must re-enter the start_date backfill path
        rather than the last_trade_id incremental path (which would
        crash because the buffer has no rows to read `trade_id` from).
        """

        client = MagicMock()
        cache = SpotKlineCache(client, kline_size=300, n_rows=100)

        with patch(
            'binancial.compute.spot_kline_cache.get_trades_historical',
        ) as mock_fetch:
            mock_fetch.side_effect = [
                pd.DataFrame(),
                _make_trades_df(start_id=2000, count=4),
            ]
            cache.fetch()
            assert cache.cached_trade_count == 0
            assert cache.last_trade_id is None

            cache.fetch()

        assert mock_fetch.call_count == 2
        # Second call must use the start_date path again, NOT last_trade_id
        second_kwargs = mock_fetch.call_args_list[1].kwargs
        assert 'start_date' in second_kwargs
        assert second_kwargs.get('last_trade_id') is None
        assert cache.cached_trade_count == 4
        assert cache.last_trade_id == 2003
