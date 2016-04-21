import numpy as np
import pandas as pd
from cme_backtest.data_utils.quantgo_utils import _reindex_data
from trading.events import OrderEvent
from abc import ABCMeta, abstractmethod


class Strategy(object):

    __metaclass__ = ABCMeta

    def __init__(self, events, data, products, initial_cash, *args, **kwargs):
        """
        The Strategy is an ABC that presents an interface for taking market data and
        generating corresponding OrderEvents which are sent to the ExecutionHandler.

        :param events: (Queue)
        :param data: (DataHandler)
        :param products: (list) (FuturesContract)
        :param initial_cash: (float)
        :param args:
        :param kwargs:
        """
        self.events = events
        self.data = data
        self.products = products
        self.curr_dt = None
        self.positions = {product.symbol: 0 for product in self.products}
        self.positions_series = {product.symbol: pd.DataFrame(data=None, columns=['dt', 'pos'])
                                 for product in self.products}
        self.transactions_series = pd.DataFrame(data=None, columns=['dt', 'amount', 'price', 'symbol'])
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.curr_pnl = 0
        self.last_bar = None
        self.initialize(*args, **kwargs)

    def order(self, product, quantity, order_type='MARKET', price=None, order_time=None):
        """
        Generate an order and place it into events.
        :param product: (FuturesContract)
        :param order_type: (str) 'MARKET' or 'LIMIT'
        :param quantity: (int)
        :param price: (float)
        :param order_time: (DateTime)
        """
        order = OrderEvent(product, quantity, order_type, price, order_time)
        self.events.put(order)

    @abstractmethod
    def new_tick_update(self, market_event):
        """
        Internal updates on new tick.
        Updates positions, values, time series, returns, etc.
        :param market_event: (MarketEvent)
        """
        raise NotImplementedError('Strategy.new_tick_update()')

    @abstractmethod
    def new_tick(self):
        """
        Call back for when the strategy receives a new tick.
        self.last_bar is automatically updated before this.
        """
        raise NotImplementedError('Strategy.new_tick()')

    def new_fill_update(self, fill_event):
        """
        Updates positions.
        :param fill_event: (FillEvent)
        """
        self.positions[fill_event.symbol] += fill_event.quantity
        self.cash -= fill_event.fill_cost
        self.transactions_series[fill_event.symbol].loc[len(self.transactions_series)] = \
            [fill_event.fill_time, fill_event.quantity, fill_event.fill_price, fill_event.symbol]

    @abstractmethod
    def new_fill(self, fill_event):
        """
        Call back for when an order placed by the strategy is filled.
        self.positions, self.cash, and self.transactions_series are all automatically updated before this.
        :param fill_event: (FillEvent)
        :return:
        """
        raise NotImplementedError("Strategy.new_fill()")

    @abstractmethod
    def finished(self):
        """
        Call back for when a backtest (or live-trading) is finished.
        Creates the time_series (DataFrame)
        """
        raise NotImplementedError("Strategy.finished()")

    def initialize(self, *args, **kwargs):
        """
        Initialize the strategy
        """
        pass

    # @abstractmethod
    # def new_day(self, event):
    #     """
    #     Call back for when the strategy receives a tick that is a new day.
    #     :param event:
    #     :return:
    #     """
    #     raise NotImplementedError("new_day()")


class FuturesStrategy(Strategy):

    def __init__(self, events, data, products, initial_cash=0, continuous=True):
        super(FuturesStrategy, self).__init__(events, data, products, initial_cash)
        self.cash_series = pd.Series(data=None)
        self.positions_series = {product.symbol: pd.Series(data=None) for product in self.products}
        self.transactions_series = {product.symbol: pd.DataFrame(data=None,
                                                                 columns=['dt', 'amount', 'price', 'symbol'])
                                    for product in self.products}
        # self.time_series = {product.symbol: pd.DataFrame(data=None,
        #                                                  columns=['dt', 'level_1_price_buy', 'level_1_price_sell'])
        #                     for product in self.products}
        # self.time_series = None
        # self.time_series = _reindex_data(self.time_series)
        self.time_series = {product.symbol: pd.DataFrame(data=None, columns=['dt', 'level_1_price_buy', 'level_1_price_sell'])
                for product in self.products}
        self.time_series = _reindex_data(self.time_series)
        reform = {(outerKey, innerKey): values for outerKey, innerDict in self.time_series.iteritems()
                  for innerKey, values in innerDict.iteritems()}
        self.time_series = pd.DataFrame(reform).ffill()


    def new_tick_update(self, market_event):
        """
            Update:
            - price_series (last_bar)
            - returns (series of decimal of cumulative PnL)
            - transactions (basically the fills)
            - positions series
        :param market_event:
        :return:
        """
        self.curr_dt = market_event.dt
        self.last_bar = market_event.data
        self.time_series.loc[len(self.time_series)] = market_event.data
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

    def finished(self):
        pass
        # for symbol_time_series in self.time_series.values():
        #     symbol_time_series.set_index('dt', inplace=True)

    def get_latest_bars(self, symbol, n=1):
#         TODO: use datetime window instead
        if len(self.time_series[symbol]) < n:
            return self.time_series[symbol].ix[0:len(self.time_series[symbol])]
        return self.time_series[symbol].ix[len(self.time_series[symbol])-n:len(self.time_series[symbol])+1]


class StockStrategy(Strategy):
    def __init__(self, events, data, products, initial_cash=1000000, price_field='Open'):
        super(StockStrategy, self).__init__(events, data, products, initial_cash)
        self.price_field = price_field
        mkt_price_columns = [product.symbol+'_mkt' for product in self.products]
        position_columns = [product.symbol+'_pos' for product in self.products]
        columns = ['dt'] + mkt_price_columns + position_columns + ['cash']
        self.time_series = pd.DataFrame(data=None, columns=columns)

    def new_tick_update(self, market_event):
        self.curr_dt = market_event.dt
        self.last_bar = self.data.last_bar.copy()
        _mkt_prices = [self.last_bar[product.symbol][self.price_field] for product in self.products]
        _positions = [self.positions[product.symbol] for product in self.products]
        self.time_series.loc[len(self.time_series)] = [self.curr_dt] + _mkt_prices + _positions + [self.cash]

    def finished(self, save=False):
        for product in self.products:
            self.time_series[product.symbol] = self.time_series[product.symbol+'_pos']*\
                                               self.time_series[product.symbol+'_mkt']

        self.time_series['total_val'] = np.sum(self.time_series[product.symbol] for product in self.products) \
                                        + self.time_series['cash']
        self.time_series.set_index('dt', inplace=True)
        self.transactions_series.set_index('dt', inplace=True)
        self.returns_series = self.time_series['total_val'].pct_change().fillna(0)
        positions_cols = [product.symbol for product in self.products] + ['cash']
        self.positions_series = pd.DataFrame(data=np.array([self.time_series[product.symbol]
                                                            for product in self.products]
                                                           +[self.time_series['cash']]).transpose(),
                                             columns=positions_cols,
                                             index=self.time_series.index)
