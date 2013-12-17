# -*- coding: utf-8 -*-"""Created on Thu Dec 12 11:18:17 2013@author: DavidThis module requires pandas, numpy and scipyfunctions:    quotes_df(*symbols) ==> DataFrame of most recent quote info    history_df(syms, start,end, field) ==> DataFrame of historical dataclasses:    Portfolio: The beginnings of a portfolio object to put multiple securities                under one roof"""import pandas as pdimport numpy as npfrom scipy.optimize import nnlsfrom stocks import Stockfrom history import StockHistorydef quotes_df(*symbols):    data = [Stock(sym) for sym in symbols]    return pd.DataFrame({i.symbol: i.all for i in data})def history_df(syms, start_date, end_date, field='Adj Close'):    field = field    data = [        StockHistory(sym, start_date, end_date) for sym in syms    ]    return pd.DataFrame({i.symbol: i._field(field) for i in data})def min_var_weights(returns, allow_shorts=False):    '''    Returns a dictionary of sid:weight pairs.    allow_shorts=True --> minimum variance weights returned    allow_shorts=False --> least squares regression finds non-negative                           weights that minimize the variance     '''    cov = 2*returns.cov()    x = np.array([0.]*(len(cov)+1))    x[-1] = 1.0    p = lagrangize(cov)    if allow_shorts:          weights = np.linalg.solve(p, x)[:-1]    else:        weights = nnls(p, x)[0][:-1]    return {sym: weights[i] for i, sym in enumerate(returns)}def lagrangize(df):    '''    Utility funcion to format a DataFrame     in order to solve a Lagrangian sysem.     '''    df = df    df['lambda'] = np.ones(len(df))    z = np.ones(len(df) + 1)    x = np.ones(len(df) + 1)    z[-1] = 0.0    x[-1] = 1.0    m = [i for i in df.as_matrix()]    m.append(z)        return pd.DataFrame(np.array(m))def eff_frontier(returns, allow_shorts=False):    sigma = 2*returns.cov()    ones = [1.0]*len(sigma)    mu = [i for i in returns.mean()]    sigma['_mu']= mu    sigma['_lambda']= ones    mat = list(sigma.as_matrix())    mu.extend([0,0])    ones.extend([0,0])    mat.extend([mu,ones])    mat = np.array(mat)    b = [0.]*len(sigma)    b.append(max(max(mu),.02))    b.append(1)    if allow_shorts:        weights = np.linalg.solve(mat, b)[:-2]    else:        weights = nnls(mat, b)[0][:-2]    return {sym: weights[i] for i,sym in enumerate(returns)}class Portfolio(object):    def __init__(self, tickers):        self.tickers = tickers    def quotes(self):        return quotes_df(*self.tickers)    def history(self, start_date, end_date, field='Adj Close'):        return history_df(self.tickers, start_date, end_date, field=field)    def efficient_frontier(self, start_date, end_date, **kwargs):        shorts = kwargs.get('allow_shorts', False)        field = kwargs.get('field', 'Close')        prices = self.history(start_date, end_date, field=field)        returns = prices.pct_change().dropna()        return eff_frontier(returns, allow_shorts=shorts)            def min_var_weights(self, start_date, end_date, **kwargs):        shorts = kwargs.get('allow_shorts', False)        field = kwargs.get('field', 'Close')        prices = self.history(start_date, end_date, field=field)        returns = prices.pct_change().dropna()        return min_var_weights(returns, allow_shorts=shorts)            