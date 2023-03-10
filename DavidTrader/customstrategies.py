import backtrader as bt
#import numpy as np
from datetime import datetime
from . import customindicators
from . import mlindicators
#import re
import logging

class Strategy1(bt.Strategy):

    params = (('period', 20), ('cth_start', '08:00'), ('cth_end', '18:00'),)  
    #params = (('_ind1', bt.talib.SMA), ('_ind2', bt.talib.EMA))
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler('strat.log')
    logger.addHandler(handler)

    def __init__(self, params=None, fdata=None, indicator_dict = None, conditions =None):
        self.logger.info('Start:\n')
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close)
        self.ema = bt.indicators.MovingAverageExponential(self.data.close)
        self.rsi = bt.indicators.RSI(self.data.close)
        self.macd = bt.indicators.MACDHisto(self.data.close)
        #self.macd_hist = self.macd - self.macd_signal
        self.bb = bt.indicators.BBands(self.data.close)
        self.stoch = bt.indicators.Stochastic(self.data)
        if self.p.cth_start != None:
            self.cth_start = datetime.strptime(self.p.cth_start, '%H:%M').time()
            self.cth_end = datetime.strptime(self.p.cth_end, '%H:%M').time()
        #if params != None: 
        #  for name, val in params.items():
        #    setattr(self.params, name, val) 
        #    print(self.params)   
        #self.indicator_dict = indicator_dict
        #for self.p.:
        #  for key in indicator_dict.keys():
        #    exec('self.'+key+' = indicator_dict[key]')
        self.order = None

    def next(self):
        if self.order:
            return
        if hasattr(self, 'cth_start') and ((self.data.datetime.time() < self.cth_start) or (self.data.datetime.time() > self.cth_end)):
            return  
        if not self.position: # check if you already have a position in the market
            if (self.data.close[0] < self.bb.bot[0])  & (self.stoch.percK[0] < 20) & (self.macd.histo[0] < 0):
                self.log('Buy Create, %.2f' % self.data.close[0])
                self.order = self.buy(size=0.01) 
            if (self.data.close[0] > self.bb.bot[0]) & (self.stoch.percK[0] > 80) & (self.macd.histo[0] > 0):
                self.log('Sell Create, %.2f' % self.data.close[0])
                self.order = self.sell(size=0.01)
        else:
        # This means you are in a position, and hence you need to define exit strategy here.
            if len(self) >= (self.bar_executed + 4):
                self.log('Position Closed, %.2f' % self.data.close[0])
                self.order = self.close()
  
	  # outputting information
    def log(self, txt):
        dt=self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
        self.logger.info('%s, %s\n' % (dt.isoformat(), txt))
   
    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy():
                self.log("Executed BUY (Price: %.2f, Value: %.2f, Commission %.2f)" %
                (order.executed.price, order.executed.value, order.executed.comm))
            else:
                self.log("Executed SELL (Price: %.2f, Value: %.2f, Commission %.2f)" %
                (order.executed.price, order.executed.value, order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order was canceled/margin/rejected")
            self.order = None

class Ichimoku1(bt.Strategy):

    params = (('period', 20), ('cth_start', '08:00'), ('cth_end', '18:00'),)

    logger = logging.getLogger(__name__)
    handler = logging.FileHandler('strat.log')
    logger.addHandler(handler)
    
    def __init__(self, params=None):
        self.logger.info('Start:\n')
        # Calculate technical indicators
        self.macd = bt.indicators.MACD(self.data.close)
        self.ichimoku = bt.indicators.Ichimoku()
        self.rsi = bt.indicators.RSI(self.data.close, period=14)
        self.bb = bt.indicators.BBands(self.data.close, period=20)
        if self.p.cth_start != None:
            self.cth_start = datetime.strptime(self.p.cth_start, '%H:%M').time()
            self.cth_end = datetime.strptime(self.p.cth_end, '%H:%M').time()

        # Find support and resistance levels using fibonacci retracements
        #high = df['High'].max()
        #low = df['Low'].min()
        #df['fib_level_0'] = low + (high - low) * 0
        #df['fib_level_236'] = low + (high - low) * 0.236
        #df['fib_level_382'] = low + (high - low) * 0.382
        #df['fib_level_500'] = low + (high - low) * 0.5
        #df['fib_level_618'] = low + (high - low) * 0.618
        #df['fib_level_764'] = low + (high - low) * 0.764
        #df['fib_level_100'] = low + (high - low) * 1
        self.order = None

    def next(self):
        if self.order:
            return
        if hasattr(self, "cth_start") and ((self.data.datetime.time() < self.cth_start) or (self.data.datetime.time() > self.cth_end)):
            return  
        if not self.position: # check if you already have a position in the market
            if (self.macd.macd[0] > self.macd.signal[0]) & (self.ichimoku.senkou_span_a[0] < self.data.close[0]) & (self.ichimoku.senkou_span_b[0] > self.data.close[0]) & (self.rsi[0] < 30) & (self.data.close[0] < self.bb.bot[0]):
                self.log('Buy Create, %.2f' % self.data.close[0])
                self.order = self.buy(size=0.01) 
            if (self.macd.macd[0] < self.macd.signal[0]) & (self.ichimoku.senkou_span_a[0] > self.data.close[0]) & (self.ichimoku.senkou_span_b[0] < self.data.close[0]) & (self.rsi[0] > 70) & (self.data.close[0] > self.bb.top[0]):
                self.log('Sell Create, %.2f' % self.data.close[0])
                self.order = self.sell(size=0.01)
        else:
        # This means you are in a position, and hence you need to define exit strategy here.
            if len(self.position<0):
                if (self.macd.macd[0] > self.macd.signal[0]) & (self.ichimoku.senkou_span_a[0] < self.data.close[0]):
                    self.log('Position Closed, %.2f' % self.data.close[0])
                    self.order = self.close()
            else:
                if (self.macd.macd[0] < self.macd.signal[0]) & (self.ichimoku.senkou_span_a[0] > self.data.close[0]) & (self.ichimoku.senkou_span_b[0] < self.data.close[0]) & (self.rsi[0] > 70) & (self.data.close[0] > self.bb.top[0]):
                    self.log('Position Closed, %.2f' % self.data.close[0])
                    self.order = self.close()
	
    # outputting information
    def log(self, txt):
        dt=self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
        self.logger.info('%s, %s\n' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy():
                self.log("Executed BUY (Price: %.2f, Value: %.2f, Commission %.2f)" %
                (order.executed.price, order.executed.value, order.executed.comm))
            else:
                self.log("Executed SELL (Price: %.2f, Value: %.2f, Commission %.2f)" %
                (order.executed.price, order.executed.value, order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order was canceled/margin/rejected")
        self.order = None

"""## VWAPScalping"""

class VWAPScalping(bt.Strategy):
    params = (
        ('vwap_period', 20),
        ('stop_loss', 50),
        ('take_profit', 0.02),
        ('cth_start', '08:00'), 
        ('cth_end', '18:00'),        
    )

    logger = logging.getLogger(__name__)
    handler = logging.FileHandler('strat.log')
    logger.addHandler(handler)

    def __init__(self):
        self.logger.info('Start:\n')
        self.vwap = customindicators.VolumeWeightedAveragePrice()
        self.rsi = bt.indicators.RSI()
        self.bbands = bt.indicators.BollingerBands()
        self.sma = bt.indicators.SimpleMovingAverage(period=self.params.vwap_period)
        #self.volume = bt.indicators.Volume()
        if self.p.cth_start != None:
            self.cth_start = datetime.strptime(self.p.cth_start, '%H:%M').time()
            self.cth_end = datetime.strptime(self.p.cth_end, '%H:%M').time()            
        self.order = None

    def next(self):
        if self.order:
            return
        if hasattr(self, "cth_start") and ((self.data.datetime.time() < self.cth_start) or (self.data.datetime.time() > self.cth_end)):
            return              
        if not self.position:
            if self.data.close[0] < self.vwap[0] and self.rsi[0] < 30 and self.data.close[0] < self.bbands.bot[0] and self.data.volume[0] > 100:
                self.log('Buy Create, %.2f' % self.data.close[0])
                self.buy_bracket(size=0.01, limitprice=self.data.close[0]*(1+self.p.take_profit), stopprice=self.data.close[0]-self.p.stop_loss)
                #self.buy(size=0.01)
                #self.sell(exectype=bt.Order.Stop, price=self.data.close[0]*(1 - self.params.stop_loss))
                #self.sell(exectype=bt.Order.Limit, price=self.data.close[0] *(1+ self.params.take_profit))
        else:
            if self.data.close[0] > self.vwap[0] and self.rsi[0] > 70 and self.data.close[0] > self.bbands.top[0]:
                self.log('Sell Create, %.2f' % self.data.close[0])
                self.sell_bracket(size=0.01, limitprice=self.data.close[0]*(1+self.p.take_profit), stopprice=self.data.close[0]-self.p.stop_loss)                
                #self.sell(size=0.01)
                #self.buy(exectype=bt.Order.Stop, price=self.data.close[0]*(1 + self.params.stop_loss))
                #self.buy(exectype=bt.Order.Limit, price=self.data.close[0] *(1- self.params.take_profit))

    # outputting information
    def log(self, txt):
        dt=self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
        self.logger.info('%s, %s\n' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy(): #and order.exectype not in [bt.Order.Stop, bt.Order.Limit]:
                self.log("Executed BUY (Price: %.2f, Value: %.2f, Commission %.2f)" %
                (order.executed.price, order.executed.value, order.executed.comm))
                self.bar_executed = len(self)
            elif order.issell(): #and order.exectype not in [bt.Order.Stop, bt.Order.Limit]:
                self.log("Executed SELL (Price: %.2f, Value: %.2f, Commission %.2f)" %
                (order.executed.price, order.executed.value, order.executed.comm))
                self.bar_executed = len(self)
            elif order.exectype in [bt.Order.Stop, bt.Order.Limit]:
                self.log("Position CLOSED (Price: %.2f, Value: %.2f, Commission %.2f)" %
                (order.executed.price, order.executed.value, order.executed.comm))                
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order was canceled/margin/rejected")
        self.order = None

"""## SupportRes"""

class SupportRes(bt.Strategy):

    params = (
        ('stop_loss', 50),
        ('take_profit', 0.025),
        ('cth_start', '08:00'), 
        ('cth_end', '18:00'),          
    )
    
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler('strat.log')
    logger.addHandler(handler)
    
    def __init__(self):
        self.logger.info('Start:\n')        
        self.rsi = bt.indicators.RSI()
        if self.p.cth_start != None:
            self.cth_start = datetime.strptime(self.p.cth_start, '%H:%M').time()
            self.cth_end = datetime.strptime(self.p.cth_end, '%H:%M').time()            
        self.order = None

    def next(self):
        if self.order:
            return
        if hasattr(self, "cth_start") and ((self.data.datetime.time() < self.cth_start) or (self.data.datetime.time() > self.cth_end)):
            return            
        if not self.position:
            if self.data.close[0] <= self.rsi[0]:
                # Place a buy trade
                self.log('Buy Create, %.2f' % self.data.close[0])
                size = 0.01
                self.buy_bracket(size=size, limitprice=self.data.close[0]*(1+self.p.take_profit), stopprice=self.data.close[0]-self.p.stop_loss)                
                #self.buy(size=0.01)
                #self.close(exectype=bt.Order.Stop, price=self.data.close[0] *(1- self.p.stop_loss))
                #self.close(exectype=bt.Order.Limit, price=self.data.close[0]*(1 + self.params.take_profit))                
        # Check if the price is at or above the resistance level
        else:
            if self.data.close[0] >= self.rsi[0]:
                # Place a sell trade
                self.log('Sell Create, %.2f' % self.data.close[0])
                self.sell_bracket(size=0.01, limitprice=self.data.close[0]*(1+self.p.take_profit), stopprice=self.data.close[0]-self.p.stop_loss)                  
                #self.sell(size=0.01)
                #self.close(exectype=bt.Order.Stop, price=self.data.close[0] *(1+ self.params.stop_loss))
                #self.close(exectype=bt.Order.Limit, price=self.data.close[0] *(1- self.params.take_profit))

    # outputting information
    def log(self, txt):
        dt=self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
        self.logger.info('%s, %s\n' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy(): #and order.exectype not in [bt.Order.Stop, bt.Order.Limit]:
                self.log("Executed BUY (Price: %.2f, Value: %.2f, Commission %.2f)" %
                (order.executed.price, order.executed.value, order.executed.comm))
                self.bar_executed = len(self)
            else:# order.issell(): #and order.exectype not in [bt.Order.Stop, bt.Order.Limit]:
                self.log("Executed SELL (Price: %.2f, Value: %.2f, Commission %.2f)" %
                (order.executed.price, order.executed.value, order.executed.comm))
                self.bar_executed = len(self)              
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order was canceled/margin/rejected")
        self.order = None

"""## Random Forest (RFR.../RFC...)"""

class RFR1(bt.Strategy):
    params = (
        ('cth_start', '08:00'), 
        ('cth_end', '18:00'),         
    )

    logger = logging.getLogger(__name__)
    handler = logging.FileHandler('strat.log')
    logger.addHandler(handler)

    def __init__(self):
        self.logger.info('Start:\n')        
        self.rfpp = mlindicators.RandomForestPredictor()
        if self.p.cth_strat:
            self.cth_start = datetime.strptime(self.p.cth_start, '%H:%M').time()
            self.cth_end = datetime.strptime(self.p.cth_end, '%H:%M').time()        
        self.order = None

    def next(self):
        if self.order:
            return
        if hasattr(self, 'cth_start') and ((self.data.datetime.time() < self.cth_start) or (self.data.datetime.time() > self.cth_end)):
            return            
        if not self.position: # check if you already have a position in the market
            if (self.rfpp[0] > self.data.close[0]):
                self.log('Buy Create (last candle price %.2f, RF prediction for next candle %.2f)' % (self.data.close[0], self.rfpp[0]))
                self.order = self.buy(size=0.01) 
            if (self.rfpp[0] < self.data.close[0]):
                self.log('Sell Create (last candle price %.2f, RF prediction for next candle %.2f)' % (self.data.close[0], self.rfpp[0]))
                self.order = self.sell(size=0.01)
        else:
        # This means you are in a position, and hence you need to define exit strategy here.
            if (self.position > 0 and self.rfpp[0] < self.close[0]) or (self.position < 0 and self.rfpp[0] > self.close[0]):
                self.log('Position Closed, %.2f' % self.data.close[0])
                self.order = self.close()

    # outputting information
    def log(self, txt):
        dt=self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
        self.logger.info('%s, %s\n' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy():
                self.log("Executed BUY (Price: %.2f, Value: %.2f, Commission %.2f)" %
                (order.executed.price, order.executed.value, order.executed.comm))
            else:
                self.log("Executed SELL (Price: %.2f, Value: %.2f, Commission %.2f)" %
                (order.executed.price, order.executed.value, order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order was canceled/margin/rejected")
        self.order = None

class CustomStrategyFromHelper(bt.Strategy):

    params = (('cth_start', None),('cth_end', None), ('stop_loss', 0.1), ('take_profit', 50), ('indicators', None), ('signals', None),)

    logger = logging.getLogger(__name__)
    handler = logging.FileHandler('strat.log')
    logger.addHandler(handler)

    def __init__(self):#, params=None, indicators=None, signals=None):
        #if params != None: 
        #    for name, val in params.items():
        #        setattr(self.params, name, val) 
                #print(self.params) 
        self.logger.info('Start:\n')  
        if self.p.cth_start and self.p.cth_end:
            self.cth_start = datetime.strptime(self.p.cth_start, '%H:%M').time()
            self.cth_end = datetime.strptime(self.p.cth_end, '%H:%M').time()    
        if self.p.indicators !=  None:
            for i in range(len(self.p.indicators)):
                indic_def = f'self.myindicator{i+1}= {self.p.indicators[i].with_prefix}('
                for par in self.p.indicators[i].params_in:
                    indic_def += f"{par[0]}={par[1]},"
                indic_def = indic_def[:-1] + ")"
                exec(indic_def)
        if self.p.signals != None:
            self.signal_buy = self.p.signals['buy']
            self.signal_sell = self.p.signals['sell'] 

    def next(self):
        if self.order:
            return
        if hasattr(self, 'cth_start') and ((self.data.datetime.time() < self.cth_start) or (self.data.datetime.time() > self.cth_end)):
            return            
        if not self.position:
            if eval(self.signal_buy):
                # Place a buy trade
                self.log('Buy Create, %.2f' % self.data.close[0])
                size = 0.01
                self.buy_bracket(size=size, limitprice=self.data.close[0]*(1+self.p.take_profit), stopprice=self.data.close[0]-self.p.stop_loss/size)                
        else:
            if eval(self.signal_sell):
                # Place a sell trade
                self.log('Sell Create, %.2f' % self.data.close[0])
                self.sell_bracket(size=0.01, limitprice=self.data.close[0]*(1+self.p.take_profit), stopprice=self.data.close[0]-self.p.stop_loss/size)                  

    # outputting information
    def log(self, txt):
        dt=self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
        self.logger.info('%s, %s\n' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy(): #and order.exectype not in [bt.Order.Stop, bt.Order.Limit]:
                self.log("Executed BUY (Price: %.2f, Value: %.2f, Commission %.2f)" %
                (order.executed.price, order.executed.value, order.executed.comm))
                self.bar_executed = len(self)
            else:# order.issell(): #and order.exectype not in [bt.Order.Stop, bt.Order.Limit]:
                self.log("Executed SELL (Price: %.2f, Value: %.2f, Commission %.2f)" %
                (order.executed.price, order.executed.value, order.executed.comm))
                self.bar_executed = len(self)              
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order was canceled/margin/rejected")
        self.order = None

### Strategy Parser ###
class StrategyParser:
    def __init__(self, strat_str=None):
        self.original_text = strat_str
        self.strategy_class_name = self.GetStrategyName()
        self.replace_imports() 
        self.addlogger()        
        return 

    def GetStrategyName(self, name=None):
        debutind = self.original_text.find("class ")
        name_lastind = self.original_text.find("(bt.Strategy)")
        self.parsed_text = self.original_text[debutind:]
        detected_name = self.original_text[debutind+len("class "):name_lastind]
        if name:
            self.parsed_text = "class " + name + self.parsed_text[name_lastind-debutind:]    
        return detected_name
    
    def replace_imports(self):
        imports_end = self.original_text.find("class ")
        imports = self.original_text[:imports_end].splitlines()
        btlabel = ""
        liblabels = dict()
        for line in imports:
            line = line.replace("backtrader.", "bt.")
            words = line.split(" ")
            if line.find("import backtrader as ") != -1:
                btlabel = words[-1] + "."
            elif "RandomForest" in line and "sklearn.ensemble" not in line:
                self.parsed_text = self.parsed_text.replace("RandomForest", "mlindicators.RandomForestPredictor()#")
            elif words[0] == "from":
                impfunc = line.replace(f"from {words[1]} import ", "")
                impfunc = impfunc.split(",")
                for fun in impfunc:
                    fun = fun.strip() 
                    liblabels[fun] = words[1]+"."+fun
        if btlabel != "":
            self.parsed_text = self.parsed_text.replace(btlabel, "bt.")
        for key in liblabels.keys():
            self.parsed_text = self.parsed_text.replace(key, liblabels[key])     
        return
    
    def addlogger(self): 
        loginit = "\n    logger = logging.getLogger(__name__)\n    handler = logging.FileHandler('strat.log')\n    logger.addHandler(handler)\n\n"
        init_start = self.parsed_text.find("    def __init__(")
        self.parsed_text = self.parsed_text[:init_start]+loginit+self.parsed_text[init_start:]
        print(self.parsed_text) 

        init_start = self.parsed_text.find("__init__(")        
        init_start2 = self.parsed_text[init_start:].find(":")
        logstart = "\n        self.logger.info('Start:\\n')\n"
        #restrict_hours = "        if self.p.cth_start != None:\n"
        #restrict_hours += "            self.cth_start = datetime.strptime(self.p.cth_start, '%H:%M').time()\n"
        #restrict_hours += "            self.cth_end = datetime.strptime(self.p.cth_end, '%H:%M').time()\n"
        newstr = self.parsed_text[:init_start2+init_start+1]+logstart+self.parsed_text[init_start2+init_start+1:]
        self.parsed_text = newstr

        logfunc = "\n\n    def log(self, txt):\n        dt=self.datas[0].datetime.date(0)\n        print('%s, %s' % (dt.isoformat(), txt))\n        self.logger.info('%s, %s\\n' % (dt.isoformat(), txt))\n\n"
        self.parsed_text += logfunc

        notifytradefunc = "    def notify_order(self, order):\n        if order.status == order.Completed:\n"
        notifytradefunc += '            if order.isbuy():\n                self.log("Executed BUY (Price: %.2f, Value: %.2f, Commission %.2f)" %\n'
        notifytradefunc += '                (order.executed.price, order.executed.value, order.executed.comm))\n'
        notifytradefunc += '            else:\n'
        notifytradefunc += '                self.log("Executed SELL (Price: %.2f, Value: %.2f, Commission %.2f)" %\n'
        notifytradefunc += '                (order.executed.price, order.executed.value, order.executed.comm))\n'
        notifytradefunc += '        elif order.status in [order.Canceled, order.Margin, order.Rejected]:\n'
        notifytradefunc += '            self.log("Order was canceled/margin/rejected")\n'
        notifytradefunc += '        self.order = None\n\n' 
        self.parsed_text += notifytradefunc
        print(self.parsed_text)      
        return