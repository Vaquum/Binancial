def get_trades_realtime(stream, symbol, file_path):

    '''Starts a realtime streaming of trades onto a file.
    
    stream | init_binance_api | realtime stream object
    symbol | str | the symbol of the pair to be streamed
    file_path | str | the path to the file where the results are stored.
    
    NOTE: The columns written to the file are:

    - 'event_time'
    - 'trade_id`
    - 'price'
    - 'quantity'
    
    '''

    import datetime as dt
    
    f = open(file_path, 'a')
    
    stream.start()

    def handle_socket_message(msg):

        try:
            event_time = dt.datetime.fromtimestamp(msg['E'] / 1000)
            event_time = event_time.strftime('%Y-%m-%d %H:%M:%S')
            
            price = round(float(msg['p']), 1)

            trade = f"{event_time},{msg['t']},{price},{msg['q']}"
            
            f.write(trade + '\n')
        
        except Exception as error:

            print("MSG : " + str(msg))
            print("Exception : " + str(error))

            stream.stop_socket(stream)

    stream.start_trade_socket(callback=handle_socket_message, symbol=symbol)
    
    stream.join()
