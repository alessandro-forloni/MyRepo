import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt

###########################################################
# -----------------------TO DO LIST-----------------------
#
# - Consider average future return instead of single return
#
# - Normalize data (for speed)
#
# - Consider cross-validation
#
############################################################


max_lag = 10

fName = '/home/ale/Documenti/Trading Studies/Data/FIB_Data_New.xlsx'

data = pd.read_excel(fName, sheetname = '1M')

#Get Deltas
data['change'] = data['Close']-data['Open']
data['range'] = data['High']-data['Open']



df_temp = pd.DataFrame(data['Date'])
df_temp['time'] = data['Time']
df_temp['change'] = data['change']
df_temp['volume'] = data['Vol']
df_temp['close'] = data['Close']

#Create Lags
for i in range(1,max_lag):
    
    df_temp['change-'+str(i)] = df_temp['change'].shift(i)
    df_temp['volume-'+str(i)] = df_temp['volume'].shift(i)
    


#Eliminate first max_lag elements of the day    
i = 1

while i < df_temp.shape[0]:
    
    if((df_temp['Date'][i]-df_temp['Date'][i-1]).total_seconds() > 0):
        
        #Remove following max_lag observations
        for j in range(0,max_lag):
            df_temp = df_temp.drop(i)
            i = i + 1
           
    i = i + 1
    
df_temp = df_temp.dropna(how = 'any')

#Create new index
dates = [str(x)[:10].replace('-','') for x in df_temp['Date']]
times = [str(x)[:5].replace(':','') for x in df_temp['time']]
new_index = [x+'-'+y for x,y in zip(dates,times)]

#Create and fill new dataframe
df = pd.DataFrame(index = new_index)


for i in range(1,max_lag):
    
    df['change-'+str(i)] = df_temp['change-'+str(i)].values
    df['volume-'+str(i)] = df_temp['volume-'+str(i)].values




##Create output21
#out = df['return'] + df['return'].shift(-1)+ \
#      df['return'].shift(-2) + df['return'].shift(-3)+ \
#      df['return'].shift(-4)
#      
#y = (out/5 >= 0)*1
#
y = (df_temp['change'] > 0)*1

for_later_use = df_temp['close']

#Clear Memory
del df_temp
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
#
#%%
#
#Let's Play
def optimize():
    
    best_N = 0
    best = 0
    
    for i in range(2,25):
        
        knn_clf = KNeighborsClassifier(i, weights = 'distance')
        knn_clf.fit(X_train,y_train)
        score = knn_clf.score(X_test,y_test)
        
        if score > best:
            best = score
            best_N = i
            
    print('Best Score: ', best, ' - Optimal n-neighbors: ', best_N)       
    return(best_N)  
##
##   
#optimize()
  
N = 18

#print('I suggest using ', optimize(), 'neighbors')

knn_clf = KNeighborsClassifier(N, weights = 'distance')
knn_clf.fit(X_train,y_train)

print('Classification Accuracy', knn_clf.score(X_test,y_test))
#
justosee = pd.DataFrame(y_test)
justosee['y_cap'] = knn_clf.predict(X_test)
justosee['prob'] = knn_clf.predict_proba(X_test)[:,1]
#
dist_vector = np.zeros(X_test.shape[0])
#
#Create columns with neighor dates
#for j in range(1,N+1):
#    justosee['neighbor-'+str(j)] = np.zeros(justosee.shape[0])
    
for i in range(0,X_test.shape[0]):
    dist_vector[i] = knn_clf.kneighbors(X_test.iloc[i,:].values.reshape(1,-1))[0].sum()
    
#    for j in range(0,N):
#        
#        ix = knn_clf.kneighbors(X_test.iloc[i,:].values.reshape(1,-1))[1][0,j]
#        justosee['neighbor-'+str(j+1)][i] = X_train.index[ix]
#        

#justosee['actual'] = y.iloc[sep:]
#Value for scaling   
delta =  dist_vector.max() - dist_vector.min()
#Compute distance
justosee['dist'] = (dist_vector-dist_vector.min())/delta
justosee['close'] = for_later_use.iloc[sep:]
##Sort dataframe
##justosee = justosee.sort_values('dist')
#
##%%
#
##Strategy backtest
#K =10000
#portfolio_value = np.ones(justosee.shape[0])
#justosee['strat'] = justosee['y_cap']*2 - 1
#
#for i in range(1,justosee.shape[0]):
#    
##    portfolio_value[i] = portfolio_value[i-1]*(1+justosee['strat'][i]*justosee['actual'][i])
#    portfolio_value[i] = portfolio_value[i-1]+ K*(justosee['strat'][i]*justosee['actual'][i])
#
#plt.plot(portfolio_value)
#plt.xticks(range(0,justosee.shape[0]), justosee.index, rotation=45)
#plt.title('Strategy Performance')
#    
#%%
# SOME PLOOOOTS
start = 1000
end = 1148
plt.figure()
plt.subplot(211)
plt.plot(justosee['close'].iloc[start:end])
plt.grid(True)
plt.subplot(212)
plt.plot(justosee['prob'].iloc[start:end])
plt.plot(justosee['dist'].iloc[start:end])
plt.plot(justosee['prob'].iloc[start:end].index, 0.5*np.ones(end-start))
plt.grid(True)