class VolumeConfirmedMomentumCrossover:
    
    def __init__(self, volume_multiplier=1.2,
                 breakout_percentage=0.01,
                 short_term_momentum_threshold=0.005):
        
        '''
        Initialize the Volume Confirmed Momentum Crossover strategy.

        volume_multiplier | float | volume must exceed this multiple of average volume
        breakout_percentage | float | breakout threshold as a percentage of recent range
        short_term_momentum_threshold | float | minimum short-term price change for momentum
        '''
        
        self.volume_multiplier = volume_multiplier
        self.breakout_percentage = breakout_percentage
        self.short_term_momentum_threshold = short_term_momentum_threshold

    def run(self, ticker, accountant, price_usdt, timestamp):

        '''
        Execute the Volume Confirmed Momentum Crossover strategy.

        ticker | pandas dataframe | historical price data
        accountant | Accountant object | account information
        price_usdt | float | current price of the asset
        timestamp | datetime | current timestamp
        '''
        
        import numpy as np

        # Extract key features
        rolling_avg_short = ticker.loc[timestamp]['rolling_avg_10']
        rolling_avg_medium = ticker.loc[timestamp]['rolling_avg_15']
        rolling_avg_long = ticker.loc[timestamp]['rolling_avg_45']
        price_change_1h = ticker.loc[timestamp]['1h_change']
        price_change_24h = ticker.loc[timestamp]['24h_change']
        rolling_max_10 = ticker.loc[timestamp]['rolling_max_10']
        rolling_min_10 = ticker.loc[timestamp]['rolling_min_10']
        current_volume = ticker.loc[timestamp]['volume']
        avg_volume = ticker['volume'].rolling(window=45).mean().loc[timestamp]

        # Define thresholds dynamically
        volume_threshold = avg_volume * self.volume_multiplier
        breakout_threshold = (rolling_max_10 - rolling_min_10) * self.breakout_percentage

        # Trading logic
        if rolling_avg_short > rolling_avg_medium > rolling_avg_long:
            # Bullish momentum confirmed by short, medium, and long averages
            if price_change_1h > breakout_threshold and current_volume > volume_threshold and price_change_24h > 0.02:
                action = 'buy'
            else:
                action = 'hold'
        elif rolling_avg_short < rolling_avg_long:
            # Bearish trend: Short average below long
            if price_change_1h > self.short_term_momentum_threshold and price_usdt > np.mean(accountant.account['buy_price_usdt']) * 1.03:
                action = 'sell'
            else:
                action = 'hold'
        else:
            # Neutral zone
            action = 'hold'

        return action