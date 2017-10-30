import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.finance import candlestick2_ochl


#Threshold for Volume representation
Threshold = 150

#Basic Cross Ball plot
plt.rc_context({'axes.edgecolor':'green','axes.facecolor':'black', 
                'ytick.color':'green','xtick.color':'green',
                'grid.color':'grey', 'grid.linestyle':'--'})

def prop_round_1(n):
    
    return(n)

def prop_round_5(n):
    
    if n <= 10:
         if n<=5:
             return(5)
         else:
             return(10)
    elif n > 55:
        return(100)
    else:
        return(10*int(n/10)+prop_round_5(n-10*int(n/10)))

#df2 = pd.read_excel('FIB_Book.xlsm', sheetname = 'Output')[800:]
df2 = pd.read_excel('data-06-09.xlsx', sheetname = 'Sheet1')

#Recreate to reindex
df = pd.DataFrame(df2.values)
df.columns = df2.columns

cap_indexes = df[df['Volume'] > Threshold].index
df.loc[cap_indexes ,'Volume'] = 1#Threshold
    
neg_index = df['B/A'][df['B/A']=='B'].index
zero_index = df['B/A'][df['B/A']=='X'].index

df.loc[neg_index,'Volume'] = -df.loc[neg_index,'Volume']
df.loc[zero_index,'Volume'] = 0

#Create grouy column
df['group_colon'] = np.zeros(df.shape[0])

for i in range(0,df.shape[0]):
    df.iloc[i,-1] = 100*df['Time'][i].hour + prop_round_5(df['Time'][i].minute)

#%%
Vol_Delta = df[['group_colon','Volume']].groupby('group_colon').sum()
p_max = df[['group_colon','Price']].groupby('group_colon').max()
p_min = df[['group_colon','Price']].groupby('group_colon').min()
p_close = df[['group_colon','Price']].groupby('group_colon').last()
p_open = df[['group_colon','Price']].groupby('group_colon').first()

ix = range(0,Vol_Delta.shape[0])
#%%
#Plot
fig = plt.figure()
fig.patch.set_facecolor('black')
fig.patch.set_edgecolor('green')


ax = fig.add_subplot(211)
plt.grid(True)
ax2 = fig.add_subplot(212)
plt.grid(True)

width = 0.65
ax.plot(ix,p_close, 'bx')
ax.plot(ix,p_max, 'g^')
ax.plot(ix,p_min, 'rv')
ax2.bar(ix, Vol_Delta.values, width, color='r')

