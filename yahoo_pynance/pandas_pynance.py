# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 11:18:17 2013

@author: David


This module relies on pandas.

functions:
    quotes_df(*symbols) ==> DataFrame of most recent quote info
    history_df(syms, start,end, field) ==> DataFrame of historical data
    
classes:
    Portfolio: The beginnings of a portfolio object to put multiple securities 
               under one roof
               
"""

import pandas as pd
from stocks import Stock
from history import StockHistory

def quotes_df(*symbols):
    data = [Stock(sym) for sym in symbols]
    return pd.DataFrame({i.symbol: i.all for i in data})
    
def history_df(syms, start_date, end_date, field='Adj Close'):
    field = field
    data = [
        StockHistory(sym, start_date, end_date) for sym in syms
    ]
    return pd.DataFrame({i.symbol: i._field(field) for i in data})

    
class Portfolio(object):
    
    def __init__(self, tickers):
        self.tickers = tickers
    
    def get_quotes(self):
        return quotes_df(*self.tickers)
    
    def history(self, start_date, end_date, field='Adj Close'):
        return history_df(self.tickers, start_date, end_date, field=field)
        
        
    