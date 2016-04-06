from abc import ABCMeta, abstractmethod

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