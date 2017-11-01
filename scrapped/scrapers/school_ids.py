# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 15:39:38 2017

@author: wessonmo
"""

import requests
from bs4 import BeautifulSoup
import csv

url = "http://web1.ncaa.org/stats/StatsSrv/careersearch"

schools = BeautifulSoup(str(BeautifulSoup((requests.get(url).content),"lxml").find_all("select",{"name": "searchOrg"})),"lxml").find_all("option",value=lambda x: x != "X")

with open('C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\schools.csv', 'wb') as schoolcsv:
    schoolwriter = csv.writer(schoolcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
    
    for school in schools:
        schoolwriter.writerow([int(school['value']),school.contents[0].encode("utf-8")])