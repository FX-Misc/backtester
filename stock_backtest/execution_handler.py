import utils.data_utils.yahoo_finance as yf
from Queue import Queue
from events import StockBacktestOrderEvent, StockBacktestFillEvent
from trading.execution_handler import ExecutionHandler

PRICE_FIELD = 'Open'  # which O/H/L/C field to fill orders with

class StockBacktestExecutionHandler(ExecutionHandler):

    def __init__(self, events):
        """
        Handles simulated execution using inter-day data.
        :param events: (Queue)
        """
        super(StockBacktestExecutionHandler, self).__init__(events)
        self.symbol_data = {}
        self.resting_orders = Queue()

    def process_order(self, order_event):
        assert isinstance(order_event, StockBacktestOrderEvent)
        self._check_symbol_data(order_event.symbol)
        self._place_order(order_event)

    def process_resting_orders(self, market_event):
        """
        Got a new market update, check if we can fill any resting orders.
        :param market_event: (StockBacktestMarketEvent)
        """

        # go through the resting orders, get the latest data at market_event.dt and see if we can fill any orders
        raise NotImplementedError("Arvind, implement this")

    def _check_symbol_data(self, symbol):
        """
        Load all data for a symbol if haven't done so already.
        :param symbol: (str)
        """
        if symbol not in self.symbol_data:
           self.symbol_data[symbol] = yf.get_stock_data(symbol)


    def _place_order(self, order_event):
        """
        Handles either a MARKET or LIMIT order.
        :param order_event: (StockBacktestOrderEvent)
        :return:
        """
        if order_event.order_type is 'MARKET':
            self._fill_market_order(order_event)  # fill immediately at the current price

        elif order_event.order_type is 'LIMIT':
            self._process_limit_order(order_event)  # place a limit order

    def _fill_market_order(self, order_event):
        """
        Fills an order at the current market price and puts the fill event into the queue.
        :param order_event: (StockBacktestOrderEvent)
        """
        if order_event.quantity == 0:
            return
        sym_data = self.symbol_data[order_event.symbol].ix[order_event.dt]
        fill_price = sym_data[PRICE_FIELD]
        fill_event = self.create_fill_event(order_event, fill_price, order_event.dt)
        self.events.put(fill_event)

    def _process_limit_order(self, order_event):
        raise NotImplementedError("Arvind, implement this")

    def create_fill_event(self, order_event, fill_price, fill_time):
        """
        Make a fill event and put it back into the events queue.
        :param order_event:
        :param fill_price:
        :param fill_time:
        :return: (StockBacktestFillEvent)
        """
        fill_event = StockBacktestFillEvent(None, None, None, None, None)
        self.events.put(fill_event)
        raise NotImplementedError("Arvind, implement this")
