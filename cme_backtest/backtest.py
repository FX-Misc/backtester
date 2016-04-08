from Queue import Empty
from data_handler import CMEBacktestDataHandler
from trading.backtest import Backtest


class CMEBacktest(Backtest):
    def __init__(self, events, strategy, data, execution, start_date, end_date,
                 start_time=None, end_time=None):

        assert isinstance(data, CMEBacktestDataHandler)
        super(CMEBacktestDataHandler, self).__init__(events, strategy, data, execution, start_date, end_date)

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
            # Handle events
            while True:
                try:
                    event = self.events.get(False)
                except Empty:
                    break
                else:
                    if event is not None:
                        event_handlers[event.type](event)

    def _handle_market_event(self, market_event):
        self.strategy.new_tick(market_event)
        self.execution.process_resting_orders(market_event)

    def _handle_order_event(self, order_event):
        self.execution.process_order(order_event)
        self.events_log.append(order_event)

    def _handle_fill_event(self, fill_event):
        self.strategy.new_fill(fill_event)
        self.events_log.append(fill_event)
