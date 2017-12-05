import pandas as pd
import re
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import matplotlib.pyplot as plt

remove_char = '([\\t\'\.\,]+)|([^\x00-\x7F]+)| (i+(v*)$|(j|s)r)'

rosters = pd.read_csv('csv\\rosters_cfbr.csv', header = 0)
rosters.loc[:,'mod_name'] = rosters.loc[:,'player'].apply(lambda x: re.sub(remove_char,'',x.lower()))

recruits = pd.read_csv('csv\\recruits.csv', header = 0)
recruits.loc[:,'mod_name'] = recruits.loc[:,'name'].apply(lambda x: re.sub(remove_char,'',x.lower()))

team_match = pd.read_csv('csv\\team_index.csv', header = 0)

#for season in range(2009,2018):
#    for team in list(rosters['team'].drop_duplicates()):
#        roster = rosters.loc[(rosters['season'] == season) & (rosters['team'] == team) & (pd.isnull(rosters['href']) == False),]
#        for index, row in roster.iterrows():
#            other_players = roster.loc[(roster['href'] != row['href'])]
#            match = process.extractOne(row['player'], list(other_players['player']))
#            if match[1] > 90:
#                print(season,team,row['player'],match)
#                break


#rosters.loc[(rosters['team'] == 'Alabama') & (rosters['season'] == 2009)]

player_match = pd.DataFrame(columns = ['href_247', 'href_cfbr', 'team_cfbr', 'season', 'player'])
for season in reversed(range(rosters['season'].min() - 4,rosters['season'].max() + 1)):
    print(season)
    for college in list(recruits.loc[recruits['season'] == season,'college'].drop_duplicates().sort_values()):
        try:
            team_name = team_match.loc[team_match['name_247'] == college,'name_cfbr'].iloc[0]
        except:
            continue
        
        for i in range(4):
            for threshold in [100,93,87]:
                recruit_class = recruits.loc[(recruits['season'] == season) & (recruits['college'] == college) & (~recruits['href'].isin(player_match.loc[~pd.isnull(player_match['team_cfbr']),'href_247'])),]
                roster = rosters.loc[(rosters['season'] == season + i) & (rosters['team'] == team_name) & (~rosters['href'].isin(player_match.loc[player_match['team_cfbr'] == team_name,'href_cfbr'])),]
                if len(roster) > 0:
                    for index, row in recruit_class.iterrows():
                        fuzzymatch = process.extractOne(row['mod_name'], list(roster['mod_name']), scorer = fuzz.partial_ratio)
                        if fuzzymatch[1] >= threshold:
                            roster_player = roster.loc[roster['mod_name'] == fuzzymatch[0]].iloc[0]
                            if not pd.isnull(roster_player['href']):
                                player_match.loc[len(player_match)] = [row['href'],roster_player['href'],team_name,season,None]
                            else:
                                player_match.loc[len(player_match)] = [row['href'],None,team_name,season,roster_player['player']]
#                            if fuzzymatch[1] < 93:
#                                print(season,college,row['mod_name'],fuzzymatch)
                                  
pos_match = pd.DataFrame(columns = ['cfbr','rct','total'])
for index, row in player_match.loc[pd.isnull(player_match['player'])].iterrows():
    ros_pos = rosters.loc[rosters['href'] == row['href_cfbr'],'pos'].iloc[0]
    rct_pos = recruits.loc[recruits['href'] == row['href_247'],'pos'].iloc[0]
    if (pd.isnull(ros_pos) == False) and (pd.isnull(rct_pos) == False):
        total = pos_match.loc[(pos_match['cfbr'] == ros_pos) & (pos_match['rct'] == rct_pos)]
        if len(total) > 0:
            index = total.iloc[0].name
            pos_match.loc[index] = [ros_pos,rct_pos,total['total'].iloc[0] + 1]
        else:
            pos_match.loc[len(pos_match)] = [ros_pos,rct_pos,1]
    
for season in reversed(range(rosters['season'].min() - 4,rosters['season'].max() + 1)):
    print(season)
    for college in list(recruits.loc[recruits['season'] == season,'college'].drop_duplicates().sort_values()):
        try:
            team_name = team_match.loc[team_match['name_247'] == college,'name_cfbr'].iloc[0]
        except:
            continue
        
        for i in range(4):
            recruit_class = recruits.loc[(recruits['season'] == season) & (recruits['college'] == college) & (~recruits['href'].isin(player_match.loc[~pd.isnull(player_match['team_cfbr']),'href_247'])),]
            roster = rosters.loc[(rosters['season'] == season + i) & (rosters['team'] == team_name) & (~rosters['href'].isin(player_match.loc[player_match['team_cfbr'] == team_name,'href_cfbr'])),]
            if len(roster) > 0:
                for index, row in recruit_class.iterrows():
                    fuzzymatch = process.extractOne(row['mod_name'], list(roster['mod_name']), scorer = fuzz.partial_ratio)
                    fuz_last = fuzzymatch[0].split()[-1].split('-')# if (fuzzymatch[0].find('-') > -1) else [fuzzymatch[0].split()[-1]]
                    rct_last = row['mod_name'].split()[-1].split('-')
                    
                    roster_player = roster.loc[roster['mod_name'] == fuzzymatch[0]].iloc[0]
                    rost_pos = list(pos_match.loc[(pos_match['total'] >= 25) & (pos_match['cfbr'] == roster_player['pos']),'rct'])
                    
                    if ((fuz_last[0] in rct_last) or (rct_last[0] in fuz_last)) and (row['pos'] in rost_pos):
                        if not pd.isnull(roster_player['href']):
                            player_match.loc[len(player_match)] = [row['href'],roster_player['href'],team_name,season,None]
                        else:
                            player_match.loc[len(player_match)] = [row['href'],None,team_name,season,roster_player['player']]
                        print(row['mod_name'],fuzzymatch)
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
                                
        
        
        
        
        
        

            for class_ in ['non-juco','juco']:
                for match_atmpt,class2 in zip(range(4),['FR','SO','JR','SR']):
                    roster_class = rosters.loc[(rosters['season'] == season + match_atmpt) & (rosters['team'] == team_name)
                        & (~rosters['href'].isin(player_match.loc[player_match['team_cfbr'] == team_name,'href_cfbr'])),]
                    if class_ == 'non-juco':
                        roster_class = roster_class.loc[(roster_class['class'] == class2) | pd.isnull(rosters['class']),]
                    else:
                        roster_class = roster_class.loc[(roster_class['class'] != 'FR') | pd.isnull(rosters['class']),]
    
                    if len(roster_class) > 0:
                        recruit_class = recruits.loc[(recruits['season'] == season) & (recruits['college'] == college)
                                & (~recruits['href'].isin(player_match.loc[~pd.isnull(player_match['team_cfbr']),'href_247'])),]
                        if class_ == 'non-juco':
                             recruit_class = recruit_class.loc[recruits['instgroup'] != 'JuniorCollege',]
                        else:
                             recruit_class = recruit_class.loc[recruits['instgroup'] == 'JuniorCollege',]
    
                        for index, row in recruit_class.iterrows():
                            fuzzymatches = process.extractOne(row['mod_name'], list(roster_class['mod_name']))
                            if fuzzymatches[1] >= threshold:
                                if (threshold >= 87)\
                                    or ((((row['mod_name'].split()[-1] in fuzzymatches[0].split()[-1])
                                        or (fuzzymatches[0].split()[-1] in row['mod_name'].split()[-1]))
                                        if (row['mod_name'].count('-') > 0) or (fuzzymatches[0].count('-') > 0)
                                            else (fuzzymatches[0].split()[-1] == row['mod_name'].split()[-1]))
                                    and (fuzz.partial_ratio(row['mod_name'].split()[0], fuzzymatches[0].split()[0]) >= 50)):
                                        roster_matches = roster_class.loc[roster_class['mod_name'] == fuzzymatches[0],]
                                        if len(roster_matches.loc[~pd.isnull(roster_class['href'])]) == 1:
                                            player_match.loc[len(player_match),] = [row['href'],roster_matches['href'].iloc[0], team_name, None, None]
                                        elif len(roster_matches.loc[pd.isnull(roster_class['href'])]) == 1:
                                            player = roster_matches.loc[pd.isnull(roster_class['href']),'player'].iloc[0]
                                            player_match.loc[len(player_match),] = [row['href'],None, team_name, season, player]
                                        elif len(roster_matches.loc[pd.isnull(roster_class['href']) & ~pd.isnull(roster_class['class']),]) == 1:
                                            player = roster_matches.loc[pd.isnull(roster_class['href']),'player'].iloc[0]
                                            player_match.loc[len(player_match),] = [row['href'],None, team_name, season, player]
                                        elif len(roster_matches.loc[roster_matches['href'].str.contains('iii'),]) == 1:
                                            player = roster_matches.loc[roster_matches['href'].str.contains('iii'),'player'].iloc[0]
                                            player_match.loc[len(player_match),] = [row['href'],None, team_name, season, player]
                                        else:
                                            raise ValueError('wrong number of matches')
            
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
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