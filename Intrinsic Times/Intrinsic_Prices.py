'''

=================================

- Read TestData.csv
- Set a threshold
- Initialize the class that does the job of discretizing
- Print execution time for the core calculation
- Eventually plot price and discretized series on top

=================================

'''
import os
import pandas as pd
import matplotlib.pyplot as plt
import Discretizer



fPath = os.path.dirname(os.path.realpath(__file__))
fName = fPath + '/TestData.csv'

data = pd.read_csv(fName)

#USE BID+ASK/2 and clean otherwise discretization class 
# will not work

df = (data['Ask']+data['Bid'])/2
df = df.dropna(how = 'any')

#Initialize objects
# Threshold is expressed in percentage
core = Discretizer.Filter(df,thresh = 0.02)
core2 = Discretizer.Filter(df,thresh = 0.015)

# Divide series into intrinsic sets
# The output (X) is a dataframe of price levels
# And the index is the time at which the price 
# is registered
# The code also prints the average overshoot, that I have computed
# as the average percentage move after a new 'up' or 'down' mode
# is detected 

X1 = core.Discretize()
X2 = core2.Discretize()

#Plot Results
fig = plt.figure()

ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

#Actualy plotting the result only for the first 500 prices
core.visualize(ax1 , 500)
core2.visualize(ax2 , 500)
