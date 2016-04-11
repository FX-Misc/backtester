import json
import logging
import numpy as np
import pandas as pd
from collections import OrderedDict
from abc import ABCMeta, abstractmethod

class Strategy(object):
    """
    The Strategy is an ABC that presents an interface for taking market data and
    generating corresponding OrderEvents which are sent to the ExecutionHandler.
    """
    __metaclass__ = ABCMeta

    def __init__(self, events, data, products, initial_cash, *args, **kwargs):

        self.events = events
        self.data = data
        self.products = products

        self.curr_dt = None
        self.positions = OrderedDict()
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.curr_pnl = 0
        self.last_bar = None

        mkt_price_columns = [product.symbol+'_mkt' for product in self.products]
        position_columns = [product.symbol+'_pos' for product in self.products]
        columns = ['dt'] + mkt_price_columns + position_columns + ['cash']
        self.time_series = pd.DataFrame(data=None, columns=columns)
        self.transactions = {product.symbol: [] for product in self.products}
        # self.initialize(*args, **kwargs)
        logFormatter = logging.Formatter("%(asctime)s %(message)s")
        fileHandler = logging.FileHandler('output/strategy_log', mode='w')
        fileHandler.setFormatter(logFormatter)
        self.logger = logging.getLogger('Strategy')
        logging.basicConfig(format=' %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)
        self.logger.addHandler(fileHandler)
        self.logger.propagate = False

    def order(self, symbol, quantity, price=None, type='MARKET'):
        """
        Generate an order and place it into events.
        :param symbol:
        :param quantity:
        :param price:
        :param type:
        :return:
        """
        raise NotImplementedError('Strategy.order()')

    @abstractmethod
    def new_tick_update(self, market_event):
        raise NotImplementedError('Strategy.new_tick_update()')

    @abstractmethod
    def new_tick(self, market_event):
        """
        Call back for when the strategy receives a new tick.
        :param event: (MarketEvent)
        :return:
        """
        raise NotImplementedError('Strategy.new_tick()')

    def new_fill_update(self, fill_event):
        """
        Updates positions.
        :param fill_event: (FillEvent)
        """
        self.positions[fill_event.symbol] += fill_event.quantity
        self.cash -= fill_event.fill_cost

    @abstractmethod
    def new_fill(self, fill_event):
        """
        Call back for when an order placed by the strategy is filled.
        :param fill_event: (FillEvent)
        :return:
        """
        raise NotImplementedError("Strategy.new_fill()")

    @abstractmethod
    def finished(self):
        """
        Call back for when a backtest (or live-trading) is finished.
        """
        raise NotImplementedError("Strategy.finished()")

    # @abstractmethod
    # def initialize(self, *args, **kwargs):
    #     """
    #     Initialize the strategy
    #     """
    #     raise NotImplementedError("initialize()")

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
        super(FuturesStrategy, self).__init__(events, data, products)

    def new_tick_update(self, market_event):
        """
        Update:
            - price_series (last_bar)
            - returns (series of decimal of cumulative PnL)
            - transactions (basically the fills)
            - positions series
        """
        self.last_bar = self.data.get_latest(n=1)
        for product in self.products:
            # self.time_series[product.symbol+'_mkt'].append((last_bar['level_1_price_buy'] + last_bar['level_1_price_sell']) / 2.)
            mkt_price = (self.last_bar[product.symbol]['level_1_price_buy'] + self.last_bar[product.symbol]['level_1_price_sell'])/2.
            pnl_ = self.cash + sum([self.positions[product.symbol] * product.tick_value * (self.last_bar[product.symbol]['level_1_price_buy']
                                    if self.positions[product.symbol] < 0
                                    else self.last_bar['level_1_price_sell']) for product.symbol in self.products])
            # self.spread[sym].append(last_bar['level_1_price_sell'] - last_bar['level_1_price_buy'])

    def finished(self):
        pass

class StockStrategy(Strategy):
    def __init__(self, events, data, products, initial_cash=1000000, price_field='Open'):
        super(StockStrategy, self).__init__(events, data, products, initial_cash)
        self.price_field = price_field

    def new_tick_update(self, market_event):
        self.curr_dt = market_event.dt
        self.last_bar = self.data.get_latest(n=1)
        mkt_prices = [self.last_bar[product.symbol][self.price_field] for product in self.products]
        _positions = [self.positions[product.symbol] for product in self.products]
        self.time_series.loc[len(self.time_series)] = [self.curr_dt] + mkt_prices + _positions + [self.cash]

    def finished(self):
        for product in self.products:
            self.time_series[product.symbol+'_val'] = self.time_series[product.symbol+'_pos']*\
                                                      self.time_series[product.symbol+'_mkt']
        self.time_series['val'] = np.sum(self.time_series[product.symbol+'_val'] for product in self.products) \
                                  + self.time_series['cash']
        self.time_series['returns'] = self.time_series['val'].pct_change().fillna(0)
        self.time_series.set_index('dt', inplace=True)
        self.time_series.fillna(0)