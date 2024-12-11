def datetime_related(df):

    df['weekday'] = [i.dayofweek + 1 for i in df['open_time']]
    df['hour'] = [i.hour + 1 for i in df['open_time']]
    df['date'] = [i.strftime('%Y-%m-%d') for i in df['open_time']]
    df['hour@day'] = df['hour'].astype(str) + '@' + df['weekday'].astype(str)

    return df