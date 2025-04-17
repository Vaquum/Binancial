# Changelog

## 14:45 on 14-08-2024

- Enhanced `get_trades_historical` function to support retrieving any number of trades using ID-based pagination
  - Added functionality to make multiple API calls when limit exceeds 1000
  - Maintains backward compatibility with existing implementation
  - Improved documentation to reflect new capability

## 15:23 on 19-03-2024

- Locked all package versions in setup.py and requirements.txt:
  - python-binance==1.0.28
  - pandas==2.2.3
  - numpy==1.26.4
  - wrangle==0.7.6
  - tqdm==4.67.1
  - xgboost==2.0.3
  - scikit-learn==1.4.1.post1 