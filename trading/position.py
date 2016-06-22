class Position(object):

    def __init__(self, symbol):
        self.symbol = symbol
        self.quantity = 0
        self.avg_cost = 0

    def update_position(self, fill_event):
        """
        Update the quantity of position as well as the cost average.

        :param fill_event: (FillEvent)
        """
        self.avg_cost = ((self.avg_cost*self.quantity)+(fill_event.fill_cost))/(self.quantity+fill_event.quantity)
        self.quantity += fill_event.quantity

    def __str__(self):
        return "Quantity: {}, AvgCost: {}".format(self.quantity, self.avg_cost)

    def __repr__(self):
        return str(self)
