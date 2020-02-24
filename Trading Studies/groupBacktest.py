# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 22:19:38 2020

@author: alex_
"""

import pandas as pd
import numpy as np

#matrix = np.random.randn(200,5)/100 + 5
#col_names = ['a','b','c','d','e']
#fake_index = pd.DatetimeIndex(start = '01/01/2020', periods = 200, freq = 'D')
#windowBackPeriod = 20
#holdingPeriod = 10
#
#df = pd.DataFrame(matrix, 
#                      columns = col_names, 
#                               index = fake_index
#                               )



class groupBacktest():
    
    def __init__(self, period=20, holdingPeriod = 10):
         
        self.windowBackPeriod = period
        self.holdingPeriod = holdingPeriod
        
        self.df = pd.DataFrame(matrix, 
                               columns = col_names, 
                               index = fake_index
                               )
        self.n_components = self.df.shape[1]
        
        # compute returns
        self.dfReturns = self.df/self.df.shift(1) - 1
        
        # rolling returns and rolling vola
        self.dfRollingReturns = self.dfReturns.rolling(self.windowBackPeriod).sum()
        #self.dfRollingVolas = dfReturns.rolling(windowBackPeriod*2).std()
        
        self.dfRanks = self.rankStockReturns()
        self.dfSelect = self.selectStocks()
        
        self.dfPosition = self.getStrategyPosition()
        self.dfStrategyReturns = self.getStrategyReturns()
        
    def rankStockReturns(self):
        
        # each day rank Returns
        dfRanks = self.dfRollingReturns.rank(axis=1)
        return dfRanks.replace(np.nan, 0)

    def selectStocks(self):
        
        
        
        fridayIndicator = self.lookForFridays()
        selection = self.dfRanks.multiply(fridayIndicator, 
                                          axis = "index"
                                          )
        selection.replace(0, np.nan, inplace=True)
        selection.replace(self.n_components, -1, inplace=True)
        
        # rimpiazza tutto ciò che non è 1 o 5
        for x in range(2,self.n_components):
            selection.replace(x, 0, inplace=True)
        return selection
        
    def getStrategyPosition(self):
        
        positionTemp = self.dfSelect.fillna(method = 'ffill')
        positionTemp.replace(np.nan, 0, inplace=True)
        return positionTemp
        
    def lookForFridays(self):
        # get where date is friday
        day_of_week = [x.weekday() for x in pd.to_datetime(self.df.index)]
        isFriday = pd.Series(np.array(day_of_week) == 4, index=self.dfRanks.index)
        
        return isFriday
    
    def getStrategyReturns(self):
        
        tempStratReturns = self.dfPosition.shift(1)*self.dfReturns
        tempStratReturns.replace(np.nan, 0, inplace=True)
        return tempStratReturns
        
        
testClass = groupBacktest()

