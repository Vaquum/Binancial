def is_day_highlow(data):

    '''Creates columns with boolean value that says if the sample is
    the highest or lowest of the day.
    
    data | pandas dataframe | data from get_historical_klines
    '''

    day_min = data[['date', 'low']].groupby('date').min()

    out = []

    for i in range(len(data)):
        if day_min.loc[data.iloc[i]['open_time'].strftime('%Y-%m-%d')]['low'] == data.iloc[i]['low']:
            out.append(True)
        else:
            out.append(False)

    data['day_lowest'] = out

    day_max = data[['date', 'high']].groupby('date').max()

    out = []

    for i in range(len(data)):
        if day_max.loc[data.iloc[i]['open_time'].strftime('%Y-%m-%d')]['high'] == data.iloc[i]['high']:
            out.append(True)
        else:
            out.append(False)

    data['day_highest'] = out

    return data
