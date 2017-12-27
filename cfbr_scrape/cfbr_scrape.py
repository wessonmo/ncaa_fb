import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import os
import calendar
import time
import csv
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

cfbr_folder_path = 'cfbr_scrape\\csv\\'
pos_group_df = pd.read_csv(cfbr_folder_path + 'cfbr_pos_group.csv', header = 0)

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
    for i in range(0,100):
        try:
            roster_req = requests.get(roster_url, headers = header)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(2)
            pass
    roster_soup = BeautifulSoup(roster_req.content, 'lxml')
    
    try:
        players = roster_soup.find('table', {'id': 'roster'}).find('tbody').find_all('tr', {'class': None})
    except:
        return
    for player in players:
        player_name = player.contents[0].text[:-1] if player.contents[0].text[-1] == '*' else player.contents[0].text.strip()
        if (' ' in player_name):
            player_name = re.sub(remove_char,'',player_name.lower())
        else:
            continue

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
    
def stats_scrape(roster_df,team_name,skip_stats):
    team_href = roster_df.iloc[0]['team_href']
    season = int(roster_df.iloc[0]['season'])

    stats_url = 'https://www.sports-reference.com' + team_href + str(season) + '.html'
    for i in range(0,100):
        try:
            stats_req = requests.get(stats_url, headers = header)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(2)
            pass
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
                player_loc = re.sub(remove_char,'',player_loc.lower().strip())
                var = 'player_name'
            if player_loc not in list(roster_df[var]):
                player_href = player_loc if var == 'player_href' else None
                player_name = re.sub(remove_char,'',player_row.contents[1].contents[0].text.lower().strip()) if (var == 'player_href') else player_loc
                if (' ' in player_name):
                    row_list = [season,team_href,team_name,player_name,player_href]
                    roster_df.loc[len(roster_df)] = row_list + [None] * (len(roster_df.columns) - 5)
                else:
                    continue
            index = roster_df.loc[roster_df[var] == player_loc].iloc[0].name
            for stat in player_row.contents[2:]:
                roster_df.set_value(index,stat.get('data-stat'),float(0 if ((stat.text == '') or (skip_stats == True)) else stat.text))
                
    stats_df = roster_df.drop_duplicates()
    stats_df['dedupe'] = 0
    return stats_df
    
def active_roster(min_season, current_date):
    try:
        active_roster_df = pd.read_csv(cfbr_folder_path + 'cfbr_active_rosters.csv', header = 0)
        
        modified_time = os.path.getmtime(cfbr_folder_path + 'cfbr_team_info.csv')
        roster_year = current_date[0] if (current_date[1] > 7) else current_date[0] - 1
        new_roster_time = calendar.timegm(time.strptime(str(roster_year)+str(8),'%Y%m'))
        current_time = calendar.timegm(time.gmtime())
        
        time_since_modify = current_time - modified_time
        time_since_roster = current_time - new_roster_time
        if time_since_modify > time_since_roster:
            pass
        else:
            return active_roster_df
    except:
        pass
    
    active_roster_df = pd.DataFrame(columns = ['season','team_href'])
    
    school_re = re.compile('.*(?=[0-9]{4}\.html)')
    
    for season in range(min_season, roster_year + 1):
        url = 'https://www.sports-reference.com/cfb/years/' + str(season) + '-standings.html'
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.content, 'lxml').find('table', {'id': 'standings'})
        
        teams = soup.find('tbody').find_all('tr')
        for team in teams:
            try:
                href = school_re.search(team.contents[1].contents[0].get('href')).group(0)
                active_roster_df.loc[len(active_roster_df)] = [season,href]
            except:
                continue
    
    active_roster_df.to_csv(cfbr_folder_path + 'cfbr_active_rosters.csv', index = False)
    return active_roster_df
    
def href_dedupe_process(seasons,team_href,match_list):
    temp_df = pd.DataFrame(columns = ['player_href','player_name','season','team_href','class','class_ind','pos_group_list','phys'])
    for href in match_list:
        if 'custom_href' in href:
            continue
        player_url = 'https://www.sports-reference.com' + href
        for i in range(0,100):
            try:
                player_req = requests.get(player_url, headers = header)
                break
            except requests.exceptions.ConnectionError:
                time.sleep(2)
                pass
        player_soup = BeautifulSoup(player_req.content, 'lxml')

        name = player_soup.find('div', {'id': 'info'}).contents[1].contents[1].contents[1].text.strip().lower()
        name = re.sub(remove_char,'',name)
        try:
            pos_list = re.sub(': ','',player_soup.find('div', {'id': 'info'}).contents[1].contents[1].contents[4].contents[2].strip()).split('/')
            pos_group_list = []
            for pos in pos_list:
                if pos in list(pos_group_df['pos']):
                    pos_group_list.append(pos_group_df.loc[pos_group_df['pos'] == pos,'pos_group'].iloc[0])
                else:
                    pos_group_list.append('unknwn')
        except:
            pos_group_list = ['unknwn']
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
                class_ind = 0 if class_ == None else 1
                temp_df.loc[len(temp_df)] = [href,name,season,new_team_href,class_,class_ind,pos_group_list,phys]
    
    rem_href = []
    for href in match_list:
        prev_list = []
        prev_class = None
        for index, row in temp_df.loc[temp_df['player_href'] == href].iterrows():
            if row['class'] in prev_list:
                if row['class'] == prev_class:
                    continue
                else:
                    rem_href.append(href)
            else:
                prev_list.append(row['class'])
                prev_class = row['class']
    temp_df = temp_df.loc[~temp_df['player_href'].isin(rem_href)]
                          
    for season in list(temp_df['season'].drop_duplicates()):
        temp_rows = temp_df.loc[temp_df['season'] == season]
        if len(temp_rows) > 2:
            raise ValueError('too many players in one season')
        elif len(temp_rows) == 2:
            pos_list1, pos_list2 = temp_rows['pos_group_list'].iloc[0], temp_rows['pos_group_list'].iloc[1]
            class1, class2 = temp_rows['class'].iloc[0], temp_rows['class'].iloc[1]
            if ((class1 != class2) & (None not in [class1,class2]))\
                | ((len(list(set(pos_list1) & set(pos_list2))) == 0) & ('unknwn' not in (pos_list1 + pos_list2))):
                raise ValueError('likely not same player')
            else:
                break
    
    
    if (len(temp_df['player_href'].drop_duplicates()) == 0):
        winner = match_list[-1]
        losers = list(set(match_list) - set([winner]))
        return winner, losers
    elif len(temp_df['player_href'].drop_duplicates()) == 1:
        winner = temp_df['player_href'].iloc[0]
        losers = list(set(match_list) - set([winner]))
        return winner, losers
    elif len(temp_df['player_href'].drop_duplicates()) > 2:
        if len(temp_df['player_name'].drop_duplicates()) == 2:
            names_hrefs = temp_df[['player_href','player_name']].drop_duplicates()
            names_hrefs = names_hrefs.groupby('player_name').agg(lambda x: x.nunique())
            dedup_href_name = names_hrefs.loc[names_hrefs['player_href'] == 2].index[0]
            
            temp_df2 = temp_df.loc[temp_df['player_name'] == dedup_href_name]
            href1 = temp_df2['player_href'].drop_duplicates().iloc[0]
            href1_df = temp_df2.loc[temp_df2['player_href'] == href1]
            href2 = temp_df2['player_href'].drop_duplicates().iloc[1]
            href2_df = temp_df2.loc[temp_df2['player_href'] == href2]
            
            if len(href1_df) > len(href2_df):
                winner = href1
                losers = list(set(match_list) - set([winner]))
            elif len(href1_df) < len(href2_df):
                winner = href2
                losers = list(set(match_list) - set([winner]))
            else:
                raise ValueError('too many player_hrefs2')
            return winner, losers
        elif len(temp_df['player_name'].drop_duplicates()) == 1:
            hrefs_w_class = temp_df.groupby('player_href').agg({"class_ind": lambda x: x.sum()})
            class_max = hrefs_w_class['class_ind'].max()
            
            if len(hrefs_w_class.loc[hrefs_w_class['class_ind'] == class_max]) == 1:
                winner = hrefs_w_class.loc[hrefs_w_class['class_ind'] == class_max].index[0]
                losers = list(set(match_list) - set([winner]))
                return winner, losers
            elif len(hrefs_w_class.loc[hrefs_w_class['class_ind'] == class_max]) == 2:
                href1 = hrefs_w_class.loc[hrefs_w_class['class_ind'] == class_max].index[0]
                href1_df = temp_df.loc[temp_df['player_href'] == href1]
                href1_name = href1_df['player_name'].iloc[0]
                
                href2 = hrefs_w_class.loc[hrefs_w_class['class_ind'] == class_max].index[1]
                href2_df = temp_df.loc[temp_df['player_href'] == href2]
                href2_name = href2_df['player_name'].iloc[0]
                pass
            else:
                raise ValueError('too many player_hrefs3')
        else:
            raise ValueError('too many player_hrefs')
    else:
        href1 = temp_df['player_href'].drop_duplicates().iloc[0]
        href1_df = temp_df.loc[temp_df['player_href'] == href1]
        href1_name = href1_df['player_name'].iloc[0]
        
        href2 = temp_df['player_href'].drop_duplicates().iloc[1]
        href2_df = temp_df.loc[temp_df['player_href'] == href2]
        href2_name = href2_df['player_name'].iloc[0]
        
    href1_pos_set = set(pos for sublist in href1_df['pos_group_list'] for pos in sublist)
    href2_pos_set = set(pos for sublist in href2_df['pos_group_list'] for pos in sublist)       
    if (len(list(set(href1_pos_set - set(['unknwn'])) & set(href2_pos_set - set(['unknwn'])))) == 0)\
        & (href1_pos_set != set(['unknwn'])) & (href2_pos_set != set(['unknwn'])):
        if href1_name == href2_name:
            raise ValueError('same names and mismatch pos_group')
        else:
            raise ValueError('mismatching names and pos_group')
    else:
        if (len(href1_df) == len(href2_df)) | (team_href not in list(href1_df['team_href'])) | (team_href not in list(href2_df['team_href'])):
            href1_df = href1_df.loc[href1_df['team_href'] == team_href]
            href2_df = href2_df.loc[href2_df['team_href'] == team_href]
        if len(href1_df) == len(href2_df):
            href1_df = href1_df.loc[pd.isnull(href1_df['class']) == False]
            href2_df = href2_df.loc[pd.isnull(href2_df['class']) == False]
        
        if len(href1_df) > len(href2_df):
            winner = href1
            losers = list(set(match_list) - set([href1]))
        elif len(href1_df) < len(href2_df):
            winner = href2
            losers = list(set(match_list) - set([href2]))
        elif (True in list(href1_df['phys'])) and (False in list(href2_df['phys'])):
            winner = href1
            losers = list(set(match_list) - set([href1]))
        elif (True in list(href2_df['phys'])) and (False in list(href1_df['phys'])):
            winner = href2
            losers = list(set(match_list) - set([href2]))
        else:
            winner = href2
            losers = list(set(match_list) - set([href2]))
        return winner, losers
    
def player_stats_deduped(stats_df):
    try:
        matches = pd.read_csv(cfbr_folder_path + 'cfbr_player_matches.csv', header = None)
        skip_list = [set(re.sub('\[|\]|\'|,','',x).split()) for x in matches.loc[pd.isnull(matches[3]) == False,0].head()]
    except:
        skip_list = []

    for min_season in range(stats_df['season'].min(),stats_df['season'].max() - 3):
        seasons = range(min_season,min_season + 5)
        print(seasons)
        for team_href in list(stats_df.loc[stats_df['season'].isin(seasons) & (stats_df['dedupe'] == 0),'team_href'].drop_duplicates()):
            print('\t' + team_href)
            players_df = stats_df.loc[stats_df['season'].isin(seasons) & (stats_df['team_href'] == team_href),['player_name','player_href']].drop_duplicates()
            for index, row in players_df.iterrows():
                name_list = [row['player_name']]
                fuzzymatches = process.extract(row['player_name'],list(players_df.loc[players_df['player_name'] != row['player_name'],'player_name'].drop_duplicates()),limit = 2,scorer = fuzz.token_set_ratio)
                for fuzzymatch in fuzzymatches:
                    if (fuzzymatch[1] >= 87):
                        name_list += [fuzzymatch[0]]
                match_list = list(players_df.loc[players_df['player_name'].isin(name_list),'player_href'].drop_duplicates())
                if (len(match_list) >= 2) and (set(match_list) not in skip_list):
                    try:
                        winner,losers = href_dedupe_process(seasons,team_href,match_list)
                        error_msg = None
                    except Exception as e:
                        error_msg = str(e)
                        skip_list.append(set(match_list))
                        
                    match = 'likely' if error_msg == None else 'unsure'
                    with open(cfbr_folder_path + 'cfbr_player_matches.csv', 'ab') as matchcsv:
                        matchwriter = csv.writer(matchcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                        matchwriter.writerow([match_list,fuzzymatch[1],match,error_msg])
                            
                    if error_msg != None:
                        continue
                    
                    stats_df.loc[(stats_df['season'].isin(seasons) & (stats_df['team_href'] == team_href)) & (stats_df['player_href'].isin(losers) | stats_df['player_name'].isin(name_list)),'player_href'] = winner
                    players_df.loc[players_df['player_href'].isin(losers),'player_href'] = winner
                elif (len(match_list) == 1) and (set(match_list) not in skip_list) and (name_list > 1):
                    stats_df.loc[stats_df['season'].isin(seasons) & (stats_df['team_href'] == team_href) & stats_df['player_name'].isin(name_list),'player_href'] = match_list[0]
                    players_df.loc[players_df['player_name'].isin(name_list),'player_href'] = match_list[0]
            stats_df.loc[stats_df['season'].isin(seasons) & (stats_df['dedupe'] == 0) & (stats_df['team_href'] == team_href),'dedupe'] = 1
    return stats_df
    
def player_stats_scrape(min_season, current_date):
    try:
        player_stats_df = pd.read_csv(cfbr_folder_path + 'cfbr_player_stats.csv', header = 0)
    except:
        player_stats_df = pd.DataFrame(columns = ['season', 'team_schoolname'])
        
    team_info_df = team_info_cfbr_scrape()
    active_rosters = active_roster(min_season, current_date)
    
    season = None
    for index, row in active_rosters.sort_values(['season','team_href']).iterrows():
        if int(row['season']) != season:
            season = int(row['season'])
            print(season)
        team_schoolname = team_info_df.loc[team_info_df['team_href'] == row['team_href'],'team_schoolname'].iloc[0]
        if len(player_stats_df.loc[(player_stats_df['team_schoolname'] == team_schoolname) & (player_stats_df['season'] == season),]) < 1:
            print('\t' + team_schoolname)
            roster_df = roster_scrape(season, row['team_href'],team_schoolname)
            try:
                roster_df.iloc[0]
            except:
                continue
            
            skip_stats = (season >= (current_date[0] - (1 if current_date[1] == 1 else 0)))
            stats_df = stats_scrape(roster_df,team_schoolname,skip_stats)
            
            if len(player_stats_df) == 0:
                player_stats_df = stats_df
            else:
                player_stats_df = pd.concat([stats_df,player_stats_df])
    
    player_stats_df['pos_group'] = pd.merge(player_stats_df[['pos']], pos_group_df, how = 'left', on = 'pos')['pos_group']
    
    player_stats_df.loc[:,player_stats_df.columns[7:-2]] = player_stats_df.loc[:,player_stats_df.columns[7:-2]].fillna(0)
    player_stats_df = player_stats_df.drop_duplicates().reset_index(drop = True)
    i, prev_team, prev_name = 1, None, None
    for index, row in player_stats_df.loc[pd.isnull(player_stats_df['player_href'])].sort_values(['player_name','team_href']).iterrows():
        if (row['team_href'] == prev_team) & (row['player_name'] == prev_name):
            pass
        elif (row['player_name'] == prev_name):
            i += 1
            prev_team = row['team_href']
        else:
            i, prev_team, prev_name = 1, row['team_href'], row['player_name']
        player_stats_df.set_value(index,'player_href','custom_href/' + re.sub(' ','-',row['player_name']) + '-' + str(i))
    player_stats_df.to_csv(cfbr_folder_path + 'cfbr_player_stats.csv', index = False)
    
    if len(player_stats_df.loc[player_stats_df['dedupe'] == 0]) > 0:
        dedupe_in = player_stats_df
        dedupe_out = player_stats_deduped(dedupe_in).drop_duplicates().reset_index(drop = True)
        dedupe_out.to_csv(cfbr_folder_path + 'cfbr_player_stats_dedupe.csv', index = False)
        
        player_stats_df['dedupe'] = 1
        player_stats_df.to_csv(cfbr_folder_path + 'cfbr_player_stats.csv', index = False)
        return dedupe_out
    else:
        return player_stats_df