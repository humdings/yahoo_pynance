'''
Created on Wed Dec 18 2013

@author: David Edwards


Yahoo Pynance Core

This module only depends on the Python 2.7 standard lib.
It is intended to be a high level API for Yahoo Finance csv data.

API Reference 
http://code.google.com/p/yahoo-finance-managed/wiki/CSVAPI


FUNCTIONS:

str_to_dt():
    convert yahoo date strings to datetime objects
    
    input: yahoo_date_string
    output: datetime.datetime object

_historical_data():
    used by the StockHistory class to get raw data
    input: ticker, start_date, end_date
    output: dict of dicts
    e.g.
    
    {datetime.datetime(2013, 11, 13, 0, 0): {'Adj Close': 1032.47,
                                            'Close': 1032.47,
                                            'High': 1032.85,
                                            'Low': 1006.5,
                                            'Open': 1006.75,
                                            'Volume': 1579400.0},
    ...
    ...
    }
    
sector_data:
    Reads the rows of the sector/industry/company csv
    into a list of the rows.
    see below for more

sector_dict:
    puts sector_data into a dict with the format
            'industry_name': {fields: values}
            
    e.g.
    {'Healthcare': {'1-Day Price Chg %': -0.59,
                    'Debt to Equity': 74.877,
                    'Div. Yield %': 2.627,
                    'Market Cap': '83045.59B',
                    'Net Profit Margin (mrq)': 16.661,
                    'P/E': 28.574,
                    'Price To Free Cash Flow (mrq)': 218.548,
                    'Price to Book': 34.871,
                    'ROE %': 19.842},
     ...
     ...
    }
    
CLASSES:
    StockHistory
    StockChart
    Stock

see classes for more

'''

import os
import datetime
import cStringIO
import csv
import webbrowser

from urllib2 import Request, urlopen
from urllib import urlencode, urlretrieve


def str_to_dt(date):
    ''' Converts Yahoo Date Strings to datetime objects. '''
    yr = int(date[0:4])
    mo = int(date[5:7])
    day = int(date[8:10])
    return datetime.datetime(yr,mo, day)

def _historical_data(sym, start_date, end_date, **kwargs):
    start_date = str(start_date)
    end_date = str(end_date)
    url = 'http://ichart.finance.yahoo.com/table.csv?' 
    url += 's={}&a={}&b={}&c={}&d={}&e={}&f={}&g={}'.format(  
        sym,  
        str(int(start_date[5:7]) - 1),  
        str(int(start_date[8:10])),  
        str(int(start_date[0:4])),  
        str(int(end_date[5:7]) - 1),  
        str(int(end_date[8:10])),
        str(int(end_date[0:4])),
        kwargs.get('interval', 'd'),
    )  
    url += '&ignore=.csv'  
    req = Request(url)
    resp = urlopen(req)
    content = str(resp.read().decode('utf-8').strip())
    daily_data = content.splitlines()
    hist_dict = dict()
    keys = daily_data[0].split(',')
    for day in daily_data[1:]:
        day_data = day.split(',')
        date = str_to_dt(day_data[0])
        hist_dict[date] = {}
        for i in range(1, len(keys)):
            try:
                hist_dict[date][keys[i]] = float(day_data[i])
            except ValueError:
                hist_dict[date][keys[i]] = day_data[i]
    return hist_dict    
    

class StockHistory(object):
    """
    Date format must be 'YYYY-MM-DD' or a datetime object.

    keyword arg 'interval' is supported.
        'd' ==> days,
        'w' ==> weeks,
        'm' ==> monthts,
        'v' ==> dividends only. Warning, this raises a KeyError 
                                if a stock doesn't offer dividends.
    """
    def __init__(self, symbol, start_date, end_date, **kwargs):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.data = _historical_data(symbol, start_date, end_date, **kwargs)
        self.dates = sorted(self.data.keys())
    
    def _field(self, field, **kwargs):
        data = {
            date: self.data[date][field] for date in self.dates
        }
        if kwargs.get('as_list', False):
            return [v for k, v in sorted(data.items())]
        return data
        
    def fields(self, *fields):
        data ={}
        for dt in self.dates:
            data[dt] = {field: self.data[dt][field] for field in fields}
        return data
        
    def volumes(self, **kwargs):
        return self._field('Volume', **kwargs)
    
    def prices(self, **kwargs):
        return self._field('Adj Close', **kwargs)
    
    def close_prices(self, **kwargs):
        return self._field('Close', **kwargs)
    
    def open_prices(self, **kwargs):
        return self._field('Open', **kwargs)
    
    def highs(self, **kwargs):
        return self._field('High', **kwargs)
    
    def lows(self, **kwargs):
        return self._field('Low', **kwargs)
    
    
"""
INDUSTRY SECTORS

Name                            Tag

Basic_Materials                 1
Conglomerates                   2
Consumer_Goods                  3
Financial                       4
Healthcare                      5
Industrial_Goods                6
Services                        7
Technology                      8
Utilities                       9

This section was thrown together and should be improved upon.

For now, sector_data() is the gets sector/industry/companies data.

Use sector_data(sector=Tag) for a specific sector, the default is all sectors.

For company data using sector_data(sector='ID') will work but I am not
too sure of the 'ID' pattern.

Reference
http://code.google.com/p/yahoo-finance-managed/wiki/csvCompanyDownload
"""


def sector_data(**kwargs):
    '''
    This gets a list of the rows in the csv.
    Further processing is required to put it in 
    more useful formats.
    '''
    field = kwargs.get('field', 'coname')
    sector = kwargs.get('sector', 's_')
    sort_direction = kwargs.get('sort_direction', 'u')
    url = 'http://biz.yahoo.com/p/csv/'
    url += sector
    url += field
    url += sort_direction + '.csv'  
    response = urlopen(url).read().strip('\x00')
    output = cStringIO.StringIO(response)
    return [row for row in csv.reader(output, dialect='excel')]

def sector_dict(**kwargs):
    '''
    Returns sector data as a dict of dicts.
    
        key=sector/company;
        value={fields: field values}

    Useful for working with Pandas DataFrames.
    '''
    cr = sector_data(**kwargs)
    idx = cr.pop(0)[1::]
    cols = [i.pop(0) for i in cr]
    d = {
        cols[i]: {
            idx[j]: cr[i][j]for j in range(len(idx))
        } for i in range(len(cols))
    }
    for i in d:
        for j in d[i]:
            try:
                d[i][j] = float(d[i][j])
            except ValueError:
                pass
    return d



class StockChart():
    """
    Gets a stock chart from Yahoo that can be opened in
    a browser or saved to a file for use elsewhere.
    
    url parameters:
    Stock symbol is the bare minimum unless called from a stock object,
    then no parameters are required. Optional keyword args are outlined
    below.

    keyword arguments:
        timespan: 1d, 5d, 3m, 6m, 1y, 2y, 5y, my (max years)
            eg: tspan = 3m 
        type: line=l, bar=b, candle=c
            eg: type = b   
        scale: on/off for logarithmic/linear
            eg: scale = on
        size: s, m, l
            eg: size=m
        avgs: moving average indicators.
            pass a list of day lengths as strings prepended
            with 'e' for exponential and 'm' for simple.
            eg: avgs=['m5','m20','e5','e20']
            
        """
    def __init__(self, symbol, **kwargs):
        self.symbol = symbol
        self.kwargs = kwargs
        self.url = self._url()
        
    def open_in_browser(self):
        webbrowser.open_new(self.url)
    
    def save(self, path):
        urlretrieve(self.url, path)
        self.abspath = os.path.abspath(path)
        
    def _url(self):
        kwargs = self.kwargs
        symbol = self.symbol
        url = "http://chart.finance.yahoo.com/z?"
        params = urlencode({
            's': symbol,
            't': kwargs.get('tspan','6m'),
            'q': kwargs.get('type', 'l'),
            'l': kwargs.get('scale', 'off'),
            'z': kwargs.get('size', 's'),
            'p': ','.join(kwargs.get('avgs',''))
        })
        url += "%s"%params
        return url


class Stock(object):
    '''
    A timestamped Stock object with the most
    recent quotes according to Yahoo.

    NOTE: Yahoo csv data can be up to 15 min delayed.

    Methods:
        self.history(start_date, end_date) ==> StockHistory obj
        
        self.chart(**kwargs) ==> StockChart obj
        
        self.update() ==> call self.__init__() to update quotes.
    
    '''
    
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
    
    def __getitem__(self,item):
        return self.all[item]
    
    def __iter__(self):
        return iter(self.all)
        
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

