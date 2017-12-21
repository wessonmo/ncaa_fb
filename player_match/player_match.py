import pandas as pd
#from bs4 import BeautifulSoup
#import requests
#import re
#import os
#import calendar
import time
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from espn.espn_team_info import team_info_espn
from x247_scrape.x247_scrape import team_info_247_scrape, recruits_247_scrape
from cfbr_scrape.cfbr_scrape import team_info_cfbr_scrape, player_stats_scrape

match_folder_path = 'player_match\\csv\\'

def team_match():
    team_espn = team_info_espn()
    team_cfbr = team_info_cfbr_scrape()
    team_247 = team_info_247_scrape()
    
    team_dict = {'espn_teamid': list(team_espn['espn_teamid']), 'espn_fullname': list(team_espn['team_fullname']),
                 'espn_schoolname': list(team_espn['team_schoolname']),'espn_abvname': list(team_espn['team_abvname']),
                 'x247_href': [None]*len(team_espn),'cfbr_href': [None]*len(team_espn)}
    team_index = pd.DataFrame.from_dict(team_dict)
    
    for threshold in [84,54]:
        rem_index = team_index.loc[pd.isnull(team_index['x247_href']),]
        for index, row in rem_index.iterrows():
            rem_247 = team_247.loc[~team_247['team_href'].isin(team_index['x247_href']),]
            fuzzymatch = process.extractOne(row['espn_fullname'], list(rem_247['team_fullname']),scorer=fuzz.token_sort_ratio)
            if (fuzzymatch[1] > threshold) and (row['espn_teamid'] != 2000):
                href = rem_247.loc[rem_247['team_fullname'] == fuzzymatch[0],'team_href'].iloc[0]
                team_index.set_value(index,'x247_href',href)
                
    for threshold, name_type in zip([92,69,95],['schoolname','fullname','abvname']):
        rem_index = team_index.loc[pd.isnull(team_index['cfbr_href']),]
        for index, row in rem_index.iterrows():
            rem_cfbr = team_cfbr.loc[~team_cfbr['team_href'].isin(team_index['cfbr_href']),]
            if len(rem_cfbr) > 0:
                search_name = row['espn_fullname'] if pd.isnull(row['espn_' + name_type]) else row['espn_' + name_type]
                fuzzymatch = process.extractOne(search_name, list(rem_cfbr.loc[pd.isnull(rem_cfbr['team_' + name_type]) == False,'team_' + name_type]),scorer=fuzz.token_sort_ratio)
                if fuzzymatch[1] > threshold:
                    href = rem_cfbr.loc[rem_cfbr['team_' + name_type] == fuzzymatch[0],'team_href'].iloc[0]
                    team_index.set_value(index,'cfbr_href',href)
            
    return team_index

def match_values(rost_class,match_name):
    rost_player = rost_class.loc[rost_class['player_name'] == match_name].iloc[0]
    if pd.isnull(rost_player['player_href']):
        match_list = [rost_player['team_href'],None,rost_player['season'],rost_player['player_name']]
    else:
        match_list = [rost_player['team_href'],rost_player['player_href'],None,None]
    return match_list
    
def player_match(min_season):    
    
    current_date = [int(x) for x in time.strftime('%Y %m').split()]
    recruits_df = recruits_247_scrape(min_season, current_date)
    rosters_df = player_stats_scrape(min_season,current_date)
    max_season = min(recruits_df['season'].max(),rosters_df['season'].max())
    
    team_index = team_match()
    
    player_match = pd.DataFrame(columns = ['cfbr_teamhref','cfbr_playerhref','cfbr_season','cfbr_playername','x247_season','x247_instgroup','x247_playerhref'])
    
    for season in reversed(range(min_season - 4,max_season + 1)):
        rct_teams = list(recruits_df.loc[(recruits_df['season'] == season) & (recruits_df['team_href'].isin(team_index['x247_href'])),'team_href'].drop_duplicates())
        for rct_team in rct_teams:
            cfbr_teamhref = team_index.loc[team_index['x247_href'] == rct_team,'cfbr_href'].iloc[0]
            rct_class = recruits_df.loc[(recruits_df['season'] == season) & (recruits_df['team_href'] == rct_team)]
            if len(rct_class) > 0:
                for threshold in [100,92,80]:
                    for i in range(1,4):
                        matched = player_match.loc[(player_match['cfbr_teamhref'] == cfbr_teamhref) & (pd.isnull(player_match['cfbr_playerhref']) == False),]
                        rost_class = rosters_df.loc[(rosters_df['season'] == season) & (rosters_df['team_href'] == cfbr_teamhref)
                            & (~rosters_df['player_href'].isin(matched['cfbr_playerhref']))]
                        if len(rost_class) > 0:
                            for index, row in rct_class.iterrows():
                                fuzzymatches = process.extract(row['recruit_name'],rost_class['player_name'],limit = 2)
                                if fuzzymatches[0][1] == 100:
                                    if fuzzymatches[1][1] != 100:
                                        player_match.loc[len(player_match)] = match_values(rost_class,fuzzymatches[0][0])\
                                                         + [row['season'],row['instgroup'],row['player_href']]
                                    else:
                                        'dedupe protocol'
                                elif fuzzymatches[1][1] > 92:
                                    'dedupe protocol'
                                elif fuzzymatches[0][1] > threshold:
                                    player_match.loc[len(player_match)] = match_values(rost_class,fuzzymatches[0][0])\
                                                         + [row['season'],row['instgroup'],row['player_href']]