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
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(web_link)
    time.sleep(5)
    sports_bar = driver.find_element(by=By.XPATH, value ='//*[@id="filterbox-ref-sport-tree"]').get_attribute('innerHTML')
    soup = BeautifulSoup(sports_bar)
    links = [l['href'] for l in soup.find_all('a', href=True)]
    random.shuffle(links)
    for l in links:
        if 'futbal' in l:
            time.sleep(random.randint(5, 12))
            driver.get(web_link + l)
            table = driver.find_element(by=By.XPATH, value ='//*[@id="competition-list-content"]/section/div[2]/div/div[1]/table').get_attribute('innerHTML')
            soup = BeautifulSoup(table)
            records = []
            for row in soup.find_all("tr","tablesorter-hasChildRow"):
                record = {}
                bets = row.find_all('td','col-odds')
                record["match_name"] = row.find('td','col-title')['data-value']
                record["bet_1"] = bets[0].getText().strip()
                record["bet_0"] = bets[1].getText().strip()
                record["bet_2"] = bets[2].getText().strip()
                record["bet_10"] = bets[3].getText().strip()
                record["bet_20"] = bets[4].getText().strip()
                record["bet_12"] = bets[5].getText().strip()
                ts = int(row.find('td','col-date')['data-value']) / 1000
                record["date"] = datetime.fromtimestamp(ts)
                records.append(record)
            print(records)


