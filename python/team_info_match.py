import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz


team_info_espn = pd.read_csv('csv\\team_info_espn.csv', header = 0)
team_info_247 = pd.read_csv('csv\\team_info_247.csv', header = 0)
team_info_cfbr = pd.read_csv('csv\\team_info_cfbr.csv', header = 0)
team_info_cfbr.loc[:,'full'] = team_info_cfbr.apply(lambda x: str(x['name'] + ' ' + x['nickname']), axis = 1)

team_index = pd.DataFrame(columns = ['id_espn','id_cfbr'])

team_index.loc[233,'id_espn'] = team_info_espn.loc[team_info_espn['school'] == 'VMI','id'].iloc[0]
for i,match_threshold in zip(range(7),[100,90,80,70,60,55,100]):
    name_type_espn = 'full' if i < 6 else 'school'
    name_set_espn = list(team_info_espn.loc[~team_info_espn['id'].isin(list(team_index['id_espn'])),name_type_espn])

    name_type_247 = 'name' if i < 6 else 'college'
    df_247 = team_info_247.loc[(pd.isnull(team_info_247[name_type_247]) == False)
        & (~team_info_247['id'].isin(list(team_index.index))),]
    
    for index, row in df_247.iterrows():
        fuzzy_matchespn = process.extractOne(row[name_type_247], name_set_espn,scorer=fuzz.token_sort_ratio)
        if fuzzy_matchespn[1] >= match_threshold:
            id_espn = team_info_espn.loc[team_info_espn[name_type_espn] == fuzzy_matchespn[0],'id'].iloc[0]
            team_index.set_value(index,'id_espn', id_espn)

team_index.loc[223,'id_cfbr'] = team_info_cfbr.loc[team_info_cfbr['full'] == 'Nevada-Las Vegas Rebels','id'].iloc[0]
for i,match_threshold in zip(range(6),[100,90,80,70,65,60]):
    name_type_cfbr = 'full'# if i < 4 else 'nickname'
    name_set_cfbr = list(team_info_cfbr.loc[~team_info_cfbr['id'].isin(list(team_index['id_cfbr'])),name_type_cfbr])
    
    name_type_247 = 'name'# if i < 6 else 'nickname'
    df_247 = team_info_247.loc[(pd.isnull(team_info_247[name_type_247]) == False)
        & (team_info_247['id'].isin(list(team_index.loc[pd.isnull(team_index['id_cfbr']),].index))),]

    for index, row in df_247.iterrows():
        fuzzy_matchcfbr = process.extractOne(row[name_type_247], name_set_cfbr,scorer=fuzz.token_sort_ratio)
        if fuzzy_matchcfbr[1] >= match_threshold:
            id_cfbr = team_info_cfbr.loc[team_info_cfbr[name_type_cfbr] == fuzzy_matchcfbr[0],'id'].iloc[0]
            team_index.set_value(index,'id_cfbr', id_cfbr)

team_index.loc[:,'id_247'] = team_index.index
team_index.sort_values('id_247').reset_index(drop = True).to_csv('csv\\team_index.csv', index = False)