import logging
import os
import sys
import threading
import time

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
log = logging.getLogger('Backtest')
from bt.data_handler import DataHandler
from ib_live.ib_connection import IBConnection
from bt.events import MarketEvent

class IBDataHandler(DataHandler, IBConnection):

    def __init__(self, events, config):
        self.events = events
        self.port = config['PORT']
        self.client_id = config['DATA_CLIENT_ID']
        super(IBDataHandler, self).__init__(self.port, self.events, self.client_id)

        # Subscribe to mkt data feed
        contract = config['CONTRACT']
        self._req_mkt_data(contract)

        # Reply handler thread
        thread = threading.Thread(target=self._reply_handler, args=())
        thread.daemon = True
        thread.start()

        self.symbols = config['SYMBOLS']
        self.last_tick = {}

        log.info("IBDataHandler initialized!")

    def _req_mkt_data(self, contract):
        """
        tickerId (int) The ticker id. Must be a unique value. When the market data returns,
                        it will be identified by this tag. This is also used when canceling the market data.
        contract (Contract)	This class contains attributes used to describe the contract.
        genericTicklist	(String) A comma delimited list of generic tick types.  Tick types can be found in
                                the Generic Tick Types page.
        snapshot (boolean) Check to return a single snapshot of market data and have the market data
                          subscription cancel. Do not enter any genericTicklist values if you use snapshot.

        :param type:
        :return:
        """
        self.connection.reqMarketDataType(3)  # type 3 is for delayed data
        self.connection.reqMktData(12356, contract, "", False)

    def get_latest_bars(self, n=1):
        return self.last_tick

    def update_bars(self):
        pass

    def listen_data(self):
        pass

    # Message Handlers
    def _reply_handler(self):
        """
        Handle all type of replies from IB in a separate thread.
        :return:
        """
        reply_handlers = {
            'connectionClosed': super(IBDataHandler, self).handle_connection_closed_msg,
            'error': super(IBDataHandler, self).handle_error_msg,
            'managedAccounts': super(IBDataHandler, self).handle_managed_accounts_msg,
            'nextValidId': super(IBDataHandler, self).handle_next_valid_id_msg,
            'tickPrice': self._handle_tick_price,
            'tickSize': self._handle_tick_size
        }

        while True:
            try:
                msg = self.messages.popleft()
                try:
                    msg_dict = dict(msg.items())
                    msg_dict['typeName'] = msg.typeName
                    event = reply_handlers[msg.typeName](msg_dict)  # format message as dict
                    self.events.put(event)
                except KeyError, e:
                    print repr(e)
                    print msg.typeName, 'NEED TO HANDLE THIS KIND OF MESSAGE'
            except IndexError:
                time.sleep(self.msg_interval)

    def _handle_tick_size(self, msg):
        """
        tickerId (int) The ticker Id that was specified previously in the call to reqMktData()
        field (int) Specifies the type of price. Pass the field value into TickType.getField(int tickType)
                    to retrieve the field description.  For example, a field value of 0 will map to bidSize,
                    a field value of 3 will map to askSize, etc.

                    0 = bid size
                    3 = ask size
                    5 = last size
                    8 = volume

        size (int) Specifies the size for the specified field
        :param msg: tickSize message
        :return:
        """
        delayed_size_fields = {
            69: 'bid_size',
            70: 'ask_size',
            74: 'last_size'
        }
        try:
            size = msg['size']
            self.last_tick[delayed_size_fields[msg['field']]] = size
            return MarketEvent(None)
        except KeyError:
            pass

    def _handle_tick_price(self, msg):
        """
        Updates the current market price
        tickerId (int) The ticker Id that was specified previously in the call to reqMktData()
        field (int) Specifies the type of price. Pass the field value into TickType.getField(int tickType)
                    to retrieve the field description.  For example, a field value of 1 will map to bidPrice,
                    a field value of 2 will map to askPrice, etc.
                    1 = bid
                    2 = ask
                    4 = last
                    6 = high
                    7 = low
                    9 = close
        price (double) Specifies the price for the specified field
        canAutoExecute (int) Specifies whether the price tick is available for automatic execution.
                        Possible values are:
                        0 = not eligible for automatic execution
                        1 = eligible for automatic execution
        :param msg: tickPrice message
        :return:
        """
        delayed_price_fields = {
            66: 'bid_price',
            67: 'ask_price',
            68: 'foo',
            75: 'last_price',
            72: 'high_price',
            73: 'low_price',
            76: 'close_price',
        }
        price = msg['price']
        self.last_tick[delayed_price_fields[msg['field']]] = price
        return MarketEvent(None)
