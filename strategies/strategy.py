from abc import ABCMeta, abstractmethod
from backtester.events import OrderEvent

class Strategy(object):
    """
    The Strategy is also an ABC that presents an interface for taking market data and
    generating corresponding SignalEvents, which are ultimately utilised by the
    Portfolio object.
    A SignalEvent contains a ticker symbol, a direction (LONG or SHORT)
    and a timestamp.
    """
    __metaclass__ = ABCMeta

    def __init__(self, bars, events, *args, **kwargs):
        self.bars = bars
        self.events = events
        self.cur_time = None
        self.initialize(*args, **kwargs)

    def order(self, symbol, quantity, price=None, type='market'):
        if self.cur_time is None:
            raise Exception("Must update self.cur_time")
        if quantity == 0:
            return

        if type == "market":
            order_event = OrderEvent(symbol, self.cur_time, 'MARKET', quantity, price)
        else:
            raise NotImplementedError("Order type {} not implemented".format(type))

        self.events.put(order_event)

    @abstractmethod
    def initialize(self, *args, **kwargs):
        """
        Initialize the strategy
        """
        raise NotImplementedError("initialize()")

    @abstractmethod
    def new_tick(self, event):
        """
        Call back for when the strategy receives a new tick.
        :param event:
        :return:
        """
        self.cur_time = event.datetime

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
        raise NotImplementedError("new_fill()")

    @abstractmethod
    def finished(self):
        """
        Call back for when a backtest (or live-trading) is finished.
        """
        raise NotImplementedError("finished()")
