import backtrader as bt
import yfinance as yf
import pandas as pd
import os
import re
import glob
from datetime import datetime, timezone, timedelta

"""## Fetch data"""

#ROOT_PATH = os.curdir
#ROOT_FILENAME = 'lastfetchdata'
YF_INTERVALS = ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
YF_PERIODS = ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
YF_MAX_PERIODS = {'1m': 7, '2m': 7, '5m': 7, '15m':7, '30m':7, '60m': 730, '90m':7, '1h':730}

'''    
    def __init__(self):
        self.interval = dict()
        for file in glob.glob(os.path.join(self.ROOT_PATH, self.ROOT_FILENAME+'*.csv')):
            f = file.split('/')[-1]
            self.interval[re.split('\.|\_', f)[-2]] = file 
        #print(self.interval)
        return

    def isuptodate(self, interval):
        if self.interval and interval in self.interval.keys():
            df = pd.read_csv(self.interval[interval], index_col='Datetime')
            lastcandle = datetime.fromisoformat(df.index[-1])
            #print(lastcandle)
            tnow = datetime.utcnow()
            tnow = tnow.replace(tzinfo = timezone.utc)
            timedif = timedelta(days=self.days(interval), hours=self.hours(interval), minutes=self.minutes(interval))
            #print(tnow)
            #print(timedif)  
            #print(tnow - lastcandle > timedif)          
            return (tnow - lastcandle < timedif)
        else:
            return False
'''

def hours(interval):
    hours = 0
    if interval[-1] == 'h':
        hours = int(interval[:-1])
    return hours

def minutes(interval):
    minutes = 0
    if interval[-1] == 'm':
        minutes = int(interval[:-1])
    return minutes

def days(interval):
    days = 0
    if interval[-1] == 'd':
        days = int(interval[:-1])
    if interval[-2:] == 'wk':
        days = int(interval[:-2])*7
    if interval[-2:] == 'mo':
        days = int(interval[:-2])*30
    if interval[-1] == 'y':
        days = int(interval[:-1])*365            
    return days

'''
    def fetch_data(self, interval='1d', ticker="BTC-USD", period=None):       
        #fetchflag = False
        if not self.isuptodate(interval):
            #print('Updating...')
            self.update(interval, ticker)
        if not period:
            return bt.feeds.YahooFinanceCSVData(dataname=self.interval[interval], adjclose=False, swapcloses=True, round=False)
        else:
            tnow = datetime.utcnow()
            tnow = tnow.replace(tzinfo = timezone.utc)    
            fromdate = tnow - timedelta(days=self.days(period), hours=self.hours(period), minutes=self.minutes(period))
            return bt.feeds.YahooFinanceCSVData(dataname=self.interval[interval], fromdate=fromdate, adjclose=False, swapcloses=True, round=False)
        
    def update(self, interval, ticker):
        btcdata = yf.Ticker(ticker)
        yfinterval, step = self.interval2yf(interval)
        if self.interval and interval in self.interval.keys():
            df_old = pd.read_csv(self.interval[interval], index_col='Datetime')
            fecha = datetime.fromisoformat(df_old.index[-1]) + timedelta(days=self.days(interval), hours=self.hours(interval), minutes=self.minutes(interval))
            try:
                df_new = btcdata.history(interval = yfinterval, start=fecha)
            except:
                if yfinterval in self.YF_MAX_PERIODS.keys():
                    tnow = datetime.utcnow()
                    tnow = tnow.replace(tzinfo = timezone.utc)    
                    start = tnow - timedelta(days=self.YF_MAX_PERIODS[yfinterval])
                    df_new = btcdata.history(interval = yfinterval, start=start)
                else:
                    df_new = btcdata.history(interval = yfinterval, period=None)
            if step != 0:
                df_new = df_new.iloc[1::step]
            #print(len(df_old))    
            df = pd.concat([df_old, df_new], axis=0)
            df.index.name = 'Datetime'
            #print(len(df))                   
        else:
            if yfinterval in self.YF_MAX_PERIODS.keys():
                tnow = datetime.utcnow()
                tnow = tnow.replace(tzinfo = timezone.utc)    
                start = tnow - timedelta(days=self.YF_MAX_PERIODS[yfinterval])
                df = btcdata.history(interval = yfinterval, start=start)
            else:
                df = btcdata.history(interval = yfinterval, period=None)
            if step != 0:
                df = df.iloc[1::step]
        self.interval[interval] = os.path.join(self.ROOT_PATH, self.ROOT_FILENAME+'_'+interval+'.csv')
        df['Volume'].replace(to_replace = 0.0, method= 'ffill', inplace=True)
        df.to_csv(self.interval[interval])
        return
'''    
def interval2yf(interval):
    h = self.hours(interval)
    m = self.minutes(interval)
    d = self.days(interval)
    if interval in self.YF_INTERVALS:
        return interval, 0
    elif h > 0 and h < 24:
        return '1h', h
    elif d > 0 and d < 7:
        return '1d', d
    elif m == 45 or m == 75:
        return '15m', m//15
    elif m%5 == 0:
        return '5m', m//5
    elif m%2 == 0:
        return '2m', m//2
    elif m > 0:
        return '1m', m