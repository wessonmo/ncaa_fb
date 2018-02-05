import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import numpy as np

pbp_folder = 'E:\\college football\\pbp'

pbp = pd.read_csv(pbp_folder + '\\csv\\' + 'espn_pbp.csv', header = 0)
#pbp.drop_duplicates().reset_index(drop = True).to_csv(pbp_folder + '\\csv\\' + 'espn_pbp.csv', index = False)
#playtype_df = pd.read_csv('espn\\csv\\espn_playtype_group.csv', header = 0)
#pbp = pd.merge(pbp,playtype_df,how = 'left', on = 'playtype')
pbp = pbp.drop_duplicates(pbp.columns.difference(['playid'])).reset_index(drop = True)

success = pbp.loc[~pbp.playtype.isin(['kickoff','extra point'])]
success.loc[:,'sub_driveid'] = (success.down == 1).cumsum()

final_play = success.groupby('sub_driveid', as_index = False).last()
final_play_skip = list(final_play.loc[(final_play.down != 4) & ((final_play.offid != final_play.endid) | final_play.playtype.isin(['punt','field goal']) | (final_play.scoringtype == 'safety')),'sub_driveid'].drop_duplicates())

first_play = success.groupby('sub_driveid', as_index = False).first()
first_play_skip = list(first_play.loc[first_play.period.isin([2,4]) & (first_play.clock <= 600) & (first_play.yrd2end > 20),'sub_driveid'].drop_duplicates())

other_skip = list(success.loc[(success.dist < 0) & (success.down != 4),'sub_driveid'].drop_duplicates())

skip_ids = set(first_play_skip + final_play_skip + other_skip)
                          
final_play_succ = final_play.loc[~final_play.sub_driveid.isin(skip_ids)]
final_play_succ['success'] = np.where(final_play_succ.down != 4, 1, 0)

success = pd.merge(success.loc[~success.sub_driveid.isin(skip_ids)], final_play_succ[['sub_driveid','success']], how = 'left', on = 'sub_driveid')
#success[['driveid','sub_driveid','down','playtype','text','success']].head(15)


success.loc[success.down.isin(range(1,4))].groupby(['down','dist'], as_index = False)['success'].agg(['count', np.mean, np.std]).reset_index().to_csv('play_success.csv')