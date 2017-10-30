import csv
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

try:
    team_info_247 = pd.read_csv('csv\\team_info_247.csv', header = 0)
except:
    team_info_247 = pd.DataFrame(columns = ['name','href'])
    
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 \
        Safari/537.36'}
        
    url = 'https://247sports.com/league/NCAA-FB/Teams'
    req = requests.get(url, headers = header)
    soup = BeautifulSoup(req.content, 'lxml')
    
    confs = soup.find_all('li', {'class': 'team-block_itm'})
    for conf in confs:
        for team in conf.contents[1].contents[3:]:
            if team != ' ':
                href = team.contents[1].get('href')
                name = team.contents[1].text
                if href not in team_info_247['href']:
                    team_info_247.loc[len(team_info_247),:] = [name,'https:' + href]
                                
    
    recruits = pd.read_csv('csv\\recruits.csv', header = 0)
    recruits.loc[:,'new_href'] = recruits.loc[:,'college_href']\
        .apply(lambda x: None if pd.isnull(x) else re.compile('.*(?=\/Season)').search(x).group(0))
    
    recruits = recruits.loc[pd.isnull(recruits['new_href']) == False,['college','new_href']]\
                         .drop_duplicates().sort_values(['college']).reset_index(drop = True)
                         
    team_info_247 = pd.merge(recruits, team_info_247, how = 'left', left_on = 'new_href', right_on = 'href')
    team_info_247 = team_info_247.loc[:,['college','name','href']]
    team_info_247.to_csv('csv\\team_info_247.csv')

team_info_espn = pd.read_csv('csv\\team_info_espn.csv', header = 0)
team_info_espn = team_info_espn.loc[:,['team_id','full_name','nickname']].drop_duplicates()
team_info_espn.loc[:,'nickname'] = team_info_espn.loc[:,'nickname'].apply(lambda x: re.sub('\'','',x))
team_info_espn.loc[:,'full_name'] = team_info_espn.loc[:,'full_name'].apply(lambda x: re.sub('\'','',x))

#match_nums = []
#match_nums.append([fuzzy_match[1],row['name'],fuzzy_match[0]])
team_info_247.loc[:,'espn_id'] = None
for i in range(3):
    match_threshold = 89 if i < 1 else 100 if i > 1 else 77
    
    name_type_espn = 'full_name' if i < 2 else 'nickname'
    name_set_espn = list(team_info_espn.loc[~team_info_espn['team_id'].isin(team_info_247['espn_id']),name_type_espn])
    
    name_type_247 = 'name' if i < 2 else 'college'
    df_247 = team_info_247.loc[(pd.isnull(team_info_247[name_type_247]) == False) & pd.isnull(team_info_247['espn_id']),]
    
    for index, row in df_247.iterrows():
        fuzzy_match = process.extractOne(row[name_type_247], name_set_espn)
        if fuzzy_match[1] >= match_threshold:
            team_info_247.set_value(index,'espn_id',team_info_espn.loc[team_info_espn[name_type_espn] == fuzzy_match[0],'team_id'].iloc[0])
        else:
            print(i,row[name_type_247],fuzzy_match)

#
#
#for index, row in team_info_247.loc[pd.isnull(team_info_247['name']) == False,].iterrows():
#    fuzzy_match = process.extractOne(row['name'], team_info_espn['full_name'])
#    if fuzzy_match[1] >= 89:
#        team_info_247.set_value(index,'espn_id',team_info_espn.loc[team_info_espn['full_name'] == fuzzy_match[0],'team_id'].iloc[0])
#
#second_pass = list(team_info_espn.loc[~team_info_espn['team_id'].isin(team_info_247['espn_id']),'full_name'])
#for index, row in team_info_247.loc[(pd.isnull(team_info_247['name']) == False) & pd.isnull(team_info_247['espn_id']),].iterrows():
#    fuzzy_match = process.extractOne(row['name'], second_pass)
#    if fuzzy_match[1] >= 85:
#        print(fuzzy_match[1],row['name'],fuzzy_match[0])
#        team_info_247.set_value(index,'espn_id',team_info_espn.loc[team_info_espn['full_name'] == fuzzy_match[0],'team_id'].iloc[0])
#            
#third_pass = list(team_info_espn.loc[~team_info_espn['team_id'].isin(team_info_247['espn_id']),'nickname'])
#for index, row in team_info_247.loc[(pd.isnull(team_info_247['college']) == False) & pd.isnull(team_info_247['espn_id']),].iterrows():
#    fuzzy_match = process.extractOne(row['college'], third_pass)
#    if fuzzy_match[1] == 100:
#        print(fuzzy_match[1],row['college'],fuzzy_match[0])