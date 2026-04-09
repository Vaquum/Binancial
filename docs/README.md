# Binancial Documentation

## Overview

Binancial is a Binance API wrapper that provides single-line commands for fetching market data and building custom klines from raw trades.

## Reading Order

### New Users

1. [README](../README.md) - what Binancial is, installation, quick start
2. [Guides](#guides) - workflows for common tasks

### Contributors

1. [Developer](Developer/Documentation-System.md) - documentation and contribution rules

## Guides

### Data Module

The `data` module wraps the four fundamental Binance API endpoints:

- `get_klines_historical` - fetch pre-aggregated candlestick data
- `get_trades_historical` - fetch individual trades with date-range filtering and pagination
- `get_klines_realtime` - stream live candlestick data to file
- `get_trades_realtime` - stream live trade data to file
- `get_all_pairs` - list all available USDT trading pairs

### Compute Module

The `compute` module builds derived data products from raw trades:

- `get_spot_klines` - aggregate raw trades into 19-column klines with OHLC, statistical measures, volume, maker metrics, and liquidity metrics

### Utils Module

The `utils` module provides shared helpers:

- `init_binance_api` - initialize Binance API client (historical or realtime mode)
- `get_colnames` - standardized column names for klines and trades data
- `add_klines_features` - add technical features to klines data

## Reference

### get_spot_klines Output Columns

| Column | Description |
|---|---|
| datetime | UTC-aware kline bucket timestamp |
| open | Price of first trade by trade_id |
| high | Maximum price |
| low | Minimum price |
| close | Price of last trade by trade_id |
| mean | Mean price |
| std | Population standard deviation of price |
| median | Median price |
| iqr | Interquartile range (Q75 - Q25) of price |
| volume | Sum of trade quantities |
| maker_ratio | Fraction of trades where buyer is maker |
| no_of_trades | Number of trades in the bucket |
| open_liquidity | Price x quantity of first trade |
| high_liquidity | Maximum price x quantity |
| low_liquidity | Minimum price x quantity |
| close_liquidity | Price x quantity of last trade |
| liquidity_sum | Sum of price x quantity |
| maker_volume | Sum of maker trade quantities |
| maker_liquidity | Sum of maker trade price x quantity |
