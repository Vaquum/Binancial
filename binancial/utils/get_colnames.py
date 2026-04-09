def get_colnames(cols_for: str = 'klines') -> list[str]:

    '''Get column names for klines or trades data'''

    if cols_for == 'klines':
        return ['open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'qav', 'num_trades', 'taker_base_vol',
                'taker_quote_vol', 'ignore']

    if cols_for == 'trades':
        return ['trade_id', 'price', 'quantity', 'quote_quantity',
                'time', 'buyer_is_maker']

    msg = f"cols_for must be 'klines' or 'trades', got {cols_for!r}"
    raise ValueError(msg)