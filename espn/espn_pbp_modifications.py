import os
import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import re
import ujson
import csv

pbp_folder = 'E:\\college football\\pbp'

pbp = pd.read_csv(pbp_folder + '\\csv\\' + 'espn_pbp.csv', header = 0)
playtype_df = pd.read_csv('espn\\csv\\espn_playtype_group.csv', header = 0)
pbp = pd.merge(pbp,playtype_df,how = 'left', on = 'playtype')
pbp['fumble'] = pbp.text.apply(lambda x: 1 if re.compile('fumble', re.I).search(x) else 0)
pbp['interception'] = pbp.playtype.apply(lambda x: 1 if 'Interception' in x else 0)

for index, row in pbp.iterrows():
    if not pd.isnull(row.text):
        if len(re.findall('penalty',row.text.lower())) > 1:
            print(row.text)
            raise Exception
        prior, post = None, None
        if re.compile('penalty', re.I).search(row.text):
            pen_index = row.text.lower().index('penalty')
            
            if pen_index not in [0,1]:
                if re.compile('[A-Z]').search(row.text[pen_index - 2]):
                    prior = re.compile('[A-Z]+(( )*[A-Z])*(?= (penalty|PENALTY|Penalty))').search(row.text).group(0)
            if pen_index not in [len(row.text) - 9, len(row.text) - 8]:
                if re.compile('[A-Z]').search(row.text[pen_index + 2]):
                    post = re.compile('(?<=(penalty|PENALTY|Penalty) )[A-Z]+(( )*[A-Z])*').search(row.text).group(0)
                    
            if (prior != None) and (post != None):
                prior_match = process.extractOne()
                post_match = process.extractOne()
        

for index, row in pbp.loc[pd.isnull(pbp.playtype_group)].iterrows():
    if row.playtype == 'Safety':
        try:
            if re.compile(' pass | sack', re.I).search(row.text):
                pbp.set_value(index,'playtype_group','pass')
            elif re.compile('kickoff', re.I).search(row.text):
                pbp.set_value(index,'playtype_group','kickoff')
            elif re.compile(' punt', re.I).search(row.text):
                pbp.set_value(index,'playtype_group','punt')
            elif (re.compile(' penalty', re.I).search(row.text)) and (not re.compile('decline').search(row.text)):
                pbp.set_value(index,'playtype_group','penalty')
            else:
                pbp.set_value(index,'playtype_group','safety')
        except:
            pbp.set_value(index,'playtype_group','safety')
    elif 'Fumble' in row.playtype:
        try:
            if re.compile(' pass | sack', re.I).search(row.text):
                pbp.set_value(index,'playtype_group','pass')
            elif re.compile('kickoff', re.I).search(row.text):
                pbp.set_value(index,'playtype_group','kickoff')
            else:
                pbp.set_value(index,'playtype_group','fumble')
        except:
            pbp.set_value(index,'playtype_group','fumble')
        pbp.set_value(index,'fumble',1)

pbp.loc[pbp.playtype_group.isin(['pass','rush']),'dist'].value_counts().head(40)
pbp.loc[pbp.playtype_group.isin(['kickoff']),'yrdline'].value_counts()
        
for text in pbp.loc[(pbp.dist == 0) & (~pbp.playtype_group.isin(['kickoff','extra point','penalty','end half'])),'text'].head(25):
    print(text)
    
    pbp.loc[pbp.driveid == driveid].iloc[7].text


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