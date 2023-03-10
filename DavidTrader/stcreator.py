#import numpy as np
from flask import request, render_template, flash, redirect, url_for, send_file, Blueprint, current_app
#from werkzeug.utils import secure_filename
#from importlib.resources import files as irfiles
import backtrader as bt
import yfinance as yf
import matplotlib.pyplot as plt
#import pandas as pd
#import numpy as np
import re
#from trading_ig import IGService
#from trading_ig.config import config
#from datetime import datetime, timezone, timedelta
#from sklearn.ensemble import RandomForestRegressor
from . import customindicators
from . import mlindicators
from . import customstrategies
from .fetchdata import YF_INTERVALS, YF_MAX_PERIODS, YF_PERIODS, days
#import customindicators
#import mlindicators
#import customstrategies
#import time
import sklearn
import os
import ta
import inspect
from DavidTrader import cache
import logging
# configure the logger
logging.basicConfig(level=logging.INFO)
try:
    import talib
except:
    print("TA-Lib not found")


'''
filefolder='/var/www/html/airafiles'
UPLOAD_FOLDER = os.path.join(filefolder, 'original')
DOWNLOAD_FOLDER = os.path.join(filefolder, 'results')
if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.isdir(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

DATAPATH = irfiles('aira')
MODELS_PATH = DATAPATH.joinpath('aimodels')
PATHYES = MODELS_PATH.joinpath('modelyes')
PATHNO = MODELS_PATH.joinpath('modelno') 
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
'''

bp = Blueprint('stcreator', __name__)

#global compdict 
compdict= {"gt": ">", "ge": ">=", "eq": "==", "lt": "<", "le": "<="}

class indicator_info():

    prefix_list = ('bt.indicators', 'customindicators', 'mlindicators')

    def __init__(self, name):
        self.indicator = name
        self.prefix = self.get_prefix()
        self.with_prefix = self.prefix+self.indicator
        self.read_parameters()
        return

    def get_prefix(self):
        prefix = "data."
        for pref in self.prefix_list:
            if hasattr(eval(pref), self.indicator):
                prefix = pref+"."
                break
        return prefix
    
    def read_parameters(self):
        self.flag_refine=False
        self.params_out = None
        self.params_in = None
        if self.prefix[:-1] in self.prefix_list:
            ind = eval(self.with_prefix)
            outp = ind.lines.getlinealiases()
            if len(outp) > 1:
                self.flag_refine = True
                self.params_out = outp
            paramin = list(ind.params._gettuple())
            params_in = []
            for par in paramin:
                if isinstance(par[1], (int, float)):
                    params_in.append(par)
            if len(params_in) > 0: 
                self.params_in = tuple(params_in)
        #print(self.params_out)
        #print(f"Refine: {self.flag_refine}")
        return    

    def __getstate__(self):
        indict = {'indicator': self.indicator}
        indict['prefix'] = self.prefix
        indict['with_prefix'] = self.with_prefix
        indict['params_in'] = self.params_in
        indict['params_out'] = self.params_out
        indict['flag_refine'] = self.flag_refine
        return indict

    def __setstate__(self, state):
        self.indicator = state['indicator']
        self.prefix = state['prefix']
        self.with_prefix = state['with_prefix']
        self.params_in = state['params_in']
        self.params_out = state['params_out']
        self.flag_refine = state['flag_refine']
        return

def validate_condition(cond):
    spstr = re.split('[<|>|=]=?', cond)
    return len(spstr) == 2

def indicators_list():
    indlist = [ind for ind in dir(bt.indicators) if inspect.isclass(eval('bt.indicators.'+ind)) and issubclass(eval('bt.indicators.'+ind), bt.Indicator)]
    #indlist = [ind for ind in dir(bt.indicators) if inspect.isclass(ind) and (isinstance(ind, bt.Indicator) or issubclass(ind, bt.Indicator))]
    for cind in dir(customindicators):
        if inspect.isclass(eval('customindicators.'+cind)) and issubclass(eval('customindicators.'+cind), bt.Indicator):
            indlist.append(cind)
            #print(cind)
    for mlind in dir(mlindicators):
        if inspect.isclass(eval('mlindicators.'+mlind)) and issubclass(eval('mlindicators.'+mlind), bt.Indicator):    
            indlist.append(mlind)
            #print(mlind)
    indlist.append('open')
    indlist.append('close')
    indlist.append('high')
    indlist.append('low')
    indlist.append('volume')
    indlist = sorted(indlist, key=str.casefold)
    return indlist

def strategy_list():
    stratlist = [strat for strat in dir(customstrategies) if inspect.isclass(eval('customstrategies.'+strat)) and issubclass(eval('customstrategies.'+strat), bt.Strategy) and strat != "CustomStrategyFromHelper"]
    stratlist = sorted(stratlist, key=str.casefold)
    return stratlist

@bp.route('/', methods=('GET','POST'))
def index():   
    if request.method == 'POST':
        if request.form['raw_strategy'] != "":
            newstrategy = customstrategies.StrategyParser(strat_str=request.form['raw_strategy'])
            strategy = {'name': newstrategy.strategy_class_name, 'def': newstrategy.parsed_text}         
            cache.set('strategy', strategy)
            print(f"strategy: {strategy['name']}")
            return redirect(url_for('stcreator.backtest_parameters'))
        elif request.form['strategy'] and request.form['strategy'] != "":
            strategy = {'name': request.form['strategy']}         
            cache.set('strategy', strategy)
            print(f"strategy: {strategy['name']}")
            return redirect(url_for('stcreator.backtest_parameters'))
        else:
            flash('Error: unknown strategy') 
    return render_template('index.html', strategy_ls = strategy_list())

@bp.route('/openlong', methods=('GET','POST'))
def open_long():
    strategy = {'name': 'CustomStrategyFromHelper', 'params': None, 'signals': None}
    cache.set('strategy', strategy)
    print(f"strategy: {strategy['name']}")
    #with current_app.app_context():
    #    cache = current_app.cache #extensions['cache']
    #    print(f"cache type: {type(cache)}")
    conditions_open_long = cache.get('conditions_open_long')
    #print(f"conditions_open_long: {conditions_open_long}")
    if not conditions_open_long:
        conditions_open_long = ""
    ind1 = None
    ind2 = None
    indlocals = []
    indicators_ls = indicators_list()
    if request.method == 'POST' and "add-button" not in request.form.keys():
        #print(request.form.keys())
        ncond = int(request.form['n_conditions']) 
        #print(ncond)
        #print(request.form.keys())
        for i in range(ncond):
            ind1 = indicator_info(request.form['indicator1_'+str(i+1)])
            print(ind1)
            cond = ind1.with_prefix
            if ind1.prefix != 'data.':
                indlocals.append(ind1)
            comp = compdict[request.form['comparator_'+str(i+1)]]
            cond+=comp
            if request.form['indicator2_'+str(i+1)] != "":
                ind2 = indicator_info(request.form['indicator2_'+str(i+1)])
                cond+= ind2.with_prefix
                if ind2.prefix != 'data.':
                    indlocals.append(ind2)                    
            if request.form['offset_'+str(i+1)] != "0" or request.form['offset_'+str(i+1)] != "":
                cond+=request.form['offset_'+str(i+1)]
            flash(cond)
            if validate_condition(cond):
                if i > 0:
                    conditions_open_long += " "+request.form['andor'+str(i)]+" "
                conditions_open_long+=cond
            else:
                flash("Error: wrong condition")
        print(conditions_open_long)
        cache.set('conditions_open_long', conditions_open_long)
    #print(indicators_ls)
    if len(indlocals) > 0:
        #print(len(indlocals))
        #print(indlocals[0].params_in)
        #print()
        cache.set('indics', indlocals)
        #cache.set('indicators', indlocals)
        return redirect(url_for('stcreator.refine', currentstage='open_long', nextstage='open_short')) #render_template("refine.html", openclose = "open", longshort = "long", ind1=ind1, ind2=ind2, nextstage = "stcreator.open_short")
    else: 
        return render_template("stratbase.html", indicators_ls = indicators_ls, openclose = "open", longshort = "long")

@bp.route('/openshort', methods=('GET','POST'))
def open_short():
    conditions_open_short = cache.get('conditions_open_short')
    #print(f"conditions_open_short: {conditions_open_short}")
    if not conditions_open_short:
        conditions_open_short = ""
    ind1 = None
    ind2 = None
    indlocals = []
    indicators_ls = indicators_list()
    if request.method == 'POST' and "add-button" not in request.form.keys():
        #print(request.form.keys())
        ncond = int(request.form['n_conditions']) 
        #print(ncond)
        #print(request.form.keys())
        for i in range(ncond):
            ind1 = indicator_info(request.form['indicator1_'+str(i+1)])
            print(ind1)
            cond = ind1.with_prefix
            if ind1.prefix != 'data.':
                indlocals.append(ind1)
            comp = compdict[request.form['comparator_'+str(i+1)]]
            cond+=comp
            if request.form['indicator2_'+str(i+1)] != "":
                ind2 = indicator_info(request.form['indicator2_'+str(i+1)])
                cond+= ind2.with_prefix
                if ind2.prefix != 'data.':
                    indlocals.append(ind2)                    
            if request.form['offset_'+str(i+1)] != "0" or request.form['offset_'+str(i+1)] != "":
                cond+=request.form['offset_'+str(i+1)]
            flash(cond)
            if validate_condition(cond):
                if i > 0:
                    conditions_open_short += " "+request.form['andor'+str(i)]+" "
                conditions_open_short+=cond
            else:
                flash("Error: wrong condition")
        print(conditions_open_short)
        cache.set('conditions_open_short', conditions_open_short)
    #print(indicators_ls)
    if len(indlocals) > 0:
        print(len(indlocals))
        print(indlocals[0].params_in)
        #print()
        cache.set('indics', indlocals)
        return redirect(url_for('stcreator.refine', currentstage='open_short', nextstage='close')) #render_template("refine.html", openclose = "open", longshort = "long", ind1=ind1, ind2=ind2, nextstage = "stcreator.open_short")
    else: 
        return render_template("stratbase.html", indicators_ls = indicators_ls, openclose = "open", longshort = "short")

@bp.route('/close', methods=('GET','POST'))
def close():
    strategy = cache.get('strategy') 
    if request.method == 'POST':
        strategy['params'] = {'stop_loss': request.form["stop_loss"], 'take_profit': request.form["take_profit"]}
        cache.set('strategy', strategy)
        print(f"strategy: {strategy['name']}")
        print(f"strategy params: {strategy['params']['stop_loss']}, {strategy['params']['take_profit']}")
        return redirect(url_for('stcreator.backtest_parameters'))
    return render_template("close.html", openclose = "close", longshort = "long/short")

@bp.route('/closelong', methods=('GET','POST'))
def close_long():
    #global conditions_close_long
    return render_template("stratbase.html", indicators_ls = indicators_list())

@bp.route('/closeshort', methods=('GET','POST'))
def close_short():
    #global conditions_close_short
    return render_template("stratbase.html", indicators_ls = indicators_list())

@bp.route('/refine', methods=('GET', 'POST'))
def refine():
    indicators = cache.get('indicators')
    if indicators:
        indcount = len(indicators)
    else:
        indcount = 0
    current = request.args.get('currentstage')
    conds = cache.get('conditions_'+current)
    indics = cache.get('indics')
    #print(f"Number of indicators to refine: {len(indics)}")
    nextstage = request.args.get('nextstage')
    if request.method == 'POST':
        for ind in indics:
            print(ind.indicator)
            parins = list(ind.params_in)
            for i in range(len(ind.params_in)):
                parins[i] = list(parins[i])
                parins[i][1] = request.form[ind.indicator+'.'+parins[i][0]]
                parins[i] = tuple(parins[i])
            ind.params_in = tuple(parins)
            icond = conds.find(ind.with_prefix)
            newname = 'self.myindicator'+str(indcount+1)
            indcount+=1
            if ind.flag_refine:
                newname+="."+request.form[ind.indicator+"_out"]
            newname += "[0]"
            conds = conds[:icond]+newname+conds[icond+len(ind.with_prefix):]
            indicators.append(ind)    
        cache.set('conditions_'+current, conds)
        cache.set('indicators', indicators)
        return redirect(url_for('stcreator.'+nextstage))
    return render_template('refine.html', indics = indics)

@bp.route('/backtestparams', methods=('GET', 'POST'))
def backtest_parameters():
    strategy = cache.get("strategy")
    print(f"strategy: {strategy['name']}")
    indicators = cache.get("indicators")
    signals = {"buy": cache.get("conditions_open_long"), "sell": cache.get("conditions_open_short")} 
    #if params in 
    if request.method == 'POST' and "timeframe" in request.form.keys():
        timeframe = request.form['timeframe']
        backtestperiod = request.form['period']
        if 'params' not in strategy.keys():
            strategy["params"] = dict()        
        if request.form["restrict_hours"] == "yes":
            strategy['params']['cth_start'] = request.form['cth_start']
            strategy['params']['cth_end'] = request.form['cth_end']
        else:
            strategy['params']['cth_start'] = None
            strategy['params']['cth_end'] = None
        initial_capital = request.form["init_cash"]
        #comission
        #size?
        cache.set("strategy", strategy)
        if days(backtestperiod) <= YF_MAX_PERIODS[timeframe]:
            cerebro = bt.Cerebro(runonce=True)  # This creates the cerebro instance
            if strategy['name'] in strategy_list():
                strat = eval("customstrategies."+strategy["name"])
                cerebro.addstrategy(strat, cth_start=strategy['params']['cth_start'], cth_end=strategy['params']['cth_end'])
            elif strategy['name'] == "CustomStrategyFromHelper":
                strat = customstrategies.CustomStrategyFromHelper
                cerebro.addstrategy(strat, cth_start=strategy['params']['cth_start'], cth_end=strategy['params']['cth_end'], stop_loss=strategy['params']["stop_loss"], take_profit=strategy['params']["take_profit"], indicators=indicators, signals=signals)
            else: #Pasted strategy
                exec(strategy['def'])
                strat = eval(strategy["name"])
                cerebro.addstrategy(strat) #, cth_start=strategy['params']['cth_start'], cth_end=strategy['params']['cth_end'])
            cerebro.broker.setcash(float(initial_capital))
            cerebro.broker.setcommission(commission=0.02)
            data = bt.feeds.PandasData(dataname=yf.download('BTC-USD', interval=timeframe, period=backtestperiod))
            cerebro.adddata(data) # data should be fetched separately
            initcash = cerebro.broker.getvalue()
            flash('<START> Brokerage account: $%.2f' % cerebro.broker.getvalue())
            btrun = cerebro.run()
            with open(btrun[0].logger.handlers[0].baseFilename) as f:
                logs = f.read()
                starti = logs[::-1].find(":tratS")
                print(f"start: {starti}")
                logs = logs[-starti:].splitlines()
                for line in logs:
                    flash(line)
                #f.close()
            #os.remove(btrun[0].logger.handlers[0].baseFilename)
            flash('<FINISH> Brokerage account: $%.2f' % cerebro.broker.getvalue())
            balance = cerebro.broker.getvalue() - initcash
            flash('<FINISH> Balance: $%.2f' % balance)
            #btfig = cerebro.plot(iplot=False, style='candlestick', loc="grey", grid=False, returnfig=True)
            btfig = cerebro.plot(iplot=True, style='candlestick', loc="grey", grid=False, returnfig=True)
            btfig = btfig[0]
            if isinstance(btfig,list):
                btfig = btfig[0]
            btfig.savefig("btplot.png")
            #cerebro.plot(iplot=False, style='candlestick',loc='grey', grid=False)
            return render_template("results.html", strategy_name = strategy["name"], timeframe = timeframe, period = backtestperiod, image_path = "../btplot.png")
        else:
            flash('Error: incompatible timeframe and backtest period.')
    return render_template("backtest.html", YF_INTERVALS=YF_INTERVALS, YF_PERIODS=YF_PERIODS)


#if __name__ == '__main__':
#    app.run(debug=True)