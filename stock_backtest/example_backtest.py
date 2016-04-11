import tabulate
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import analytics.tears as tears
from Queue import Queue
from utils.stock import Stock
from stock_backtest.data_handler import StockBacktestDataHandler
from stock_backtest.execution_handler import StockBacktestExecutionHandler
from stock_backtest.backtest import StockBacktest
from strategies.buy_strategy import BuyStrategy
import analytics.plotting as plot
from analytics.plotting import plot_holdings
# from pyfolio.pyfolio.plotting import plot_holdings

def run():
    events = Queue()
    products = [Stock('AAPL'), Stock('MSFT')]
    symbols = [product.symbol for product in products]
    start_date = dt.datetime(year=2012, month=1, day=1)
    end_date = dt.datetime(year=2016, month=1, day=10)
    data = StockBacktestDataHandler(events, symbols, start_date, end_date)
    execution = StockBacktestExecutionHandler(events)
    strategy = BuyStrategy(events, data, products, initial_cash=100000)
    backtest = StockBacktest(events, strategy, data, execution, start_date, end_date)
    backtest.run()
    while(1):
        if(not backtest.continue_backtest):
            print tabulate.tabulate(strategy.time_series, headers='keys', tablefmt='pipe')
            # returns = results['returns']
            # holdings_fig = plt.figure()
            # for i in range(len(symbols)):
            #     symbol = symbols[i]
            #     positions = pd.DataFrame(data=np.array([results[symbol], results['cash']]).transpose(),
            #                              index=results.index,
            #                              columns=[symbol, 'cash'])
            #     ax = holdings_fig.add_subplot(len(symbols), 1, i+1)
            #     plot_holdings(returns, positions, ax=ax)
            # rolling_returns = fig.add_subplot(1,1,1)
            # plot.plot_rolling_returns(strategy.time_series['returns'], ax=rolling_returns)
            # plt.show()
            tears.create_returns_tear_sheet(strategy.time_series['returns'])
            break

def plot_all_holdings(symbols):
    holdings_fig = plt.figure()
    for i in range(len(symbols)):
        symbol = symbols[i]
        positions = pd.DataFrame(data=np.array([results[symbol], results['cash']]).transpose(),
                                 index=results.index,
                                 columns=[symbol, 'cash'])
        ax = holdings_fig.add_subplot(len(symbols), 1, i+1)
        plot_holdings(returns, positions, ax=ax)

if __name__ == "__main__":
    run()
