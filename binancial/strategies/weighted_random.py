class WeightedRandom:

    def __init__(self, buy_weight=1, sell_weight=1, hold_weight=1):
        
        '''
        Initialize the Weighted Random strategy.

        buy_weight | int | weight for the 'buy' action
        sell_weight | int | weight for the 'sell' action
        hold_weight | int | weight for the 'hold' action
        '''
        
        self.weights = [buy_weight, sell_weight, hold_weight]

    def run(self, ticker, accountant, price_usdt, timestamp):
        
        '''
        A weighted random strategy that makes buy, sell, or hold decisions
        based on weighted probabilities.

        ticker | pandas dataframe | historical price data
        accountant | Accountant object | account information
        price_usdt | float | current price of the asset
        timestamp | datetime | current timestamp
        '''

        import random

        actions = ['buy', 'sell', 'hold']
        action = random.choices(actions, weights=self.weights, k=1)[0]
        return action
    