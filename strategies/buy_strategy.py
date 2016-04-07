from trading.strategy import Strategy

class BuyStrategy(Strategy):
    def __init__(self, events, data, initial_capital=1000000):
        super(BuyStrategy, self).__init__(events, data)

    def new_tick(self, event):
        pass

    def new_fill(self, event):
        pass

    def finished(self):
        pass
