import data_utils.yahoo_finance as yf

class Stock(object):
    def __init__(self, symbol, name=None, sector=None):
        self.symbol = symbol
        self.name = name if name is not None else yf.get_company_name(symbol)
        self.sector = sector if sector is not None else yf.get_company_sector(symbol)

if __name__ == "__main__":
    stock = Stock('AAPL')
    print stock.__dict__