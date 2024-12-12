def get_all_pairs():

    '''Returns all available ticker pairs on Binance'''

    from ..utils.init_binance_api import init_binance_api

    client = init_binance_api(mode='historical')

    tickers = client.get_all_tickers()
    symbols = [i['symbol'] for i in tickers if 'USDT' in i['symbol']]

    return symbols
