from random import randint
from trading.strategy import Strategy


class BuyStrategy(Strategy):
    def __init__(self, events, data, products, initial_cash=1000000):
        super(BuyStrategy, self).__init__(events, data, products, initial_cash)
        self.curr_dt = None
        self.prod1 = products[0]
        self.sym1 = products[0].symbol
        self.buy_int = 0

    def new_tick(self):
        random_buy = randint(1, 1000)
        if random_buy == 10:
            random_direction = randint(0, 1)
            if random_direction == 0:
                order_qty = 1
            else:
                order_qty = -1
            self.order(self.prod1, order_qty, order_type='MARKET', price=None, order_time=self.curr_dt)

    def new_fill(self, fill_event):
        pass

    def finished(self):
        pass
