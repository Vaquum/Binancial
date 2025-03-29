from typing import Any
from datetime import datetime
import logging
import nest_asyncio
from contextlib import contextmanager
from pathlib import Path

def get_trades_realtime(stream: Any, symbol: str, file_path: str | Path) -> None:
    '''Starts a realtime streaming of trades onto a file.
    
    Args:
        stream: Binance API realtime stream object
        symbol: The symbol of the pair to be streamed
        file_path: The path to the file where the results are stored
    
    Returns:
        None
    
    Raises:
        ValueError: If input parameters are invalid
        IOError: If file operations fail
        Exception: For other unexpected errors
    
    Note:
        The columns written to the file are:
        - 'event_time'
        - 'trade_id'
        - 'price'
        - 'quantity'
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
            event_time = datetime.fromtimestamp(msg['E'] / 1000)
            event_time_str = event_time.strftime('%Y-%m-%d %H:%M:%S')
            price = round(float(msg['p']), 1)
            trade = f"{event_time_str},{msg['t']},{price},{msg['q']}"
            
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
            logger.info(f"Starting trade stream for {symbol}")
            stream.start()
            
            # Store socket id for proper cleanup
            socket_id = stream.start_trade_socket(
                callback=handle_socket_message,
                symbol=symbol
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
        logger.info("Trade stream ended")
