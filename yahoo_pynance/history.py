# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 21:21:06 2013

@author: edwards7011
"""
from urllib2 import Request, urlopen
from utils import str_to_dt


def _historical_data(sym, start_date, end_date, **kwargs):
    start_date = str(start_date)
    end_date = str(end_date)
    url = 'http://ichart.yahoo.com/table.csv?'  
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
            return data.values()
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
    
        
