from Queue import Empty

from stock_backtest.stock_data_handler import StockDatahandler
from stock_backtest.stock_execution_handler import StockExecutionHandler
from trading.backtest import Backtest


class StockBacktest(Backtest):
    def __init__(self, events, strategy, data, execution, start_date, end_date, initial_capital=1000000):
        """
        :param events: (Queue)
        :param strategy: (Strategy)
        :param data: (DataHandler)
        :param execution: (ExecutionHandler)
        :param start_date: (DateTime)
        :param end_date: (DateTime)
        """

        assert isinstance(data, StockDatahandler)
        assert isinstance(execution, StockExecutionHandler)
        # TODO: datetime assertion?
        super(StockBacktest, self).__init__(events, strategy, data, execution, start_date, end_date)


    def run(self):

        while True:
            if self.continue_backtest:
                self.data.update()
            else:
                break
            # Handle events
            while True:
                try:
                    event = self.events.get(False)
                except Empty:
                    break
                else:
                    if event is not None:
                        self._event_handler(event)

    def _event_handler(self, event):
        event_handlers = {
            'MARKET': self._handle_market_event(event),
            'ORDER': self._handle_order_event(event),
            'FILL': self._handle_fill_event(event)
        }
        if event.type == 'MARKET':
            self.strategy.new_tick(event)
            self.execution.process_resting_orders(event)

        elif event.type == 'ORDER':
            self.execution.process_order(event)

        elif event.type == 'FILL':
            self.strategy.new_fill(event)

    def _handle_market_event(self, market_event):
        pass

    def _handle_order_event(self, order_event):
        pass

    def _handle_fill_event(self, fill_event):
        pass