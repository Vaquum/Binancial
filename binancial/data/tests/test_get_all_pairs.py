"""Tests for get_all_pairs function."""
from unittest.mock import MagicMock

from binancial.data.get_all_pairs import get_all_pairs


def test_get_all_pairs_filters_usdt():
    """Test that only USDT pairs are returned."""
    client = MagicMock()
    client.get_all_tickers.return_value = [
        {'symbol': 'BTCUSDT', 'price': '93000.00'},
        {'symbol': 'ETHUSDT', 'price': '3500.00'},
        {'symbol': 'BTCEUR', 'price': '85000.00'},
        {'symbol': 'ETHBTC', 'price': '0.037'},
        {'symbol': 'BNBUSDT', 'price': '700.00'},
    ]

    result = get_all_pairs(client)

    assert result == ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    client.get_all_tickers.assert_called_once()


def test_get_all_pairs_empty():
    """Test with no tickers."""
    client = MagicMock()
    client.get_all_tickers.return_value = []

    result = get_all_pairs(client)

    assert result == []
