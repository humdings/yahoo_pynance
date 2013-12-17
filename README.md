yahoo_pynance
=============

Python tools for the Yahoo finance csv API.

Each stock object has access to its quotes, history, and charts.
pynance only depends on the standard library but works well
with Pandas DataFrames. 

``` 
>>> google = Stock('GOOG')

>>> google
<GOOG: 2013-12-16 21:46:33.338000>

>>> google.all

{'avg_daily_volume': 1827530.0,
 'book_value': 248.353,
 'change': 12.1899,
 'dividend_per_share': 0.0,
 'dividend_yield': 'N/A',
 'earnings_per_share': 36.746,
 'ebitda': '17.599B',
 'fifty_day_moving_avg': 1041.89,
 'fifty_two_week_high': 1092.3101,
 'fifty_two_week_low': 695.52,
 'market_cap': '358.5B',
 'price': 1072.98,
 'price_book_ratio': 4.27,
 'price_earnings_growth_ratio': 1.53,
 'price_earnings_ratio': 28.87,
 'price_sales_ratio': 6.18,
 'short_ratio': 3.5,
 'stock_exchange': '"NasdaqNM"',
 'timestamp': datetime.datetime(2013, 12, 16, 21, 46, 33, 338000),
 'two_hundred_day_moving_avg': 929.126,
 'volume': 1606175.0}

>>> today = datetime.datetime.today()

>>> other_day = today - datetime.timedelta(days=5)

>>> history = google.history(other_day, today)

>>> history.prices()

{datetime.datetime(2013, 12, 11, 0, 0): 1077.29,
 datetime.datetime(2013, 12, 12, 0, 0): 1069.96,
 datetime.datetime(2013, 12, 13, 0, 0): 1060.79,
 datetime.datetime(2013, 12, 16, 0, 0): 1072.98}

>>> history.volumes()

{datetime.datetime(2013, 12, 11, 0, 0): 1695800.0,
 datetime.datetime(2013, 12, 12, 0, 0): 1595900.0,
 datetime.datetime(2013, 12, 13, 0, 0): 2162400.0,
 datetime.datetime(2013, 12, 16, 0, 0): 1602000.0}
 
 ```

