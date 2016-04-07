from trading.strategy import Strategy

class BuyStrategy(Strategy):
    def __init__(self, events):
        super(BuyStrategy, self).__init__(events)