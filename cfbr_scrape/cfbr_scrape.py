import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import os
import calendar
import time
from fuzzywuzzy import process

cfbr_folder_path = 'cfbr_scrape\\csv\\'

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'}

def team_info_cfbr_scrape():
    try:
        team_info_df = pd.read_csv(cfbr_folder_path + 'cfbr_team_info.csv', header = 0)
        
        modified_time = os.path.getmtime(cfbr_folder_path + 'cfbr_team_info.csv')
        current_time = calendar.timegm(time.gmtime())
        if float(current_time - modified_time)/(60*60*24) > 365:
            pass
        else:
            return team_info_df
    except:
        pass
    
    team_info_df = pd.DataFrame(columns = ['team_fullname', 'team_schoolname','team_href', 'capacity', 'city'])
    
    cap_re = re.compile('(?<=cap\. ).*(?=\))')
    city_re = re.compile('(?<=Location:).*(?= )')
    
    url = 'https://www.sports-reference.com/cfb/schools/'
    req = requests.get(url, headers = header)
    soup = BeautifulSoup(req.content, 'lxml')
    
    teams = soup.find('table', {'id': 'schools'}).find('tbody').find_all('tr', {'class': None})
    for team in teams:
        max_year = int(team.contents[3].text)
        if max_year > 1980:
            name = team.contents[1].text
            href = team.contents[1].contents[0].get('href')
            print(name,href)
    
            info_url = 'https://www.sports-reference.com' + href 
            info_req = requests.get(info_url, headers = header)
            info_soup = BeautifulSoup(info_req.content, 'lxml')
            
            school_info = info_soup.find('div', {'id': 'info'}).contents[1].contents[3]
            full_name = school_info.find('h1').contents[1].text
            cap = int(re.sub(',','',cap_re.search(school_info.text).group(0))) if cap_re.search(school_info.text) else None
            city = city_re.search(school_info.text).group(0).strip() if city_re.search(school_info.text) else None
    
            team_info_df.loc[len(team_info_df),] = [full_name,name,href,cap,city]
            
    team_info_df.to_csv(cfbr_folder_path + 'cfbr_team_info.csv', index = False)
    return team_info_df
    
def roster_scrape(season, team_href, team_name):
    roster_df = pd.DataFrame(columns = ['season', 'team_href', 'team_schoolname', 'player_name', 'player_href', 'class', 'pos'])
                
    roster_url = 'https://www.sports-reference.com' + team_href + str(season) + '-roster.html'
    roster_req = requests.get(roster_url, headers = header)
    roster_soup = BeautifulSoup(roster_req.content, 'lxml')
    
    try:
        players = roster_soup.find('table', {'id': 'roster'}).find('tbody').find_all('tr', {'class': None})
    except:
        return
    for player in players:
        player_name = player.contents[0].text[:-1] if player.contents[0].text[-1] == '*' else player.contents[0].text

        try:
            player_href = player.contents[0].contents[0].get('href')
        except:
            player_href = None
        class_ = None if player.contents[1].text == '' else player.contents[1].text
        pos = None if player.contents[2].text == '' else player.contents[2].text

        roster_df.loc[len(roster_df),] = [season, team_href, team_name, player_name, player_href, class_, pos]
    
    for index2, row2 in roster_df.loc[pd.isnull(roster_df['player_href'])].iterrows():
        match = process.extractOne(row2['player_name'], roster_df.loc[(pd.isnull(roster_df['player_href']) == False),'player_name'])
        if match[1] > 90:
            roster_df.drop(index2, inplace = True)
            
    roster_df = roster_df.reset_index(drop = True)
    return roster_df
    
def stats_scrape(roster_df,team_name):
    team_href = roster_df.iloc[0]['team_href']
    season = int(roster_df.iloc[0]['season'])

    stats_url = 'https://www.sports-reference.com' + team_href + str(season) + '.html'
    stats_req = requests.get(stats_url, headers = header)
    stats_soup = BeautifulSoup(stats_req.content, 'lxml')
    
    for table_type in ['passing','rushing_and_receiving','defense_and_fumbles','returns','kicking_and_punting']:
        try:
            table_soup = BeautifulSoup(stats_soup.find('div', {'id': 'all_' + table_type}).contents[-2], 'lxml')
        except:
            continue
        player_rows = table_soup.find('tbody').find_all('tr')
        for player_row in player_rows:
            try:
                player_loc = player_row.contents[1].contents[0].get('href')
                var = 'player_href'
            except:
                player_loc = player_row.contents[1].text
                var = 'player_name'
            if player_loc not in list(roster_df[var]):
                player_href = player_loc if var == 'player_href' else None
                player_name = player_row.contents[1].contents[0].text if (var == 'player_href') else player_row.contents[1].text
                row_list = [season,team_href,team_name,player_name,player_href]
                roster_df.loc[len(roster_df)] = row_list + [None] * (len(roster_df.columns) - 5)
            index = roster_df.loc[roster_df[var] == player_loc].iloc[0].name
            for stat in player_row.contents[2:]:
                roster_df.set_value(index,stat.get('data-stat'),float(0 if stat.text == '' else stat.text))
                
    stats_df = roster_df.fillna(0)
    return stats_df

def player_stats_scrape(min_season, current_year):    
    team_info_df = team_info_cfbr_scrape()
    
    try:
        player_stats_df = pd.read_csv(cfbr_folder_path + 'cfbr_player_stats.csv', header = 0)
    except:
        player_stats_df = pd.DataFrame(columns = ['season', 'team_schoolname'])
    
    for season in range(min_season, current_year + 1):
        for index, row in team_info_df.iterrows():
            print(season,row['team_schoolname'])
            if len(player_stats_df.loc[(player_stats_df['team_schoolname'] == row['team_schoolname']) & (player_stats_df['season'] == season),]) < 1:
                roster_df = roster_scrape(season, row['team_href'], row['team_schoolname'])
                try:
                    roster_df.iloc[0]
                except:
                    continue
                
                stats_df = stats_scrape(roster_df,row['team_schoolname'])
                    
                if len(player_stats_df) == 0:
                    player_stats_df = stats_df
                elif season == current_year:
                    player_stats_df = pd.concat([player_stats_df,roster_df])
                else:
                    player_stats_df = pd.concat([player_stats_df,stats_df])
                        
    player_stats_df.reset_index(drop = True).to_csv(cfbr_folder_path + 'cfbr_player_stats.csv', index = False)
    return player_stats_df.drop_duplicates()