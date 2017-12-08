import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import os
import calendar
import time

x247_folder_path = 'x247_scrape\\csv\\'

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'}

def team_info_247_scrape():
    try:
        team_info_df = pd.read_csv(x247_folder_path + '247_team_info.csv', header = 0)
        
        modified_time = os.path.getmtime(x247_folder_path + '247_team_info.csv')
        current_time = calendar.timegm(time.gmtime())
        if float(current_time - modified_time)/(60*60*24) > 365:
            pass
        else:
            return team_info_df
    except:
        pass
    
    team_info_df = pd.DataFrame(columns = ['team_fullname','team_href','team_hrefname'])
    
    abbrv_re = re.compile('((?<=\/\/).*(?=\.247))|((?<=college\/).*)')
        
    url = 'https://247sports.com/league/NCAA-FB/Teams'
    req = requests.get(url, headers = header)
    soup = BeautifulSoup(req.content, 'lxml')
    
    confs = soup.find_all('li', {'class': 'team-block_itm'})
    for conf in confs:
        for team in conf.contents[1].contents[3:]:
            if team != ' ':
                name = team.contents[1].text
                if name == 'Albany':
                    name = 'Albany Great Danes'
                elif name == 'Virginia Military Institute Keydets':
                    name = 'VMI Keydets'
                
                href = team.contents[1].get('href')
                href_name = href if abbrv_re.search(href) == None else abbrv_re.search(href).group(0)
                if href not in team_info_df['team_href']:
                    team_info_df.loc[len(team_info_df)] = [name,'https:' + href,href_name]
                                     
    team_info_df.to_csv(x247_folder_path + '247_team_info.csv', index = False)
    return team_info_df

def recruits_247_scrape(min_season, latest_class):
    try:
        recruits_df = pd.read_csv(x247_folder_path + '247_recruits.csv', header = 0)
    except:
        recruits_df = pd.DataFrame(columns = ['season','instgroup','page'])
        
    for season in range(min_season - 4, latest_class + 1):
        for instgroup in ['HighSchool','JuniorCollege','PrepSchool']:
            for page in range(1,100):
                if page not in list(recruits_df.loc[(recruits_df['season'] == season) & (recruits_df['instgroup'] == instgroup),'page'].drop_duplicates()):
                    url = 'https://247sports.com/Season/' + str(season) + '-Football/CompositeRecruitRankings?ViewPath=~%2FViews%2F247Sports%2FPlayerSportRanking%2F_SimpleSetForSeason.ascx&InstitutionGroup=' + instgroup + '&Page=' + str(page)
                    req = requests.get(url, headers = header)
                    soup = BeautifulSoup(req.content, 'lxml').find('section', {'id': 'page-content'})
                    
                    recruits = soup.contents
                    if len(recruits) < 2:
                        break
                    else:
                        for recruit in recruits:
                            if recruit == ' ':
                                continue
                            elif recruit.contents[1].get('data-js') == 'showmore':
                                continue
                            elif recruit.contents[1].get('class')[0] != 'dfp_ad':
                                name = re.sub(r'[^\x00-\x7F]+','',recruit.contents[6].contents[1].contents[1].text)
                                
                                if name == ' ':
                                    continue
                                try:
                                    college = recruit.contents[8].contents[1].contents[0].get('title')
                                    college_href = recruit.contents[8].contents[1].get('href')
                                except:
                                    continue
                                href = recruit.contents[6].contents[1].contents[1].get('href')
                                origin = re.sub(r'[^\x00-\x7F]+','',recruit.contents[6].contents[1].contents[3].text.strip())
                                paren = origin.count('(')
                                school = origin.split(' (')[0]
                                try:
                                    city = origin.split(' (')[paren].split(', ')[0]
                                    state = origin.split(' (')[paren].split(', ')[1][:-1]
                                except:
                                    city,state = None,None
                                pos = recruit.contents[6].contents[3].contents[1].text
                                ht = recruit.contents[6].contents[3].contents[3].text
                                wt = recruit.contents[6].contents[3].contents[5].text
                                rate = recruit.contents[6].contents[5].contents[7].text
                                stars = len(recruit.contents[6].contents[5].find_all('span', {'class': 'icon-starsolid yellow'}))
                                rct_srvs = len(recruit.contents[6].contents[5].contents[9].find_all('span', {'class': 'yellow'}))
                                
                            recruits_df.loc[len(recruits_df)] = [season,instgroup,page,name,href,school,city,state,pos,ht,wt,rate,stars,
                                                                rct_srvs,college,college_href]
                                                            
    recruits_df.drop_duplicates().to_csv(x247_folder_path + '247_recruits.csv', index = False)
    return recruits_df.drop_duplicates()