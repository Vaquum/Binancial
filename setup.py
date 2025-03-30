from setuptools import setup, find_packages

setup(
    name='binancial',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'python-binance==1.0.28',
        'pandas==2.2.3',
        'numpy==1.26.4',
        'wrangle==0.7.6',
        'tqdm==4.67.1',
        'xgboost==2.0.3',
        'scikit-learn==1.4.1.post1',
    ],
    author='Mikko Kotila',
    description='A Binance API-wrapper that brings all klines and trades data end-points to single-line commands.',
    python_requires='>=3.9',
) 