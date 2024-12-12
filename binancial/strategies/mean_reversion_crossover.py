class MeanReversionCrossover:
    def __init__(self, sell_threshold=1.01):
        '''
        Initialize the Mean Reversion Crossover strategy with parameters.

        sell_threshold | float | the threshold for selling an asset
        '''
        self.sell_threshold = sell_threshold

    def run(self, ticker, accountant, price_usdt, timestamp):
        '''
        Execute the trading logic for the strategy.

        ticker | pandas dataframe | historical price data
        accountant | Accountant object | account information
        price_usdt | float | current price of the asset
        timestamp | datetime | current timestamp
        '''

        import numpy as np

        if ticker.loc[timestamp]['rolling_avg_45'] > ticker.loc[timestamp]['rolling_avg_10']:
            action = 'buy'
        elif ticker.loc[timestamp]['rolling_avg_45'] < ticker.loc[timestamp]['rolling_avg_10']:
            if price_usdt > np.mean(accountant.account['buy_price_usdt']) * self.sell_threshold:
                action = 'sell'
            else:
                action = 'hold'
        else:
            action = 'hold'

        return action
    