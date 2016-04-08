import logging
import threading
from abc import ABCMeta, abstractmethod
log = logging.getLogger('Backtest')

class Backtest(object):

    def __init__(self, events, strategy, data, execution, start_date, end_date):
        """
        Backtest base.
        """
        self.events = events
        self.strategy = strategy
        self.data = data
        self.execution = execution
        self.start_date = start_date
        self.end_date = end_date
        self.continue_backtest = True

    __metaclass__ = ABCMeta

    def run(self):
        """
        Run the backtest.
        """
        event_handler_thread = threading.Thread(target=self.event_handler, args=())
        event_handler_thread.start()

    @abstractmethod
    def event_handler(self):
        raise NotImplementedError('Backtest.event_handler()')

    def log_backtest_info(self):
        info = 'Running backtest with parameters: \n ' \
               'Strategy: {} \n ' \
               'Execution: {} \n ' \
               'Start date: {}, End date: {}' \
            .format(self.strategy.__class__.__name__,
                    self.execution.__class__.__name__,
                    self.start_date, self.end_date)
        log.info(info)