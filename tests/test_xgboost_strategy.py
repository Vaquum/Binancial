import pytest
import pandas as pd
import numpy as np
import warnings
from binancial.strategies.xgboost import XGBoostStrategy

@pytest.fixture
def sample_data():
    '''Create sample historical data for testing'''
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='H')
    n_samples = len(dates)
    
    # Create base price and volume data
    data = {
        'open_time': dates,
        'open': np.random.uniform(45000, 55000, n_samples),
        'high': np.random.uniform(45000, 55000, n_samples),
        'low': np.random.uniform(45000, 55000, n_samples),
        'close': np.random.uniform(45000, 55000, n_samples),
        'volume': np.random.uniform(100, 1000, n_samples),
        'close_time': dates + pd.Timedelta(hours=1),
        'qav': np.random.uniform(2000000, 3000000, n_samples),
        'num_trades': np.random.randint(1000, 5000, n_samples),
        'taker_base_vol': np.random.uniform(50, 500, n_samples),
        'taker_quote_vol': np.random.uniform(2000000, 3000000, n_samples),
        'ignore': 0
    }
    
    df = pd.DataFrame(data)
    
    # Add technical indicators
    df['rsi_14'] = 50 + np.random.uniform(-20, 20, n_samples)
    df['roc_12'] = np.random.uniform(-5, 5, n_samples)
    df['bb_upper_20'] = df['close'] + np.random.uniform(100, 500, n_samples)
    df['bb_middle_20'] = df['close']
    df['bb_lower_20'] = df['close'] - np.random.uniform(100, 500, n_samples)
    
    # MACD components
    df['macd_line'] = np.random.uniform(-100, 100, n_samples)
    df['macd_signal'] = np.random.uniform(-100, 100, n_samples)
    df['macd_histogram'] = df['macd_line'] - df['macd_signal']
    
    # EMAs
    df['ema_2'] = df['close'].ewm(span=2).mean()
    df['ema_3'] = df['close'].ewm(span=3).mean()
    df['ema_5'] = df['close'].ewm(span=5).mean()
    df['ema_10'] = df['close'].ewm(span=10).mean()
    df['ema_20'] = df['close'].ewm(span=20).mean()
    df['ema_40'] = df['close'].ewm(span=40).mean()
    df['ema_80'] = df['close'].ewm(span=80).mean()
    
    # Other indicators
    df['atr_14'] = np.random.uniform(100, 500, n_samples)
    df['cci_20'] = np.random.uniform(-100, 100, n_samples)
    
    # Ichimoku components
    df['ichimoku_conversion_line'] = df['close'] + np.random.uniform(-500, 500, n_samples)
    df['ichimoku_base_line'] = df['close'] + np.random.uniform(-500, 500, n_samples)
    df['ichimoku_a'] = df['close'] + np.random.uniform(-500, 500, n_samples)
    df['ichimoku_b'] = df['close'] + np.random.uniform(-500, 500, n_samples)
    
    # Price ratios and other metrics
    df['high_low_ratio'] = df['high'] / df['low']
    df['high_close_ratio'] = df['high'] / df['close']
    df['low_close_ratio'] = df['low'] / df['close']
    df['volatility'] = np.random.uniform(0, 0.1, n_samples)
    df['obv'] = np.cumsum(np.random.uniform(-1000, 1000, n_samples))
    df['volume_change'] = df['volume'].pct_change()
    
    # Fractals
    df['fractals_bearish_5'] = np.random.choice([True, False], n_samples)
    df['fractals_bullish_5'] = np.random.choice([True, False], n_samples)
    
    return df

@pytest.fixture
def strategy(sample_data):
    '''Create a strategy instance with sample data'''
    return XGBoostStrategy(historical_data=sample_data)

def test_strategy_initialization(sample_data):
    '''Test strategy initialization'''
    strategy = XGBoostStrategy(historical_data=sample_data)
    assert strategy.model is not None
    assert strategy.scaler is not None
    assert strategy.lookback_window == 10
    assert len(strategy.feature_columns) > 0
    assert strategy.is_fitted == True

def test_untrained_model_behavior():
    '''Test behavior when model is not trained'''
    strategy = XGBoostStrategy()  # Initialize without historical data
    assert strategy.is_fitted == False
    
    # Should issue a warning and return 'hold'
    with pytest.warns(RuntimeWarning, match='XGBoost model is not trained'):
        action = strategy.run(pd.DataFrame(), None, 50000, pd.Timestamp.now())
        assert action == 'hold'

def test_feature_preparation(strategy, sample_data):
    '''Test feature preparation'''
    features = strategy._prepare_features(sample_data)
    assert isinstance(features, np.ndarray)
    assert features.shape[1] == len(strategy.feature_columns)

def test_run_method(strategy, sample_data):
    '''Test run method returns valid action'''
    action = strategy.run(sample_data, None, 50000, pd.Timestamp.now())
    assert action in ['buy', 'sell', 'hold']

def test_insufficient_data_handling(strategy):
    '''Test handling of insufficient data'''
    small_data = pd.DataFrame({
        'open': [1, 2],
        'high': [1, 2],
        'low': [1, 2],
        'close': [1, 2],
        'volume': [100, 200]
    })
    action = strategy.run(small_data, None, 50000, pd.Timestamp.now())
    assert action == 'hold'

def test_missing_features_handling(strategy, sample_data):
    '''Test handling of missing feature columns'''
    incomplete_data = sample_data[['open', 'high', 'low', 'close', 'volume']].copy()
    action = strategy.run(incomplete_data, None, 50000, pd.Timestamp.now())
    assert action == 'hold' 