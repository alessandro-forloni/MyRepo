# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 18:52:13 2017

@author: Alessandro

Support module for Neural Indicator trader

"""
import pandas as pd
import numpy as np

class Indicator():
    
    def __init__(self,df):
        
        self.df = df
        
        
    def prova(self):
        
        print("hello")
        
        
        
    def EMA(self,p):
        
        k = 2/(1+p)
        ema = np.zeros(len(self.df))
        ema[0] = self.df[0]
        
        for i in range(1,len(ema)):
            
            ema[i] = self.df[i]*k+ema[i-1]*(1-k)
        
        return ema
    
    
        

    def Bollinger(self,p,d):
        
        mid = self.df.rolling(p).mean()
        
        sd =  self.df.rolling(p).std()
        
        temp = pd.DataFrame()
        temp['Boll_Down'] = mid-d*sd - self.df
        temp['Boll_Up'] = mid+d*sd - self.df
            
        return temp
    
    
    def VWAP(self,vol,p):
        
        
        cumTPVol = (self.df*vol).rolling(p).sum() 
        
        return cumTPVol/(vol.rolling(p).sum())
    
    def Parabolic_SAR():
        
        return 0
    
    def RSI(self,p):
        #VERY VERY SIMILAR, BUT IS NOT THE SAME!!!!
        
        delta = self.df-self.df.shift(1)
        
        #Get only positive gains
        delta_plus = (delta*(delta > 0)).rolling(p).sum()
        #Count how many in moving window are positive
        #delta_plus_count = (delta > 0).rolling(p).sum()
        
        delta_minus = -(delta*(delta < 0)).rolling(p).sum()
        #delta_minus_count = (delta < 0).rolling(p).sum()
        
        average_gain = delta_plus/p#delta_plus_count
        average_loss = delta_minus/p#delta_minus_count
       
        RS = average_gain/average_loss
        
        return 100-100/(1+RS)
    
    def MACD_Delta(self, long, short, signal):
        
        line = self.EMA(short) - self.EMA(long)
        
        k = 2/(1+signal)
        sig = np.zeros(len(self.df))
        sig[0] = line[0]
        
        for i in range(1,len(sig)):
            
            sig[i] = line[i]*k+sig[i-1]*(1-k)
        
        return line-sig
    
    def Heikin_Ashi_proxy(self,H,L,O):
        #Returns array of 0 and 1 for down or up Heikin-Ashi candle
        
       
        opens = np.zeros(len(self.df))
        
        closes = (self.df + H + L + O)/4
        
        opens[0] = O[0]
                
        
        for i in range(1,len(opens)):
            
            opens[i] = (opens[i-1]+closes[i-1])/2
                 
        return (closes > opens)*1
    
    
    def Trend_Strength(self,p):
        #Sums returns to see where is the trend going
        # Basically is an easy alternative to SAR & ADX
        
        deltas = self.df - self.df.shift(1)
        
        return deltas.rolling(p).sum()/p
        
        
        
        
        