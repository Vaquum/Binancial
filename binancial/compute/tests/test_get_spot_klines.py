"""Tests for get_spot_klines and its internal helpers."""
import datetime as dt
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from binancial.compute.get_spot_klines import (
    KLINE_COLUMNS,
    _build_chunks,
    _parse_datetime,
    aggregate_trades,
    get_spot_klines,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_trades_df(trade_ids, prices, quantities, times_ms, maker_flags):
    """Build a trades DataFrame matching get_trades_historical output."""
    times = pd.to_datetime([t * 1_000_000 for t in times_ms], utc=False)
    return pd.DataFrame({
        'time': times,
        'trade_id': trade_ids,
        'price': [float(p) for p in prices],
        'quantity': [float(q) for q in quantities],
        'quote_quantity': [float(p) * float(q) for p, q in zip(prices, quantities)],
        'buyer_is_maker': maker_flags,
    })


def _ts(year, month, day, hour=0, minute=0, second=0):
    """Return milliseconds since epoch for a given datetime."""
    return int(dt.datetime(year, month, day, hour, minute, second).timestamp() * 1000)


# ---------------------------------------------------------------------------
# _build_chunks
# ---------------------------------------------------------------------------

class TestBuildChunks:

    def test_splits_evenly(self):
        chunks = _build_chunks('2025-01-01 00:00:00', '2025-01-01 01:00:00', 4)
        assert len(chunks) == 4
        # First chunk starts at start, last chunk ends at end
        assert chunks[0][0] == '2025-01-01 00:00:00'
        assert chunks[-1][1] == '2025-01-01 01:00:00'
        # Chunks are contiguous (no gaps)
        for i in range(len(chunks) - 1):
            assert chunks[i][1] == chunks[i + 1][0]

    def test_single_chunk(self):
        chunks = _build_chunks('2025-01-01', '2025-01-02', 1)
        assert len(chunks) == 1
        assert chunks[0] == ('2025-01-01 00:00:00', '2025-01-02 00:00:00')

    def test_date_only_format(self):
        chunks = _build_chunks('2025-01-01', '2025-01-02', 2)
        assert len(chunks) == 2
        assert chunks[0][0] == '2025-01-01 00:00:00'
        assert chunks[1][1] == '2025-01-02 00:00:00'


class TestParseDatetime:
    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match='Invalid datetime format'):
            _parse_datetime('not-a-date')


# ---------------------------------------------------------------------------
# aggregate_trades
# ---------------------------------------------------------------------------

class TestAggregateTrades:

    def test_empty_input(self):
        empty = pd.DataFrame(columns=['time', 'trade_id', 'price', 'quantity',
                                       'quote_quantity', 'buyer_is_maker'])
        result = aggregate_trades(empty, kline_size=1)
        assert list(result.columns) == KLINE_COLUMNS
        assert len(result) == 0

    def test_single_kline_bucket(self):
        """All trades in the same second -> one kline row."""
        base = _ts(2025, 1, 1, 0, 0, 0)
        trades = _make_trades_df(
            trade_ids=[1, 2, 3, 4],
            prices=[100, 105, 95, 102],
            quantities=[1.0, 2.0, 0.5, 1.5],
            times_ms=[base, base + 100, base + 200, base + 300],
            maker_flags=[True, False, True, False],
        )

        result = aggregate_trades(trades, kline_size=1)

        assert len(result) == 1
        row = result.iloc[0]

        # OHLC: open = price of min trade_id, close = price of max trade_id
        assert row['open'] == 100.0   # trade_id 1
        assert row['close'] == 102.0  # trade_id 4
        assert row['high'] == 105.0
        assert row['low'] == 95.0

        # Volume
        assert row['volume'] == pytest.approx(5.0)
        assert row['no_of_trades'] == 4

        # Maker ratio: 2 maker out of 4
        assert row['maker_ratio'] == pytest.approx(0.5)

        # Maker volume: only maker trades contribute
        assert row['maker_volume'] == pytest.approx(1.5)  # 1.0 + 0.5

    def test_multiple_kline_buckets(self):
        """Trades spanning two seconds -> two kline rows."""
        base = _ts(2025, 1, 1, 0, 0, 0)
        trades = _make_trades_df(
            trade_ids=[1, 2, 3, 4],
            prices=[100, 101, 200, 201],
            quantities=[1.0, 1.0, 1.0, 1.0],
            times_ms=[base, base + 500, base + 1000, base + 1500],
            maker_flags=[True, True, False, False],
        )

        result = aggregate_trades(trades, kline_size=1)

        assert len(result) == 2
        # First bucket
        assert result.iloc[0]['open'] == 100.0
        assert result.iloc[0]['close'] == 101.0
        assert result.iloc[0]['no_of_trades'] == 2
        assert result.iloc[0]['maker_ratio'] == pytest.approx(1.0)
        # Second bucket
        assert result.iloc[1]['open'] == 200.0
        assert result.iloc[1]['close'] == 201.0
        assert result.iloc[1]['maker_ratio'] == pytest.approx(0.0)

    def test_kline_size_groups_correctly(self):
        """kline_size=60 groups trades across a minute."""
        base = _ts(2025, 1, 1, 0, 0, 0)
        trades = _make_trades_df(
            trade_ids=[1, 2, 3],
            prices=[100, 101, 102],
            quantities=[1.0, 1.0, 1.0],
            # second 0, second 30, second 59 — all in one 60s bucket
            times_ms=[base, base + 30_000, base + 59_000],
            maker_flags=[True, False, True],
        )

        result = aggregate_trades(trades, kline_size=60)
        assert len(result) == 1
        assert result.iloc[0]['no_of_trades'] == 3

    def test_open_close_follow_trade_id_not_time(self):
        """Open/close are by trade_id order, not time order."""
        base = _ts(2025, 1, 1, 0, 0, 0)
        # trade_id 10 has lowest id but arrives at time +200ms
        # trade_id 5 has higher id but arrives at time +0ms
        # After sort by trade_id: 5 first, 10 last
        trades = _make_trades_df(
            trade_ids=[10, 5],
            prices=[999, 111],
            quantities=[1.0, 1.0],
            times_ms=[base + 200, base],
            maker_flags=[False, False],
        )

        result = aggregate_trades(trades, kline_size=1)
        assert result.iloc[0]['open'] == 111.0   # trade_id 5 (min)
        assert result.iloc[0]['close'] == 999.0  # trade_id 10 (max)

    def test_liquidity_metrics(self):
        """Verify liquidity = price * quantity, and open/close liquidity match trade_id order."""
        base = _ts(2025, 1, 1, 0, 0, 0)
        trades = _make_trades_df(
            trade_ids=[1, 2, 3],
            prices=[100, 200, 150],
            quantities=[2.0, 1.0, 3.0],
            times_ms=[base, base + 100, base + 200],
            maker_flags=[True, False, True],
        )

        result = aggregate_trades(trades, kline_size=1)
        row = result.iloc[0]

        assert row['open_liquidity'] == pytest.approx(200.0)   # 100 * 2
        assert row['close_liquidity'] == pytest.approx(450.0)  # 150 * 3
        assert row['high_liquidity'] == pytest.approx(450.0)   # max
        assert row['low_liquidity'] == pytest.approx(200.0)    # min(200, 200, 450)
        assert row['liquidity_sum'] == pytest.approx(850.0)    # 200+200+450, rounded to 1dp

    def test_std_uses_population(self):
        """std should use ddof=0 (population std), not ddof=1 (sample std)."""
        base = _ts(2025, 1, 1, 0, 0, 0)
        prices = [10.0, 20.0]
        expected_pop_std = np.std(prices, ddof=0)  # 5.0
        expected_sample_std = np.std(prices, ddof=1)  # ~7.07

        trades = _make_trades_df(
            trade_ids=[1, 2],
            prices=prices,
            quantities=[1.0, 1.0],
            times_ms=[base, base + 100],
            maker_flags=[False, False],
        )

        result = aggregate_trades(trades, kline_size=1)
        assert result.iloc[0]['std'] == pytest.approx(expected_pop_std, abs=1e-6)
        assert result.iloc[0]['std'] != pytest.approx(expected_sample_std, abs=0.1)

    def test_columns_and_dtypes(self):
        """Output has exactly 19 columns in the right order."""
        base = _ts(2025, 1, 1, 0, 0, 0)
        trades = _make_trades_df(
            trade_ids=[1],
            prices=[100],
            quantities=[1.0],
            times_ms=[base],
            maker_flags=[True],
        )

        result = aggregate_trades(trades, kline_size=1)
        assert list(result.columns) == KLINE_COLUMNS
        assert result['datetime'].dt.tz is not None  # UTC-aware
        assert result['no_of_trades'].dtype == np.int64


# ---------------------------------------------------------------------------
# get_spot_klines (full pipeline with mocked API)
# ---------------------------------------------------------------------------

class TestGetSpotKlines:

    @patch('binancial.compute.get_spot_klines._fetch_chunk')
    def test_parallel_deduplicates_boundary_trades(self, mock_fetch):
        """Trades appearing in two adjacent chunks are deduplicated."""
        base = _ts(2025, 1, 1, 0, 0, 0)

        # 3 buckets: second 0 (ids 1-3), second 1 (ids 4-5), second 2 (id 6 dup as 3)
        chunk_a = _make_trades_df(
            trade_ids=[1, 2, 3, 4, 5],
            prices=[100, 101, 102, 200, 201],
            quantities=[1.0, 1.0, 1.0, 1.0, 1.0],
            times_ms=[base, base + 100, base + 200, base + 1000, base + 1100],
            maker_flags=[True, True, False, True, False],
        )
        # Chunk B has trade_id 5 duplicated (boundary overlap) + new trades in second 2
        chunk_b = _make_trades_df(
            trade_ids=[5, 6, 7],
            prices=[201, 300, 301],
            quantities=[1.0, 1.0, 1.0],
            times_ms=[base + 1100, base + 2000, base + 2100],
            maker_flags=[False, True, False],
        )

        mock_fetch.side_effect = [chunk_a, chunk_b]
        client = MagicMock()

        result = get_spot_klines(
            client, kline_size=1,
            start_date='2025-01-01 00:00:00', end_date='2025-01-01 00:01:00',
            workers=2,
        )

        # 3 buckets, last dropped -> 2 rows; trade_id 5 deduped
        assert len(result) == 2
        assert result.iloc[0]['no_of_trades'] == 3  # bucket 0: ids 1,2,3

    @patch('binancial.compute.get_spot_klines._fetch_chunk')
    def test_empty_chunks_handled(self, mock_fetch):
        """If some chunks return empty DataFrames, result is still correct."""
        base = _ts(2025, 1, 1, 0, 0, 0)

        # Need 2 buckets so one survives the partial kline drop
        non_empty = _make_trades_df(
            trade_ids=[1, 2, 3, 4],
            prices=[100, 101, 200, 201],
            quantities=[1.0, 1.0, 1.0, 1.0],
            times_ms=[base, base + 100, base + 1000, base + 1100],
            maker_flags=[True, False, True, False],
        )
        empty = pd.DataFrame(columns=['time', 'trade_id', 'price', 'quantity',
                                       'quote_quantity', 'buyer_is_maker'])

        mock_fetch.side_effect = [empty, non_empty, empty]
        client = MagicMock()

        result = get_spot_klines(
            client, kline_size=1,
            start_date='2025-01-01 00:00:00', end_date='2025-01-01 00:03:00',
            workers=3,
        )

        # 2 buckets, last dropped -> 1 row
        assert len(result) == 1
        assert result.iloc[0]['no_of_trades'] == 2

    @patch('binancial.compute.get_spot_klines._fetch_chunk')
    def test_all_chunks_empty(self, mock_fetch):
        """If all chunks are empty, return empty DataFrame with correct columns."""
        empty = pd.DataFrame(columns=['time', 'trade_id', 'price', 'quantity',
                                       'quote_quantity', 'buyer_is_maker'])
        mock_fetch.return_value = empty
        client = MagicMock()

        result = get_spot_klines(
            client, kline_size=1,
            start_date='2025-01-01 00:00:00', end_date='2025-01-01 00:01:00',
            workers=2,
        )

        assert list(result.columns) == KLINE_COLUMNS
        assert len(result) == 0

    @patch('binancial.compute.get_spot_klines._fetch_chunk')
    def test_kline_bucket_spanning_chunk_boundary(self, mock_fetch):
        """Trades in the same kline bucket split across chunks are aggregated together."""
        base = _ts(2025, 1, 1, 0, 0, 0)

        # Two buckets: second 0 has trades from both chunks, second 1 has extras
        chunk_a = _make_trades_df(
            trade_ids=[1, 2, 5, 6],
            prices=[100, 101, 300, 301],
            quantities=[1.0, 1.0, 1.0, 1.0],
            times_ms=[base + 100, base + 200, base + 1000, base + 1100],
            maker_flags=[True, False, True, True],
        )
        chunk_b = _make_trades_df(
            trade_ids=[3, 4],
            prices=[102, 103],
            quantities=[1.0, 1.0],
            times_ms=[base + 300, base + 400],
            maker_flags=[True, True],
        )

        mock_fetch.side_effect = [chunk_a, chunk_b]
        client = MagicMock()

        result = get_spot_klines(
            client, kline_size=1,
            start_date='2025-01-01 00:00:00', end_date='2025-01-01 00:01:00',
            workers=2,
        )

        # 2 buckets, last dropped -> 1 row with 4 trades (ids 1-4)
        assert len(result) == 1
        assert result.iloc[0]['no_of_trades'] == 4
        assert result.iloc[0]['open'] == 100.0   # trade_id 1
        assert result.iloc[0]['close'] == 103.0  # trade_id 4

    @patch('binancial.data.get_trades_historical')
    def test_no_dates_single_threaded(self, mock_get_trades):
        """Without both start/end dates, falls back to single-threaded fetch."""
        base = _ts(2025, 1, 1, 0, 0, 0)
        trades = _make_trades_df(
            trade_ids=[1, 2, 3],
            prices=[100, 101, 200],
            quantities=[1.0, 1.0, 1.0],
            times_ms=[base, base + 100, base + 1000],
            maker_flags=[True, False, True],
        )
        mock_get_trades.return_value = trades
        client = MagicMock()

        result = get_spot_klines(client, kline_size=1)

        mock_get_trades.assert_called_once()
        # 2 buckets, last dropped -> 1 row
        assert len(result) == 1

    @patch('binancial.compute.get_spot_klines._fetch_chunk')
    def test_partial_kline_dropped(self, mock_fetch):
        """The last kline is always dropped to avoid partial data."""
        base = _ts(2025, 1, 1, 0, 0, 0)

        trades = _make_trades_df(
            trade_ids=[1, 2, 3, 4, 5, 6],
            prices=[100, 101, 200, 201, 300, 301],
            quantities=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            times_ms=[base, base + 100, base + 1000, base + 1100,
                       base + 2000, base + 2100],
            maker_flags=[True, False, True, False, True, False],
        )

        mock_fetch.return_value = trades
        client = MagicMock()

        result = get_spot_klines(
            client, kline_size=1,
            start_date='2025-01-01 00:00:00', end_date='2025-01-01 00:01:00',
            workers=1,
        )

        # 3 kline buckets (second 0, 1, 2), last dropped -> 2 rows
        assert len(result) == 2
        # Last remaining row should be second 1, not second 2
        assert result.iloc[-1]['open'] == 200.0
