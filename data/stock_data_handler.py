import pandas as pd
import datetime as dt
from data_handler import DataHandler


class StockDatahandler(DataHandler):
    # TODO: multiple symbol support
    def __init__(self, events, start_date, end_date):
        """
        Handles data for (one) stock using pandas/yahoo finance API.
        :param events: (Queue)
        :param start_date: (datetime)
        :param end_date: (datetime)
        :return:
        """
        super(StockDatahandler, self).__init__(events)
        # initialize other stuff here


    def get_latest(self, n=1):
        pass

    def update(self):
        pass


if __name__ == "__main__":
    data = StockDatahandler()