"""Tests for get_trades_historical function."""
import pytest
from unittest.mock import MagicMock, patch, call
import pandas as pd

from binancial.data.get_trades_historical import get_trades_historical


def _make_trade(trade_id, price, qty, time, is_buyer_maker):
    return {
        'id': trade_id,
        'price': str(price),
        'qty': str(qty),
        'quoteQty': str(float(price) * float(qty)),
        'time': time,
        'isBuyerMaker': is_buyer_maker,
        'isBestMatch': True,
    }


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    return MagicMock()


def test_get_trades_historical_default_limit(mock_client):
    """Test get_trades_historical with default limit."""
    trades = [
        _make_trade(i, 100 + i, 1, 1629283200000 + i * 1000, i % 2 == 0)
        for i in range(1000)
    ]
    mock_client.get_historical_trades.return_value = trades

    result = get_trades_historical(mock_client)

    mock_client.get_historical_trades.assert_called_once_with(symbol='BTCUSDT', limit=1000)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1000
    assert list(result.columns) == ['time', 'trade_id', 'price', 'quantity', 'quote_quantity', 'buyer_is_maker']
    assert result['trade_id'].dtype == int
    assert result['buyer_is_maker'].dtype == bool


def test_get_trades_historical_pagination(mock_client):
    """Test get_trades_historical with pagination (limit > 1000)."""
    batch_1 = [
        _make_trade(i, 100 + i, 1, 1629283200000 + i * 1000, i % 2 == 0)
        for i in range(1000)
    ]
    batch_2 = [
        _make_trade(1000 + i, 200 + i, 2, 1629284200000 + i * 1000, i % 2 == 0)
        for i in range(500)
    ]
    mock_client.get_historical_trades.side_effect = [batch_1, batch_2]

    result = get_trades_historical(mock_client, limit=1500)

    assert mock_client.get_historical_trades.call_count == 2
    assert len(result) == 1500
    assert result['trade_id'].nunique() == 1500

    # Verify fromId uses last_id + 1 to avoid duplicates
    second_call_kwargs = mock_client.get_historical_trades.call_args_list[1][1]
    assert second_call_kwargs['fromId'] == 1000


def test_get_trades_historical_no_duplicates_at_boundary(mock_client):
    """Test that pagination doesn't produce duplicate trades at batch boundaries."""
    batch_1 = [_make_trade(i, 100, 1, 1629283200000, False) for i in range(1000)]
    batch_2 = [_make_trade(1000 + i, 100, 1, 1629283200000, False) for i in range(200)]
    mock_client.get_historical_trades.side_effect = [batch_1, batch_2]

    result = get_trades_historical(mock_client, limit=1200)

    assert result['trade_id'].nunique() == len(result)


def test_get_trades_historical_start_date(mock_client):
    """Test that start_date resolves to a fromId via aggregate trades."""
    import datetime as dt

    start_ms = int(dt.datetime.strptime('2025-01-01', '%Y-%m-%d').timestamp() * 1000)

    mock_client.get_aggregate_trades.return_value = [
        {'a': 1, 'p': '100', 'q': '1', 'f': 5000, 'l': 5002, 'T': start_ms, 'm': True, 'M': True}
    ]

    trades = [_make_trade(5000 + i, 100, 1, start_ms + i * 100, False) for i in range(10)]
    mock_client.get_historical_trades.return_value = trades

    result = get_trades_historical(mock_client, start_date='2025-01-01', limit=10)

    mock_client.get_aggregate_trades.assert_called_once_with(symbol='BTCUSDT', startTime=start_ms, limit=1)
    mock_client.get_historical_trades.assert_called_once_with(symbol='BTCUSDT', limit=10, fromId=5000)
    assert len(result) == 10


def test_get_trades_historical_end_date_filters(mock_client):
    """Test that trades past end_date are filtered out."""
    import datetime as dt

    end_ms = int(dt.datetime.strptime('2025-01-02', '%Y-%m-%d').timestamp() * 1000)

    trades = [
        _make_trade(i, 100, 1, end_ms - 2000 + i * 1000, False)
        for i in range(5)
    ]
    # trades at: end_ms-2000, end_ms-1000, end_ms, end_ms+1000, end_ms+2000
    mock_client.get_historical_trades.side_effect = [trades, []]

    result = get_trades_historical(mock_client, end_date='2025-01-02', limit=100)

    # Only trades with time <= end_ms should be included
    assert len(result) == 3


def test_get_trades_historical_start_and_end_date(mock_client):
    """Test with both start_date and end_date."""
    import datetime as dt

    start_ms = int(dt.datetime.strptime('2025-01-01', '%Y-%m-%d').timestamp() * 1000)
    end_ms = int(dt.datetime.strptime('2025-01-02', '%Y-%m-%d').timestamp() * 1000)

    mock_client.get_aggregate_trades.return_value = [
        {'a': 1, 'p': '100', 'q': '1', 'f': 5000, 'l': 5000, 'T': start_ms, 'm': True, 'M': True}
    ]

    trades = [
        _make_trade(5000 + i, 100, 1, start_ms + i * 1000, False)
        for i in range(5)
    ]
    mock_client.get_historical_trades.side_effect = [trades, []]

    result = get_trades_historical(mock_client, start_date='2025-01-01', end_date='2025-01-02', limit=100)

    mock_client.get_aggregate_trades.assert_called_once()
    assert len(result) == 5
    assert result.iloc[0]['trade_id'] == 5000
