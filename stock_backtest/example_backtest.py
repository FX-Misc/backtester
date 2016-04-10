"""
Example backtesting a trading strategy.
"""
import tabulate
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from Queue import Queue
from stock_backtest.data_handler import StockBacktestDataHandler
from stock_backtest.execution_handler import StockBacktestExecutionHandler
from stock_backtest.backtest import StockBacktest
from strategies.buy_strategy import BuyStrategy
from pyfolio.pyfolio.tears import create_full_tear_sheet
from analytics.plotting import plot_holdings
# from pyfolio.pyfolio.plotting import plot_holdings

def run():
    events = Queue()
    symbols = ['AAPL', 'MSFT']
    start_date = dt.datetime(year=2012, month=1, day=1)
    end_date = dt.datetime(year=2012, month=1, day=31)
    data = StockBacktestDataHandler(events, symbols, start_date, end_date)
    execution = StockBacktestExecutionHandler(events)
    strategy = BuyStrategy(events, data, initial_capital=1000000)
    backtest = StockBacktest(events, strategy, data, execution, start_date, end_date)
    backtest.run()
    while(1):
        if(not backtest.continue_backtest):
            symbols = ['AAPL', 'MSFT']
            all_data = data.all_symbol_data
            results = pd.DataFrame(data=strategy.positions_series.values(), index=strategy.positions_series.keys())
            results['cash'] = strategy.cash_series.values()
            results['position_value'] = all_data['AAPL']['Open']*results['AAPL']
            results['value'] = results['cash'] + results['position_value']
            results['pnl'] = 100*results['value'].pct_change().fillna(0)
            results['returns'] = 1-results['value']/strategy.initial_capital
            # print tabulate.tabulate(results, headers='keys', tablefmt='pipe')

            returns = results['returns']
            holdings_fig = plt.figure()

            plt.show()
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

 # Parameters
 #    ----------
 #    returns : pd.Series
 #        Daily returns of the strategy, noncumulative.
 #         - Time series with decimal returns.
 #         - Example:
 #            2015-07-16    -0.012143
 #            2015-07-17    0.045350
 #            2015-07-20    0.030957
 #            2015-07-21    0.004902
 #    positions : pd.DataFrame, optional
 #        Daily net position values.
 #         - Time series of dollar amount invested in each position and cash.
 #         - Days where stocks are not held can be represented by 0 or NaN.
 #         - Non-working capital is labelled 'cash'
 #         - Example:
 #            index         'AAPL'         'MSFT'          cash
 #            2004-01-09    13939.3800     -14012.9930     711.5585
 #            2004-01-12    14492.6300     -14624.8700     27.1821
 #            2004-01-13    -13853.2800    13653.6400      -43.6375
 #    transactions : pd.DataFrame, optional
 #        Executed trade volumes and fill prices.
 #        - One row per trade.
 #        - Trades on different names that occur at the
 #          same time will have identical indicies.
 #        - Example:
 #            index                  amount   price    symbol
 #            2004-01-09 12:18:01    483      324.12   'AAPL'
 #            2004-01-09 12:18:01    122      83.10    'MSFT'
 #            2004-01-13 14:12:23    -75      340.43   'AAPL'
 #    gross_lev : pd.Series, optional
 #        The leverage of a strategy.
 #         - Time series of the sum of long and short exposure per share
 #            divided by net asset value.
 #         - Example:
 #            2009-12-04    0.999932
 #            2009-12-07    0.999783
 #            2009-12-08    0.999880
 #            2009-12-09    1.000283
 #    slippage : int/float, optional
 #        Basis points of slippage to apply to returns before generating
 #        tearsheet stats and plots.
 #        If a value is provided, slippage parameter sweep
 #        plots will be generated from the unadjusted returns.
 #        Transactions and positions must also be passed.
 #        - See txn.adjust_returns_for_slippage for more details.
 #    live_start_date : datetime, optional
 #        The point in time when the strategy began live trading,
 #        after its backtest period. This datetime should be normalized.
 #    hide_positions : bool, optional
 #        If True, will not output any symbol names.
 #    bayesian: boolean, optional
 #        If True, causes the generation of a Bayesian tear sheet.
 #    round_trips: boolean, optional
 #        If True, causes the generation of a round trip tear sheet.
 #    cone_std : float, or tuple, optional
 #        If float, The standard deviation to use for the cone plots.
 #        If tuple, Tuple of standard deviation values to use for the cone plots
 #         - The cone is a normal distribution with this standard deviation
 #             centered around a linear regression.
 #    bootstrap : boolean (optional)
 #        Whether to perform bootstrap analysis for the performance
 #        metrics. Takes a few minutes longer.
 #    set_context : boolean, optional
 #        If True, set default plotting style context.
 #         - See plotting.context().