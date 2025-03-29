from setuptools import setup, find_packages

setup(
    name='binancial',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'python-binance',
        'pandas',
        'numpy',
        'wrangle',
        'tqdm',
        'xgboost==2.0.3',
        'scikit-learn==1.4.1.post1',
    ],
    author='Mikko Kotila',
    description='A trading bot framework for Binance',
    python_requires='>=3.12',
) 