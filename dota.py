# -*- coding: utf-8 -*-
"""
Created on Mon May 30 00:25:20 2022

@author: fmontaguti
"""
import requests, json, time, os
import numpy as np
import pandas as pd

## Functions
# Colect match by match id
def get_match_by_id(match_id):
    m_id = str(match_id)
    request = requests.get('http://api.opendota.com/api/matches/' + m_id)
    if request.ok:
        print('GET:',m_id)
        data = request.json()
        with open(m_id + '_data.json','w') as file:
            json.dump(data,file)
            
# Colect team by team id
def get_team_by_id(team_id):
    t_id = str(team_id)
    request = requests.get('http://api.opendota.com/api/teams/' + t_id)
    if request.ok:
        print('GET:',t_id)
        data = request.json()
    return(data)
    
# This is all ESL ONE Stockolm dota matches(ID) according to OpenDota
matches = [6582379623,6582249405,6582140888,6582012262,6581700268,6581622092,6580732041,6580625364,6580504708,6580376211,
            6580245004,6580016442,6579931950,6579165262,6579091075,6578909443,6578799684,6578674296,6578511105,6578432820,
            6578354994,6576223979,6576116877,6575974930,6575811382,6575685774,6575589562,6575506610,6574848748,6574739883,
            6574603408,6574482766,6574385083,6574188575,6574108422,6573568264,6573503063,6573407404,6573291227,6573182161,
            6573058524,6572937926,6572822253,6572725458,6572659357,6571966593,6571965781,6571843720,6571843204,6571732248,
            6571738707,6571582160,6571554679,6571442714,6571446779,6571305244,6571306390,6571280989,6571201844,6571200692,
            6571204733,6570398588,6570391220,6570284918,6570288241,6570172820,6570116439,6570016479,6570018786,6569867107,
            6569845922,6569732558,6569733548,6569705664,6569623765,6569582522,6569577483,6569495972,6569495782,6569502056,
            6568751767,6568705223,6568647082,6568623245,6568523627,6568508914,6568412845,6568401515,6568237950,6568205642,
            6568188836,6568101413,6568101177,6568099598,6568003158,6568000902,6567999161,6567917643,6567920917,6567928490,
            6567330746,6567327850,6567245668,6567240449,6567147786,6567143852,6567132607,6567029565,6567037682,6567037281,
            6566885647,6566878745,6566840888,6566781397,6566767216,6566744482,6566656802,6566631729,6566627889,6566556663,
            6566559037,6566559541]

## Collecting matches data
# Applying matches function
for match in matches:
    get_match_by_id(match)
    time.sleep(2)

## Reading Data     
picks = []
esl_data = []
for file in os.listdir('/data'):
    with open(file,'r') as f:
        # Reading Data
        data = json.load(f)
        # Appending to with list comphrehention
        [picks.append(line) for line in data['picks_bans']]
        # Creating new dataframe
        esl_data.append([data['match_id'],
                         data['series_id'],
                         data['start_time'],
                         data['radiant_team_id'],
                         data['dire_team_id'],
                         data['radiant_win'],
                         data['radiant_score'],
                         data['dire_score'],
                         data['duration'],
                         data['first_blood_time']])
        
# Setting column names
esl_names = ['match_id','series_id','start_time','radiant_team_id','dire_team_id',
             'radiant_win','radiant_score','dire_score','duration','first_blood_time']
pick_names = ['hero_id','is_pick','match_id','ord','order','team']
# Apllying some structure
esl_data = pd.DataFrame(esl_data,columns=esl_names)
picks = pd.DataFrame(picks,columns=pick_names)
# Fixing Start Time type
esl_data['start_time'] = pd.to_datetime(esl_data['start_time'],unit='s')

## Collecting Heros
heros = requests.get('https://api.opendota.com/api/heroes').json()
heros = pd.DataFrame(heros)

## Collecting Teams
teams = pd.concat([esl_data['radiant_team_id'],esl_data['dire_team_id']]).unique()

# Applying teams function
team_data = []
for team in teams:
    team_data.append(get_team_by_id(team))
    time.sleep(2)
# Converting to dataframe
team_data = pd.DataFrame.from_dict(team_data)

## Data Wrangling

# Merging match with team data
esl_data = pd.merge(esl_data,team_data[['team_id','name']],left_on='radiant_team_id',right_on='team_id')
esl_data = pd.merge(esl_data,team_data[['team_id','name']],left_on='dire_team_id',right_on='team_id')
# Renaming Column
esl_data = esl_data.rename(columns={'name_x':'radiant_team','name_y':'dire_team'})
esl_data['kills'] = esl_data['radiant_score']+esl_data['dire_score']
# Fixing date-time to date-only
esl_data['start_time'] = esl_data['start_time'].dt.date
# Droping columns
esl_data.drop(['radiant_team_id','dire_team_id','team_id_y','team_id_x'],axis=1,inplace=True)

## Picks
picks = pd.merge(picks,heros[['id','localized_name']],left_on='hero_id',right_on='id')
picks = pd.merge(picks,esl_data[['match_id','radiant_team','dire_team']])
# Fixing Team
picks['team'] = np.where(picks['team']==0, picks['radiant_team'], picks['dire_team'])
picks.drop(['hero_id','ord','id','dire_team','radiant_team'],axis=1,inplace=True)
# Renaming Column
picks = picks.rename(columns={'localized_name':'hero'})

# Check who won the match and merging with pick dataframe
match_win = esl_data[['match_id','radiant_win','radiant_team','dire_team']]
match_win['win'] = np.where(match_win['radiant_win']== True, match_win['radiant_team'], match_win['dire_team'])
match_win.drop(['radiant_win','radiant_team','dire_team'],axis=1,inplace=True)
# Merging data and changing to 0 1 format
picks = pd.merge(picks,match_win)
picks['win'] = np.where(picks['team']==picks['win'],1,0)

## Tournament_stats
master_data = esl_data.melt(id_vars=['start_time','match_id','series_id','radiant_win'],
                                                 value_vars=['radiant_team','dire_team'],
                                                 var_name='side',value_name='team')
# Checking who won the series
master_data['win'] = np.where( (master_data['radiant_win']==True) & (master_data['side']=='radiant_team')
                                    | (master_data['radiant_win']==False) & (master_data['side']=='dire_team'),1,0)


## Number of Matches & Teams by day
matches_by_day = esl_data.groupby('start_time')['match_id'].count()
matches_by_day = matches_by_day.reset_index()
teams_by_day = master_data.groupby('start_time')['team'].nunique()
teams_by_day = teams_by_day.reset_index()
# Merging datasets
tournament = pd.merge(matches_by_day,teams_by_day)
tournament.columns = ['date', 'matches', 'teams']

## Team Stats (WIN-LOSS)
team_stats = master_data.groupby('team').agg(wins=('win','sum'),games=('match_id','count'))
# Multiplying loss to -1 and sorting values
team_stats['loss'] = (team_stats['games']-team_stats['wins'])*-1
team_stats = team_stats.sort_values('wins',ascending=False)
team_stats = team_stats.reset_index()

## Series Win dataframe
win = master_data.groupby(['start_time','series_id','team'])['win'].sum().reset_index()
# We need to pivot the rows from series and collect data
series = []
for i in win['series_id'].unique():
    serie = win.loc[win['series_id']==i]
    wide = serie.pivot(index=['series_id','start_time'],columns=['team','win'],values=['team','win'])
    wide = wide.reset_index()
    series.append(np.concatenate(wide.values))
# Apply some structure change columns index and renaming then
series_result = pd.DataFrame(series)
series_result = series_result.reindex(columns=[0,1,2,4,5,3])
series_result.columns = ['Series ID','Date','Team A','A','B','Team B']

## Saving data for Dashboard

esl_data.to_csv('esl_data.csv', index=False)
picks.to_csv('picks.csv', index=False)
team_data.to_csv('teams.csv', index=False)
team_stats.to_csv('team_stats.csv',index=False)
tournament.to_csv('tournament.csv',index=False)
master_data.to_csv('master_data.csv', index=False)
series_result.to_csv('series_result.csv',index=False)