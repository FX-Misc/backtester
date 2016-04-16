import datetime as dt
from Queue import Queue
from trading.stock import Stock
from stock_backtest.data_handler import StockBacktestDataHandler
from stock_backtest.execution_handler import StockBacktestExecutionHandler
from stock_backtest.backtest import StockBacktest
from strategies.buy_strategy import BuyStrategy
from bokeh.client import push_session
from bokeh.plotting import figure, curdoc, vplot


p = figure(toolbar_location=None) # x_range=(0, 100), y_range=(0, 100), toolbar_location=None)
p.border_fill_color = 'black'
p.background_fill_color = 'black'
p.outline_line_color = None
p.grid.grid_line_color = None
r = p.line(x=[], y=[])
ds = r.data_source
session = push_session(curdoc())
# create a callback that will add a number in a random location
def callback(x_val, y_val):
    ds.data['x'].append(x_val)
    ds.data['y'].append(y_val)
    # ds.data['text_color'].append(RdYlBu3[i%3])
    # ds.data['text'].append(str(i))
    ds.trigger('data', ds.data, ds.data)

curdoc().add_periodic_callback(callback, 50)
session.show() # open the document in a browser
events = Queue()
products = [Stock('MSFT'), Stock('ORCL')]
symbols = [product.symbol for product in products]
start_date = dt.datetime(year=2012, month=1, day=1)
end_date = dt.datetime(year=2016, month=1, day=10)
data = StockBacktestDataHandler(events, symbols, start_date, end_date, callback)
execution = StockBacktestExecutionHandler(events)
strategy = BuyStrategy(events, data, products, initial_cash=100000)
backtest = StockBacktest(events, strategy, data, execution, start_date, end_date)
backtest.run()
# session.loop_until_closed() # run forever