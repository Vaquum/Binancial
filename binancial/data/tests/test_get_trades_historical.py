"""Tests for get_trades_historical function."""
import pytest
from unittest.mock import MagicMock, patch
import pandas as pd

from binancial.data.get_trades_historical import get_trades_historical


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    client = MagicMock()
    
    # Mock trades data with proper structure
    mock_trades_1 = [
        {'id': 1, 'price': '100', 'qty': '1', 'time': 1629283200000, 
         'isBuyerMaker': True, 'isBestMatch': True},
        {'id': 2, 'price': '101', 'qty': '2', 'time': 1629283300000, 
         'isBuyerMaker': False, 'isBestMatch': True},
    ]
    
    mock_trades_2 = [
        {'id': 3, 'price': '102', 'qty': '3', 'time': 1629283400000, 
         'isBuyerMaker': True, 'isBestMatch': True},
        {'id': 4, 'price': '103', 'qty': '4', 'time': 1629283500000, 
         'isBuyerMaker': False, 'isBestMatch': True},
    ]
    
    # Setup the mock to return different data for different calls
    client.get_historical_trades.side_effect = [
        mock_trades_1,
        mock_trades_2,
        []  # Empty list for any additional calls
    ]
    
    return client


@patch('binancial.data.get_trades_historical.get_colnames')
@patch('binancial.data.get_trades_historical.wr')
def test_get_trades_historical_default_limit(mock_wr, mock_get_colnames, mock_client):
    """Test get_trades_historical with default limit."""
    # Setup mocks
    mock_get_colnames.return_value = ['id', 'price', 'qty', 'time', 'buyer_is_maker']
    mock_wr.col_move_place.return_value = pd.DataFrame({
        'id': [1, 2], 
        'price': [100, 101], 
        'qty': [1, 2], 
        'time': [1629283200000, 1629283300000],
        'buyer_is_maker': [True, False]
    })
    
    # Call the function
    result = get_trades_historical(mock_client)
    
    # Assertions
    mock_client.get_historical_trades.assert_called_once()
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


@patch('binancial.data.get_trades_historical.get_colnames')
@patch('binancial.data.get_trades_historical.wr')
def test_get_trades_historical_pagination(mock_wr, mock_get_colnames, mock_client):
    """Test get_trades_historical with pagination (limit > 1000)."""
    # Setup mocks
    mock_get_colnames.return_value = ['id', 'price', 'qty', 'time', 'buyer_is_maker']
    mock_wr.col_move_place.return_value = pd.DataFrame({
        'id': [1, 2, 3, 4], 
        'price': [100, 101, 102, 103], 
        'qty': [1, 2, 3, 4], 
        'time': [1629283200000, 1629283300000, 1629283400000, 1629283500000],
        'buyer_is_maker': [True, False, True, False]
    })
    
    # Call the function with limit > 1000 to trigger pagination
    result = get_trades_historical(mock_client, limit=2500)
    
    # Assertions
    assert mock_client.get_historical_trades.call_count >= 2
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    
    # Verify fromId parameter was used for pagination
    args, kwargs = mock_client.get_historical_trades.call_args_list[1]
    assert 'fromId' in kwargs 