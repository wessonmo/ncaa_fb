import os
import json
import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import re
import ujson
import time
import numpy as np

espn_folder_path = 'espn\\csv\\'

play_info = pd.DataFrame(columns = ['gameid','driveid','playid','period','clock','offid','offfield','down','dist','yrdline','playtype','yardage','text','endid'])
    
pbp_folder = 'E:\\college football\\pbp'
for season in reversed(os.listdir(pbp_folder)):
    print(season)
    for week in os.listdir(pbp_folder + '\\' + season):
        print('\t' + week)
        diff = []
        for file_ in os.listdir(pbp_folder + '\\' + season + '\\' + week + '\\full\\'):
#            print('\t\t' + file_)
            with open(pbp_folder + '\\' + season + '\\' + week + '\\full\\' + file_) as json_data:                
                data = ujson.load(json_data)
                
            
            if data['id'] in list(play_info.gameid):
                continue
            gameid = data['id']

            for team in data['teams']:
                if team['homeAway'] == 'home':
                    home = team['id']
                    home_score = team['score']
                    home_name = team['team']['displayName']
                    home_name_list = [team['team']['displayName'].lower(),team['team']['abbreviation'].lower(),team['team']['nickname'].lower()]
                else:
                    away = team['id']
                    away_score = team['score']
                    away_name = team['team']['displayName']
                    away_name_list = [team['team']['displayName'].lower(),team['team']['abbreviation'].lower(),team['team']['nickname'].lower()]
            
            prev_qtr = None
            for drive in data['drives']['previous']:
                if drive['start']['period']['number'] > 4:
                    break
                
                if drive['start']['period']['number'] != prev_qtr:
                    if drive['start']['period']['number'] in [1,3]:
                        home_tor, away_tor = 3, 3
                    prev_qtr = drive['start']['period']['number']

                driveid = drive['id']

                for play in drive['plays']:
                    try:
                        play['type']
                    except:
                        continue
                    
                    if play['type']['text'] == 'End Period':
                        continue
                    try:
                        if 'Timeout' in play['type']['text'] == 'Timeout':
                            to_name = re.compile('(?<=Timeout ).*(?=\,)').search(play['text']).group(0).lower()
                            if to_name not in (home_name_list + away_name_list):
                                to_team = process.extractOne(to_name,(home_name_list + away_name_list), scorer = fuzz.token_sort_ratio)[0]
                            else:
                                to_team = to_name
                            if to_name in home_name_list:
                                home_tor -= 1
                            else:
                                away_tor -= 1
                            continue
                    except:
                        pass
                    play_list = [gameid,driveid]
                    play_list.append(play['id'])#play_id
                    play_list.append(play['period']['number'])#period
                    clock = play['clock']['displayValue']
                    play_list.append(int(clock.split(':')[0])*60 + int(clock.split(':')[1]))#clock (in seconds)
                    play_list.append(play['start']['team']['id'])#start_id
                    if data['competitions'][0]['neutralSite'] == True:
                        off_field = 'neutral'
                    else:
                        off_field = 'home' if play['start']['team']['id'] == home else 'away'
                    play_list.append(off_field)#off_field
                    play_list.append(play['start']['down'])#down
                    play_list.append(play['start']['distance'])#dist
                    play_list.append(play['start']['yardLine'])#yrdline
                    play_list.append(play['type']['text'])#playtype
                    play_list.append(play['statYardage'])#yardage
                    play_list.append(play['text'])#text
                    try:
                        play_list.append(play['end']['team']['id'])#end_id
                    except:
                        play_list.append(None)#end_id

                    play_info.loc[len(play_info)] = play_list
play_info.drop_duplicates().sort_values(['gameid','driveid','playid']).to_csv(espn_folder_path + 'espn_pbp.csv', index = False)