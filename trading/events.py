class Event(object):
    """
    The Event is the fundamental class unit of the event-driven system.
    It contains a type (such as "MARKET", "SIGNAL", "ORDER" or "FILL")
    that determines how it will be handled within the event-loop.
    """


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with corresponding bars
    """
    def __init__(self, datetime):
        self.type = 'MARKET'
        self.datetime = datetime


class NewDayEvent(Event):
    """
    New day, gives previous day's data, called only when there is a previous day existing
    """
    def __init__(self, prev_data, next_date):
        self.type = 'NEWDAY'
        self.prev_data = prev_data
        self.prev_date = prev_data.reset_index()['time'].values[0]
        self.next_date = next_date


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.

    Params:
    symbol (string):
    order_type (string): 'MARKET' or 'LIMIT'
    quantity (int):
    price (float): if market order
    """
    def __init__(self, symbol, order_type, quantity, price=None):
        self.type = 'ORDER'
        self.symbol = symbol
        assert order_type is 'MARKET' or order_type is 'LIMIT'
        self.order_type = order_type
        # assert isinstance(quantity, int), "Order quantity must be int"
        self.quantity = quantity
        self.price = price
        if order_type is 'LIMIT':
            assert price is not None, "Invalid price for LIMIT order"
            try:
                self.price = float(self.price)
            except TypeError:
                print "Invalid price for LIMIT ORDER"
            #assert type(price) is FloatType, "LIMIT order price must be float"


class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned from a brokerage.
    Stores the quantity of an instrument actually filled and at what price.
    In addition, stores the commission of the trade from the brokerage.

    Params:
    fill_time (datetime):
    symbol (string):
    exchange (string);
    quantity (int):
    fill_cost (float):
    commission (float):
    """
    def __init__(self, fill_time, symbol, exchange, quantity, fill_cost, commission=0):
        self.type = 'FILL'
        self.fill_time = fill_time
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.fill_cost = fill_cost
        self.commission = commission
