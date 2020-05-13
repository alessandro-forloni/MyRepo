# -*- coding: utf-8 -*-
"""
Created on Wed May 13 20:33:48 2020

@author: alex_
"""

import pandas as pd

file_name = 'D1.csv'
df = pd.read_csv(file_name)

teams = df.HomeTeam.unique()

statsDict = {}

# ricostruisci classifica e stats
for team in teams:
    
    teamDict = {}
    
    dfFilteredHome = df[df.HomeTeam == team]
    dfFilteredAway = df[df.AwayTeam == team]
    
    deltaGoalsHome = dfFilteredHome.FTHG - dfFilteredHome.FTAG
    deltaGoalsAway = dfFilteredAway.FTHG - dfFilteredAway.FTAG
    
    homeWins = sum(deltaGoalsHome > 0)
    homeDraws = sum(deltaGoalsHome == 0)
    homeLosses = sum(deltaGoalsHome < 0)
    
    awayWins = sum(deltaGoalsAway < 0)
    awayDraws = sum(deltaGoalsAway == 0)
    awayLosses = sum(deltaGoalsAway > 0)
    
    points = 3*(homeWins + awayWins) + 1*(homeDraws + awayDraws)
    
    awayPoints = awayDraws + 3*awayWins
    homePoints = homeDraws + 3*homeWins
    
    teamDict['homeWins'] = homeWins
    teamDict['homeDraws'] = homeDraws
    teamDict['homeLosses'] = homeLosses
    teamDict['awayWins'] = awayWins
    teamDict['awayDraws'] = awayDraws
    teamDict['awayLosses'] = awayLosses
    
    teamDict['points'] = points
    teamDict['awayPoints'] = awayPoints
    teamDict['homePoints'] = homePoints
    
    
    teamDict['homeGoals'] = dfFilteredHome.FTHG.sum()
    teamDict['awayGoals'] = dfFilteredAway.FTAG.sum()
    
    
    # fill dictionary
    statsDict[team] = teamDict
    


    
dfFinal = pd.DataFrame.from_dict(statsDict, orient = 'index')

dfFinal['rank'] = dfFinal.points.rank(ascending=False).astype(int)
ranking_dict = dfFinal.points.rank(ascending=False).astype(int).to_dict()

# statistiche relative ad altre squadre
df['RankHome'] = df.HomeTeam.map(ranking_dict)
df['RankAway'] = df.AwayTeam.map(ranking_dict)

df['RankHomeGroup'] = 1*(df['RankHome'] < 6) + 1*(df['RankHome'] < 12)  + 1*(df['RankHome'] <= 18)
df['RankAwayGroup'] = 1*(df['RankAway'] < 6) + 1*(df['RankAway'] < 12)  + 1*(df['RankAway'] <= 18)

dfFinal['RankGroup'] = 1*(dfFinal['rank'] < 6) + 1*(dfFinal['rank'] < 12)  + 1*(dfFinal['rank'] <= 18)
    
deltaRankedDict = {}

for team in teams:
    
    dfFilteredHome = df[df.HomeTeam == team][['RankAwayGroup', 'FTHG', 'FTAG']]
    dfFilteredAway = df[df.AwayTeam == team][['RankHomeGroup', 'FTHG', 'FTAG']]
    
    dfFilteredHome['delta'] = dfFilteredHome.FTHG -  dfFilteredHome.FTAG
    dfFilteredAway['delta'] = dfFilteredAway.FTAG -  dfFilteredAway.FTHG
    
    delta_goals_home = dfFilteredHome.groupby('RankAwayGroup')['delta'].sum()
    delta_goals_away = dfFilteredAway.groupby('RankHomeGroup')['delta'].sum()
    
    delta_goals = delta_goals_home + delta_goals_away
    
    deltaRankedDict[team] = delta_goals.to_dict()
    
dfDeltaGoalsRanked = pd.DataFrame.from_dict(deltaRankedDict, orient='index')

dfMerged = dfFinal.merge(dfDeltaGoalsRanked, left_index = True, right_index = True)


#%%

# analizza la domenica in arrivo
fixtures = [
            ['Augsburg', 'Wolfsburg'],
            ['Dortmund','Schalke 04'],
            ['Fortuna Dusseldorf','Paderborn'],
            ['Hoffenheim','Hertha'],
            ['RB Leipzig','Freiburg'],
            ['Ein Frankfurt',"M'gladbach"],
            ['FC Koln','Mainz'],
            ['Union Berlin','Bayern Munich'],
            ['Werder Bremen','Leverkusen']] 

dfComing = pd.DataFrame(fixtures, columns = ['HT', 'AT'])
dfComing['HomeRank'] = dfComing['HT'].map(dfMerged.RankGroup.to_dict())
dfComing['AwayRank'] = dfComing['AT'].map(dfMerged.RankGroup.to_dict())

dfComing['homePoints'] = dfComing['HT'].map(dfMerged.points.to_dict())
dfComing['awayPoints'] = dfComing['AT'].map(dfMerged.points.to_dict())

#dfComing['homeGoals'] = dfComing['HT'].map(dfMerged.homeGoals.to_dict())
#dfComing['awayGoals'] = dfComing['AT'].map(dfMerged.awayGoals.to_dict())

dfComing['deltaPoints'] = dfComing['homePoints'] - dfComing['awayPoints']
#dfComing['deltaGoals'] = dfComing['homeGoals'] - dfComing['awayGoals']

deltaComingDictRanked = {}

for ix, row in dfComing.iterrows():
    
    rankAway = row.AwayRank
    rankHome = row.HomeRank
    
    homeTeam = row.HT
    awayTeam = row.AT
    
    deltaGoalsRankedHome = deltaRankedDict[homeTeam][rankAway]
    deltaGoalsRankedAway = deltaRankedDict[awayTeam][rankHome]
    
    deltaComingDictRanked[ix] = [deltaGoalsRankedHome, deltaGoalsRankedAway]
    

dfDeltaRanked = pd.DataFrame.from_dict(deltaComingDictRanked, 
                                       orient="index", 
                                       columns = ['deltaRankedHome','deltaRankedAway']
                                       )

dfNew = dfComing.merge(dfDeltaRanked, left_index = True, right_index = True)

