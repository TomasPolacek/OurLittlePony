import random
import time
from datetime import datetime
from webbrowser import Chrome

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

import config
from scrapers import *

if __name__ == "__main__":

    web_link = "https://www.ifortuna.sk"
    # driver = webdriver.Chrome(ChromeDriverManager().install())
    driver = webdriver.Chrome("C:/Users/martin_ilavsky/Documents/chromedriver.exe")
    driver.get(web_link)
    time.sleep(5)
    sports_bar = driver.find_element(by=By.XPATH, value ='//*[@id="filterbox-ref-sport-tree"]').get_attribute('innerHTML')
    soup = BeautifulSoup(sports_bar)
    links = [l['href'] for l in soup.find_all('a', href=True)]
    random.shuffle(links)
    for l in links:
        if l.count('/') > 2 and 'm-atp-chall-sanremo-dvojhra' in l:
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
                try:
                    record = {}
                    bets = row.find_all('td')
                    for i,h in enumerate(headers):
                        to_ins = None
                        if i == 0:
                            to_ins = bets[i]['data-value']
                        elif 'dátum' in h:
                            ts = int(bets[i]['data-value']) / 1000
                            to_ins = datetime.fromtimestamp(ts)
                        else:
                            to_ins = bets[i].getText().strip()

                        record[headers[i]] = to_ins
                except Exception as e:
                    pass
                if len(record) != 0:
                    records.append(record)
            print(records)


