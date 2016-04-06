from abc import ABCMeta, abstractmethod
from data.stock_data_handler import StockDatahandler

class Backtest(object):

    def __init__(self, events, strategy, data, execution, start_date, end_date):
        """


        """
        self.events = events
        self.strategy = strategy
        self.data = data
        self.execution = execution
        self.start_date = start_date
        self.end_date = end_date
        self.continue_backtest = True

    __metaclass__ = ABCMeta

    @abstractmethod
    def run(self):
        """
        Run the backtest.
        :return:
        """
        raise NotImplementedError("Backtest.run()")


class StockBacktest(Backtest):
    def __init__(self, events, strategy, data, execution, start_date, end_date):
        """
        :param events: (Queue)
        :param strategy: (Strategy)
        :param data: (DataHandler)
        :param execution: (ExecutionHandler)
        :param start_date: (DateTime)
        :param end_date: (DateTime)
        """

        assert isinstance(data, StockDatahandler)
        super(StockBacktest, self).__init__(events, strategy, data, execution, start_date, end_date)

    def run(self):
        while True:
            if self.continue_backtest:
                self.data.update()


class FuturesBacktest(Backtest):
    def __init__(self, events, strategy, data, execution, start_date, end_date,
                 start_time=None, end_time=None):

        assert isinstance(data, StockDatahandler)
        super(FuturesBacktest, self).__init__(events, strategy, data, execution, start_date, end_date)