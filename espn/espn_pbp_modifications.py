import os
import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import re
import ujson
import csv

pbp_folder = 'E:\\college football\\pbp'

pbp = pd.read_csv(pbp_folder + '\\csv\\' + 'espn_pbp.csv', header = 0)
#playtype_df = pd.read_csv('espn\\csv\\espn_playtype_group.csv', header = 0)
#pbp = pd.merge(pbp,playtype_df,how = 'left', on = 'playtype')

drives = list(pbp.driveid.drop_duplicates())
for drive in drives:
    plays = pbp.loc[pbp.driveid == drive]


pbp.loc[(pbp.playtype == 'pass') & (pbp.fumble == 1)].head()

pbp.playtype.value_counts()
pbp.loc[pbp.fumble == 1].playtype.value_counts()
float(499617)/float(540668)
float(5877)/float(6832)

for index, row in pbp.iterrows():
    drive_plays = pbp.loc[pbp.driveid == row.driveid]
    if len(drive_plays) > 1:
        for index2, row2 in drive_plays.iterrows():
            fourth_down = drive_plays.loc[(drive_plays.playid > row2.playid) & (drive_plays.down == 4),'playid'].min()
            goal_to_go = 
            drive_plays.loc[(drive_plays.playid > row2.playid) & ()]
            break
    else:


pbp.loc[(pbp.yrdline < 5) & pbp.playtype.isin(['Pass','Pass Completion','Pass Incompletion','Pass Reception','Rush','Rushing Touchdown','Passing Touchdown'])].head()

safe_words = re.compile('sack|pass|kickoff')
#for index, row in pbp.loc[pbp.playtype.isin(['Fumble Recovery (Opponent)','Fumble Recovery (Own)','Fumble Return Touchdown'])].head(15).iterrows():
for index, row in pbp.loc[pbp.playtype.isin(['Fumble Recovery (Opponent)','Fumble Recovery (Own)','Fumble Return Touchdown'])].iterrows():
    if re.compile('punt').search(row.text):
        print(row.text)