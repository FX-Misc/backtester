import numpy as np
import pandas as pd
from trading.events import OrderEvent
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
        self.positions = {product.symbol: 0 for product in self.products}
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.curr_pnl = 0
        self.last_bar = None
        self.transactions_series = pd.DataFrame(data=None, columns=['dt', 'amount', 'price', 'symbol'])

    def order(self, symbol, quantity, type='MARKET', price=None, order_time=None):
        """
        Generate an order and place it into events.
        :param symbol:
        :param quantity:
        :param price:
        :param type:
        :return:
        """
        order = OrderEvent(symbol, quantity, type, price, order_time)
        self.events.put(order)

    @abstractmethod
    def new_tick_update(self, market_event):
        raise NotImplementedError('Strategy.new_tick_update()')

    @abstractmethod
    def new_tick(self):
        """
        Call back for when the strategy receives a new tick.
        self.last_bar is automatically updated before this.
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
        self.transactions_series.loc[len(self.transactions_series)] = [fill_event.fill_time, fill_event.quantity,
                                                                       fill_event.fill_price, fill_event.symbol]

    @abstractmethod
    def new_fill(self):
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
        super(FuturesStrategy, self).__init__(events, data, products, initial_cash)
        mkt_price_columns = [product.symbol+'_mkt_bid' for product in self.products] + \
                            [product.symbol+'_mkt_ask' for product in self.products]
        position_columns = [product.symbol+'_pos' for product in self.products]
        columns = ['dt'] + mkt_price_columns + position_columns + ['cash']
        self.time_series = pd.DataFrame(data=None, columns=columns)

    def new_tick_update(self, market_event):
        """
        Update:
            - price_series (last_bar)
            - returns (series of decimal of cumulative PnL)
            - transactions (basically the fills)
            - positions series
        """
        self.curr_dt = market_event.dt
        self.last_bar = self.data.last_bar.copy()
        _mkt_bids = [self.last_bar[product.symbol]['level_1_price_buy'] for product in self.products]
        _mkt_asks = [self.last_bar[product.symbol]['level_1_price_sell'] for product in self.products]
        _positions = [self.positions[product.symbol] for product in self.products]
        self.time_series.loc[len(self.time_series)] = [self.curr_dt] + _mkt_bids + _mkt_asks + _positions + [self.cash]
        # for product in self.products:
        #     # self.time_series[product.symbol+'_mkt'].append((last_bar['level_1_price_buy'] + last_bar['level_1_price_sell']) / 2.)
        #     mkt_price = (self.last_bar[product.symbol]['level_1_price_buy'] + self.last_bar[product.symbol]['level_1_price_sell'])/2.
        #     pnl_ = self.cash + sum([self.positions[product.symbol] * product.tick_value * (self.last_bar[product.symbol]['level_1_price_buy']
        #                             if self.positions[product.symbol] < 0
        #                             else self.last_bar['level_1_price_sell']) for product.symbol in self.products])
        #     # self.spread[sym].append(last_bar['level_1_price_sell'] - last_bar['level_1_price_buy'])

    def finished(self):
        self.time_series.set_index('dt', inplace=True)


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
        self.positions_series = pd.DataFrame(np.array([self.time_series[product.symbol] for product in self.products] +
                                              [self.time_series['cash']]
                                             ).transpose(),
                                             columns=positions_cols,
                                             index=self.time_series.index)