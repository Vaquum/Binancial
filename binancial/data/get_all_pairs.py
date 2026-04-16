from typing import Any


def get_all_pairs(client: Any) -> list[str]:

    '''Returns all available ticker pairs on Binance

    client | init_binance_api | historical client object
    '''

    tickers = client.get_all_tickers()
    symbols = [i['symbol'] for i in tickers if 'USDT' in i['symbol']]

    return symbols
