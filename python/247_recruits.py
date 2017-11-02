import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 \
    Safari/537.36'}
    
try:
    scraped = pd.read_csv('csv\\recruits.csv', header = 0)
except:
    headers = ['season','instgroup','page','rk','name','href','school','city','state','pos','ht','wt','rate','stars','rct_srvs','college',
               'college_href']
    scraped = pd.DataFrame(columns = headers)
       
for season in range(2000,2019):
    for instgroup in ['HighSchool','JuniorCollege','PrepSchool']:
        for page in range(1,100):
            if page not in list(scraped.loc[(scraped['season'] == season) & (scraped['instgroup'] == instgroup),'page'].drop_duplicates()):
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
                            try:
                                college = recruit.contents[8].contents[1].contents[0].get('title')
                                college_href = recruit.contents[8].contents[1].get('href')
                            except:
                                continue
                            name = re.sub(r'[^\x00-\x7F]+','',recruit.contents[6].contents[1].contents[1].text)
                            rk = recruit.contents[1].contents[1].text.strip()
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
                            
                        scraped.loc[len(scraped),] = [season,instgroup,page,rk,name,href,school,city,state,pos,ht,wt,rate,stars,rct_srvs,
                                                        college,college_href]
                            
scraped.drop_duplicates().to_csv('csv\\recruits.csv', index = False)