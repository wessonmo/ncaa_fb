# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 09:18:33 2017

@author: wessonmo
"""

import csv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time




url = "http://web1.ncaa.org/stats/StatsSrv/careersearch"

with open('C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\divs.csv', 'wb') as divcsv:
    divwriter = csv.writer(divcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
    
    driver = webdriver.Firefox()
    with open('C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\schools.csv', 'rb') as schoolcsv:
        schoolreader = csv.reader(schoolcsv, delimiter = ',', quotechar = '"')
        for school in schoolreader:
            school_id = school[0]
            
            driver.get(url)
            
            team = driver.find_element_by_name('teamSearch').find_element_by_name('searchOrg')
            year = driver.find_element_by_name('teamSearch').find_element_by_name('academicYear')
            sport = driver.find_element_by_name('teamSearch').find_element_by_name('searchSport')
            submit = driver.find_element_by_name('teamSearch').find_element_by_class_name('button')
            
            Select(team).select_by_value(str(school_id))
            Select(year).select_by_value("X")
            Select(sport).select_by_value("MFB")
            submit.click()        
            
            time.sleep(1)
            
            soup1 = BeautifulSoup(driver.page_source,"lxml").find_all("form", {"name":"results"})
            cols = len(BeautifulSoup(str(soup1),"lxml").find_all("td",width = True))
            
            if cols < 2:
                soup2 = BeautifulSoup(str(soup1),"lxml").find_all("table",width="100%",border=lambda x: x != "1")
                
                results = BeautifulSoup(str(soup2),"lxml").find_all("tr", bgcolor=lambda x: x != "#CCCCCC")
                for row in results:
                    season = row.contents[3].text.encode("utf-8")
                    division = row.contents[7].text.encode("utf-8")
                    divwriter.writerow([school_id,season,division])
            else:
                soup3 = BeautifulSoup(str(soup1),"lxml").find_all("td",width="30%")
                soup4 = BeautifulSoup(str(soup3),"lxml").find_all("table",width="100%",border=lambda x: x != "1")
                
                pages = len(BeautifulSoup(str(soup4),"lxml").find_all("tr", bgcolor=lambda x: x != "#CCCCCC"))
                for page in range(1,pages + 1):
                    soup1b = BeautifulSoup(str(soup1),"lxml").find_all("td",width="70%")
                    soup2 = BeautifulSoup(str(soup1b),"lxml").find_all("table",width="100%",border=lambda x: x != "1")
                    
                    results = BeautifulSoup(str(soup2),"lxml").find_all("tr", bgcolor=lambda x: x != "#CCCCCC")
                    for row in results:
                        season = row.contents[3].text.encode("utf-8")
                        division = row.contents[7].text.encode("utf-8")
                        divwriter.writerow([school_id,season,division])
                        
                    if page == pages:
                        pass
                    else:
                        driver.find_elements_by_xpath("(//a[starts-with(@href,'javascript:showNext')])")[int(page - 1)].click()
            
driver.quit()