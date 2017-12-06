import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

remove_char = '([\\t\'\.\,]+)|([^\x00-\x7F]+)| (i+(v*)$|(j|s)r)'

rosters = pd.read_csv('csv\\rosters_cfbr.csv', header = 0)
recruits = pd.read_csv('csv\\recruits.csv', header = 0)

team_match = pd.read_csv('csv\\team_index.csv', header = 0)

try:
    player_match = pd.read_csv('csv\\player_match.csv', header = 0)
except:
    player_match = pd.DataFrame(columns = ['href_247', 'href_cfbr', 'instgroup', 'team_cfbr', 'season', 'player'])
    
for season in reversed(range(rosters['season'].min() - 4,rosters['season'].max() + 1)):
    print(season)
    for college in list(recruits.loc[recruits['season'] == season,'college'].drop_duplicates().sort_values()):
        try:
            team_name = team_match.loc[team_match['name_247'] == college,'name_cfbr'].iloc[0]
        except:
            continue
        
        for i in range(4):
            for threshold in [100,93,87]:
                matched_players = player_match.loc[~pd.isnull(player_match['href_cfbr']),]
                recruit_class = recruits.loc[(recruits['season'] == season) & (recruits['college'] == college) & (~recruits['href'].isin(matched_players['href_247'])),]
                roster = rosters.loc[(rosters['season'] == season + i) & (rosters['team'] == team_name) & (~rosters['href'].isin(matched_players['href_cfbr'])),]
                if len(roster) > 0:
                    for index, row in recruit_class.iterrows():
                        if i == 0:
                            rost_class = [None,'FR'] if (row['instgroup'] == 'HighSchool') else [None,'FR','SO','JR','SR']
                        elif i == 1:
                            rost_class = [None,'FR','SO'] if (row['instgroup'] == 'HighSchool') else [None,'FR','SO','JR','SR']
                        elif i == 2:
                            rost_class = [None,'FR','SO','JR'] if (row['instgroup'] == 'HighSchool') else [None,'FR','SO','JR','SR']
                        else:
                            rost_class = [None,'SO','JR','SR']
                        
                        fuzzymatch = process.extractOne(row['mod_name'], list(roster['mod_name']), scorer = fuzz.partial_ratio)
                        if (fuzzymatch[1] >= threshold):
                            roster_player = roster.loc[roster['mod_name'] == fuzzymatch[0]].iloc[0]
                            if (roster_player['class'] in rost_class):
                                if not pd.isnull(roster_player['href']):
                                    player_match.loc[len(player_match)] = [row['href'],roster_player['href'],row['instgroup'],team_name,season,None]
                                else:
                                    player_match.loc[len(player_match)] = [row['href'],None,row['instgroup'],team_name,season,roster_player['player']]
#                                if fuzzymatch[1] < 93:
#                                    print(season,college,row['mod_name'],fuzzymatch)
                                  
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
            matched_players = player_match.loc[~pd.isnull(player_match['href_cfbr']),]
            recruit_class = recruits.loc[(recruits['season'] == season) & (recruits['college'] == college) & (~recruits['href'].isin(matched_players['href_247'])),]
            roster = rosters.loc[(rosters['season'] == season + i) & (rosters['team'] == team_name) & (~rosters['href'].isin(matched_players['href_cfbr'])),]
            if len(roster) > 0:
                for index, row in recruit_class.iterrows():
                    fuzzymatch = process.extractOne(row['mod_name'], list(roster['mod_name']), scorer = fuzz.partial_ratio)
                    fuz_last = fuzzymatch[0].split()[-1].split('-')# if (fuzzymatch[0].find('-') > -1) else [fuzzymatch[0].split()[-1]]
                    rct_last = row['mod_name'].split()[-1].split('-')
                    
                    roster_player = roster.loc[roster['mod_name'] == fuzzymatch[0]].iloc[0]

                    rost_pos = list(pos_match.loc[(pos_match['total'] >= 25) & (pos_match['cfbr'] == roster_player['pos']),'rct'])
                    if i == 0:
                        rost_class = [None,'FR'] if (row['instgroup'] == 'HighSchool') else [None,'FR','SO','JR','SR']
                    elif i == 1:
                        rost_class = [None,'FR','SO'] if (row['instgroup'] == 'HighSchool') else [None,'FR','SO','JR','SR']
                    elif i == 2:
                        rost_class = [None,'FR','SO','JR'] if (row['instgroup'] == 'HighSchool') else [None,'FR','SO','JR','SR']
                    else:
                        rost_class = [None,'SO','JR','SR']
                    
                    if ((fuz_last[0] in rct_last) or (rct_last[0] in fuz_last)) and (row['pos'] in rost_pos) and (roster_player['class'] in rost_class):
                        if not pd.isnull(roster_player['href']):
                            player_match.loc[len(player_match)] = [row['href'],roster_player['href'],row['instgroup'],team_name,season,None]
                        else:
                            player_match.loc[len(player_match)] = [row['href'],None,row['instgroup'],team_name,season,roster_player['player']]
#                        print(season,college,row['mod_name'],fuzzymatch)

#full_match_list = list(player_match.loc[pd.isnull(player_match['player']),'href_247'])
#partial_match_list = list(player_match.loc[~pd.isnull(player_match['player']),'href_247'])                            
#for season in range(rosters['season'].min() - 4,rosters['season'].max() + 1):
#    total = recruits.loc[recruits['season'] == season]
#    full_match = total.loc[total['href'].isin(full_match_list)]
#    temp_match = total.loc[total['href'].isin(partial_match_list)]
#    
#    print(str(season))
#    print('\tfull_match: ' + str(float(len(full_match))/float(len(total))))
#    print('\tpart_match: ' + str(float(len(full_match) + len(temp_match))/float(len(total))))


player_match.drop_duplicates().reset_index(drop = True).to_csv('csv\\player_match.csv', index = False)
