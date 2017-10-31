import pandas as pd
import os
import json
import re

pbp_folder = 'E:\\college football\\pbp'

team_info = pd.DataFrame(columns = ['id', 'full', 'school', 'nickname', 'abbv'])

for season in os.listdir(pbp_folder):
    for week in os.listdir(pbp_folder + '\\' + season):
        if week[-2:].strip() in ['1','2','3']:
            for file_ in os.listdir(pbp_folder + '\\' + season + '\\' + week + '\\full\\'):
                with open(pbp_folder + '\\' + season + '\\' + week + '\\full\\' + file_) as json_data:
                    data = json.load(json_data)
                
                for team in data['teams']:
                    if team['team']['id'] not in list(team_info['id']):
                        team_info.loc[len(team_info),] = [team['team']['id'], team['team']['displayName'], team['team']['nickname'],
                                      team['team']['name'], team['team']['abbreviation']]

team_info.loc[:,'full'] = team_info.loc[:,'full'].apply(lambda x: re.sub(r'\xe9','e',x))
team_info.sort_values('full').reset_index(drop = True).to_csv('csv\\team_info_espn.csv', index = False)