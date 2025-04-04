def add_klines_features(df):

    '''Add various features to the klines data
    
    df | pandas dataframe | klines data
    '''    
    
    import wrangle as wr

    from ..features.trend_and_momentum import trend_and_momentum
    from ..features.is_day_highlow import is_day_highlow
    from ..features.price_changes_related import price_changes_related
    from ..features.datetime_related import datetime_related
    from ..features.time_windows import time_windows

    # all the datetime related
    df = datetime_related(df)

    # all the price changes related
    df = price_changes_related(df)

    # analyze trend and momentum of the samples
    df = trend_and_momentum(df)

    # if the sample is day highest or lowest
    df = is_day_highlow(df)

    # add various time windows related columns
    df = time_windows(df)

    # cleanup column order
    df = wr.col_move_place(df, 'hour')
    df = wr.col_move_place(df, 'weekday')
    df = wr.col_move_place(df, 'date')
    df = wr.col_move_place(df, 'open_time')

    return df
