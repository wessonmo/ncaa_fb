import pandas as pd
import time
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from espn.espn_team_info import team_info_espn
from x247_scrape.x247_scrape import team_info_247_scrape, recruits_247_scrape
from cfbr_scrape.cfbr_scrape import team_info_cfbr_scrape, player_stats_scrape

match_folder_path = 'player_match\\csv\\'

def team_match():
    team_espn = team_info_espn()
    team_cfbr = team_info_cfbr_scrape()
    team_247 = team_info_247_scrape()
    
    team_dict = {'espn_teamid': list(team_espn['espn_teamid']), 'espn_fullname': list(team_espn['team_fullname']),
                 'espn_schoolname': list(team_espn['team_schoolname']),'espn_abvname': list(team_espn['team_abvname']),
                 'x247_href': [None]*len(team_espn),'cfbr_href': [None]*len(team_espn)}
    team_index = pd.DataFrame.from_dict(team_dict)
    
    for threshold in [84,54]:
        rem_index = team_index.loc[pd.isnull(team_index['x247_href']),]
        for index, row in rem_index.iterrows():
            rem_247 = team_247.loc[~team_247['team_href'].isin(team_index['x247_href']),]
            fuzzymatch = process.extractOne(row['espn_fullname'], list(rem_247['team_fullname']),scorer=fuzz.token_sort_ratio)
            if (fuzzymatch[1] > threshold) and (row['espn_teamid'] != 2000):
                href = rem_247.loc[rem_247['team_fullname'] == fuzzymatch[0],'team_href'].iloc[0]
                team_index.set_value(index,'x247_href',href)
                
    for threshold, name_type in zip([92,69,95],['schoolname','fullname','abvname']):
        rem_index = team_index.loc[pd.isnull(team_index['cfbr_href']),]
        for index, row in rem_index.iterrows():
            rem_cfbr = team_cfbr.loc[~team_cfbr['team_href'].isin(team_index['cfbr_href']),]
            if len(rem_cfbr) > 0:
                search_name = row['espn_fullname'] if pd.isnull(row['espn_' + name_type]) else row['espn_' + name_type]
                fuzzymatch = process.extractOne(search_name, list(rem_cfbr.loc[pd.isnull(rem_cfbr['team_' + name_type]) == False,'team_' + name_type]),scorer=fuzz.token_sort_ratio)
                if fuzzymatch[1] > threshold:
                    href = rem_cfbr.loc[rem_cfbr['team_' + name_type] == fuzzymatch[0],'team_href'].iloc[0]
                    team_index.set_value(index,'cfbr_href',href)
            
    return team_index
    
def player_match(min_season):    
    
    current_date = [int(x) for x in time.strftime('%Y %m').split()]
    recruits_df = recruits_247_scrape(min_season, current_date)            
    rosters_df = player_stats_scrape(min_season,current_date)
    
    team_index = team_match()
    
    potential_match = pd.DataFrame(columns = ['team_href','recruit_href','fuzzymatches','match_type',])
    
    rosters_df['x247_href'] = None
    rosters_df['x247_rating'] = None
    
    for rct_season in reversed(range(int(recruits_df['season'].min()),int(recruits_df['season'].max() + 1))):
        seasons = range(rct_season,rct_season + 5)
        rct_teams = list(recruits_df.loc[(recruits_df['season'] == rct_season) & (recruits_df['team_href'].isin(team_index['x247_href'])),'team_href'].drop_duplicates())
        for rct_team in rct_teams:
            cfbr_teamhref = team_index.loc[team_index['x247_href'] == rct_team,'cfbr_href'].iloc[0]
            for threshold in [100,92,81]:
                matched = rosters_df.loc[(pd.isnull(rosters_df['x247_href']) == False) & (rosters_df['team_href'] == cfbr_teamhref),['x247_href','player_href']].drop_duplicates()
                rct_class = recruits_df.loc[(~recruits_df['recruit_href'].isin(matched['x247_href'])) & (recruits_df['season'] == rct_season) & (recruits_df['team_href'] == rct_team) & (recruits_df['team_href'] == rct_team)]
                rost_class = rosters_df.loc[(~rosters_df['player_href'].isin(matched['player_href'])) & (rosters_df['season'].isin(seasons)) & (rosters_df['team_href'] == cfbr_teamhref),['player_name','player_href']].drop_duplicates()
                if (len(rost_class) > 0) & (len(rost_class) > 0):
                    for index,row in rct_class.iterrows():
                        initial_match = process.extractOne(row['recruit_name'],rost_class['player_name'],scorer = fuzz.token_set_ratio)
                        if initial_match[1] >= threshold:
                            initial_href = rost_class.loc[rost_class['player_name'] == initial_match[0],'player_href'].iloc[0]
                            other_rost = list(rost_class.loc[rost_class['player_href'] != initial_href,'player_name'].drop_duplicates())
                            other_match = process.extractOne(row['recruit_name'],other_rost,scorer = fuzz.token_set_ratio)
                            if other_match[1] > (initial_match[1] - 8):
                                potential_match.loc[len(potential_match)] = [rct_team,row['recruit_href'],[initial_match,other_match],'secondary']
                            else:
                                rosters_df.loc[(rosters_df['player_name'] == initial_match[0]) & (rosters_df['season'].isin(seasons)) & (rosters_df['team_href'] == cfbr_teamhref),'x247_href'] = row['recruit_href']
                                rosters_df.loc[(rosters_df['player_name'] == initial_match[0]) & (rosters_df['season'].isin(seasons)) & (rosters_df['team_href'] == cfbr_teamhref),'x247_rating'] = row['rating']
                        elif (threshold == 81) & (initial_match[1] > 78):
                            initial_href = rost_class.loc[rost_class['player_name'] == initial_match[0],'player_href'].iloc[0]
                            other_rost = list(rost_class.loc[rost_class['player_href'] != initial_href,'player_name'].drop_duplicates())
                            other_match = process.extractOne(row['recruit_name'],other_rost,scorer = fuzz.token_set_ratio)
                            if other_match[1] < (initial_match[1] - 8):
                                rct_pos = row['pos_group']
                                initial_pos = rosters_df.loc[(rosters_df['season'].isin(seasons)) & (rosters_df['team_href'] == cfbr_teamhref) & (rosters_df['player_name'] == initial_match[0]),'pos_group'].iloc[0]
                                if rct_pos == initial_pos:
                                    rosters_df.loc[(rosters_df['player_name'] == initial_match[0]) & (rosters_df['season'].isin(seasons)) & (rosters_df['team_href'] == cfbr_teamhref),'x247_href'] = row['recruit_href']
                                    rosters_df.loc[(rosters_df['player_name'] == initial_match[0]) & (rosters_df['season'].isin(seasons)) & (rosters_df['team_href'] == cfbr_teamhref),'x247_rating'] = row['rating']
                                    potential_match.loc[len(potential_match)] = [rct_team,row['recruit_href'],initial_match,'pos_match']
                                else:
                                    potential_match.loc[len(potential_match)] = [rct_team,row['recruit_href'],initial_match,'primary']
                            else:
                                potential_match.loc[len(potential_match)] = [rct_team,row['recruit_href'],[initial_match,other_match],'both']
                        elif (threshold == 81) & (initial_match[1] > 75):
                            potential_match.loc[len(potential_match)] = [rct_team,row['recruit_href'],initial_match,'primary']
            
            print(seasons[0],rct_team)
                                               
    rosters_df['x247_rating'] = rosters_df['x247_rating'].fillna(0)
    rosters_df.to_csv(match_folder_path + 'matched_stats.csv', index = False)
    
    potential_match = potential_match.loc[~potential_match['recruit_href'].isin(rosters_df['x247_href'])]
    potential_match.to_csv(match_folder_path + 'potential_match.csv', index = False)
player_match(2009)