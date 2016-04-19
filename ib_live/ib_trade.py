import time
import json
from strategies.paper_strategy import ClassifierStrategy
from ib_live.ib_data_handler import IBDataHandler
from ib_live.ib_execution_handler import IBExecutionHandler
from queue import Queue, Empty
from trading.futures_contract import FuturesContract

class IBTrade(object):
    def __init__(self, events, strategy, data, execution, **kwargs):
        self.events = events
        self.strategy = strategy
        self.data = data
        self.execution = execution
        self.running = True

    def run(self):
        self._log_trading_info()
        self.event_handler()

    def event_handler(self):
        event_handlers = {
            'MARKET': self._handle_market_event,
            'ORDER': self._handle_order_event,
            'FILL': self._handle_fill_event,
        }

        while True:
            if self.running:
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
        self.strategy.new_tick()

    def _handle_order_event(self, order_event):
        self.execution.process_new_order(order_event)

    def _handle_fill_event(self, fill_event):
        self.strategy.new_fill_update(fill_event)
        self.strategy.new_fill(fill_event)


    def _log_trading_info(self):
        print "STARTING TRADING \n" \
              "Strategy: {} \n" \
              "Execution: {} \n"\
            .format(self.strategy.__class__.__name__,
                    self.execution.__class__.__name__)


IB_CONFIG = json.load(open('test_ib_config.json', 'r'))
events = Queue()
products = [FuturesContract('GC', exp_year=2016, exp_month=6)]
data = IBDataHandler(events, products, IB_CONFIG)
execution = IBExecutionHandler(events, IB_CONFIG)
strategy = ClassifierStrategy(events, data, products=products)
ib_trade = IBTrade(events, strategy, data, execution)
time.sleep(5)
ib_trade.run()