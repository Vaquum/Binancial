def get_klines_realtime(stream, symbol, file_path):

    '''Starts a realtime streaming of trades onto a file.
    
    stream | init_binance_api | realtime stream object
    symbol | str | the symbol of the pair to be streamed
    file_path | str | the path to the file where the results are stored.
    
    NOTE: The columns written to the file are:

    - 'event_time'
    - 'kline_start_time'
    - 'kline_close_time'
    - 'first_trade_id'
    - 'last_trade_id'
    - 'open_price'
    - 'close_price'
    - 'high_price'
    - 'low_price'
    - 'base_asset_volume'
    - 'quote_asset_volume'
    - 'no_of_trades'
    
    '''
    
    import datetime as dt
    from ..utils.init_binance_api import init_binance_api

    f = open(file_path, 'a')

    stream.start()

    def handle_socket_message(msg):
        
        f.flush()
        
        try:
            event_time = dt.datetime.fromtimestamp(msg['E'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            kline_start_time = dt.datetime.fromtimestamp(msg['k']['t'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            kline_close_time = dt.datetime.fromtimestamp(msg['k']['T'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            first_trade_id = str(msg['k']['f'])
            last_trade_id = str(msg['k']['L'])
            open_price = msg['k']['o']
            close_price = msg['k']['c']
            high_price = msg['k']['h']
            low_price = msg['k']['l']
            base_asset_volume = msg['k']['v']
            quote_asset_volume = msg['k']['q']
            no_of_trades = str(msg['k']['n'])

            trade = ','.join([event_time,
                              kline_start_time,
                              kline_close_time,
                              first_trade_id,
                              last_trade_id,
                              open_price,
                              close_price,
                              high_price,
                              low_price,
                              base_asset_volume,
                              quote_asset_volume,
                              no_of_trades])

            f.write(trade + '\n')

        except Exception as error:

            print("MSG : " + str(msg))
            print("Exception : " + str(error))

            stream.stop_socket(stream)

    stream.start_kline_socket(callback=handle_socket_message,
                              symbol=symbol,
                              interval='1m')
    
    stream.join()
