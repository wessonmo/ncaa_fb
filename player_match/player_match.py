import pandas as pd
#from bs4 import BeautifulSoup
#import requests
#import re
#import os
#import calendar
#import time
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from espn.espn_team_info import team_info_espn
from x247_scrape.x247_scrape import team_info_247_scrape, recruits_247_scrape
from cfbr_scrape.cfbr_scrape import team_info_cfbr_scrape, player_stats_scrape

match_folder_path = 'player_match\\csv\\'

min_season = 2009

def team_match():
    team_espn = team_info_espn()
    team_247 = team_info_247_scrape()
    team_cfbr = team_info_cfbr_scrape()
    
    team_dict = {'espn_teamid': list(team_espn['espn_teamid']), 'espn_fullname': list(team_espn['team_fullname']),
                 'x247_fullname': [None]*len(team_espn), 'cfbr_fullname': [None]*len(team_espn)}
    team_index = pd.DataFrame.from_dict(team_dict)
    
    for threshold in [84,54]:
        rem_index = team_index.loc[pd.isnull(team_index['x247_fullname']),]
        for index, row in rem_index.iterrows():
            rem_247 = team_247.loc[~team_247['team_fullname'].isin(team_index['x247_fullname']),]
            fuzzymatch = process.extractOne(row['espn_fullname'], list(rem_247['team_fullname']),scorer=fuzz.token_sort_ratio)
            if fuzzymatch[1] > threshold:
                team_index.set_value(index,'x247_fullname',fuzzymatch[0])
                
    for threshold in [84,69,0]:
        rem_index = team_index.loc[pd.isnull(team_index['cfbr_fullname']),]
        for index, row in rem_index.iterrows():
            rem_cfbr = team_cfbr.loc[~team_cfbr['team_fullname'].isin(team_index['cfbr_fullname']),]
            fuzzymatch = process.extractOne(row['espn_fullname'], list(rem_cfbr['team_fullname']),scorer=fuzz.token_sort_ratio)
            try:
                if (fuzzymatch[1] > threshold) or ((threshold == 0) and (index in [17,83,176,184,203])):
                    team_index.set_value(index,'cfbr_fullname',fuzzymatch[0])
            except:
                break
            
    return team_index