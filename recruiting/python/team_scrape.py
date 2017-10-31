import pandas as pd

try:
    pd.read_csv('csv\\team_info_247.csv', header = 0)
except:    
    from bs4 import BeautifulSoup
    import requests
    import re
    
    abbrv_re = re.compile('((?<=https:\/\/).*(?=\.247))|((?<=college\/).*)')
    
    teams = pd.DataFrame(columns = ['name','href'])
    
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 \
        Safari/537.36'}
        
    url = 'https://247sports.com/league/NCAA-FB/Teams'
    req = requests.get(url, headers = header)
    soup = BeautifulSoup(req.content, 'lxml')
    
    confs = soup.find_all('li', {'class': 'team-block_itm'})
    for conf in confs:
        for team in conf.contents[1].contents[3:]:
            if team != ' ':
                href = team.contents[1].get('href')
                name = team.contents[1].text
                if href not in teams['href']:
                    teams.loc[len(teams),:] = [name,'https:' + href]
                                
    
    recruits = pd.read_csv('csv\\recruits.csv', header = 0)
    recruits.loc[:,'new_href'] = recruits.loc[:,'college_href']\
        .apply(lambda x: None if pd.isnull(x) else re.compile('.*(?=\/Season)').search(x).group(0))
    
    recruits = recruits.loc[pd.isnull(recruits['new_href']) == False,['college','new_href']]\
                         .drop_duplicates().sort_values(['college']).reset_index(drop = True)
                         
    team_info_247 = pd.merge(recruits, teams, how = 'left', left_on = 'new_href', right_on = 'href')
    team_info_247 = team_info_247.loc[:,['college','name','href']].reset_index(drop = True)
    team_info_247.loc[:,'short'] = team_info_247.loc[:,'href'].apply(lambda x: None if pd.isnull(x) else abbrv_re.search(x).group(0))
    team_info_247.loc[:,'id'] = team_info_247.index
    team_info_247.to_csv('csv\\team_info_247.csv', index = False)