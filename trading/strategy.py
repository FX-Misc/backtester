import logging
from abc import ABCMeta, abstractmethod
from trading.events import OrderEvent

class Portfolio(object):
    def __init__(self, products, initial_cash):
        self.positions = {product.symbol: 0 for product in products}
        self.cash = initial_cash
        self.pnl = 0

class Strategy(object):

    __metaclass__ = ABCMeta

    def __init__(self, events, data, products, initial_cash, *args, **kwargs):
        """
        The Strategy is an ABC that presents an interface for taking market data and
        generating corresponding OrderEvents which are sent to the ExecutionHandler.

        :param events: (Queue)
        :param data: (DataHandler)
        :param products: (list) (FuturesContract)
        :param initial_cash: (float)
        :param args:
        :param kwargs:
        """
        self.events = events
        self.data = data
        self.products = products
        self.symbols = [product.symbol for product in self.products]

        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.last_bar = None
        self.initialize(*args, **kwargs)

        self.portfolio = Portfolio(self.products, self.initial_cash)

        self.price_series = {product.symbol: [] for product in self.products}
        self.positions_series = {product.symbol: [] for product in self.products}
        self.transactions_series = []
        self.pnl_series = []
        self.cash_series = []

        self.curr_dt = None

        logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger(__name__)


    def order(self, product, quantity, order_type='MARKET', price=None, order_time=None):
        """
        Generate and send an order to be executed.

        :param product: (Product) FuturesContract or Stock
        :param order_type: (str) 'MARKET' or 'LIMIT'
        :param quantity: (int)
        :param price: (float)
        :param order_time: (DateTime)
        """
        order_time = order_time if order_time is not None else self.curr_dt
        order = OrderEvent(product, quantity, order_type, price, order_time)
        self.log.info(str(order))
        self.events.put(order)

    @abstractmethod
    def new_tick_update(self, market_event):
        """
        Internal updates on new tick.
        Updates positions, values, time series, returns, etc.
        :param market_event: (MarketEvent)
        """
        raise NotImplementedError('Strategy.new_tick_update()')

    @abstractmethod
    def new_tick(self):
        """
        Call back for when the strategy receives a new tick.
        self.last_bar is automatically updated before this.
        """
        raise NotImplementedError('Strategy.new_tick()')

    def new_fill_update(self, fill_event):
        """
        Updates internals on a new fill.
        Update:
            - current cash
            - current positions
            - transactions series

        :param fill_event: (FillEvent)
        """

        self.cash -= fill_event.fill_cost
        self.positions[fill_event.symbol] += fill_event.quantity
        self.transactions_series.append(fill_event)
        self.log.info(str(fill_event))

    @abstractmethod
    def new_fill(self, fill_event):
        """
        Call back for when an order placed by the strategy is filled.
        This should be implemented by the strategy.

        new_fill_update is called prior to this callback.
        Updated before this callback:
            self.positions
            self.cash
            self.transactions_series

        :param fill_event: (FillEvent)
        """
        raise NotImplementedError("Strategy.new_fill()")

    @abstractmethod
    def finished(self):
        """
        Call back for when a backtest (or live-trading) is finished.
        Creates the time_series (DataFrame)
        """
        raise NotImplementedError("Strategy.finished()")

    def initialize(self, *args, **kwargs):
        """
        Initialize the strategy
        """
        pass

    # @abstractmethod
    # def new_day(self, event):
    #     """
    #     Call back for when the strategy receives a tick that is a new day.
    #     :param event:
    #     :return:
    #     """
    #     raise NotImplementedError("new_day()")
