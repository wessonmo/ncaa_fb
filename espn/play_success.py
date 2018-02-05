import pandas as pd
import numpy as np

pbp_folder = 'E:\\college football\\pbp'

pbp = pd.read_csv(pbp_folder + '\\csv\\' + 'espn_pbp.csv', header = 0)

for index, row in pbp.iterrows():
    if () & () & ():
        if row.down == 1:
            succ = 0.9718*np.exp(-0.031*row.dist)
        elif row.down == 2:
            succ = 0.9389*np.exp(-0.055*row.dist)
        elif row.down == 3:
            succ = 0.6256*np.exp(-0.071*row.dist)