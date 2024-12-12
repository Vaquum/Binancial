class Random:
    
    def run(self, ticker, accountant, price_usdt, timestamp):
        '''
        A random strategy that makes buy, sell, or hold decisions
        based on a coin toss.

        ticker | pandas dataframe | historical price data
        accountant | Accountant object | account information
        price_usdt | float | current price of the asset
        timestamp | datetime | current timestamp
        
        '''

        import random
        
        action = random.choice(['buy', 'sell', 'hold'])
        return action
    