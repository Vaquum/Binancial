"""Tests for get_klines_historical function."""
from unittest.mock import MagicMock

from binancial.data.get_klines_historical import get_klines_historical


def test_get_klines_historical_returns_dataframe():
    """Test that get_klines_historical returns a properly formatted DataFrame."""
    client = MagicMock()

    # Mock klines data: 12 columns per row, matching Binance API format
    mock_klines = [
        [
            1735689600000,  # open_time
            '93000.00',     # open
            '94000.00',     # high
            '92000.00',     # low
            '93500.00',     # close
            '100.5',        # volume
            1735693199999,  # close_time
            '9350000.0',    # qav
            '5000',         # num_trades
            '50.0',         # taker_base_vol
            '4650000.0',    # taker_quote_vol
            '0',            # ignore
        ],
        [
            1735693200000,
            '93500.00',
            '95000.00',
            '93000.00',
            '94500.00',
            '200.3',
            1735696799999,
            '18900000.0',
            '8000',
            '100.0',
            '9400000.0',
            '0',
        ],
    ]
    client.get_historical_klines.return_value = mock_klines

    result = get_klines_historical(
        client, symbol='BTCUSDT', interval='1h',
        start_date='2025-01-01', end_date='2025-01-02',
    )

    assert len(result) == 2
    assert list(result.columns) == [
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'qav', 'num_trades', 'taker_base_vol',
        'taker_quote_vol', 'ignore',
    ]
    assert result['open'].dtype == float
    assert hasattr(result['open_time'].dtype, 'tz') or str(result['open_time'].dtype).startswith('datetime')


def test_get_klines_historical_default_params():
    """Test default parameters."""
    client = MagicMock()
    client.get_historical_klines.return_value = [
        [1735689600000, '93000', '94000', '92000', '93500',
         '100', 1735693199999, '9350000', '5000', '50', '4650000', '0'],
    ]

    result = get_klines_historical(client)

    client.get_historical_klines.assert_called_once_with(
        'BTCUSDT', '1h', start_str=None, end_str=None,
    )
    assert len(result) == 1
