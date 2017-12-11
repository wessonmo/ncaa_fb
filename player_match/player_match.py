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

def team_match(min_season, latest_rct_class):
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
                    
    for index, row in team_index.loc[~pd.isnull(team_index['cfbr_href'])].iterrows():
        print(row['cfbr_href'],row['x247_href'])
            
    return team_index
    
def player_match(min_season):    
    
    curr_dt = time.strftime('%Y %m').split()
    
    latest_rct_class = int(curr_dt[0]) - (1 if int(curr_dt[1]) < 3 else 0)
    recruits_df = recruits_247_scrape(min_season, latest_rct_class)
    
    latest_roster = int(curr_dt[0]) - (1 if int(curr_dt[1]) < 8 else 0)
    rosters_df = player_stats_scrape(min_season,latest_roster)
    rosters_df['x247_playerhref'] = None
    
    team_index = team_match(min_season, latest_rct_class)
    
    player_match = pd.DataFrame(columns = ['cfbr_season','cfbr_teamhref','cfbr_playerhref','cfbr_playername','x247_season','x247_instgroup','x247_playerhref'])
    
    for season in reversed(range(min_season - 4,latest_rct_class + 1)):
        rct_teams = list(recruits_df.loc[(recruits_df['season'] == season) & (recruits_df['team_href'].isin(team_index['x247_href'])),'team_href'].drop_duplicates())
        for rct_team in rct_teams:
            cfbr_teamhref = team_index.loc[team_index['x247_href'] == rct_team,'cfbr_href'].iloc[0]
#            matched = player_match.loc[(player_match['season'] == season) & (rosters_df['team_href'] == cfbr_teamhref)]

            rost_class = rosters_df.loc[(rosters_df['season'] == season) & (rosters_df['team_href'] == cfbr_teamhref)]
            rct_class = recruits_df.loc[(recruits_df['season'] == season) & (recruits_df['team_href'] == rct_team)]
            
            if (len(rct_class) > 0) and (len(rost_class) > 0):
                for index, row in rost_class.iterrows():
                    fuzzymatches = process.extract(row['player_name'],rost_class['rct_name'],limit = 2)
                    if (fuzzymatches[0][1] > 90) & (fuzzymatches[1][1] > 90):
                        raise ValueError('double match')
            for threshold in [100,93,87]:
                for i in range(4):
                    
            
            
            
            
            
            
        for index, row in team_index.loc[~pd.isnull(team_index['x247_href'])].iterrows():
            if not (pd.isnull(row['cfbr_href']) | pd.isnull(row['x247_href'])):
                full_rct = recruits_df.loc[(recruits_df['season'] == season) & (recruits_df['college_href'] == row['x247_href'])]
                full_rost = rosters_df.loc[(rosters_df['season'] == season) & (rosters_df['team_href'] == row['cfbr_href'])]
                for i in range(4):
                    
                        already_matched = rosters_df.loc[(rosters_df['season'] == season) & (rosters_df['team_href'] == row['cfbr_href']) & (~pd.isnull(rosters_df['x247_playerhref']))]
                        unmatch_rost = full_rost.loc[~full_rost['player_href'].isin(already_matched['player_href'])]
                        if len(unmatch_rost) > 0:
                            unmatch_rct = full_rct.loc[~full_rct['href'].isin(already_matched['x247_playerhref'])]
                            for index2,row2 in unmatch_rct.iterrows():
                                if i == 0:
                                    rost_class = [None,'FR'] if (row2['instgroup'] == 'HighSchool') else [None,'FR','SO','JR','SR']
                                elif i == 1:
                                    rost_class = [None,'FR','SO'] if (row2['instgroup'] == 'HighSchool') else [None,'FR','SO','JR','SR']
                                elif i == 2:
                                    rost_class = [None,'FR','SO','JR'] if (row2['instgroup'] == 'HighSchool') else [None,'FR','SO','JR','SR']
                                else:
                                    rost_class = [None,'SO','JR','SR']
                                
                                fuzzymatch = process.extractOne(row2['mod_name'], list(unmatch_rost['mod_name']), scorer = fuzz.partial_ratio)
                                rost_player = unmatch_rost.loc[unmatch_rost['mod_name'] == fuzzymatch[0]].iloc[0]
                                if (fuzzymatch[1] >= threshold) and (rost_player['class'] in rost_class):
                                    index3 = rosters_df.loc[(rosters_df['season'] == season) & (rosters_df['team_href'] == row['cfbr_href']) & (rosters_df['mod_name'] == fuzzymatch[0])].iloc[0].name
                                    rosters_df.set_value(index3,'x247_playerhref',row2['href'])