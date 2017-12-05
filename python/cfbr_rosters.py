import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
from fuzzywuzzy import process

href_re = re.compile('(?<=schools\/).*(?=\/)')

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 \
    Safari/537.36'}
    
remove_char = '([\\t\'\.\,]+)|([^\x00-\x7F]+)| (i+(v*)$|(j|s)r)'

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
#    rosters = pd.DataFrame(columns = ['season', 'team', 'player', 'mod_name', 'starter', 'href', 'class', 'pos'])
    
    for season in range(2009,2018):
        for index, row in team_hrefs.iterrows():
            if len(rosters.loc[(rosters['team'] == row['name']) & (rosters['season'] == season),]) < 1:
                team = pd.DataFrame(columns = ['season', 'team', 'player', 'mod_name', 'starter', 'href', 'class', 'pos'])
                
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
                    raw_name = player.contents[0].text[:-1] if player.contents[0].text[-1] == '*' else player.contents[0].text
                    mod_name = re.sub(remove_char,'',raw_name.lower())
    
                    starter = 1 if player.contents[0].text[-1] == '*' else 0
                    try:
                        href = player.contents[0].contents[0].get('href')
                    except:
                        href = None
                    class_ = None if player.contents[1].text == '' else player.contents[1].text
                    pos = None if player.contents[2].text == '' else player.contents[2].text
        
                    team.loc[len(team),] = [season, row['name'], raw_name, mod_name, starter, href, class_, pos]
                
                for index2, row2 in team.loc[pd.isnull(team['href'])].iterrows():
                    match = process.extractOne(row2['mod_name'], team.loc[(pd.isnull(team['href']) == False),'mod_name'])
                    if match[1] > 90:
                        team.drop(index2, inplace = True)
                        
                team = team.reset_index(drop = True)
                        
                for index3, row3 in team.loc[pd.isnull(team['href']) == False].iterrows():
                    other_players = team.loc[(pd.isnull(team['href']) == False) & (team['href'] != row3['href']),]
                    match = process.extractOne(row3['mod_name'], list(other_players['mod_name']))
                    if match[1] > 90:
                        similar = team.loc[(team['href'] != row3['href']) & (team['mod_name'] == match[0])].iloc[0]
                        if (row3['pos'] == similar['pos']) | (match[1] == 100):
                            player1_url = 'https://www.sports-reference.com' + row3['href']
                            player1_req = requests.get(player1_url, headers = header)
                            player1_soup = BeautifulSoup(player1_req.content, 'lxml')
                            player1_years = len(player1_soup.find_all('th', {'data-stat': 'year_id'}))
                            
                            player2_url = 'https://www.sports-reference.com' + similar['href']
                            player2_req = requests.get(player2_url, headers = header)
                            player2_soup = BeautifulSoup(player2_req.content, 'lxml')
                            player2_years = len(player2_soup.find_all('th', {'data-stat': 'year_id'}))
                            
                            if player1_years >= player2_years:
                                try:
                                    team.drop(similar.name, inplace = True)
                                except:
                                    continue
                            else:
                                try:
                                    team.drop(index3, inplace = True)
                                except:
                                    continue
                                
#                rosters = pd.concat([rosters,team]).drop_duplicates().reset_index(drop = True)
                with open('my_csv.csv', 'ab') as f:
                    team.to_csv('csv\\rosters_cfbr.csv', index = False)
                print(season, team['team'].iloc[0])
                        
                        

                        
team_hrefs.loc[:,'id'] = team_hrefs.sort_values('name').reset_index(drop = True).index

team_hrefs.to_csv('csv\\team_info_cfbr.csv', index = False)
#rosters.drop_duplicates().to_csv('csv\\rosters_cfbr.csv', index = False)