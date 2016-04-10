import json
import logging
from abc import ABCMeta, abstractmethod


class Strategy(object):
    """
    The Strategy is an ABC that presents an interface for taking market data and
    generating corresponding OrderEvents which are sent to the ExecutionHandler.
    """
    __metaclass__ = ABCMeta

    def __init__(self, events, data, *args, **kwargs):

        self.data = data
        self.events = events
        self.curr_time = None
        self.positions = {}
        self.curr_pnl = 0

        # self.positions_series =
        # self.price_series = {sym: [] for sym in self.symbols}

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
    def new_tick(self, market_event):
        """
        Call back for when the strategy receives a new tick.
        :param event: (MarketEvent)
        :return:
        """
        self.curr_time = market_event.datetime

    # @abstractmethod
    # def update_price_series(self):
    #     raise NotImplementedError('Strategy.update_price_series()')
    #
    # @abstractmethod
    # def update_positions_series(self):
    #     raise NotImplementedError('Strategy.update_positions_series()')


    def update_positions(self, fill_event):
        self.positions['dt'] = fill_event.fill_time.strftime("%y/%m/%e-%H:%M:%S.%f")
        if fill_event.symbol not in self.positions:
            self.positions[fill_event.symbol] = 0
        self.positions[fill_event.symbol] += fill_event.quantity
        self.logger.info(json.dumps(self.positions.copy()))


    # def update_metrics(self):
    #     last_bar = self.bars.get_latest_bars(n=1)
    #     pnl_ = self.cash + sum([self.pos[sym] * self.contract_multiplier[sym] *
    #                             (last_bar['level_1_price_buy']
    #                              if self.pos[sym] < 0 else
    #                              last_bar['level_1_price_sell']) for sym in self.symbols])
    #     self.pnl.append(pnl_)
    #     self.time_series.append(self.cur_time)
    #     for sym in self.symbols:
    #         self.price_series[sym].append((last_bar['level_1_price_buy'] + last_bar['level_1_price_sell']) / 2.)
    #         self.spread[sym].append(last_bar['level_1_price_sell'] - last_bar['level_1_price_buy'])

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
    def __init__(self, events, data):
        super(FuturesStrategy, self).__init__(events, data)

class StockStrategy(Strategy):
    def __init__(self, events, data):
        super(StockStrategy, self).__init__(events, data)

