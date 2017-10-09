# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 19:32:37 2017

@author: wessonmo
"""

import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import time
import os
import pandas as pd

url = "http://web1.ncaa.org/stats/StatsSrv/careersearch"

player_exist = os.path.exists("C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\players.csv")
game_exist = os.path.exists("C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\games.csv")
missing_exist = os.path.exists("C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\missing_games.csv")

try:
    if player_exist and game_exist and missing_exist:
        with open('C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\players.csv', 'ab') as playercsv:
            playerwriter = csv.writer(playercsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
            
            with open('C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\games.csv', 'ab') as gamecsv:
                gamewriter = csv.writer(gamecsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                
                with open('C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\missing_games.csv', 'ab') as misscsv:
                    misswriter = csv.writer(misscsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                    
                    driver = webdriver.PhantomJS("C:\\Users\\wessonmo\\Documents\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe")
                    schoolcsv = pd.read_csv("C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\schools.csv",header = None).sort_values(0).reset_index(drop=True)
                    last_team = pd.read_csv("C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\players.csv",header = None).sort_values([1,0]).reset_index(drop=True)[1].max()
                    
                    i = 0
                    for school_id in list(schoolcsv[schoolcsv[0] >= last_team][0]):
                        for year in range(2009,2018):
                            driver.get(url)
                            
                            team = driver.find_element_by_name('teamSearch').find_element_by_name('searchOrg')
                            season = driver.find_element_by_name('teamSearch').find_element_by_name('academicYear')
                            sport = driver.find_element_by_name('teamSearch').find_element_by_name('searchSport')
                            submit = driver.find_element_by_name('teamSearch').find_element_by_class_name('button')
                            
                            Select(team).select_by_value(str(school_id))
                            Select(season).select_by_value(str(year))
                            Select(sport).select_by_value("MFB")
                            submit.click()
                            
                            time.sleep(0.5)
                            
                            try:
                                WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH,"/html/body/form")))
                            except:
                                try:
                                    WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH,"/html/body/p[2]")))
                                except:
                                    time.sleep(5)
        
                            if "Your search returned 0 matches." not in str(BeautifulSoup(driver.page_source,"lxml")):
                                
                                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"(//*//a[starts-with(@href,'javascript:showTeamPage')])")))
                                driver.find_element_by_xpath("(//*//a[starts-with(@href,'javascript:showTeamPage')])").click()
                                
                                time.sleep(0.5)
                                
                                try:
                                    WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH,"/html/body/form/table[5]")))
                                except:
                                    try:
                                        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH,"/html/body/form/table[3]/tbody/tr[1]/td")))
                                    except:
                                        time.sleep(5)
                                
                                if "An unrecoverable system error occured.  Please try again later.  " not in str(BeautifulSoup(driver.page_source,"lxml")):
                                    
                                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/form/table[5]")))
                                    soup1 = BeautifulSoup(driver.page_source,"lxml").find_all("table", {"class":"statstable"})[1]
                                    players = BeautifulSoup(str(soup1),"lxml").find_all("tr")
                                    for player in players[3:]:
                                        name = player.contents[1].contents[1].contents[0].encode("utf-8")
                                        player_id = int(re.compile("[0-9]{1,}").search(player.contents[1].contents[1].get("href")).group(0))
                                        first = re.sub("\\.","",player.contents[1].contents[1].contents[0].encode("utf-8").split(", ")[0])
                                        last = player.contents[1].contents[1].contents[0].encode("utf-8").split(", ")[1]
                                        class_ = player.contents[3].contents[0].encode("utf-8").strip()
                                        position = player.contents[7].contents[0].encode("utf-8").strip()
                                        stats = []
                                        for j in range(11,121, 2):
                                            try:
                                                stats.append(float(player.contents[j].contents[0].encode("utf-8").strip()))
                                            except:
                                                stats.append(None)
                                        playerwriter.writerow([year,school_id,name,player_id,class_,first,last] + stats)
                                        
                                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/form/table[2]/tbody/tr/td[1]/table/tbody/tr[6]/td[2]/a")))
                                    driver.find_element_by_xpath("/html/body/form/table[2]/tbody/tr/td[1]/table/tbody/tr[6]/td[2]/a").click()
                                    
                                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/table/tbody/tr[3]/td/form/table[2]")))
                                    soup2 = BeautifulSoup(driver.page_source,"lxml").find_all("table", height = False)[2]
                                    results = BeautifulSoup(str(soup2),"lxml").find_all("tr", class_ = lambda x: x != "schoolColors")
                                    for row in results:
                                        try:
                                            opponent = int(re.compile("(?<=\().*(?=\))").search(str(row.contents[1]).encode("utf-8")).group())
                                        except:
                                            opponent = re.sub("\\n|%","",row.contents[1].text.encode("utf-8")).strip()
                                        date = row.contents[3].text.encode("utf-8")
                                        score = row.contents[5].text.encode("utf-8")
                                        location = str(row.contents[9].text.encode("utf-8")).strip()[0]
                                        city = row.contents[11].text.encode("utf-8")
                                        try:
                                            length = str(row.contents[13].text.encode("utf-8")).strip()
                                        except:
                                            length = "-"
                                        try:
                                            attend = int(re.sub(',', '',row.contents[15].text.encode("utf-8")))
                                        except:
                                            attend = None
                                        gamewriter.writerow([year,school_id,opponent,date,score,location,city,length,attend])
                                    misswriter.writerow([year,school_id,0])
                                else:
                                    misswriter.writerow([year,school_id,1])
                                
                                if i == 50:
                                    driver.quit()
                                    time.sleep(10)
                                    i = 0
                                else:
                                    i = i + 1
                            else:
                                break
    else:
        with open('C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\players.csv', 'wb') as playercsv:
            playerwriter = csv.writer(playercsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
            
            with open('C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\games.csv', 'wb') as gamecsv:
                gamewriter = csv.writer(gamecsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                
                with open('C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\missing_games.csv', 'wb') as misscsv:
                    misswriter = csv.writer(misscsv, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                    
                    driver = webdriver.PhantomJS("C:\\Users\\wessonmo\\Documents\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe")
                    schoolcsv = pd.read_csv("C:\\Users\\wessonmo\\Documents\\GitHub\\ncaa_football\\csv\\schools.csv",header = None).sort_values(0).reset_index(drop=True)
                    
                    i = 0
                    for school_id in list(schoolcsv[0]):
                        for year in range(2009,2018):
                            driver.get(url)
                            
                            team = driver.find_element_by_name('teamSearch').find_element_by_name('searchOrg')
                            season = driver.find_element_by_name('teamSearch').find_element_by_name('academicYear')
                            sport = driver.find_element_by_name('teamSearch').find_element_by_name('searchSport')
                            submit = driver.find_element_by_name('teamSearch').find_element_by_class_name('button')
                            
                            Select(team).select_by_value(str(school_id))
                            Select(season).select_by_value(str(year))
                            Select(sport).select_by_value("MFB")
                            submit.click()
                            
                            time.sleep(0.5)
                            
                            try:
                                WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH,"/html/body/form")))
                            except:
                                try:
                                    WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH,"/html/body/p[2]")))
                                except:
                                    time.sleep(5)
        
                            if "Your search returned 0 matches." not in str(BeautifulSoup(driver.page_source,"lxml")):
                                
                                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"(//*//a[starts-with(@href,'javascript:showTeamPage')])")))
                                driver.find_element_by_xpath("(//*//a[starts-with(@href,'javascript:showTeamPage')])").click()
                                
                                time.sleep(0.5)
                                
                                try:
                                    WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH,"/html/body/form/table[5]")))
                                except:
                                    try:
                                        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH,"/html/body/form/table[3]/tbody/tr[1]/td")))
                                    except:
                                        time.sleep(5)
                                
                                if "An unrecoverable system error occured.  Please try again later.  " not in str(BeautifulSoup(driver.page_source,"lxml")):
                                    
                                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/form/table[5]")))
                                    soup1 = BeautifulSoup(driver.page_source,"lxml").find_all("table", {"class":"statstable"})[1]
                                    players = BeautifulSoup(str(soup1),"lxml").find_all("tr")
                                    for player in players[3:]:
                                        name = player.contents[1].contents[1].contents[0].encode("utf-8")
                                        player_id = int(re.compile("[0-9]{1,}").search(player.contents[1].contents[1].get("href")).group(0))
                                        first = re.sub("\\.","",player.contents[1].contents[1].contents[0].encode("utf-8").split(", ")[0])
                                        last = player.contents[1].contents[1].contents[0].encode("utf-8").split(", ")[1]
                                        class_ = player.contents[3].contents[0].encode("utf-8").strip()
                                        position = player.contents[7].contents[0].encode("utf-8").strip()
                                        stats = []
                                        for j in range(11,121, 2):
                                            try:
                                                stats.append(float(player.contents[j].contents[0].encode("utf-8").strip()))
                                            except:
                                                stats.append(None)
                                        playerwriter.writerow([year,school_id,name,player_id,class_,first,last] + stats)
                                        
                                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/form/table[2]/tbody/tr/td[1]/table/tbody/tr[6]/td[2]/a")))
                                    driver.find_element_by_xpath("/html/body/form/table[2]/tbody/tr/td[1]/table/tbody/tr[6]/td[2]/a").click()
                                    
                                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,"/html/body/table/tbody/tr[3]/td/form/table[2]")))
                                    soup2 = BeautifulSoup(driver.page_source,"lxml").find_all("table", height = False)[2]
                                    results = BeautifulSoup(str(soup2),"lxml").find_all("tr", class_ = lambda x: x != "schoolColors")
                                    for row in results:
                                        try:
                                            opponent = int(re.compile("(?<=\().*(?=\))").search(str(row.contents[1]).encode("utf-8")).group())
                                        except:
                                            opponent = re.sub("\\n|%","",row.contents[1].text.encode("utf-8")).strip()
                                        date = row.contents[3].text.encode("utf-8")
                                        score = row.contents[5].text.encode("utf-8")
                                        location = str(row.contents[9].text.encode("utf-8")).strip()[0]
                                        city = row.contents[11].text.encode("utf-8")
                                        try:
                                            length = str(row.contents[13].text.encode("utf-8")).strip()
                                        except:
                                            length = "-"
                                        try:
                                            attend = int(re.sub(',', '',row.contents[15].text.encode("utf-8")))
                                        except:
                                            attend = None
                                        gamewriter.writerow([year,school_id,opponent,date,score,location,city,length,attend])
                                    misswriter.writerow([year,school_id,0])
                                else:
                                    misswriter.writerow([year,school_id,1])
                                
                                if i == 50:
                                    driver.quit()
                                    time.sleep(10)
                                    i = 0
                                else:
                                    i = i + 1
                            else:
                                break
except Exception,e:
    print(Exception,e)


driver.quit()