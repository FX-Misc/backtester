import utils.yahoo_finance as yf

class Stock(object):
    def __init__(self, symbol, name=None, sector=None):
        self.symbol = symbol
        self.name = name if name is not None else yf.get_company_name(symbol)
        self.sector = sector if sector is not None else yf.get_company_sector(symbol)
