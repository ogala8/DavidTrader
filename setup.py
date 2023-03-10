import setuptools

with open("README.md") as file:
    read_me_description = file.read()

setuptools.setup(
    name="DavidTrader",
    version="0.1",
    author="Omar Galarraga",
    author_email="omar.galarraga@polesante.eu",
    description="Backtest and trading bot with Machine Learning",
    long_description=read_me_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ogala8/DavidTrader.git",
    keywords=['trading','machine learning', 'backtesting'],
    packages=['DavidTrader'],
    include_package_data=True, 
    install_requires = [
        'Flask>=1.1.2',
        'Flask-Caching',
        'pandas>=1.4.4',
        'werkzeug>=2.0.3',    
        'numpy',
        'backtrader',
        'yfinance',
        'scikit-learn',
        'matplotlib',
        'TA-Lib',
        'ta',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.9',
)