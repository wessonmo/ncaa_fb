import os
import calendar
import time
import json
import pandas as pd
import re

def team_info_espn():
    try:
        espn_folder_path = 'espn\\csv\\'
        team_info_df = pd.read_csv(espn_folder_path + 'espn_team_info.csv', header = 0)
        
        modified_time = os.path.getmtime(espn_folder_path + 'espn_team_info.csv')
        current_time = calendar.timegm(time.gmtime())
        if float(current_time - modified_time)/(60*60*24) > 365:
            pass
        else:
            return team_info_df
    except:
        pass
    
    team_info_df = pd.DataFrame(columns = ['espn_teamid', 'team_fullname', 'team_schoolname', 'team_nickname', 'team_abbv'])
    
    pbp_folder = 'E:\\college football\\pbp'
    for season in os.listdir(pbp_folder):
        for week in os.listdir(pbp_folder + '\\' + season):
            if week[-2:].strip() in ['1','2','3']:
                for file_ in os.listdir(pbp_folder + '\\' + season + '\\' + week + '\\full\\'):
                    with open(pbp_folder + '\\' + season + '\\' + week + '\\full\\' + file_) as json_data:
                        data = json.load(json_data)
                    
                    for team in data['teams']:
                        team = team['team']
                        if team['id'] not in list(team_info_df['id']):
                            team_fullname = re.sub(r'\xe9','e',team['displayName'])
                            team_info_df.loc[len(team_info_df)] = [team['id'],team_fullname,None,team['name'],
                                             team['abbreviation']]
                                             
    team_info_df['team_schoolname'] = team_info_df.apply(lambda x: x['team_fullname'] if pd.isnull(x['team_nickname']) else re.sub(' ' + x['team_nickname'],'',x['team_fullname']), axis = 1)
    team_info_df['team_abvname'] = team_info_df.apply(lambda x: None if pd.isnull(x['team_nickname']) else str(x['team_abbv'] + ' ' + x['team_nickname']), axis = 1)
        
    team_info_df.sort_values('team_fullname').reset_index(drop = True).to_csv(espn_folder_path + 'espn_team_info.csv', index = False)
    return team_info_df