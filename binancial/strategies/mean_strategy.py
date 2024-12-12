def mean_strategy(ticker, accountant, price_usdt, timestamp):

    '''An example strategy for trading. Note that this can be
    replaced with any other trading strategy by following the same
    template.

    ticker | pandas dataframe | historical price data
    accountant | Accountant object | account information
    price_usdt | float | current price of the asset
    timestamp | datetime | current timestamp    
    
    '''
    
    import numpy as np
    
    if ticker.loc[timestamp]['rolling_avg_45'] > ticker.loc[timestamp]['rolling_avg_10']:
        action = 'buy'
    
    elif ticker.loc[timestamp]['rolling_avg_45'] < ticker.loc[timestamp]['rolling_avg_10']:
        if price_usdt > np.mean(accountant.account['buy_price_usdt']) * 1.01:
            action = 'sell'
        else:
            action = 'hold'

    else:
        action = 'hold'
       
    return action
