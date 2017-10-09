# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 20:00:18 2017

@author: wessonmo
"""

import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

with open('C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\recruits.csv', 'wb') as recruitcsv:
    recruitwriter = csv.writer(recruitcsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
    driver = webdriver.Firefox()
    for year in range(2005,2018):
        for page in range(1,100):
            url = "http://247sports.com/Season/" + str(year) + "-Football/CompositeRecruitRankings?ViewPath=~%2FViews%2FPlayerSportRanking%2F_SimpleSetForSeason.ascx&InstitutionGroup=HighSchool&Page=" + str(page)
            try:
                driver.get(url)
                
                if BeautifulSoup(str(BeautifulSoup(driver.page_source,"lxml").find_all("section", {"class": "clearfix main"})),"lxml").find_all("ul") != []:
                    recruits = BeautifulSoup(str(BeautifulSoup(driver.page_source,"lxml").find_all("section", {"class": "clearfix main"})),"lxml").find_all("ul")
            
                    for recruit in recruits:
                        name = recruit.contents[3].contents[4].contents[1].contents[1].contents[0].encode("utf-8")
                        href = recruit.contents[3].contents[4].contents[1].contents[1].get("href")
                        rtg = float(recruit.contents[3].contents[4].contents[3].contents[7].contents[6].encode("utf-8").strip())
                        try:
                            pos = recruit.contents[3].contents[4].contents[3].contents[1].contents[0].encode("utf-8")
                        except:
                            pos = "None"
                        try:
                            height = float(recruit.contents[3].contents[4].contents[3].contents[3].contents[0].encode("utf-8").split("-")[0])*12 + float(recruit.contents[3].contents[4].contents[3].contents[3].contents[0].encode("utf-8").split("-")[1])
                        except:
                            height = recruit.contents[3].contents[4].contents[3].contents[3].contents[0].encode("utf-8")
                        try:
                            weight = float(recruit.contents[3].contents[4].contents[3].contents[5].contents[0].encode("utf-8"))
                        except:
                            weight = recruit.contents[3].contents[4].contents[3].contents[5].contents[0].encode("utf-8")
                        try:
                            team = recruit.contents[5].contents[1].contents[0].get("alt")
                        except:
                            team = "None"
                        recruitwriter.writerow([year,name,href,rtg,pos,height,weight,team])
                else:
                    break
            except TimeoutException:
                driver.quit()
                driver = webdriver.Firefox()
                driver.get(url)
                
                if BeautifulSoup(str(BeautifulSoup(driver.page_source,"lxml").find_all("section", {"class": "clearfix main"})),"lxml").find_all("ul") != []:
                    recruits = BeautifulSoup(str(BeautifulSoup(driver.page_source,"lxml").find_all("section", {"class": "clearfix main"})),"lxml").find_all("ul")
            
                    for recruit in recruits:
                        name = recruit.contents[3].contents[4].contents[1].contents[1].contents[0].encode("utf-8")
                        href = recruit.contents[3].contents[4].contents[1].contents[1].get("href")
                        rtg = float(recruit.contents[3].contents[4].contents[3].contents[7].contents[6].encode("utf-8").strip())
                        try:
                            pos = recruit.contents[3].contents[4].contents[3].contents[1].contents[0].encode("utf-8")
                        except:
                            pos = "None"
                        try:
                            height = float(recruit.contents[3].contents[4].contents[3].contents[3].contents[0].encode("utf-8").split("-")[0])*12 + float(recruit.contents[3].contents[4].contents[3].contents[3].contents[0].encode("utf-8").split("-")[1])
                        except:
                            height = recruit.contents[3].contents[4].contents[3].contents[3].contents[0].encode("utf-8")
                        try:
                            weight = float(recruit.contents[3].contents[4].contents[3].contents[5].contents[0].encode("utf-8"))
                        except:
                            weight = recruit.contents[3].contents[4].contents[3].contents[5].contents[0].encode("utf-8")
                        try:
                            team = recruit.contents[5].contents[1].contents[0].get("alt")
                        except:
                            team = "None"
                        recruitwriter.writerow([year,name,href,rtg,pos,height,weight,team])
                else:
                    break
            
driver.quit()