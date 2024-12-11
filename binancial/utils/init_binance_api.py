def init_binance_api(mode, api_key, api_secret):

    from binance import ThreadedWebsocketManager
    from binance.client import Client

    if mode == 'realtime':
        client = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)

    elif mode == 'historical':
        client = Client(api_key, api_secret)
    
    else:
        raise AttributeError("mode must be either 'historical' or 'realtime'")

    return client
