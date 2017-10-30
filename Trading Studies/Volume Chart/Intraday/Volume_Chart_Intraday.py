"""
=========================================================
Volume distribution chart given usual dataframe of prices
=========================================================

- Inputs are Start Index and length of Window
- Plots exactly as other code
- Window span of 30 mins

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#Basic Cross Ball plot
plt.rc_context({'axes.edgecolor':'green','axes.facecolor':'black', 'ytick.color':'green','xtick.color':'green','grid.color':'grey', 'grid.linestyle':'--'})

ipt = input('Start:')
start = int(ipt)

ipt2 = input('\nWindow:')
window = int(ipt2)

############################################################
# GET DATAAAAAA
fName = '/home/ale/Documenti/Trading Studies/Data/FIB_Data_New.xlsx'

if 'data' not in locals():
    data = pd.read_excel(fName, Sheetname = '1M')

############################################################

#Convert datetimes to simple strings
#data['Date'] = data['Date'].apply(lambda x: str(x)[:10])

grouper = np.zeros(data.shape[0])
counter = 0

for i in range(2,len(grouper)-2):
    
    if(data['Time'][i].minute == 30 or data['Time'][i].minute == 0
       or data['Time'][i-1].minute == 29 or data['Time'][i-2].minute == 28 
       or data['Time'][i+1].minute == 1 or data['Time'][i+2].minute == 2
       or (data['Time'][i].minute == 1 and data['Time'][i].hour == 9)):
        
        counter = counter + 1
        
    grouper[i] = counter 

grouper[-2:] = counter

#To start on the proper group
start = int(grouper[start])
data['Grouper'] = grouper   

groups = data['Grouper'].unique()
#N_days = len(days)

#For plotting purposes, sanity check on window
if(window > grouper[-1]):
    
    window = grouper[-1]
    
dz = dict()
label_list = []

for t in groups[start:start+window]:
    
    df = data[data['Grouper'] == t]
    dz[t] = df.groupby('Close').sum()['Vol']
    label_list.append(df['Time'].iloc[0])
    
date = str(df['Date'].iloc[0])[:10]

#%%
#Plot now, group by group

#Set left offsets
space = 200/window
lefts = np.arange(0,window)*space
count = 0
width_par = 2*window

fig, ax = plt.subplots()

for t in groups[start:start+window]:
    
    ax.barh(dz[t].index, dz[t].values/width_par, height=4, left=lefts[count])
    count = count+1
    
ax.set_xticks(lefts)
ax.set_xticklabels(label_list)
plt.xticks(rotation = 45 )

ax.set_ylabel("Data values")
ax.set_xlabel("Data sets")

ax.grid(True)
ax.set_title('Volume Distribution Plot ' +date, color = 'g')

fig.patch.set_facecolor('black')
fig.patch.set_edgecolor('green')

plt.show()    
    

