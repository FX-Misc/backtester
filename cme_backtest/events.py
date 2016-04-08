from trading import events

class CMEBacktestMarketEvent(events.MarketEvent):
    def __init__(self, dt):
        super(CMEBacktestMarketEvent, self).__init__(dt)