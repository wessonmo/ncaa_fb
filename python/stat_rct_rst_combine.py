import pandas as pd

rosters = pd.read_csv('csv\\rosters_cfbr.csv', header = 0)
recruits = pd.read_csv('csv\\recruits.csv', header = 0)
stats = pd.read_csv('csv\\stats_cfbr.csv', header = 0)

player_match = pd.read_csv('csv\\player_match.csv', header = 0)

for index, row in player_match.iterrows():
    rct_rating = float(recruits.loc[(recruits['href'] == row['href_247']) & (recruits['instgroup'] == row['instgroup']),'rate'])
    if not pd.isnull(row['href_cfbr']):
        for index2, row2 in rosters.loc[rosters['href'] == row['href_cfbr']].iterrows():
            rosters.set_value(index2,'rct_rating',rct_rating)
    else:
        rosters.loc[(rosters['season'] == row['season']) & (rosters['team'] == row['team_cfbr']) & (rosters['player'] == row['player']),'rct_rating'] = rct_rating