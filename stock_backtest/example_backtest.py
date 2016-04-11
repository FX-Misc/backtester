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
    products = [Stock('XOM'), Stock('GE')]
    symbols = [product.symbol for product in products]
    start_date = dt.datetime(year=2012, month=1, day=1)
    end_date = dt.datetime(year=2013    , month=1, day=10)
    data = StockBacktestDataHandler(events, symbols, start_date, end_date)
    execution = StockBacktestExecutionHandler(events)
    strategy = BuyStrategy(events, data, products, initial_cash=100000)
    backtest = StockBacktest(events, strategy, data, execution, start_date, end_date)
    time_series = backtest.run()
    # print tabulate.tabulate(strategy.time_series, headers='keys', tablefmt='pipe')
    # holdings_fig = plt.figure()
    # for i in range(len(symbols)):
    #     symbol = symbols[i]
    #     positions = pd.DataFrame(data=np.array([strategy.time_series[symbol+'_val'], strategy.time_series['cash']]).transpose(),
    #                              index=strategy.time_series.index,
    #                              columns=[symbol, 'cash'])
    #     ax = holdings_fig.add_subplot(len(symbols), 1, i+1)
    #     plot_holdings(strategy.time_series['returns'], positions, ax=ax)
    plt.ioff()
    positions_cols = [product.symbol+'_val' for product in products] + ['cash']
    positions = pd.DataFrame(np.array([strategy.time_series[product.symbol+'_val'] for product in products]
                             + [strategy.time_series['cash']]).transpose(), columns=positions_cols,
                             index=strategy.time_series.index)
    # positions_tear = tears.create_position_tear_sheet(strategy.time_series['returns'], positions, return_fig=True)
    returns_tear = tears.create_returns_tear_sheet(strategy.time_series['returns'], return_fig=True)
    # positions_tear.savefig('positions.png', dpi=800)
    returns_tear.savefig('returns.png', dpi=800)

if __name__ == "__main__":
    run()
