import tabulate
import pandas as pd
from random import randint
from collections import OrderedDict
from trading.events import OrderEvent
from trading.strategy import StockStrategy

class BuyStrategy(StockStrategy):
    def __init__(self, events, data, products, initial_cash=1000000):
        super(BuyStrategy, self).__init__(events, data, products, initial_cash)
        self.curr_dt = None

        self.sym1 = products[0].symbol
        self.sym2 = products[1].symbol
        self.fills = []
        self.positions_series = OrderedDict()
        self.cash_series = OrderedDict()

    def new_tick(self, market_event):
        self.curr_dt = market_event.dt
        aapl_order_qty = randint(-20,20)
        msft_order_qty = randint(-100,100)
        temp_capital = self.cash
        if self._check_order(temp_capital, self.sym1, aapl_order_qty):
            self.order(self.sym1, aapl_order_qty)
            temp_capital -= self.last_bar[self.sym1][self.price_field] * aapl_order_qty

        if self._check_order(temp_capital, self.sym2, msft_order_qty):
            self.order(self.sym2, msft_order_qty)
            temp_capital -= self.last_bar[self.sym2][self.price_field] * msft_order_qty

    def _check_order(self, capital, symbol, quantity):
        if self.last_bar[symbol][self.price_field] * quantity < capital:
            return True
        return False

    def new_fill(self, fill_event):
        pass

    def order(self, symbol, quantity, order_type='MARKET', price=None,):
        order = OrderEvent(self.curr_dt, symbol, quantity, order_type, price)
        self.events.put(order)