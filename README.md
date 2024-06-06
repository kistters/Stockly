# Stockly
API to retrieve and aggregate stock data from external sources.



# start the project 
using makefile to organize the common task of project 
```shell
# start the proejct with docker-compose
$ make
```

# search by Stocks 
```shell
python3 polygon.py --stock_ticker AAPL
python3 googlefinance.py --stock_ticker AAPL
```