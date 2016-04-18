from flask import Flask, render_template
from bokeh.embed import components
import datetime as dt
from Queue import Queue
from trading.stock import Stock
from stock_backtest.data_handler import StockBacktestDataHandler
from stock_backtest.execution_handler import StockBacktestExecutionHandler
from stock_backtest.backtest import StockBacktest
from strategies.buy_strategy_stock import BuyStrategy
from bokeh.client import push_session
from bokeh.plotting import figure, curdoc, vplot
from bokeh.models import Button
app = Flask(__name__)

# p.background_fill_color = 'white'
# p.outline_line_color = 'black'
# p.grid.grid_line_color = 'gray'
# r = p.line(x=[], y=[])
# ds = r.data_source
# session = push_session(curdoc())
# # create a callback that will add a number in a random location
# def callback(x_val, y_val):
#     ds.data['x'].append(x_val)
#     ds.data['y'].append(y_val)
#     ds.trigger('data', ds.data, ds.data)
# curdoc().add_periodic_callback(callback, 50)
# add a button widget and configure with the call back
# button = Button(label="Press Me")
# button.on_click(callback)
# put the button and plot in a layout and add to the document
# curdoc().add_root(vplot(button, p))
# session.show() # open the document in a browser


@app.route('/')
def index():
    p = figure(x_axis_type="datetime", toolbar_location=None)

    script, div = components(p)
    # script = 'test1'
    # div = 'test2'
    return render_template('sandbox.html', script=script, div=div)

if __name__ == '__main__':
    app.run()

