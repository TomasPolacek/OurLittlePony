import random
import time
from datetime import datetime
from smtplib import OLDSTYLE_AUTH
from webbrowser import Chrome

import config as c
from bs4 import BeautifulSoup
from db_handler import DB_Handler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


def scrape(opt:int = 0):
    # DB handler, connect to postgres DB
    psql = DB_Handler()

    # Delete old records
    psql.delete_older()

    web_link = "https://www.ifortuna.sk"
    driver = webdriver.Chrome(ChromeDriverManager().install())
    # driver = webdriver.Chrome("C:/Users/martin_ilavsky/Documents/chromedriver.exe")
    driver.get(web_link)
    time.sleep(5)
    sports_bar = driver.find_element(by=By.XPATH, value ='//*[@id="filterbox-ref-sport-tree"]').get_attribute('innerHTML')
    soup = BeautifulSoup(sports_bar)
    links = [l['href'] for l in soup.find_all('a', href=True)]
    random.shuffle(links)
    for l in links:
        if l.count('/') > 2:
            time.sleep(random.randint(5, 12))
            driver.get(web_link + l)
            time.sleep(2)
            table = driver.find_element(by=By.XPATH, value ='//*[@id="competition-list-content"]/section/div[2]/div/div[1]/table').get_attribute('innerHTML')
            soup = BeautifulSoup(table)
            rows = soup.find_all("tr")
            headers = []
            for h in rows[0].find_all("th"):
                headers.append(h.getText().strip())
            if 'Zápas' not in headers[0]:
                continue
            print (headers)
            print(f"LINK: {l}")
            records = []
            for row in rows[1:]:
                if 'STAV SI LIVE' in str(row):
                    continue
                record = {}
                try:
                    bets = row.find_all('td')
                    for i,h in enumerate(headers):
                        to_ins = None
                        if i == 0:
                            to_ins = bets[i]['data-value']
                        elif 'dátum' in h:
                            ts = int(bets[i]['data-value']) / 1000
                            to_ins = "'" + str(datetime.fromtimestamp(ts)) + "'"
                        elif 'viac' in h:
                            continue
                        else:
                            to_ins = str(abs(float(bets[i].getText().strip())))
                        record[headers[i]] = to_ins
                except Exception as e:
                    pass
                if len(record) != 0:
                    record[c.tab_col[0]] = "'fortuna'" #web_site
                    record[c.tab_col[1]] = "'" + l.split('/')[2] + "'" #sport_type
                    record[c.tab_col[2]] = "'" + l.split('/')[3] + "'" #sport_league


                    record[c.tab_col[3]] = "'" + record[headers[0]].split('-')[0].strip() + "'" #team1
                    record[c.tab_col[4]] = "'" + record[headers[0]].split('-')[1].strip() + "'" #team2
                    del record[headers[0]]

                    if 'viac' in record:
                        del record['viac']
 
                    def swap(new_key,old_key, d: dict):
                        if old_key in d:
                            d[new_key] = d[old_key]
                            del d[old_key]

                    swap(c.tab_col[5], '1', record) #odds_1
                    swap(c.tab_col[6], '2', record) #odds_2
                    swap(c.tab_col[7], '0', record)  #odds_x
                    swap(c.tab_col[7], 'Remíza', record) #odds_x
                    swap(c.tab_col[8], '10', record)  #odds_1x
                    swap(c.tab_col[9], '02', record)  #odds_2x
                    swap(c.tab_col[10], '12', record)  #odds_12
                    swap(c.tab_col[11], 'dátum', record)  #ts
                    print(record)
                    records.append(record)
            if records:
                psql.upsert(records)

    psql.close()




