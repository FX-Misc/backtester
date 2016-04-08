import datetime as dt
import trading.events as events

class IBMarketEvent(events.MarketEvent):
    def __init__(self, dt):
        super(IBMarketEvent, self).__init__(dt)

class IBOrderEvent(events.OrderEvent):
    """
    Handles the event of sending an Order to an execution system.
    :param symbol: (string):
    :param order_type: (string): 'MARKET' or 'LIMIT'
    :param quantity: (int):
    :param price: (float): if limit order
    """
    def __init__(self, dt, symbol, quantity, order_type=None):
        super(IBOrderEvent, self).__init__(symbol, order_type, price, quantity)
        self.datetime = dt.datetime.now()

    def __str__(self):
        return "ORDER | Symbol: {}, Time: {}, Qty: {}, Type: {}"\
            .format(self.symbol, self.datetime, self.quantity, self.order_type)

class IBFillEvent(events.FillEvent):
    """
    Subclasses FillEvent and also contains field with dicts for execution_details and contract_details.
    """
    def __init__(self, execution, contract):
        """
        :param execution: (dict) execution details
        :param contract: (dict) contract details
        """
        super(IBFillEvent, self).__init__(dt=execution['time'], symbol=contract['symbol'],
                                          exchange=execution['exchange'], quantity=execution['qty'],
                                          fill_cost=execution['qty']*execution['avg_price'], commission=0)
        # TODO: commission
        self.execution = execution
        self.contract = contract

class IBOpenOrderEvent(events.Event):
    def __init__(self):
        pass

class IBCommissionReportEvent(events.Event):
    def __init__(self):
        pass

if __name__ == "__main__":
    order = IBOrderEvent('GC', 'MARKET', 1)
    print str(order)


