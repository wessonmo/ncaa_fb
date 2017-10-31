import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz


team_info_espn = pd.read_csv('csv\\team_info_espn.csv', header = 0)
team_info_247 = pd.read_csv('csv\\team_info_247.csv', header = 0)

team_index = pd.DataFrame(columns = ['id_espn','id_247'])

for i,match_threshold in zip(range(8),[100,100,85,85,75,75,65,100]):
    name_type_espn = 'full' if i%2 == 0 else 'school'
    name_set_espn = list(team_info_espn.loc[~team_info_espn['id'].isin(list(team_index['id_espn'])),name_type_espn])
    
    name_type_247 = 'short' if i > 6 else 'name' if i%2 == 0 else 'college'
    df_247 = team_info_247.loc[(pd.isnull(team_info_247[name_type_247]) == False)
        & (~team_info_247['id'].isin(list(team_index['id_247']))),]
    
    for index, row in df_247.iterrows():
        fuzzy_match = process.extractOne(row[name_type_247], name_set_espn,scorer=fuzz.token_sort_ratio)
        if fuzzy_match[1] >= match_threshold:
            print(row[name_type_247],fuzzy_match)
            id_espn = team_info_espn.loc[team_info_espn[name_type_espn] == fuzzy_match[0],'id'].iloc[0]
            team_index.loc[len(team_index),] = [id_espn,row['id']]
            
team_index.sort_values('id_espn').reset_index(drop = True).to_csv('csv\\team_index.csv', index = False)