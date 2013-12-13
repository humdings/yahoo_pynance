# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 12:21:10 2013

@author: David Edwards
"""

import os
import webbrowser
from urllib import urlencode, urlretrieve

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
