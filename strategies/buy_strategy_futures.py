from random import randint
from trading.futures_strategy import FuturesStrategy


class BuyStrategy(FuturesStrategy):
    def __init__(self, events, data, products, initial_cash=1000000):
        super(BuyStrategy, self).__init__(events, data, products, initial_cash)
        self.curr_dt = None
        self.prod1 = products[0]
        self.sym1 = products[0].symbol
        self.fills = []
        self.buy_int = 0

    def new_tick(self):
        random_buy = randint(1, 1000)
        if random_buy == 10:
            random_direction = randint(0, 1)
            self.order(self.prod1, 1, order_type='MARKET', price=None, order_time=self.curr_dt)


    def _check_order(self, capital, symbol, quantity):
        if self.last_bar[symbol]['level_1_price_buy'] * quantity < capital:
            return True
        return False

    def new_fill(self, fill_event):
        pass