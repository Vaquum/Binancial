def get_colnames(cols_for='klines'):

    '''Get column names for klines or trades data'''

    if cols_for == 'klines':

        colnames = ['open_time',
                    'open',
                    'high',
                    'low',
                    'close',
                    'volume',
                    'close_time', 
                    'qav',
                    'num_trades',
                    'taker_base_vol', 
                    'taker_quote_vol',
                    'ignore']

    elif cols_for == 'trades':

        colnames = ['trade_id',
                    'price',
                    'quantity',
                    'quote_quantity',
                    'time',
                    'buyer_is_maker']

    return colnames