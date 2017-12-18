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
          
remove_char = '([\\t\'\.\,]+)|([^\x00-\x7F]+)| (i+(v*)$|(j|s)r)'

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

    for index, row in team_info_df.iterrows():
        name_split = row['team_schoolname'].split()
        abv = ''
        if len(name_split) > 1:
            for split in name_split:
                abv += split[0]
        abv = abv + ' ' + re.sub(row['team_schoolname'] + ' ','',row['team_fullname'])
        team_info_df.set_value(index,'team_abvname', row['team_fullname'] if (len(name_split) < 2) else abv)
        
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
        player_name = re.sub(remove_char,'',player_name.lower())

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
                player_loc = re.sub(remove_char,'',player_loc.lower())
                var = 'player_name'
            if player_loc not in list(roster_df[var]):
                player_href = player_loc if var == 'player_href' else None
                player_name = re.sub(remove_char,'',player_row.contents[1].contents[0].text.lower()) if (var == 'player_href') else player_loc
                row_list = [season,team_href,team_name,player_name,player_href]
                roster_df.loc[len(roster_df)] = row_list + [None] * (len(roster_df.columns) - 5)
            index = roster_df.loc[roster_df[var] == player_loc].iloc[0].name
            for stat in player_row.contents[2:]:
                roster_df.set_value(index,stat.get('data-stat'),float(0 if stat.text == '' else stat.text))        
                
    stats_df = roster_df.drop_duplicates()
    stats_df['dedupe'] = 0
    return stats_df
    
def active_roster(min_season, current_year):
    try:
        active_roster_df = pd.read_csv(cfbr_folder_path + 'cfbr_active_rosters.csv', header = 0)
        
        modified_time = os.path.getmtime(cfbr_folder_path + 'cfbr_team_info.csv')
        current_time = calendar.timegm(time.gmtime())
        if float(current_time - modified_time)/(60*60*24) > 365:
            pass
        else:
            return active_roster_df
    except:
        pass
    
    active_roster_df = pd.DataFrame(columns = ['season','team_href'])
    
    school_re = re.compile('.*(?=[0-9]{4}\.html)')
    
    for season in range(min_season, current_year + 1):
        url = 'https://www.sports-reference.com/cfb/years/' + str(season) + '-standings.html'
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.content, 'lxml').find('table', {'id': 'standings'})
        
        teams = soup.find('tbody').find_all('tr', {'class': None})
        for team in teams:
            href = school_re.search(team.contents[1].contents[0].get('href')).group(0)
            active_roster_df.loc[len(active_roster_df)] = [season,href]
    
    active_roster_df.to_csv(cfbr_folder_path + 'cfbr_active_rosters.csv', index = False)
    return active_roster_df
    
def href_dedupe_process(seasons,team_href,href1,href2):
    print(seasons,team_href,href1,href2)
    temp_df = pd.DataFrame(columns = ['player_href','season','team_href','class','phys'])
    for href in [href1,href2]:
        player_url = 'https://www.sports-reference.com' + href
        player_req = requests.get(player_url, headers = header)
        player_soup = BeautifulSoup(player_req.content, 'lxml')
        
        try:
            phys = True if player_soup.find('div', {'id': 'info'}).contents[1].contents[1].contents[6].text.strip() != '' else False
        except:
            phys = False
        
        player_tables = player_soup.find_all('tbody')
        for table in player_tables:
            player_rows = table.find_all('tr')
            for player_row in player_rows:
                season = int(player_row.contents[0].text) if player_row.contents[0].text[0] != '*' else int(player_row.contents[0].text[1:])
                new_team_href = re.sub('[0-9]{4}\.html','',player_row.contents[1].contents[0].get('href'))
                class_ = None if player_row.contents[3].text == '' else player_row.contents[3].text
                temp_df.loc[len(temp_df)] = [href,season,new_team_href,class_,phys]
        
    temp_df = temp_df.loc[temp_df['season'].isin(seasons) & (temp_df['team_href'] == team_href)].drop_duplicates()
    href1_df = temp_df.loc[temp_df['player_href'] == href1]
    href2_df = temp_df.loc[temp_df['player_href'] == href2]
    if len(href1_df) == len(href2_df):
        href1_df = href1_df.loc[pd.isnull(href1_df['class']) == False]
        href2_df = href2_df.loc[pd.isnull(href2_df['class']) == False]
    
    if len(href1_df) > len(href2_df):
        return href1, href2
    elif len(href1_df) < len(href2_df):
        return href2, href1
    elif (True in href1_df['phys']) and (False in href2_df['phys']):
        return href1, href2
    elif (True in href2_df['phys']) and (False in href1_df['phys']):
        return href2, href1
    elif href1 in ['/cfb/players/robert-mcclain-iii-1.html','/cfb/players/melvin-stephenson-ii-1.html']:
        return href1, href2
        ############# pairs with same position, same names (excluding suffix) ###################################
    else:
        raise ValueError(href1,href2,'indistinguishable player_hrefs')
    
def player_stats_deduped(stats_df):
    for min_season in range(stats_df['season'].min(),stats_df['season'].max() - 3):
        seasons = range(min_season,min_season + 5)
        for team_href in list(stats_df.loc[stats_df['season'].isin(seasons) & (stats_df['dedupe'] == 0),'team_href'].drop_duplicates()):
            if (seasons[0] < 2013) and (team_href in ['/cfb/schools/minnesota/','/cfb/schools/oregon/']):
                # 3 hrefs
                continue
            players_df = stats_df.loc[stats_df['season'].isin(seasons) & (stats_df['team_href'] == team_href) & (pd.isnull(stats_df['player_href']) == False),['player_name','player_href']].drop_duplicates()
            for index, row in players_df.iterrows():
                name_list = [row['player_name']]
                fuzzymatch = process.extractOne(row['player_name'],list(players_df.loc[players_df['player_name'] != row['player_name'],'player_name'].drop_duplicates()))
                if fuzzymatch[1] > 90:
                    name_list += [fuzzymatch[0]]
                match_rows = players_df.loc[players_df['player_name'].isin(name_list),'player_href'].drop_duplicates()
                if len(match_rows) == 2:
                    href1 = match_rows.drop_duplicates().iloc[0]
                    if href1 == '/cfb/players/jamil-merrell-1.html':
                        continue
                    try:
                        href2 = match_rows.drop_duplicates().iloc[1]
                    except:
                        continue

                    winner,loser = href_dedupe_process(seasons,team_href,href1,href2)
                    
                    stats_df.loc[(stats_df['player_href'] == loser) | (stats_df['player_name'].isin(name_list) & stats_df['season'].isin(seasons) & (stats_df['team_href'] == team_href) & (pd.isnull(stats_df['player_href']) == False)),'player_href'] = winner
                elif len(match_rows) > 2:
#                    raise ValueError(seasons,team_href,'too many player hrefs')
                    continue
            stats_df.loc[stats_df['season'].isin(seasons) & (stats_df['dedupe'] == 0) & (stats_df['team_href'] == team_href),'dedupe'] = 1
    return stats_df
    
def player_stats_scrape(min_season, current_year):
    try:
        player_stats_df = pd.read_csv(cfbr_folder_path + 'cfbr_player_stats.csv', header = 0)
    except:
        player_stats_df = pd.DataFrame(columns = ['season', 'team_schoolname'])
        
    team_info_df = team_info_cfbr_scrape()
    active_rosters = active_roster(min_season, current_year)
    
    season = None
    for index, row in active_rosters.sort_values(['season','team_href']).iterrows():
        if int(row['season']) != season:
            season = int(row['season'])
            print(season)
        team_schoolname = team_info_df.loc[team_info_df['team_href'] == row['team_href'],'team_schoolname'].iloc[0]
        if len(player_stats_df.loc[(player_stats_df['team_schoolname'] == team_schoolname) & (player_stats_df['season'] == season),]) < 1:
            roster_df = roster_scrape(season, row['team_href'],team_schoolname)
            try:
                roster_df.iloc[0]
            except:
                continue
            
            stats_df = stats_scrape(roster_df,team_schoolname)
                
            if len(player_stats_df) == 0:
                player_stats_df = stats_df
            elif season == current_year:
                player_stats_df = pd.concat([player_stats_df,roster_df])
            else:
                player_stats_df = pd.concat([player_stats_df,stats_df])
    
    ignore_cols = ['season', 'team_href', 'team_schoolname', 'player_name', 'player_href', 'class', 'pos']
    player_stats_df.loc[:,player_stats_df.columns.difference(ignore_cols)] = player_stats_df.loc[:,player_stats_df.columns.difference(ignore_cols)].fillna(0)
    player_stats_df = player_stats_df.drop_duplicates().reset_index(drop = True)
    player_stats_df.to_csv(cfbr_folder_path + 'cfbr_player_stats.csv', index = False)
    player_stats_df = player_stats_deduped(player_stats_df).drop_duplicates().reset_index(drop = True)
    player_stats_df.to_csv(cfbr_folder_path + 'cfbr_player_stats.csv', index = False)
    return player_stats_df