import logging
from abc import ABCMeta, abstractmethod
from events import OrderEvent

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
        # self.initialize(*args, **kwargs)

    def order(self, symbol, quantity, price=None, type='market'):
        """
        Generate an order and place it into events.
        :param symbol:
        :param quantity:
        :param price:
        :param type:
        :return:
        """
        raise NotImplementedError('Strategy.order()')

    # @abstractmethod
    # def initialize(self, *args, **kwargs):
    #     """
    #     Initialize the strategy
    #     """
    #     raise NotImplementedError("initialize()")

    @abstractmethod
    def new_tick(self, market_event):
        """
        Call back for when the strategy receives a new tick.
        :param event: (MarketEvent)
        :return:
        """
        self.curr_time = market_event.datetime

    # @abstractmethod
    # def new_day(self, event):
    #     """
    #     Call back for when the strategy receives a tick that is a new day.
    #     :param event:
    #     :return:
    #     """
    #     raise NotImplementedError("new_day()")

    @abstractmethod
    def new_fill(self, event):
        """
        Call back for when an order placed by the strategy is filled.
        :param event: (FillEvent)
        :return:
        """
        raise NotImplementedError("Strategy.new_fill()")

    @abstractmethod
    def finished(self):
        """
        Call back for when a backtest (or live-trading) is finished.
        """
        raise NotImplementedError("Strategy.finished()")
