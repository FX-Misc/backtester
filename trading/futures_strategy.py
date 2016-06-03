import collections
import numpy as np
import pandas as pd
import datetime as dt
from trading.strategy import Strategy
from cme_backtest.data_utils.quantgo_utils import _reindex_data
from futures_utils import get_base_symbol_from_symbol

class FuturesStrategy(Strategy):

    def __init__(self, events, data, products, initial_cash=0, continuous=True):
        super(FuturesStrategy, self).__init__(events, data, products, initial_cash)
        self.ticker_prods = {product.symbol: product for product in self.products}
        self.symbols = [product.symbol for product in self.products]

    def new_tick_update(self, market_event):
        """
        Automatically updates internals on new tick.
            Update:
            - pnl series
            - price_series (last_bar)
            - returns (series of cumulative PnL)
            - transactions (basically the fills)
            - positions series

        :param market_event: (MarketEvent)
        """
        self.curr_dt = market_event.dt
        self.last_bar = market_event.data

        # update the price series (we only want to store level_1 price/qty)
        for symbol in self.symbols:
            try:
                self.price_series[symbol].append(self.last_bar[symbol])
            except KeyError:
                self.price_series[symbol] = [self.last_bar[symbol]]

        # update the returns series

    def get_latest_bars(self, symbol, window, start=None):
        """
        Get data for a symbol from [start-window, start]

        :param symbol: (str)
        :param window: (pd.Timedelta)
        :param start: (pd.Timestamp / DateTime) defaults to self.curr_dt if None
        :return:
        """
        start = start if start is not None else self.curr_dt
        before = start - window
        return self.data.curr_day_data[symbol].truncate(before, start)


    def finished(self):
        self.log.info("Finished strategy {}".format(__name__))
        # for symbol_time_series in self.time_series.values():
        #     symbol_time_series.set_index('dt', inplace=True)

# self.time_series.ix[self.time_series_index] = self.curr_dt    # set the dt index
# self.time_series.append(market_event.data, ignore_index=True)
# display(self.time_series.iat[len(self.time_series):])
# self.time_series.iat[len(self.time_series):] = market_event.data
# print self.time_series.tail(1)
# self.last_bar = self.data.last_bar.copy()
# for product in self.products:
#     mkt_bid = self.last_bar[product.symbol]['level_1_price_buy']
#     mkt_ask = self.last_bar[product.symbol]['level_1_price_sell']
#     pos = self.positions[product.symbol]
#     self.time_series[product.symbol].loc[len(self.time_series[product.symbol])] = \
#         [self.curr_dt, mkt_bid, mkt_ask, pos, self.cash] + \
#         [0]*(len(self.time_series[product.symbol].keys())-5)

# add placeholder for any features that need to be calculates
# for product in self.products:
#     # self.time_series[product.symbol+'_mkt'].append((last_bar['level_1_price_buy'] + last_bar['level_1_price_sell']) / 2.)
#     mkt_price = (self.last_bar[product.symbol]['level_1_price_buy'] + self.last_bar[product.symbol]['level_1_price_sell'])/2.
#     pnl_ = self.cash + sum([self.positions[product.symbol] * product.tick_value * (self.last_bar[product.symbol]['level_1_price_buy']
#                             if self.positions[product.symbol] < 0
#                             else self.last_bar['level_1_price_sell']) for product.symbol in self.products])
#     # self.spread[sym].append(last_bar['level_1_price_sell'] - last_bar['level_1_price_buy'])
# def update_metrics(self):
#     last_bar = self.get_latest_bars(self.symbol, n=1)
#     pnl_ = self.cash + sum([self.pos[sym] * self.contract_multiplier[sym] *
#                             (last_bar['level_1_price_buy']
#                              if self.pos[sym] < 0 else
#                              last_bar['level_1_price_sell']) for sym in self.symbols])
#     self.pnl.append(pnl_)
#     self.time_series.append(self.cur_time)
#     for sym in self.symbols:
#         self.price_series[sym].append((last_bar['level_1_price_buy'] + last_bar['level_1_price_sell']) / 2.)
#         self.spread[sym].append(last_bar['level_1_price_sell'] - last_bar['level_1_price_buy'])
