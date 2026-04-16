<h1 align="center">
  <br>
  <a href="https://github.com/Vaquum"><img src="https://github.com/Vaquum/Home/raw/main/assets/Logo.png" alt="Vaquum" width="150"></a>
  <br>
</h1>

<h3 align="center">Binancial</h3>

<!-- Replace the title of the repository -->

<p align="center">
  <a href="#description">Description</a> •
  <a href="#owner">Owner</a> •
  <a href="#integrations">Integrations</a> •
  <a href="#docs">Docs</a>
</p>
<hr>

## Description

A Binance API wrapper that brings all klines and trades data endpoints to single-line commands. Builds custom klines from raw trades with 19-column output including OHLC, statistical measures, volume, maker metrics, and liquidity metrics.

### What Binancial Is

- A thin, reliable wrapper around the Binance REST API
- A compute layer that aggregates raw trades into custom klines
- A package that handles pagination, rate limits, and data formatting

### What Binancial Is Not

- Not a trading bot or strategy executor
- Not a real-time streaming framework (though it wraps the streaming endpoints)
- Not a database or data warehouse

### Features

- Fetch historical klines data with simple commands
- Retrieve any number of historical trades with datetime filtering and pagination
- Build 19-column custom klines from raw trades (replicates ClickHouse-style aggregation)
- Parallel fetching with rate-limit retry for reliable bulk data retrieval
- Clean data formatting with consistent column names and proper data types

### Quick Start

```python
from binancial.utils import init_binance_api
from binancial.compute import get_spot_klines

client = init_binance_api('historical', api_key='', api_secret='')

# Build 1-second klines from the last hour of trades
df = get_spot_klines(client, symbol='BTCUSDT', kline_size=1,
                     start_date='2025-01-01 00:00:00',
                     end_date='2025-01-01 01:00:00')
```

## Owner

- [@mikkokotila](https://github.com/mikkokotila)

## Docs

- [Documentation Hub](docs/README.md)
- [Documentation System Contract](docs/Developer/Documentation-System.md)
