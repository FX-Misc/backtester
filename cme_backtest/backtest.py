import json
from Queue import Empty
from data_handler import CMEBacktestDataHandler
from trading.backtest import Backtest

class CMEBacktest(Backtest):
    def __init__(self, events, strategy, data, execution, start_date, end_date, analytics=None,
                 start_time=None, end_time=None):

        assert isinstance(data, CMEBacktestDataHandler)
        super(CMEBacktest, self).__init__(events, strategy, data, execution, analytics, start_date, end_date)
        self.cash = 0

    def event_handler(self):
        event_handlers = {
            'MARKET': self._handle_market_event,
            'ORDER': self._handle_order_event,
            'FILL': self._handle_fill_event
        }
        while True:
            if self.data.continue_backtest:
                self.data.update()
            else:
                self.strategy.finished()
                break
            while True:
                try:
                    event = self.events.get(False)
                except Empty:
                    break
                else:
                    if event is not None:
                        event_handlers[event.type](event)

    def _handle_market_event(self, market_event):
        self.strategy.curr_dt = market_event.dt
        self.strategy.new_tick(market_event)
        self.execution.process_resting_orders(market_event)


    def _handle_order_event(self, order_event):
        self.execution.process_order(order_event)
        # self.logger.info(json.dumps(order_event.info()))

    def _handle_fill_event(self, fill_event):
        self.strategy.new_fill(fill_event)
        self.strategy._update_positions(fill_event)
        # self.logger.info(json.dumps(fill_event.info()))
