"""Tests for utils module."""
from unittest.mock import MagicMock, patch

import pytest

from binancial.utils.get_colnames import get_colnames
from binancial.utils.init_binance_api import init_binance_api


class TestGetColnames:
    def test_klines_default(self):
        cols = get_colnames()
        assert len(cols) == 12
        assert cols[0] == 'open_time'
        assert cols[-1] == 'ignore'

    def test_klines_explicit(self):
        cols = get_colnames('klines')
        assert len(cols) == 12

    def test_trades(self):
        cols = get_colnames('trades')
        assert len(cols) == 6
        assert cols[0] == 'trade_id'
        assert cols[-1] == 'buyer_is_maker'

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match='cols_for must be'):
            get_colnames('invalid')


class TestInitBinanceApi:
    @patch('binance.client.Client')
    def test_historical_mode(self, mock_client_cls):
        mock_client_cls.return_value = MagicMock()
        result = init_binance_api('historical', 'key', 'secret')
        mock_client_cls.assert_called_once_with('key', 'secret')
        assert result is not None

    @patch('binance.ThreadedWebsocketManager')
    def test_realtime_mode(self, mock_twm_cls):
        mock_twm_cls.return_value = MagicMock()
        result = init_binance_api('realtime', 'key', 'secret')
        mock_twm_cls.assert_called_once_with(
            api_key='key', api_secret='secret'
        )
        assert result is not None

    def test_invalid_mode_raises(self):
        with pytest.raises(AttributeError, match='historical'):
            init_binance_api('invalid', 'key', 'secret')
