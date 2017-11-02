import pandas as pd
import re
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import matplotlib.pyplot as plt

rosters = pd.read_csv('csv\\rosters_cfbr.csv', header = 0)
recruits = pd.read_csv('csv\\recruits.csv', header = 0)

team_match = pd.read_csv('csv\\team_index.csv', header = 0)
#match_value = []
quest_match = []
for season in reversed(range(rosters['season'].min() - 4,rosters['season'].max() + 1)):
    for college in list(recruits.loc[recruits['season'] == season,'college'].drop_duplicates().sort_values()):
        team_name = team_match.loc[team_match['name_247'] == college,'name_cfbr'].iloc[0]
        roster_class = rosters.loc[(rosters['season'] == season) & (rosters['team'] == team_name)
            & (pd.isnull(rosters['class']) | (rosters['class'] == 'FR')),]
        roster_class.loc[:,'mod_name'] = roster_class.loc[:,'player'].apply(lambda x: re.sub('([\\t\'\.\,]+)|([^\x00-\x7F]+)','',x.lower()))

        if len(roster_class) > 0:
            recruit_class = recruits.loc[(recruits['season'] == season) & (recruits['college'] == college),]
            for index, row in recruit_class.iterrows():
#                if row['name'] == 'Nick Ghazarian':
#                    break
                fuzzymatches = process.extract(re.sub('([\\t\'\.\,]+)|([^\x00-\x7F]+)','',row['name'].lower()), list(roster_class['mod_name']), limit = 2)
#                match_value.append(fuzzymatches[0][1])
                if fuzzymatches[0][1] < 95 and fuzzymatches[0][1] > 89:
                    quest_match.append([index,row['name'],fuzzymatches[0]])
                print(index, fuzzymatches[0][1], fuzzymatches[0][1] - fuzzymatches[1][1])
    if
    
    if recruit[1]['name'].count('"') > 0:
        print(recruit[1]['name'])
    try:
        x.append(re.compile('[^0-9a-zA-Z\\t\'\.\,]+').search(recruit[1]['name'].lower()).group(0))
    except:
        continue
    re.sub('\t',' ','\t')
    recruit[1]['season']


re.sub('([\\t\'\.\,]+)|([^\x00-\x7F]+)','','deont\\xe9 sheffield'.lower())