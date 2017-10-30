"""
Created on Mon Oct 23 20:38:08 2017

@author: ale

Try some Automated trading based on technical analysis

Mainly oscillators:
    
    - Will move then to neural application of this
    - RSI
    - MACD
    - EMAs
    - Trend recognition
      
"""
import pandas as pd
import Indicators
import matplotlib.pyplot as plt
import numpy as np

max_lag = 5
N_out = 5     #N_out strictly smaller than max_lag


#For calc purposes
max_lag = N_out
'''
===========================================================





===========================================================
'''
fName = '/home/ale/Documenti/Trading Studies/Data/FIB_Data_New.xlsx'
data = pd.read_excel(fName, Sheetname = '1M')

#Get Deltas
data['change'] = (data['Close']-data['Open'])
#data['change'] = data['Close']/data['Close'].shift(1)-1
#data['range'] = data['High']-data['Open']



df_temp = pd.DataFrame(data['Date'])
df_temp['time'] = data['Time']
df_temp['change'] = data['change']
df_temp['volume'] = data['Vol']
df_temp['close'] = data['Close']
df_temp['open'] = data['Open']

#Create Lags onwards and backwards
for i in range(1,max_lag+1):
    
    #Onward lags for output
    df_temp['change-'+str(i)+'-out'] = df_temp['change'].shift(-i)
    
#Put Indicators
Ind = Indicators.Indicator(df_temp['close'])

df_temp['Trend_Strength'] = Ind.Trend_Strength(50)
df_temp['RSI'] = Ind.RSI(20)
df_temp['RSI_MA2'] = df_temp['RSI'].rolling(10).mean()
df_temp['RSI_MA1'] = df_temp['RSI'].rolling(5).mean()
df_temp['EMA-10'] = Ind.EMA(10)
df_temp['EMA-20'] = Ind.EMA(20)
df_temp['MACD'] = Ind.MACD_Delta(26, 12, 9)
df_temp['MACD_MA2'] = df_temp['MACD'].rolling(10).mean()
df_temp['MACD_MA1'] = df_temp['MACD'].rolling(5).mean()

#Eliminate first max_lag elements of the day    
i = 1

while i < df_temp.shape[0]:
    
    if((df_temp['Date'][i]-df_temp['Date'][i-1]).total_seconds() > 0):
        
        #Remove previous and following max_lag observations
        for j in range(0,max_lag*2):
            df_temp = df_temp.drop(i-max_lag)
            i = i + 1
           
    i = i + 1
    
df_temp = df_temp.dropna(how = 'any')

#Create new index
dates = [str(x)[:10].replace('-','') for x in df_temp['Date']]
times = [str(x)[:5].replace(':','') for x in df_temp['time']]
new_index = [x+'-'+y for x,y in zip(dates,times)]

#Create and fill new dataframe
df = pd.DataFrame(index = new_index)

for x in df_temp.columns[6+N_out:]:
    
    df[x] = df_temp[x].values

##Create output21
out = df_temp['change']

for i in range(1,N_out+1):
        
    out = out + df_temp['change-'+str(i)+'-out']

    
y = (out >= 0)*1

#For charting purposes
close = df_temp['close']


#Clear Memory
#del df_temp
del data
del new_index
del times
del dates
###X_train, X_test, y_train, y_test = train_test_split(df, y, 
##                           test_size=0.2, random_state=42)
#
sep = int(0.8*df.shape[0])

X_train = df.iloc[:sep,:]
X_test = df.iloc[sep:,:]
y_train = y.iloc[:sep]
y_test = y.iloc[sep:]

#For backtesting
out_train = out.iloc[:sep]
out_test = out.iloc[sep:]

print('Finished pre-processing, now playing....')

#%%

start = 10400
stop = 10700
#Visualize
plt.figure()

plt.subplot(311)
plt.plot(close.values[start:stop])
#plt.plot(df['EMA-10'].values[start:stop])
#plt.plot(df['EMA-20'].values[start:stop])
plt.grid(True)

plt.subplot(312)
plt.plot(df['RSI'].values[start:stop])
plt.plot(30*np.ones(stop-start), 'r--')
plt.plot(70*np.ones(stop-start), 'r--')
plt.plot(df['RSI_MA1'] .values[start:stop])
#plt.plot(df['RSI_MA2'] .values[start:stop])
plt.grid(True)

plt.subplot(313)
plt.plot(df['Trend_Strength'].values[start:stop])
plt.plot(np.zeros(stop-start), 'r--')
plt.grid(True)
#%%

#Backtest strategy 1

#########################################

# Use RSI MAs as signal and exit triggers

# Filter with trend strength

#########################################
import Backtest

commission = 9

df_trade = pd.DataFrame()

df_trade['RSI_MA2_Diff'] = (df['RSI_MA1'] > df['RSI_MA2'])*1 - (df['RSI_MA1'] < df['RSI_MA2'])*1
df_trade['MACD_MA2_Diff'] = (df['MACD_MA1'] > df['MACD_MA2'])*1 - (df['MACD_MA1'] < df['MACD_MA2'])*1

#Filter with Trend Strength
df_trade['Filter'] = (df['Trend_Strength'] >= 0)*1 - (df['Trend_Strength'] < 0)*1

df_trade['Sum'] = (df_trade.sum(axis=1) == 3)*1

df_trade['Signal'] = (df_trade['Sum'] - df_trade['Sum'].shift(1)).shift(1)
df_trade['Signal'] = df_trade['Signal'].replace(np.nan, 0)


trades = (df_trade['Sum'].shift(1).values*df_temp['change'].values)[1:]

n_trades = round(sum(abs(df_trade['Signal']))/2)

line = trades.cumsum()*5

PnL = sum(trades)*5
sharpe = round(line.mean()/line.std(),4)

print('\nPnL:', PnL)
print('Sharpe Ratio:', sharpe)
print('Number of Trades:', n_trades)

plt.figure()
plt.plot(line)
plt.title('Equity Line')

start = 0
stop = 500

#Visualize
b = Backtest.Backtester()

b.show_signals(close.values[start:stop], df_trade['Signal'].values[start:stop])

