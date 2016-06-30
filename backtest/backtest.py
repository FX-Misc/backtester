from Queue import Empty
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
log = logging.getLogger('Backtest')


class Backtest():
    def __init__(self, events, strategy, data, execution, start_date, end_date, analytics=None,
                 start_time=None, end_time=None):

        self.start_time = start_time
        self.end_time = end_time
        self.cash = 0

        self.events = events
        self.strategy = strategy
        self.data = data
        self.execution = execution
        self.analytics = analytics
        self.start_date = start_date
        self.end_date = end_date
        self.continue_backtest = True


    def run(self):
        """
        Run the backtest.
        """
        self._log_backtest_info()
        self.event_handler()

    def finished(self):
        self.analytics.run()
        print 'FINISHED BACKTEST.\n'


    def _log_backtest_info(self):
        info = 'STARTING BACKTEST \n' \
              'Strategy: {} \n' \
              'Execution: {} \n' \
              'Start: {}, End: {} \n'.format(self.strategy.__class__.__name__,
                                             self.execution.__class__.__name__,
                                             self.start_date.strftime("%-m/%-d/%Y %H:%M"),
                                             self.end_date.strftime("%-m/%-d/%Y %H:%M"))
        # log.info(info)
        print(info)

    def event_handler(self):
        event_handlers = {
            'MARKET': self._handle_market_event,
            'ORDER': self._handle_order_event,
            'FILL': self._handle_fill_event,
            'NEW_DAY': self._handle_new_day_event
        }
        while True:
            if self.data.continue_backtest:
                self.data.update()
            else:
                self.strategy.finished()
                return
            while True:
                try:
                    event = self.events.get(False)
                except Empty:
                    break
                else:
                    if event is not None:
                        event_handlers[event.type](event)

    def _handle_market_event(self, market_event):
        self.strategy.new_tick_update(market_event)
        self.execution.process_resting_orders(market_event)

    def _handle_order_event(self, order_event):
        print str(order_event)
        log.info(str(order_event))
        self.execution.process_new_order(order_event)

    def _handle_fill_event(self, fill_event):
        print str(fill_event)
        log.info(str(fill_event))
        self.strategy.new_fill_update(fill_event)

    def _handle_new_day_event(self, new_day_event):
        self.strategy.new_day_update()
