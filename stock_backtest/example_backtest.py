"""
Example backtesting a trading strategy.
"""

import datetime as dt
from Queue import Queue
from stock_backtest.data_handler import StockBacktestDataHandler
from stock_backtest.execution_handler import StockBacktestExecutionHandler
from stock_backtest.backtest import StockBacktest
from strategies.buy_strategy import BuyStrategy

events = Queue()
symbols = ['AAPL', 'MSFT']
start_date = dt.datetime(year=2012, month=1, day=1)
end_date = dt.datetime(year=2016, month=4, day=1)
data = StockBacktestDataHandler(events, symbols, start_date, end_date)
# execution = StockBacktestExecutionHandler(events)
strategy = BuyStrategy(events, data, initial_capital=1000000)
backtest = StockBacktest(events, strategy, data, execution, start_date, end_date)


results = backtest.run()

print results  # graph this