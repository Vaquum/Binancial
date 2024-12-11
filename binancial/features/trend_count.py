def trend_count(data):
    
    '''Creates integer columns that keep count of how many
    consecutive samples rising or falling trend has
    continued
    
    data | pandas dataframe | data from get_historical_klines
    '''

    out = [] 
    count_true = 0
    count_false = 0

    for i in range(len(data)):

        if data.loc[i]['closed_higher'] == True:

            count_false = 0
            count_true += 1
            out.append([count_true, count_false])

        else:

            count_true = 0
            count_false += 1
            out.append([count_true, count_false])

    data['samples_rising'] = [i[0] for i in out]
    data['samples_falling'] = [i[1] for i in out]
    
    return data
