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
    driver.get(web_link)
    time.sleep(5)
    sports_bar = driver.find_element(by=By.XPATH, value ='//*[@id="filterbox-ref-sport-tree"]').get_attribute('innerHTML')
    soup = BeautifulSoup(sports_bar)
    sports = soup.find_all("li")
    links = [l.find('a')['href'] for l in soup.find_all("li","item-sport")]
    ignore =  ['favorit-plus','zabava','duel','stane-sa-v-roku-2022']

    for l in links:
        to_ignore = False
        
        for i in ignore:
            if i in l:
                to_ignore = True
                continue
        if not to_ignore:
            print(l)
            driver.get(web_link + l)

            # Load all matches by scrolling to the bottom
            prev_height = 0
            curr_height = driver.execute_script("return document.body.scrollHeight")

            while prev_height + 10 < curr_height:
                prev_height = curr_height
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(10)
                curr_height = driver.execute_script("return document.body.scrollHeight")
                print(f"{prev_height} {curr_height}")

            table = driver.find_element(by=By.XPATH, value='//*[@id="sport-events-list-content"]').get_attribute('innerHTML')
            soup = BeautifulSoup(table)
            sub_tables = soup.find_all("section","competition-box")

            records = []
            for t in sub_tables:
                header = t.find("div","ui-box ui-box--no-margin").find("h2","breadcrumbed-title")
                sport = header.find_all("span","title-part")[0].getText().strip()
                league = header.find_all("span","title-part")[1].find('a').getText().strip()
                print(f"{sport} {league}")

                rows = t.find_all("tr")
                headers = []
                for h in rows[0].find_all("th"):
                    headers.append(h.getText().strip())
                if 'Zápas' not in headers[0]:
                            continue

                print(headers)
                
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
                        record[c.tab_col[0]] = "'" +  web_link + "'" #web_site
                        try:
                            record[c.tab_col[1]] = "'" + c.sport[sport] + "'" #sport_type
                        except:
                            print(f"New sport category detected: {sport}, add it to config later!")
                            record[c.tab_col[1]] = "'" + sport + "'" #sport_type

                        record[c.tab_col[2]] = "'" + league.replace("'","''") + "'"#sport_league


                        record[c.tab_col[3]] = "'" + record[headers[0]].split('-')[0].strip().replace("'","''") + "'" #team1
                        record[c.tab_col[4]] = "'" + record[headers[0]].split('-')[1].strip().replace("'","''") + "'" #team2
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
                        records.append(record)
            if records:
                psql.upsert(records)

    psql.close()




