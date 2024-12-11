def mean_strategy(ticker, accountant, price_usdt, timestamp):
    
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