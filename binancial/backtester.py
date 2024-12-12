class BackTester:

    def __init__(self,
                 data,
                 strategy,
                 n_tests=50,
                 samples_per_test=360,
                 start_usdt=10000):

        '''Performs a backtest based on historical data
        
        data | dataframe | historical binance klines data
        strategy | function | a function that describes the strategy to be used 
        n_tests | int | number of samples to be drawn from the data to repeat the test
        sample_per_test | int | number of samples (e.g. seconds) to draw for each test
        start_usd | int | the amount of USDT to perform each test with
        
        '''

        import pandas as pd
        import random
        import tqdm

        from .accountant import Accountant
        from .strategies.mean_strategy import mean_strategy
        from .plots.position_timeline import position_timeline

        # a list of dataframes, one per test
        self.account_dfs = []

        # a dataframe for profits from all tests
        self.profit_df = pd.DataFrame()

        profits_list = []

        for _ in tqdm.tqdm(range(n_tests)):
            
            start = random.choice(range(len(data)))
            end = start + samples_per_test

            # initiate a new Accountant for the test
            accountant = Accountant(start_usdt=start_usdt)

            for timestamp in data.index[start:end]:

                price_usdt = data.loc[timestamp]['open']

                if accountant.account['total_btc'][-1] == 0:
                    action = 'buy'

                else:
                    action = strategy(data, accountant, price_usdt, timestamp)

                accountant.update_account(action=action,
                                          timestamp=timestamp,
                                          amount=250,
                                          price_usdt=price_usdt)

                # update the Accountant id
                accountant.update_id()
            
            # produce the account data
            account_df = pd.DataFrame(accountant.account).set_index('id')
            account_df = account_df[1:]
            open_values = data.loc[account_df.timestamp][['open']]
            open_values.reset_index(inplace=True)
            open_values['open_time'] = open_values['open_time'].astype('O')
            account_df = account_df.merge(open_values, left_on='timestamp', right_on='open_time')
            account_df = account_df.drop('open_time', axis='columns')
            
            # add tally in USDT
            account_df['tally'] = (account_df['total_btc'] * account_df['open']) + account_df['total_usdt']
            account_df['tally'] = account_df['tally'].round(2)

            account_df.index.rename('test_id', inplace=True)

            # produce the profits data
            profit = (account_df['tally'][-1:] - 10000).round(2).values[0]
            profit_rate = round(profit / 10000 * 100, 3)
            
            # handle storing of data
            self.account_dfs.append(account_df)
            profits_list.append([profit, profit_rate])

        self.profit_df['profit'] = [i[0] for i in profits_list]
        self.profit_df['profit_rate'] = [i[1] for i in profits_list]
        self.profit_df.index.rename('test_id', inplace=True)
