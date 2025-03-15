def trend_and_momentum(df):
    
    '''
    Generate trend and momentum features from the klines dataset.

    df | pandas DataFrame | Historical price data

    Returns a DataFrame with added features.
    '''

    import numpy as np

    # Ensure data is sorted by time
    df = df.sort_values('open_time')

    # 1. Exponential Moving Average (EMA)
    df['ema_10'] = df['close'].ewm(span=10, adjust=False).mean()
    df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()

    # 2. Momentum Indicator
    df['momentum'] = df['close'] - df['close'].shift(10)

    # 3. Relative Strength Index (RSI)
    df['gain'] = np.where(df['close'] > df['close'].shift(1), df['close'] - df['close'].shift(1), 0)
    df['loss'] = np.where(df['close'] < df['close'].shift(1), df['close'].shift(1) - df['close'], 0)
    avg_gain = df['gain'].rolling(window=14).mean()
    avg_loss = df['loss'].rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # 4. Average True Range (ATR)
    df['tr'] = np.maximum(df['high'] - df['low'], 
                          np.maximum(abs(df['high'] - df['close'].shift(1)), 
                                     abs(df['low'] - df['close'].shift(1))))
    df['atr'] = df['tr'].rolling(window=14).mean()

    # 5. Directional Movement Index (DMI)
    df['plus_dm'] = np.where((df['high'] - df['high'].shift(1)) > (df['low'].shift(1) - df['low']), 
                             np.maximum(df['high'] - df['high'].shift(1), 0), 0)
    df['minus_dm'] = np.where((df['low'].shift(1) - df['low']) > (df['high'] - df['high'].shift(1)), 
                              np.maximum(df['low'].shift(1) - df['low'], 0), 0)
    df['plus_di'] = 100 * (df['plus_dm'].rolling(window=14).mean() / df['atr'])
    df['minus_di'] = 100 * (df['minus_dm'].rolling(window=14).mean() / df['atr'])
    df['adx'] = 100 * (abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])).rolling(window=14).mean()

    # 6. Donchian Channel
    df['donchian_upper'] = df['high'].rolling(window=20).max()
    df['donchian_lower'] = df['low'].rolling(window=20).min()

    # 7. Trend Persistence
    rising, falling = 0, 0
    rising_trend, falling_trend = [], []
    for i in range(len(df)):
        if i > 0 and df['close'].iloc[i] > df['close'].iloc[i - 1]:
            rising += 1
            falling = 0
        elif i > 0 and df['close'].iloc[i] < df['close'].iloc[i - 1]:
            falling += 1
            rising = 0
        else:
            rising, falling = 0, 0
        rising_trend.append(rising)
        falling_trend.append(falling)
    df['trend_rising'] = rising_trend
    df['trend_falling'] = falling_trend

    # 8. Rate of Change (ROC)
    df['roc'] = (df['close'] - df['close'].shift(10)) / df['close'].shift(10) * 100

    # 9. Commodity Channel Index (CCI)
    df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
    df['cci'] = (df['typical_price'] - df['typical_price'].rolling(window=20).mean()) / (0.015 * df['typical_price'].rolling(window=20).std())

    # 10. Kaufman's Adaptive Moving Average (KAMA)
    df['kama'] = df['close'].ewm(span=10, adjust=False).mean()

    # 11. Stochastic Oscillator
    df['stoch_k'] = 100 * ((df['close'] - df['low'].rolling(window=14).min()) /
                           (df['high'].rolling(window=14).max() - df['low'].rolling(window=14).min()))
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

    # 12. Momentum Divergence
    df['momentum_divergence'] = df['momentum'] - df['roc']

    # 13. Chande Momentum Oscillator (CMO)
    df['gains'] = np.where(df['close'] > df['close'].shift(1), df['close'] - df['close'].shift(1), 0)
    df['losses'] = np.where(df['close'] < df['close'].shift(1), df['close'].shift(1) - df['close'], 0)
    df['cmo'] = 100 * (df['gains'].rolling(window=14).sum() - df['losses'].rolling(window=14).sum()) / (
            df['gains'].rolling(window=14).sum() + df['losses'].rolling(window=14).sum())

    # Drop intermediate columns if not needed
    df.drop(['tr', 'plus_dm', 'minus_dm', 'typical_price', 'gains', 'losses'], axis=1, inplace=True)

    return df
