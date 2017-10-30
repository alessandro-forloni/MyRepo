"""
=========================================================
Volume distribution chart given usual dataframe of prices
=========================================================


"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#Basic Cross Ball plot
plt.rc_context({'axes.edgecolor':'green','axes.facecolor':'black', 'ytick.color':'green','xtick.color':'green','grid.color':'grey', 'grid.linestyle':'--'})

ipt = input('Number of Days:')
window = int(ipt)

############################################################
# GET DATAAAAAA
fName = '/home/ale/Documenti/Trading Studies/Data/FIB_Data_New.xlsx'

if 'data' not in locals():
    data = pd.read_excel(fName, Sheetname = '1M')

############################################################

#Convert datetimes to simple strings
data['Date'] = data['Date'].apply(lambda x: str(x)[:10])

days = data['Date'].unique()
N_days = len(days)

#For plotting purposes, sanity check on window
if(window > N_days):
    
    window = N_days
    
dz = dict()

for d in days[-window:]:
    
    df = data[data['Date'] == d]
    dz[d] = df.groupby('Close').sum()['Vol']
    


#%%
#Plot now, day by day

#Set left offsets
space = 200/window
lefts = np.arange(0,window)*space
count = 0
width_par = 10*window

fig, ax = plt.subplots()

for d in days[-window:]:
    
    ax.barh(dz[d].index, dz[d].values/width_par, height=5, left=lefts[count])
    count = count+1
    
ax.set_xticks(lefts)
ax.set_xticklabels(days[-window:])
plt.xticks(rotation = 45 )

ax.set_ylabel("Data values")
ax.set_xlabel("Data sets")

#ax.grid(True)
ax.set_title('Volume Distribution Plot', color = 'g')

fig.patch.set_facecolor('black')
fig.patch.set_edgecolor('green')

plt.show()    
    

