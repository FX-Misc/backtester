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
        if event.type == 'MARKET':
            self.strategy.new_tick(event)
            self.execution.process_resting_orders(event)

        elif event.type == 'ORDER':
            self.execution.process_order(event)

        elif event.type == 'FILL':
            self.strategy.new_fill(event)



# class Backtest(object):
#
#     def __init__(self, events, bars, strategy, execution,
#                  start_date, end_date, start_time=None, end_time=None, initial_capital=1000000, name=None):
#
#         self.events = events
#         self.bars = bars
#         self.strategy = strategy
#         self.execution = execution
#         self.start_date = start_date
#         self.end_date = end_date
#         self.start_time = start_time
#         self.end_time = end_time
#         self.initial_capital = initial_capital
#
#         self.name = name
#
#         self.bars._load_day_data()
#
#
#         # print self.portfolio.positions
#         log.info("Backtest completed")
#
#         self.strategy.finished()
#
#         """
#         time_series = self.portfolio.time_series
#         price_series = self.portfolio.price_series[self.portfolio.symbols[0]]
#         pnl_series = self.portfolio.pnl
#         orders = self.portfolio.orders[self.portfolio.symbols[0]]
#
#         plot_backtest('backtest_results', time_series, price_series, pnl_series, orders)
#         """
#
#