import pandas as pd
from bs4 import BeautifulSoup
import requests

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 \
    Safari/537.36'}

team_hrefs = pd.read_csv('csv\\team_info_cfbr.csv', header = 0)
rosters = pd.read_csv('csv\\rosters_cfbr.csv', header = 0)
    
try:
    stats = pd.read_csv('csv\\stats_cfbr.csv', header = 0)
    hdr = False
except:
    stats = pd.DataFrame(columns = ['team_href','season'])
    hdr = True
    

for season in range(2009,2018):
    print(season)
    for index, row in team_hrefs.iterrows():
        if len(stats.loc[(stats['team_href'] == row['href']) & (stats['season'] == season),]) < 1:
            team_stat = pd.DataFrame(rosters.loc[(rosters['season'] == season) & (rosters['team'] == row['name']) & (~pd.isnull(rosters['href'])),'href'].drop_duplicates().reset_index(drop = True))
            team_stat['season'] = season
            team_stat['team_href'] = row['href']
            
            stats_url = 'https://www.sports-reference.com' + row['href'] + str(season) + '.html'
            stats_req = requests.get(stats_url, headers = header)
            stats_soup = BeautifulSoup(stats_req.content, 'lxml')
            
            for table_type in ['passing','rushing_and_receiving','defense_and_fumbles','returns','kicking_and_punting']:
                try:
                    table_soup = BeautifulSoup(stats_soup.find('div', {'id': 'all_' + table_type}).contents[-2], 'lxml')
                except:
                    continue
                player_rows = table_soup.find('tbody').find_all('tr')
                for player_row in player_rows:
                    player_href = player_row.contents[1].contents[0].get('href')
                    if player_href not in list(team_stat['href']):
                        row_list = [player_href,season,row['href']]
                        team_stat.loc[len(team_stat)] = row_list + [None] * (len(team_stat.columns) - 3)
                    index = team_stat.loc[team_stat['href'] == player_href].iloc[0].name
                    for stat in player_row.contents[2:]:
                        team_stat.set_value(index,stat.get('data-stat'),float(0 if stat.text == '' else stat.text))
                        
            team_stat = team_stat.fillna(0)

            with open('csv\\stats_cfbr.csv', 'ab') as f:
                team_stat.to_csv(f, index = False, header = hdr)
                
            hdr = False