from trading.events import OrderEvent
from trading.strategy import Strategy

PRICE_FIELD = 'Open'

class BuyStrategy(Strategy):
    def __init__(self, events, data, initial_capital=1000000):
        super(BuyStrategy, self).__init__(events, data)
        self.curr_dt = None
        self.capital = initial_capital
        self.positions = {}

        self.sym1 = 'AAPL'
        self.sym2 = 'MSFT'

        self.latest_data = None

    def new_tick(self, market_event):
        self.curr_dt = market_event.dt
        self.latest_data = self.data.get_latest()

        aapl_order_qty = 10
        msft_order_qty = 50
        if self._check_order(self.sym1, aapl_order_qty):
            self.order(self.sym1, aapl_order_qty)
            self.capital -= self.latest_data[self.sym1][PRICE_FIELD] * aapl_order_qty

        if self._check_order(self.sym2, msft_order_qty):
            self.order(self.sym2, msft_order_qty)
            self.capital -= self.latest_data[self.sym2][PRICE_FIELD] * msft_order_qty

    def _check_order(self, symbol, quantity):
        if self.latest_data[symbol][PRICE_FIELD] * quantity < self.capital:
            return True
        return False

    def new_fill(self, fill_event):
        print fill_event.__dict__

    def finished(self):
        pass

    def order(self, symbol, quantity, order_type='MARKET', price=None,):
        order = OrderEvent(self.curr_dt, symbol, quantity, order_type, price)
        self.events.put(order)