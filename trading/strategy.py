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
        self.realized_pnl = 0
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

    def update_positions(self, fill_event):
        """

        """
        self.positions['dt'] = fill_event.fill_time.strftime("%y/%m/%e-%H:%M:%S.%f")
        if fill_event.symbol not in self.positions:
            self.positions[fill_event.symbol] = 0
        self.positions[fill_event.symbol] += fill_event.quantity
        self.logger.info(json.dumps(self.positions.copy()))

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