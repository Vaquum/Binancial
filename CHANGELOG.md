# Changelog

## 15:23 on 19-03-2024

- Locked all package versions in setup.py and requirements.txt:
  - python-binance==1.0.28
  - pandas==2.2.3
  - numpy==1.26.4
  - wrangle==0.7.6
  - tqdm==4.67.1
  - xgboost==2.0.3
  - scikit-learn==1.4.1.post1

## 14:45 on 14-08-2024

- Enhanced `get_trades_historical` function to support retrieving any number of trades using ID-based pagination
  - Added functionality to make multiple API calls when limit exceeds 1000
  - Maintains backward compatibility with existing implementation
  - Improved documentation to reflect new capability

## v0.2.0

- Added `compute` module with `get_spot_klines` — builds 19-column klines from raw trades with OHLC, statistical measures, volume, maker metrics, and liquidity metrics
- Added datetime filtering (`YYYY-MM-DD HH:MM:SS`) to `get_trades_historical`
- Added parallel fetching with `ThreadPoolExecutor` for bulk trade retrieval (~4s per hour)
- Added rate-limit retry logic for Binance API (code -1003)
- Added partial kline removal to guarantee only complete data is returned
- Fixed pagination duplicates in `get_trades_historical` (off-by-one on `fromId`)
- Fixed `trade_id` precision loss (was cast to float, now stays int64)
- Fixed timezone handling — all datetime parsing and formatting now uses UTC
- Migrated from `setup.py` + `requirements.txt` to `pyproject.toml`
- Bumped Python minimum version to 3.12
- Added CI gates: style-gate (ruff), type-gate (pyright), test-gate (pytest), coverage-gate (>95%)
- Added automated release system via Claude AI
- Added documentation system contract and docs hub
- Added `nest_asyncio` to dependencies
- 38 tests, 95%+ coverage

## v0.2.1

- Relax the `pandas` dependency from the exact pin `pandas==2.2.3` to `pandas>=2.2.3,<3`. Binancial is used alongside `vaquum-limen` (currently `pandas>=2.3.1`) inside `vaquum-praxis`; with the exact pin, `pip` / `uv` couldn't satisfy both constraints and Praxis's CI dependency resolution was failing. A library-style range lets consumers resolve Binancial and Limen together without code change on either side.
- Sync runtime `__version__` in `binancial/__init__.py` with `pyproject.toml` (`0.2.0` → `0.2.1`) so both report the same version
- Reorder CHANGELOG to oldest-first / newest-at-bottom, matching the `vaquum-limen` / `vaquum-nexus` / `vaquum-praxis` convention

## v0.2.2

- Relax all remaining exact dependency pins to library-style ranges so Binancial can co-install with other Vaquum libraries (notably `vaquum-limen`) inside downstream applications. Every dep now uses a lower bound at the previously-pinned version with a conservative major-version upper cap where applicable:
  - `python-binance==1.0.28` → `python-binance>=1.0.28,<2`
  - `numpy==1.26.4` → `numpy>=1.26.4,<3` (allows numpy 2.x, which Limen requires)
  - `wrangle==0.7.6` → `wrangle>=0.7.6,<1`
  - `tqdm==4.67.1` → `tqdm>=4.67.0,<5` (floor lowered to match Limen)
  - `xgboost==2.0.3` → `xgboost>=2.0.3,<3`
  - `scikit-learn==1.4.1.post1` → `scikit-learn>=1.4.1` (no upper cap so Limen's `>=1.6.1` resolves)
  - `nest_asyncio==1.6.0` → `nest_asyncio>=1.6.0,<2`
  - `pandas` was already a range since v0.2.1
- Bump `__version__` and `pyproject.toml` version to 0.2.2
