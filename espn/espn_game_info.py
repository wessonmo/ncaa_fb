import os
import json
import pandas as pd

espn_folder_path = 'espn\\csv\\'

game_info = pd.DataFrame(columns = ['gameid','season','season_type','week','date','time','neutral','homeid','awayid','home_score','away_score'])
    
pbp_folder = 'E:\\college football\\pbp'
for season in os.listdir(pbp_folder):
    print(season)
    for week in os.listdir(pbp_folder + '\\' + season):
        print('\t' + week)
        for file_ in os.listdir(pbp_folder + '\\' + season + '\\' + week + '\\full\\'):
            with open(pbp_folder + '\\' + season + '\\' + week + '\\full\\' + file_) as json_data:
                data = json.load(json_data)
            
            if data['id'] in list(game_info.gameid):
                continue
            gameid = data['id']
            season2 = data['season']['year']
            season_type = data['season']['type']
            week2 = data['week']
            date = data['competitions'][0]['date'][:10]
            time = data['competitions'][0]['date'][11:-1]
            neutral = data['competitions'][0]['neutralSite']

            home, away = None, None
            home_score, away_score = 0, 0
            for team in data['teams']:
                if team['homeAway'] == 'home':
                    home = team['id']
                    home_score = team['score']
                else:
                    away = team['id']
                    away_score = team['score']

            game_info.loc[len(game_info)] = [gameid,season2,season_type,week2,date,time,neutral,home,away,home_score,away_score]
game_info.sort_values(['season','date','gameid']).to_csv(espn_folder_path + 'espn_game_info.csv', index = False)