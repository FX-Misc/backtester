from trading import events


class StockBacktestOrderEvent(events.OrderEvent):
    def __init__(self, dt, symbol, order_type, quantity, price=None):
        super(StockBacktestOrderEvent, self).__init__(dt, symbol, order_type, quantity, price)


class StockBacktestFillEvent(events.FillEvent):
    def __init__(self, dt, symbol, quantity, fill_cost, commission):
        super(StockBacktestFillEvent, self).__init__(dt, symbol, quantity, fill_cost, commission)
        self.exchange = 'StockBacktestExecution'
