import numpy as np

class Position(object):

    def __init__(self, symbol):
        self.symbol = symbol
        self.quantity = 0
        self.avg_cost = 0

        self.pnl_realized = 0

    def update(self, fill_event):
        """
        Update the quantity of position as well as the cost average.

        :param fill_event: (FillEvent)
        """

        # currently flat
        if self.quantity == 0:
            self._update_initial_fill(fill_event)

        # increase position
        elif np.sign(fill_event.quantity) == np.sign(self.quantity):
            self._update_increase(fill_event)

        # partial decrease
        elif np.sign(fill_event.quantity) != np.sign(self.quantity) and abs(fill_event.quantity) < abs(self.quantity):
            self._update_partial_decrease(fill_event)

    def _update_initial_fill(self, fill_event):
        """
        Initial fill (when currently flat)

        :param fill_event:
        :return:
        """
        self.quantity = fill_event.quantity
        self.avg_cost = fill_event.fill_price

    def _update_increase(self, fill_event):
        """
        Receiving new fills that increase your position.

        :param fill_event:
        :return:
        """

        self.avg_cost =  ((self.quantity*self.avg_cost)+(fill_event.fill_cost))/(self.quantity+fill_event.quantity)
        self.quantity += fill_event.quantity

    def _update_partial_decrease(self, fill_event):
        """
        Receiving new fills that partially decrease your position.

        :param fill_event:
        :return:
        """
        self.pnl_realized += ((fill_event.fill_price-self.avg_cost)*abs(fill_event.quantity))
        self.quantity += fill_event.quantity

    def _update_flatten(self, fill_event):
        """
        Receiving fills that flatten your position.

        :param fill_event:
        :return:
        """
        pass

    def _update_reverse(self, fill_event):
        pass


    def __str__(self):
        return "Quantity: {}, AvgCost: {}".format(self.quantity, self.avg_cost)

    def __repr__(self):
        return str(self)
