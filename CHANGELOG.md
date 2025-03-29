# Changelog

## 15:23 on 19-03-2024

### Added
- New XGBoost trading strategy implementation
- Added xgboost and scikit-learn dependencies
- Technical indicators (RSI, SMA) for feature engineering

### Changed
- Updated requirements.txt with new dependencies

## 15:35 on 19-03-2024

### Changed
- Modified XGBoost strategy to use pre-calculated features
- Enhanced feature set to include comprehensive technical indicators
- Improved error handling for missing features
- Updated test suite with more realistic test data

## 15:45 on 19-03-2024

### Added
- Added model training status tracking
- Added warning message for untrained model usage
- Added new test for untrained model behavior

### Fixed
- Fixed NotFittedError when using untrained XGBoost model

## 15:55 on 19-03-2024

### Changed
- Updated XGBoost strategy to use actual available technical indicators
- Added support for Ichimoku Cloud components
- Added support for MACD components
- Added support for multiple timeframe EMAs
- Added support for Bollinger Bands
- Added support for fractal patterns
- Updated test suite with actual indicator data 