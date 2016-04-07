import sys
import os
import logging
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
log = logging.getLogger('CME_BACKTEST_EXECUTION_HANDLER')

import datetime as dt
import random
from bt.cme_backtest_events import CMEBacktestFillEvent, CMEBacktestOrderEvent
from datautils.datafeed import get_data_multi
from bt.execution_handler import ExecutionHandler


# TODO: parameters instead of macros

CME_HISTORICAL_ORDER_DELAY = dt.timedelta(seconds=.01)
CME_HISTORICAL_TRANSACTION_COST = 0
MARKET_ORDERS = True

LIMIT_FILL_PROBABILITY = 0.1


class CMEBacktestExecutionHandler(ExecutionHandler):
    def __init__(self, symbols, events, second_bars=True, commission=0):
        self.symbols = symbols
        self.events = events
        self.second_bars = second_bars
        self.current_day_data = None

        self.commission = commission

        self.resting_orders = []

        self.multi_data = False
        if len(self.symbols) > 1:
            self.multi_data = True

    def process_order(self, order_event):
        """
        Updates the current_day_data and places the order.
        """
        assert type(order_event) is CMEBacktestOrderEvent, \
            "CMEBacktestExecutionHandler - event must be CMEBacktestOrder"
        self._check_day_data(order_event.datetime)
        assert self.current_day_data is not None, \
            "No data for current day!"
        self.place_order(order_event)

    def process_resting_orders(self, market_event):
        """
        On new market update, check resting orders to see if they can be filled.
        """
        assert market_event.type is 'MARKET'
        if len(self.resting_orders) == 0:
            return
        for resting_order in self.resting_orders:
            fill_time = self._get_fill_time(market_event.datetime, resting_order.symbol)
            direction = self._get_order_direction(resting_order)
            if direction is 1:
                if self._check_fill_limit_buy(resting_order, fill_time) is True:
                    self._fill_limit_order(resting_order, fill_time)
                    self.resting_orders.remove(resting_order)
            elif direction is -1:
                if self._check_fill_limit_sell(resting_order, fill_time) is True:
                    self._fill_limit_order(resting_order, fill_time)
                    self.resting_orders.remove(resting_order)

    def place_order(self, order_event):
        """
        Places a MARKET/LIMIT order
        """
        self._check_day_data(order_event.datetime)
        if order_event.order_type == 'MARKET':
            # fill immediately at the next tick
            fill_time = self._get_fill_time(order_event.datetime, order_event.symbol)
            self._fill_market_order(order_event, fill_time)
        elif order_event.order_type == 'LIMIT':
            # place a limit order
            # TODO: check if it is market-ble
            self.resting_orders.append(order_event)

    def _fill_market_order(self, order_event, fill_time):
        """
        Fills a market order by crossing the spread at the current best bid/offer
        """
        if order_event.quantity == 0:
            return
        sym_data = self.current_day_data[order_event.symbol]
        direction = self._get_order_direction(order_event)
        if direction == 1:
            fill_price = sym_data['level_1_price_sell'].asof(fill_time)
            self.create_fill_event(order_event, fill_price, fill_time)
        elif direction == -1:
            fill_price = sym_data['level_1_price_buy'].asof(fill_time)
            self.create_fill_event(order_event, fill_price, fill_time)

    def _fill_limit_order(self, order_event, fill_time):
        if order_event.quantity == 0:
            return
        direction = self._get_order_direction(order_event)
        sym_data = self.current_day_data[order_event.symbol]
        if direction == 1:
            fill_price = sym_data['level_1_price_buy'].asof(fill_time)
            self.create_fill_event(order_event, fill_price, fill_time)
        elif direction == -1:
            fill_price = sym_data['level_1_price_sell'].asof(fill_time)
            self.create_fill_event(order_event, fill_price, fill_time)

    def _check_fill_limit_buy(self, resting_order, fill_time):
        """
        Conditions to fill a limit order (BUY)
        """
        symbol = resting_order.symbol
        if resting_order.price < self.current_day_data[symbol]['level_1_price_sell'].asof(fill_time) and self._limit_fill() is True \
                or resting_order.price >= self.current_day_data[symbol]['level_1_price_sell'].asof(fill_time):
            return True
        else:
            return False

    def _check_fill_limit_sell(self, resting_order, fill_time):
        """
        Conditions to fill a limit order (SELL)
        """
        if resting_order.price > self.current_day_data['level_1_price_buy'].asof(fill_time) and self._limit_fill() is True \
                or resting_order.price <= self.current_day_data['level_1_price_buy'].asof(fill_time):
            return True
        else:
            return False

    def clear_resting_orders(self):
        if len(self.resting_orders) > 0:
            log.info("All resting orders removed")
            self.resting_orders = []

    @staticmethod
    def _get_order_direction(order_event):
        """
        Returns the direction of the order:
            1: BUY
            -1: SELL
        """
        if order_event.quantity  == 0:
            return 0
        elif order_event.quantity < 0:
            return -1
        else:
            return 1

    def _get_fill_time(self, order_time, symbol):
        """
        Applies a delay to the order_time and returns the time of the data for which the order can be filled.
        """
        execution_time = order_time + CME_HISTORICAL_ORDER_DELAY
        fill_time = self.current_day_data[symbol].index.asof(execution_time)
        return fill_time

    def create_fill_event(self, order_event, fill_price, fill_time):
        exchange = 'CMEBacktest'
        fill_cost = order_event.quantity*fill_price
        fill_event = CMEBacktestFillEvent(order_event.datetime, fill_time, order_event.symbol, order_event.quantity,
                                          fill_cost, commission=self.commission)
        log.info(fill_event)
        self.events.put(fill_event)

    def _check_day_data(self, datetime):
        """
        Check if data for the current day (based on orders) exists, if not, get the data.
        On a new day change, clears all resting orders.
        """
        if self.current_day_data is None or self.compare_dates(self.current_day_data.index[0], datetime) is False:
            date = dt.datetime(year=datetime.year, month=datetime.month, day=datetime.day)
            self.current_day_data = get_data_multi(self.symbols, date, second_bars=self.second_bars)
            self.clear_resting_orders()

    @staticmethod
    def compare_dates(dt1, dt2):
        """
        Returns:
            True: if the year, month, and day of dt1 and dt2 match
            False: otherwise
        """
        if dt1.year == dt2.year and dt1.month == dt2.month and dt1.day == dt2.day:
            return True
        else:
            return False

    @staticmethod
    def _limit_fill():
        """
        Probability function for limit fill
        """
        z = random.randint(0, 10)
        if z/10.0 < LIMIT_FILL_PROBABILITY:
            return True
        else:
            return False
