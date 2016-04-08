class Event(object):
    """
    Types include:
        MARKET:
        NEW_DAY
        ORDER
        FILL
    """


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update.
    """
    def __init__(self, dt):
        self.type = 'MARKET'
        self.dt = dt


# class NewDayEvent(Event):
#     def __init__(self, prev_data, next_date):
#         """
#         New day, gives previous day's data, called only when there is a previous day existing
#         :param prev_data: (datetime)
#         :param next_date: (datetime)
#         """
#         self.type = 'NEW_DAY'
#         self.prev_data = prev_data
#         self.prev_date = prev_data.reset_index()['time'].values[0]
#         self.next_date = next_date


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    :param datetime: (DateTime) order time
    :param symbol: (str)
    :param order_type: (str) 'MARKET', 'LIMIT'
    :param quantity: (int)
    :param price: (float)
    """
    def __init__(self, order_time, symbol, quantity, order_type='MARKET', price=None):
        self.order_time = order_time
        self.type = 'ORDER'
        self.symbol = symbol
        assert order_type is 'MARKET' or order_type is 'LIMIT'
        self.order_type = order_type
        self.quantity = quantity
        self.price = price
        if order_type is 'LIMIT':
            assert price is not None, "LIMIT order must have a price."
            try:
                self.price = float(self.price)
            except TypeError:
                print "LIMIT order has invalid price."


class FillEvent(Event):
    def __init__(self, fill_time, symbol, quantity, fill_cost, exchange, commission=0):
        """
        Encapsulates the notion of a Filled Order, as returned from a brokerage.
        Stores the quantity of an instrument actually filled and at what price.
        In addition, stores the commission of the trade from the brokerage.

        :param fill_time: (DateTime) fill time
        :param symbol: (str)
        :param exchange: (str)
        :param quantity: (int)
        :param fill_cost: (float)
        :param commission: (float)
        :return:
        """
        self.type = 'FILL'
        self.fill_time = fill_time
        self.symbol = symbol
        self.quantity = quantity
        self.fill_cost = fill_cost
        self.commission = commission
