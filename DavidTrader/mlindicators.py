from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import backtrader as bt
import numpy as np

class RandomForestPredictor(bt.Indicator):
    '''
    Author: Omar Galarraga 
    '''
    plotinfo = dict(subplot=False)

    params = (('n_estimators', 50), ('min_samples_split', 15), ('min_samples_leaf', 30),
              ('max_depth', 5), ('max_leaf_nodes', 2), ('max_features', 15), 
              ('period', 15), ('training_period', 500))

    alias = ('RFPP', 'RandomForestPricePredictor',)
    lines = ('rfpp',)
    plotlines = dict(RFPP=dict(alpha=0.50, linestyle='-.', linewidth=2.0))

    _sklparams = dict(params)
    del _sklparams['period'], _sklparams['training_period']

    def __init__(self):
        self.addminperiod = self.p.training_period + self.p.period
        self._trainData = np.empty((self.p.training_period, self.p.period))
        self._targetData = np.empty((self.p.training_period,))
        self._testData = np.empty((1,self.p.period)) 
        self._rfmodel = RandomForestRegressor(n_jobs=2).set_params(**self._sklparams)
        super(RandomForestPredictor, self).__init__()

    def nextstart(self):       
        for i in range(self.p.training_period):
            #self._targetData.append(self.data.get(ago=i,size=1))
            #self._trainData.append(list(self.data.get(ago=i+1,size=self.p.period)))
            self._targetData[i] = self.data[-i]
            for j in range(self.p.period):
                self._trainData[i,j] = self.data[-i-j-1]                  

    def next(self):
        npoints = self._targetData.shape[0]
        np.append(self._targetData, self.data[0])
        self._testData[0,0] = self.data[0]
        np.append(self._trainData, np.empty((1, self.p.period)))
        for j in range(1,self.p.period):
            self._trainData[npoints-1,j-1] = self.data[-j]
            self._testData[0,j] = self.data[-j]     
        self._rfmodel.fit(self._trainData, self._targetData)
        #self.lines.rfpp[0] = bt.indicators.ApplyN(self.data, func=self._rfmodel.predict, period=self.p.period)
        self.lines.rfpp[0] = self._rfmodel.predict(self._testData)[0]