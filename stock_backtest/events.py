from trading import events


class StockBacktestMarketEvent(events.MarketEvent):
    def __init__(self, dt):
        super(StockBacktestMarketEvent, self).__init__(dt)

class StockBacktestOrderEvent(events.OrderEvent):
    def __init__(self, order_time, symbol, quantity, order_type, price=None):
        super(StockBacktestOrderEvent, self).__init__(order_time, symbol, quantity, order_type, price)


class StockBacktestFillEvent(events.FillEvent):
    def __init__(self, fill_time, symbol, quantity, fill_cost, commission=0):
        super(StockBacktestFillEvent, self).__init__(fill_time, symbol, quantity, fill_cost,
                                                     exchange='StockBacktestExecution',
                                                     commission=commission)