'''
Created on Wed Dec 18 2013

@author: David Edwards


Yahoo Pynance API
Depends on the Python 2.7 standard lib.

API Reference
http://code.google.com/p/yahoo-finance-managed/wiki/CSVAPI
'''


import os
import datetime
import cStringIO
import csv
import webbrowser

from urllib2 import Request, urlopen
from urllib import urlencode, urlretrieve


def str_to_dt(date):
    ''' Converts Yahoo Date Strings (YYYY-MM-DD) to datetime objects. '''
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

def quote_request(symbol, stat):
    url = "http://download.finance.yahoo.com/d/quotes.csv?s=%s&f=%s" %(
        symbol, 
        stat
    )
    req = Request(url)
    response = urlopen(req)
    return str(response.read().decode('utf-8').strip())


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
            idx[j]: cr[i][j] for j in range(len(idx))
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
    fields = {
        'price': 'l1', 
        'change':'c1', 
        'volume':'v',
        'avg_daily_volume': 'a2',
        'stock_exchange': 'x',
        'market_cap':'j1',
        'book_value': 'b4',
        'ebitda': 'j4', 
        'dividend_per_share': 'd',
        'dividend_yield': 'y',
        'earnings_per_share': 'e',
        'fifty_two_week_high': 'k',
        'fifty_two_week_low': 'j', 
        'fifty_day_moving_avg': 'm3',
        'two_hundred_day_moving_avg':'m4',
        'price_earnings_ratio':'r',
        'price_earnings_growth_ratio':'r5',
        'price_sales_ratio':'p5',
        'price_book_ratio': 'p6',
        'short_ratio': 's7', 
        'revenue': 's6',
        'shares_outstanding': 'j2',
        'shares_owned': 's1',
        'pct_change_from_50_day_MA':'m8',
        'pct_change_from_200_day_MA': 'm6', 
        'one_yr_target_price': 't8',
        'dividend_pay_date': 'r1',
    }
    def __init__(self, symbol):
        self.symbol = symbol
        self.all = self._all_quote_data()
        self.timestamp = datetime.datetime.now()
        for quote in self.all:
            self.__dict__[quote] = self.all[quote]

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
        quotes = {i: self._quote_request(self.fields[i]) for i in self.fields}
        for q in quotes:
            try:
                quotes[q] = float(quotes[q])
            except ValueError:
                pass
        return quotes

    def chart(self, **kwargs):
        return StockChart(self.symbol, **kwargs)

    def history(self, start_date, end_date, **kwargs):
        return StockHistory(self.symbol, start_date, end_date, **kwargs)

    def update(self):
        self.__init__(self.symbol)
