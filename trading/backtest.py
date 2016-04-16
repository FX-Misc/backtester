import logging
import json
from abc import ABCMeta, abstractmethod
from multiprocessing.pool import Pool
import multiprocessing

class Backtest(object):

    def __init__(self, events, strategy, data, execution, start_date, end_date, analytics=None):
        """
        Backtest base.
        """
        self.events = events
        self.strategy = strategy
        self.data = data
        self.execution = execution
        self.analytics = analytics
        self.start_date = start_date
        self.end_date = end_date
        self.continue_backtest = True
        # self.logger = logging.getLogger('Backtest')
        # logFormatter = logging.Formatter("%(asctime)s %(message)s")
        # fileHandler = logging.FileHandler('output/backtest_log', mode='w')
        # fileHandler.setFormatter(logFormatter)
        # logging.basicConfig(format=' %(message)s',
        #                     datefmt='%H:%M:%S',
        #                     level=logging.DEBUG)
        # self.logger.addHandler(fileHandler)
        # self.logger.propagate = False

    __metaclass__ = ABCMeta


    def run(self):
        """
        Run the backtest.
        """
        self._log_backtest_info()
        # pool = ThreadPool(processes=1)
        # async_result = pool.apply_async(self.event_handler)
        # return async_result.get()

        pool = Pool(processes=2)
        names = ('frank', 'justin', 'osi', 'thomas')
        # pool.map(unwrap_self_f, zip([self]*len(names), names))


        self.event_handler()

    def finished(self):
        self.analytics.run()
        print 'FINISHED BACKTEST.\n'

    @abstractmethod
    def event_handler(self):
        raise NotImplementedError('Backtest.event_handler()')

    def _log_backtest_info(self):
        print 'STARTING BACKTEST \n' \
              'Strategy: {} \n' \
              'Execution: {} \n' \
              'Start: {}, End: {} \n'.format(self.strategy.__class__.__name__,
                                             self.execution.__class__.__name__,
                                             self.start_date.strftime("%-m/%-d/%Y %H:%M"),
                                             self.end_date.strftime("%-m/%-d/%Y %H:%M"))
        # self.logger.info(json.dumps(info))