import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

href_re = re.compile('(?<=schools\/).*(?=\/)')

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 \
    Safari/537.36'}

try:
    team_hrefs = pd.read_csv('csv\\team_info_cfbr.csv', header = 0)
except:
    team_hrefs = pd.DataFrame(columns = ['name', 'href', 'nickname'])
        
    url = 'https://www.sports-reference.com/cfb/schools/'
    req = requests.get(url, headers = header)
    soup = BeautifulSoup(req.content, 'lxml')
    
    teams = soup.find('table', {'id': 'schools'}).find('tbody').find_all('tr', {'class': None})
    for team in teams:
        if int(team.contents[3].text) >= 2009:
            name = team.contents[1].text
            href = team.contents[1].contents[0].get('href')
            team_hrefs.loc[len(team_hrefs),] = [name, href, None]
                           
    team_hrefs.loc[:,'hrefname'] = team_hrefs.loc[:,'href'].apply(lambda x: re.sub('-',' ',href_re.search(x).group(0)))
    
try:
    rosters = pd.read_csv('csv\\rosters_cfbr.csv', header = 0)
except:
    rosters = pd.DataFrame(columns = ['season', 'team', 'player', 'starter', 'href', 'class', 'pos'])
    
    for season in range(2009,2018):
        for index, row in team_hrefs.iterrows():
            if len(rosters.loc[(rosters['team'] == row['name']) & (rosters['season'] == season),]) < 10:
                roster_url = 'https://www.sports-reference.com' + row['href'] + str(season) + '-roster.html'
                roster_req = requests.get(roster_url, headers = header)
                roster_soup = BeautifulSoup(roster_req.content, 'lxml')
                
                if pd.isnull(row['nickname']):
                    try:
                        nickname = roster_soup.find('h1', {'itemprop': 'name'}).contents[5].text
                        team_hrefs.set_value(index,'nickname',nickname)
                    except:
                        continue
                
                try:
                    players = roster_soup.find('table', {'id': 'roster'}).find('tbody').find_all('tr', {'class': None})
                except:
                    continue
                for player in players:
                    name = player.contents[0].text[:-1] if player.contents[0].text[-1] == '*' else player.contents[0].text
                    starter = 1 if player.contents[0].text[-1] == '*' else 0
                    try:
                        href = player.contents[0].contents[0].get('href')
                    except:
                        href = None
                    class_ = None if player.contents[1].text == '' else player.contents[1].text
                    pos = None if player.contents[2].text == '' else player.contents[2].text
        
                    rosters.loc[len(rosters),] = [season, row['name'], name, starter, href, class_, pos]
                        
team_hrefs.loc[:,'id'] = team_hrefs.sort_values('name').reset_index(drop = True).index

team_hrefs.to_csv('csv\\team_info_cfbr.csv', index = False)
rosters.drop_duplicates().to_csv('csv\\rosters_cfbr.csv', index = False)