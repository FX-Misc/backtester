import logging
import threading
import json
from abc import ABCMeta, abstractmethod

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
        self.logger = logging.getLogger('Backtest')

        logFormatter = logging.Formatter("%(asctime)s %(message)s")
        fileHandler = logging.FileHandler('output/backtest_log', mode='w')
        fileHandler.setFormatter(logFormatter)
        logging.basicConfig(filemode='w',
                            format=' %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
        logging.getLogger().addHandler(logging.StreamHandler())
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        self.logger.addHandler(fileHandler)
        self.logger.addHandler(consoleHandler)

    __metaclass__ = ABCMeta

    def run(self):
        """
        Run the backtest.
        """
        self._log_backtest_info()
        event_handler_thread = threading.Thread(target=self.event_handler, args=())
        event_handler_thread.start()

    @abstractmethod
    def event_handler(self):
        raise NotImplementedError('Backtest.event_handler()')

    def _log_backtest_info(self):
        info = {
            'STRATEGY': self.strategy.__class__.__name__,
            'EXECUTION': self.execution.__class__.__name__,
            'START': self.start_date.strftime("%-m/%-d/%Y %H:%M"),
            'END': self.end_date.strftime("%-m/%-d/%Y %H:%M"),
        }
        self.logger.info(json.dumps(info))