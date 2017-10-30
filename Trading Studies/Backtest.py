#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 23:05:28 2017

@author: ale

Backtesting engine
"""
import matplotlib.pyplot as plt
import pandas as pd

class Backtester():
    
    def pnl_performance(y_cap, returns):
        
        N = len(y_cap)
        
        if(N != len(returns)):
            
            print('Houston we have a problem')
            return 0
        
        return sum(y_cap*returns)*5
    
    
    def sharpe_performance(y_cap, returns):
        
        N = len(y_cap)
        
        if(N != len(returns)):
            
            print('Houston we have a problem')
            return 0
        
        if(sum(y_cap) <= 2):
            
            return 0
        
        
        g = (y_cap*returns*5).cumsum()
        
        #g = pnl[pnl != 0]
        
        if(g.std() == 0):
            return 0
        
        return(g.mean()/g.std())
    
    
    def modified_sharpe_performance(y_cap, returns):
        #Takes into account number of trades
        
        N = len(y_cap)
        
        if(N != len(returns)):
            
            print('Houston we have a problem')
            return 0
        
        if(sum(y_cap) <= 2):
            
            return 0
        
        
        pnl = y_cap*returns*5
        
        g = pnl[pnl != 0]
        
        if(g.std() == 0):
            return 0
        
        return g.mean()/g.std()*sum(y_cap)*(len(y_cap)-sum(y_cap))
    
#    def equity_line(y_cap, returns):
#        
#        N = len(y_cap)
#        
#        if(N != len(returns)):
#            
#            print('Houston we have a problem')
#            return 0
#        
#        line = cumsum(y_cap*returns*5)
#        
#        plt.figure()
#        plt.plot(line)

    def show_signals(self, close, signals):
        #Input is vector of closing prices and 
        # Vector of 0,1,-1 indicating signals
        
        #PASS VALUES/ARRAYS, NOT DFs
        
        temp = pd.DataFrame(close, columns = ['close'])
        temp['signal'] = signals

        plt.figure()
        plt.plot(temp['close'])
        
        long_index = temp['signal'][temp['signal'] == 1].index.values
        short_index = temp['signal'][temp['signal'] == -1].index.values

        plt.plot(long_index, temp['close'][long_index], 'g^')
        plt.plot(short_index, temp['close'][short_index], 'rv')

        plt.grid(True)
        
        plt.title('Strategy Signals')