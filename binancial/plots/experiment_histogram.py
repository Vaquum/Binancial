def experiment_histogram(backtest_object):

    '''Plots the results of a backtesting experiment
    as a histogram.
    
    backtest_object | object | BackTester object

    '''

    import astetik
    import numpy as np
    import pandas as pd

    data = backtest_object.profit_df

    mean_profit = data['profit'].mean().round(3)

    astetik.hist(data=data, 
                 x='profit_rate',
                 title='Mean Profit : ' + str(mean_profit) + '\%)',
                 bins=len(data))
