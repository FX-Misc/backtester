from abc import ABCMeta, abstractmethod


class DataHandler(object):
    """
    DataHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) DataHandler object is to output a generated
    set of bars (O/H/L/C/V) for each symbol requested.

    This will replicate how a live strategy would function as current
    market data would be sent "down the pipe". Thus a historic and live
    system will be treated identically by the rest of the trading system.
    """

    __metaclass__ = ABCMeta

    def __init__(self, events):
        self.events = events

    @abstractmethod
    def get_latest(self, n=1):
        """
        Returns the last N bars from the latest_data list, or fewer if less bars are available.
        :return: (DataFrame)
        """
        raise NotImplementedError("DataHandler.get_latest_bars()")

    @abstractmethod
    def update(self):
        """
        Pushes the latest bar to the latest symbol structure for all symbols in the symbol list.
        Also should send a MarketEvent to the queue.
        """
        raise NotImplementedError("DataHandler.update_bars()")

class BacktestDataHandler(DataHandler):
    def __init__(self, events, symbols, start_date, end_date, start_time=None, end_time=None):
        super(BacktestDataHandler, self).__init__(events)
        self.continue_backtest = True
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time