def price_changes_related(df):

    '''Adds price changes related columns to a dataframe

    df | pandas dataframe | dataframe with 'close' column
    '''

    # percentile changes per time window
    df['1h_change'] = (df['close'].pct_change() * 100).round(2)
    df['2h_change'] = (df['close'].pct_change(2) * 100).round(2)
    df['4h_change'] = (df['close'].pct_change(4) * 100).round(2)
    df['8h_change'] = (df['close'].pct_change(8) * 100).round(2)
    df['12h_change'] = (df['close'].pct_change(12) * 100).round(2)
    df['24h_change'] = (df['close'].pct_change(24) * 100).round(2)

    # percentile change from previous close
    df['close_pct_change'] = (df[['close']].pct_change() * 100).round(2)

    # absolute difference from previous close
    df['close_diff'] = df['close'].diff()

    # if closed higher than previous sample
    df['closed_higher'] = df['close_pct_change'] > 0

    return df
