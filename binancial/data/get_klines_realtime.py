from typing import Any
from datetime import datetime
import logging
import nest_asyncio
from pathlib import Path

def get_klines_realtime(stream: Any, symbol: str, file_path: str | Path, interval: str = '1m') -> None:
    '''Starts a realtime streaming of klines (candlesticks) onto a file.
    
    Args:
        stream: Binance API realtime stream object
        symbol: The symbol of the pair to be streamed
        file_path: The path to the file where the results are stored
        interval: Kline interval (default: '1m')
    
    Returns:
        None
    
    Raises:
        ValueError: If input parameters are invalid
        IOError: If file operations fail
        Exception: For other unexpected errors
    
    Note:
        The columns written to the file are:
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
    
    # Input validation
    if not isinstance(symbol, str) or not symbol:
        raise ValueError('Symbol must be a non-empty string')
    if not isinstance(file_path, (str, Path)) or not file_path:
        raise ValueError('File path must be a non-empty string or Path')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Apply nest_asyncio for async compatibility
    nest_asyncio.apply()
    
    # Initialize socket id for proper cleanup
    socket_id = None
    
    def handle_socket_message(msg: dict[str, Any]) -> None:
        try:
            event_time = datetime.fromtimestamp(msg['E'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            kline_start_time = datetime.fromtimestamp(msg['k']['t'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            kline_close_time = datetime.fromtimestamp(msg['k']['T'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            first_trade_id = str(msg['k']['f'])
            last_trade_id = str(msg['k']['L'])
            open_price = msg['k']['o']
            close_price = msg['k']['c']
            high_price = msg['k']['h']
            low_price = msg['k']['l']
            base_asset_volume = msg['k']['v']
            quote_asset_volume = msg['k']['q']
            no_of_trades = str(msg['k']['n'])

            trade = ','.join([
                event_time,
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
                no_of_trades
            ])

            file.write(trade + '\n')
            file.flush()  # Ensure data is written immediately
            
        except Exception as error:
            logger.error(f"Error processing message: {error}")
            logger.error(f"Message content: {msg}")
            if socket_id:
                stream.stop_socket(socket_id)
            raise
    
    try:
        # Open file with context manager
        with open(file_path, 'a') as file:
            logger.info(f"Starting kline stream for {symbol} with interval {interval}")
            stream.start()
            
            # Store socket id for proper cleanup
            socket_id = stream.start_kline_socket(
                callback=handle_socket_message,
                symbol=symbol,
                interval=interval
            )
            
            stream.join()
            
    except IOError as io_error:
        logger.error(f"File operation failed: {io_error}")
        if socket_id:
            stream.stop_socket(socket_id)
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error: {error}")
        if socket_id:
            stream.stop_socket(socket_id)
        raise
    
    finally:
        logger.info("Kline stream ended")