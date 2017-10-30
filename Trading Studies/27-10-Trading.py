#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 18:26:49 2017

@author: ale

#########################################

# FOR TOMORROW'S TRADING SESSION
"""
import pandas as pd
import Indicators
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.finance as fnc

fName = '/home/ale/Documenti/Trading Studies/Data/FIB_Data_New.xlsx'
data = pd.read_excel(fName, Sheetname = '1M')
#%%

df = pd.DataFrame(data['Close'])

#Put Indicators
Ind = Indicators.Indicator(df['Close'])

df['Trend_Strength'] = Ind.Trend_Strength(50)
df['RSI'] = Ind.RSI(20)
df['RSI_MA2'] = df['RSI'].rolling(10).mean()
df['RSI_MA1'] = df['RSI'].rolling(5).mean()
df['EMA-10'] = Ind.EMA(10)
df['EMA-20'] = Ind.EMA(20)
df['MACD'] = Ind.MACD_Delta(50, 20, 10)
df['MACD_MA2'] = df['MACD'].rolling(10).mean()
df['MACD_MA1'] = df['MACD'].rolling(5).mean()

#%%

start = 6500
stop = 6700
#Visualize
plt.figure()

closes = data['Close'].values[start:stop]
opens = data['Open'].values[start:stop]
highs = data['High'].values[start:stop]
lows = data['Low'].values[start:stop]

ax = plt.subplot(311)

plt.grid(True)
fnc.candlestick2_ochl(ax, opens, closes, highs, lows, width=1, colorup='g', colordown='r', alpha=0.75)


plt.subplot(312)
plt.plot(df['RSI'].values[start:stop])
plt.plot(30*np.ones(stop-start), 'r--')
plt.plot(70*np.ones(stop-start), 'r--')
plt.plot(df['RSI_MA1'] .values[start:stop])
plt.plot(df['RSI_MA2'] .values[start:stop])
plt.grid(True)

plt.subplot(313)
plt.plot(df['MACD'].values[start:stop])
plt.plot(np.zeros(stop-start), 'r--')
plt.plot(df['MACD_MA1'] .values[start:stop])
plt.grid(True)

#%%

# VOLUME IMPACT

start = 5675
stop = 5800

#Visualize for volume analysis

plt.figure()

closes = data['Close'].values[start:stop]
opens = data['Open'].values[start:stop]
highs = data['High'].values[start:stop]
lows = data['Low'].values[start:stop]

ax = plt.subplot(211)

plt.grid(True)
fnc.candlestick2_ochl(ax, opens, closes, highs, lows, width=1, colorup='g', colordown='r', alpha=0.75)

plt.subplot(212)
plt.plot(data['Vol'].values[start:stop])
plt.grid(True)