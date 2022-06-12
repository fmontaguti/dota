# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 23:08:41 2022

@author: fmontaguti
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

plt.style.use('ggplot')
st.set_page_config(layout="wide")

## Reading Data
esl_data = pd.read_csv('esl_data.csv')
picks = pd.read_csv('picks.csv')
teams = pd.read_csv('teams.csv')
team_stats = pd.read_csv('team_stats.csv')
tournament = pd.read_csv('tournament.csv')
master_data = pd.read_csv('master_data.csv')
series_result = pd.read_csv('series_result.csv')
    
## Side Bar
with st.sidebar:
    st.header('Participating Teams')
    st.subheader('Winner')
    st.image(teams.loc[teams['name']=='OG']['logo_url'].item(),use_column_width =True,caption='OG')
    st.subheader('Other Teams')
    # Other teams
    side_col1, side_col2 = st.columns(2)
    with side_col1:
        for key,value in teams.loc[teams['name']!='OG'][:6].iterrows():
            st.image(value['logo_url'],use_column_width =True,caption=value['name'])
    with side_col2:
        for key,value in teams.loc[teams['name']!='OG'][6:12].iterrows():
            st.image(value['logo_url'],use_column_width =True,caption=value['name'])
    
## Title
st.title('ESL One Stockholm 2022 - Dota 2 Major Overview')
st.subheader('Streamlit App by [Fernando Hold Montaguti](https://www.linkedin.com/in/fernando-hold-montaguti-1ab8a3145/)')
st.write('Dota 2 is one of the most played games on Steam, its a MOBA style-game with RPG elements where Radiant and Dire team fight against each other'
         ' in a 10 players match. ESL One Stockholm was the first Major of Dota Pro Circuit 2021/2022 with crowd in over 2 years. The overall prize money'
         ' was $ 500,000 and the event also had other activities like cosplay constest and signing sessions with the pro-players.')
st.write('The data was extracted using OpenDota API, if you want to see the extraction and transformation check my dota.py on my github.')
st.subheader('Tournament')
## Two first plots
col1, col2 = st.columns(2) 
with col1:
    ## Tournament Evolution (1)
    st.write('Evolution')
    from matplotlib.ticker import MaxNLocator
    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(tournament['date'],tournament['matches'],'o-')
    ax.plot(tournament['date'],tournament['teams'],'o-')
    ax.axvline('2022-05-14',color='black')
    ax.set_xticklabels(tournament['date'],rotation=45, ha='right')
    ax.legend(['Matches', 'Teams','Group Stage End'])
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_title(label ='Tournament Evolution')
    st.pyplot(fig)    
with col2:
    ## Teams (2)
    st.write('Teams')
    fig, ax = plt.subplots(figsize=(8,4))
    ax.bar(team_stats['team'],team_stats['wins'],color='tab:green')
    ax.bar(team_stats['team'],team_stats['loss'],color='tab:red')
    ax.set_xticklabels(team_stats['team'], rotation=45, ha='right')
    ax.set_title(label ='Win | Loss by Team (Absolute)')
    st.pyplot(fig)

### Trending heros plot (3)
st.write('Trending Heros')
# Seting Slicer & Selectbox
col3, col4 = st.columns((1,2)) 
with col3:
    option1 = st.selectbox('Select Most',('Picks','Bans'))
with col4:
    option2 = st.slider('Number of Heros',1,50,25)
# Slicing dataset according to Slicer & Selectbox
if option1=='Picks':
    heros = picks.loc[picks['is_pick']==True].groupby(['hero'])['hero'].count().sort_values(ascending=False).to_frame('total')
else:
    heros = picks.loc[picks['is_pick']==False].groupby(['hero'])['hero'].count().sort_values(ascending=False).to_frame('total')
heros.reset_index(inplace=True)
# Applying Slice
heros = heros[:option2]
# Plot Fig
fig, ax = plt.subplots(figsize=(14,3))
ax.bar(heros['hero'],heros['total'])
ax.set_xticklabels(heros['hero'], rotation=45, ha='right')
ax.set_title(label ='Top '+ str(option2) + ' ' + option1)
st.pyplot(fig)

## Statistics
st.write('Statistics')
col5, col6, col7 = st.columns(3)
with col5:
    ## Histogram Game Duration (4)
    st.write('Game Duration - [seconds]')
    fig, axes  = plt.subplots()
    sns.histplot(data = esl_data['duration'], kde=True)
    st.pyplot(fig)
with col6:
    ## Histogram First Blood (5)
    st.write('First Blood - [seconds]')
    fig, axes  = plt.subplots()
    sns.histplot(data = esl_data['first_blood_time'] , kde=True)
    st.pyplot(fig)
with col7:
    ## Histogram number of kills (6)
    st.write('Kills in Match')
    fig, axes  = plt.subplots()
    sns.histplot(data = esl_data['kills'] , kde=True)
    st.pyplot(fig)

## Win-rate by side | Series results
# Grouping win-rate by side
winrate_side = master_data.groupby('side')['win'].mean()

col8, col9 = st.columns((1.5,1))
with col8:
    ## Win Rate by Side (7)
    st.write('Win Rate by Side')
    fig, ax = plt.subplots(figsize=(1.6,1.6))
    ax.pie(winrate_side, wedgeprops={'width':0.4},labels=winrate_side.index,autopct="%.1f%%",frame=False)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    st.pyplot(fig)
with col9:
    ## Series Results (8)
    st.write('Series Results')
    st.dataframe(series_result,height=530)


## Win-rate by Hero (9)
winrate_hero = picks.loc[picks['is_pick']==True].groupby(['hero'])['win'].mean()
winrate_hero = winrate_hero.reset_index()

st.write('Win Rate by Heros')
# Seting Slicer, Selectbox & Checkbox
col10, col11, col12 = st.columns((1,1,2.5)) 
with col10:
    option3 = st.selectbox('Select',('Top','Botton'))
with col11:
    st.write('Remove 1 and 0 Win Rates?')
    option4 = st.checkbox('Remove', value=True)
with col12:
    option5 = st.slider('Number of Heros',1,50,30)
# Slicing dataset according to Slicer & Selectbox
if option3=='Top':
    hero_win = winrate_hero.sort_values(by='win',ascending=False)
else:
    hero_win = winrate_hero.sort_values(by='win',ascending=True)
# Second Check
if option4:
    hero_win = hero_win.loc[(hero_win['win']!=1) & (hero_win['win']!=0)]
# Applying Slice
hero_win = hero_win[:option5]
# Plot Fig
fig, ax = plt.subplots(figsize=(14,3))
ax.bar(hero_win['hero'],hero_win['win'])
ax.set_xticklabels(hero_win['hero'], rotation=45, ha='right')
ax.axhline(0.5,color='black')
ax.set_title(label ='Win Rate '+ str(option5) + ' ' + option3 + ' Heros')
st.pyplot(fig)

st.subheader('Author')
st.write('Please feel free to contact me with any issues, comments, or questions.')
st.write('Fernando Hold Montaguti')
col13, col14, col15 = st.columns((1,2,1))
with col13:
    st.write('Email: fmontaguti2@gmail.com')
with col14:
    st.write('Linkedin: https://www.linkedin.com/in/fernando-hold-montaguti-1ab8a3145/')
with col15:
    st.write('Github: https://github.com/fmontaguti')
