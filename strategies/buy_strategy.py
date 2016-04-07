from trading.strategy import Strategy

class BuyStrategy(Strategy):
    def __init__(self, events):
        super(BuyStrategy, self).__init__(events)

    def new_tick(self, event):
        pass

    def new_fill(self, event):
        pass

    def finished(self):
        pass
