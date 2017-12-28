import pandas as pd

match_folder_path = 'player_match\\csv\\'

rost_rct = pd.read_csv(match_folder_path + 'matched_stats.csv', header = 0)

summary_mean = pd.DataFrame(pd.pivot_table(rost_rct.loc[rost_rct['x247_rating'] != 0].groupby(['season','team_href','pos_group'])['x247_rating'].mean().reset_index(),
                                                index = ['season','team_href'], columns = 'pos_group', aggfunc = 'sum')).reset_index().fillna(0)
summary_mean.columns = list(summary_mean.columns.droplevel(1)[:2]) + list(summary_mean.columns.levels[1][:-1])

summary_sum = pd.DataFrame(pd.pivot_table(rost_rct.loc[rost_rct['x247_rating'] != 0].groupby(['season','team_href','pos_group'])['x247_rating'].sum().reset_index(),
                                                index = ['season','team_href'], columns = 'pos_group', aggfunc = 'sum')).reset_index().fillna(0)
summary_sum.columns = list(summary_sum.columns.droplevel(1)[:2]) + list(summary_sum.columns.levels[1][:-1])

summary = summary_mean[['season','team_href']]
for col in summary_mean.columns[2:]:
    if col in ['unknwn','kick']:
        continue
    summary[col + '_avg'] = summary_mean[col]

summary['total'] = summary_sum['dfront'] + summary_sum['kick'] + summary_sum['off_skill'] + summary_sum['oline'] + summary_sum['qb'] + summary_sum['secndry']
summary.sort_values(['season','total'], ascending = False).to_csv('team_ratings_summary.csv', index = False)