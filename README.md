yahoo_pynance
=============

Python tools for the Yahoo finance csv API.

Each stock object has access to its quotes, history, and charts.
pynance only depends on the standard library but works well
with Pandas DataFrames. 

``` 
>>> import datetime
>>> from pprint import pprint
>>> from yahoo_pynance.core import *
>>>
>>> google = Stock('GOOG')
>>> google
<GOOG: 2013-12-18 18:36:45.409000>
>>>
>>> google.price 
1084.75 
>>> google.price_earnings_growth_ratio 
1.54 
>>>
>>> today = datetime.datetime.today() 
>>> a_few_days_ago = today - datetime.timedelta(days=3) 
>>>
>>> history = google.history(a_few_days_ago, today) # 'yyyy-mm-dd' strings work too
>>> history 
<yahoo_pynance.core.StockHistory object at 0x0000000002D4E390> 
>>>
>>> pprint(history.data) 
{datetime.datetime(2013, 12, 16, 0, 0): {'Adj Close': 1072.98,
                                         'Close': 1072.98,
                                         'High': 1074.69,
                                         'Low': 1062.01,
                                         'Open': 1064.0,
                                         'Volume': 1602000.0},
 datetime.datetime(2013, 12, 17, 0, 0): {'Adj Close': 1069.86,
                                         'Close': 1069.86,
                                         'High': 1080.76,
                                         'Low': 1068.38,
                                         'Open': 1072.82,
                                         'Volume': 1535700.0}} 
>>>
>>> prices = history.prices() # adjusted close
>>> pprint(prices) 
{datetime.datetime(2013, 12, 16, 0, 0): 1072.98,
 datetime.datetime(2013, 12, 17, 0, 0): 1069.86} 
>>> history.prices(as_list=True) 
[1072.98, 1069.86] 
 ```

