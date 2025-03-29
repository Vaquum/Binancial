import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
import warnings


class XGBoostStrategy:
    
    def __init__(self, historical_data=None, lookback_window=10):
        '''
        Initialize the XGBoost strategy.
        
        historical_data | pandas dataframe | historical price data for training
        lookback_window | int | number of previous candles to use for prediction
        '''
        self.lookback_window = lookback_window
        self.model = XGBClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        
        # Selected features for the model
        self.feature_columns = [
            # Price action and volume
            'high_low_ratio',      # Price range
            'high_close_ratio',    # Upper wick
            'low_close_ratio',     # Lower wick
            'volume_change',       # Volume dynamics
            'obv',                 # On Balance Volume
            
            # Momentum indicators
            'rsi_14',             # Relative Strength Index
            'roc_12',             # Rate of Change
            'macd_line',          # MACD components
            'macd_signal',
            'macd_histogram',
            'cci_20',             # Commodity Channel Index
            
            # Trend indicators
            'ema_2',              # Multiple timeframe EMAs
            'ema_5',
            'ema_10',
            'ema_20',
            'ema_40',
            'ema_80',
            
            # Volatility indicators
            'volatility',
            'atr_14',             # Average True Range
            'bb_upper_20',        # Bollinger Bands
            'bb_middle_20',
            'bb_lower_20',
            
            # Ichimoku components
            'ichimoku_conversion_line',
            'ichimoku_base_line',
            'ichimoku_a',
            'ichimoku_b',
            
            # Fractal patterns
            'fractals_bearish_5',
            'fractals_bullish_5'
        ]
        
        if historical_data is not None:
            self._train_model(historical_data)
    
    def _prepare_features(self, ticker):
        '''
        Prepare features from the input data.
        
        ticker | pandas dataframe | historical price data with pre-calculated features
        '''
        # Select features and handle missing values
        features = ticker[self.feature_columns].copy()
        features = features.fillna(method='ffill').fillna(0)
        
        # Convert boolean columns to int
        bool_columns = ['fractals_bearish_5', 'fractals_bullish_5']
        for col in bool_columns:
            if col in features.columns:
                features[col] = features[col].astype(int)
        
        # Scale features
        return self.scaler.fit_transform(features.values)
    
    def _create_labels(self, df):
        '''Create trading signals based on future returns'''
        future_returns = df['close'].pct_change().shift(-1)
        threshold = 0.001  # 0.1% threshold
        
        labels = np.where(future_returns > threshold, 'buy',
                np.where(future_returns < -threshold, 'sell', 'hold'))
        return labels[:-1]  # Remove last row as we don't have future data for it
    
    def _train_model(self, historical_data):
        '''Train the XGBoost model with historical data'''
        features = self._prepare_features(historical_data)
        labels = self._create_labels(historical_data)
        
        # Remove last row and NaN values
        valid_idx = ~np.isnan(features).any(axis=1)
        features = features[valid_idx][:-1]
        labels = labels[valid_idx]
        
        self.model.fit(features, labels)
        self.is_fitted = True
    
    def run(self, ticker, accountant, price_usdt, timestamp):
        '''
        Make trading decisions using the trained XGBoost model.
        
        ticker | pandas dataframe | historical price data
        accountant | Accountant object | account information
        price_usdt | float | current price of the asset
        timestamp | datetime | current timestamp
        '''
        if not self.is_fitted:
            warnings.warn('XGBoost model is not trained. Please provide historical_data during initialization or call _train_model() before using the strategy.', RuntimeWarning)
            return 'hold'
            
        if len(ticker) < self.lookback_window:
            return 'hold'  # Not enough data
            
        try:
            features = self._prepare_features(ticker)
            
            if np.isnan(features[-1]).any():
                return 'hold'  # Invalid features
                
            prediction = self.model.predict(features[-1].reshape(1, -1))[0]
            return prediction
        except KeyError:
            # If any required feature columns are missing
            return 'hold' 