import datetime as dt
from Queue import Queue
from backtest import StockBacktest
from data_handler import StockBacktestDataHandler
from execution_handler import StockBacktestExecutionHandler

events = Queue()
symbols = ['AAPL', 'MSFT']
start_date = dt.datetime(year=2011, month=1, day=1)
end_date = dt.datetime(year=2016, month=4, day=1)

strategy = None
data = StockBacktestDataHandler(events, symbols, start_date, end_date)
execution = StockBacktestExecutionHandler(events)
backtest = StockBacktest(events, strategy,data, execution, start_date, end_date, initial_capital=100000)

backtest.run()