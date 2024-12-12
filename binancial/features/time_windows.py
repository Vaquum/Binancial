def time_windows(df):

    '''Adds time window related columns to a dataframe
    
    df | pandas dataframe | dataframe with 'close' column
    '''

    windows = [3, 5, 10, 15, 30, 45, 90, 180]

    # rolling averages
    for i in windows:

        df['rolling_avg_' + str(i)] = df['close'].rolling(i).mean().round(2)

    # rolling min
    for i in windows:

        df['rolling_min_' + str(i)] = df['close'].rolling(i).min().round(2)

    # rolling max
    for i in windows:

        df['rolling_max_' + str(i)] = df['close'].rolling(i).max().round(2)

    return df
