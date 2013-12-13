# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 21:21:25 2013

@author: David Edwards
"""
from urllib2 import Request, urlopen
import datetime
from history import StockHistory
from charts import StockChart

class Stock(object):
    
    def __init__(self, symbol):
        self.symbol = symbol
        self.all = self._all_quote_data()
        self.timestamp = datetime.datetime.now()                
        self.all['timestamp'] = self.timestamp
        self.price = self.all['price']
        self.change = self.all['change']
        self.volume = self.all['volume']
        self.avg_daily_volume = self.all['avg_daily_volume']
        self.stock_exchange = self.all['stock_exchange']
        self.market_cap = self.all['market_cap']
        self.book_value = self.all['book_value']
        self.ebitda = self.all['ebitda']
        self.dividend_per_share = self.all['dividend_per_share']
        self.dividend_yield = self.all['dividend_yield']
        self.earnings_per_share = self.all['earnings_per_share']
        self.fifty_two_week_high = self.all['fifty_two_week_high']
        self.fifty_two_week_low = self.all['fifty_two_week_low']
        self.fifty_day_moving_avg = self.all['fifty_day_moving_avg']
        self.two_hundred_day_moving_avg = self.all['two_hundred_day_moving_avg']
        self.price_earnings_ratio = self.all['price_earnings_ratio']
        self.price_earnings_growth_ratio = self.all['price_earnings_growth_ratio']
        self.price_sales_ratio = self.all['price_sales_ratio']
        self.price_book_ratio = self.all['price_book_ratio']
        self.short_ratio = self.all['short_ratio']
        
    def __repr__(self):
        return "<%s: %s>"%(self.symbol, self.timestamp)
    
    def _quote_request(self, stat):
        url = "http://download.finance.yahoo.com/d/quotes.csv?s=%s&f=%s" %(
            self.symbol, 
            stat
        )
        req = Request(url)
        response = urlopen(req)
        return str(response.read().decode('utf-8').strip())
    
    def _all_quote_data(self):
        values = self._quote_request('l1c1va2xj1b4j4dyekjm3m4rr5p5p6s7').split(',')
        quotes = dict(
            price = values[0],
            change = values[1],
            volume = values[2],
            avg_daily_volume = values[3],
            stock_exchange = values[4],
            market_cap = values[5],
            book_value = values[6],
            ebitda = values[7],
            dividend_per_share = values[8],
            dividend_yield = values[9],
            earnings_per_share = values[10],
            fifty_two_week_high = values[11],
            fifty_two_week_low = values[12],
            fifty_day_moving_avg = values[13],
            two_hundred_day_moving_avg = values[14],
            price_earnings_ratio = values[15],
            price_earnings_growth_ratio = values[16],
            price_sales_ratio = values[17],
            price_book_ratio = values[18],
            short_ratio = values[19],
        )        
        for q in quotes:
            try:
                quotes[q] = float(quotes[q])
            except ValueError:
                pass
        return quotes
        
    def chart(self, **kwargs):
        return StockChart(self.symbol, **kwargs)
    
    def history(self, start_date, end_date, **kwargs):
        return StockHistory(
            self.symbol, start_date, end_date, **kwargs
        )
    def update(self):
        self.__init__(self.symbol)
        
    
