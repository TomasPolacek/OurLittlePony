import re
from datetime import datetime
from random import randint
from time import sleep

import src.config as c
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from src.db_handler import DB_Handler
from webdriver_manager.chrome import ChromeDriverManager


class ScraperEtipos():
    def __init__(self) -> None:
        self.web_url = "https://tipkurz.etipos.sk/#/sk/najtipovanejsie"
        self.name = "Etipos"

    def scrape(self):

        # Install Chrome driver
        browser_options = webdriver.ChromeOptions()
        browser_options.add_argument("--start-maximized")
        browser_service=Service(ChromeDriverManager().install())

        # Open browser
        driver = webdriver.Chrome(service=browser_service, options=browser_options)
        driver.get(self.web_url)

        # DB handler, connect to postgres DB
        psql = DB_Handler()

        # Delete old records
        psql.delete_older()

        sleep(randint(5,12))

        # Close cookie banner
        try:
            driver.find_element(by=By.XPATH, value='//*[@id="CybotCookiebotBannerCloseButtonE2E"]').click()
        except:
            pass

        # Extract element of each sport 
        sports = driver.find_element(by=By.XPATH, value ='//*[@id="reactAppRoot"]/div/div[1]/div[3]/div/nav/ul[2]/ul[2]').find_elements(by=By.CLASS_NAME, value='nav-link')

        for sport in sports:
            # Load sport page
            driver.execute_script('arguments[0].scrollIntoView({behavior: "smooth"})', sport)
            sleep(randint(3,5))
            sport.click()

            # Scroll to load all data into poge
            while True:
                try:
                    sleep(randint(3,5))
                    element = driver.find_element(by=By.XPATH, value ='//div[@style="height: 200px;"]')
                    print("Loading all leagues into page...")
                    driver.execute_script('arguments[0].scrollIntoView({behavior: "smooth"})', element)
                except:
                    break

            table_element =  driver.find_element(by=By.XPATH, value ='//*[@id="event-list"]/div[3]/div/div[1]').get_attribute('innerHTML')
            table_bs = BeautifulSoup(table_element, 'html.parser')
            league_headers = [lh for lh in table_bs.find_all('div', {'class':"category-header"})]
            league_tables = [lt for lt in table_bs.find_all('div', {'class':"event-table"})]
            results = []
            for idx,league_header in enumerate(league_headers):
                league_table = league_tables[idx]

                sport_str = league_header.find('div', {'class':"sport-name"}).get_text()
                league_str = league_header.find('div', {'class':"sub-header"}).get_text().replace("\xa0/\xa0"," / ")

                type_of_bet = league_table.find('div', {'class':"event-info-col"}).getText().strip()
                type3 = ["Z??pas"]
                type2 = ["V????az z??pasu", "V????az (vr??tane"]
                rows = league_table.find_all('div', {'class':"grid-table-row"})
                for row in rows:
                    res = {}
                    odds = [odd for odd in row.find('div', {'class':"odds-col"}).find_all('div', {'class':"col-8"})]
                    
                    # Odds
                    is_type2 = [con for con in type2 if(con in type_of_bet)]
                    if is_type2:
                        res[c.tab_col[5]] = odds[0].getText()[-4:].replace(",",".") if odds[0].getText() != "" else "1"
                        res[c.tab_col[6]] = odds[2].getText()[-4:].replace(",",".") if odds[2].getText() != "" else "1"
                    elif type_of_bet in type3:
                        res[c.tab_col[5]] = odds[0].getText()[-4:].replace(",",".") if odds[0].getText() != "" else "1"
                        res[c.tab_col[7]] = odds[1].getText()[-4:].replace(",",".") if odds[1].getText() != "" else "1"
                        res[c.tab_col[6]] = odds[2].getText()[-4:].replace(",",".") if odds[2].getText() != "" else "1"
                    else:
                        continue

                    # Date & time
                    res[c.tab_col[11]] ="'" +  str(datetime.strptime(re.search('pt-3">(.*)</div>',str(row.find('div', {'class':"date-col"}))).group(1).replace("<br/>"," "), '%d.%m.%y %H:%M')) + "'"

                    # Oponents
                    oponents = row.find('div', {'class':"match-label"}).getText().split('-')
                    res[c.tab_col[3]] = "'" + oponents[0] + "'"
                    res[c.tab_col[4]] = "'" + oponents[1] + "'"

                    try:
                        res[c.tab_col[1]] = "'" + c.sport[sport_str] + "'"
                    except:
                        print(f"New sport category detected: {sport_str}, add it to config later!")

                    res[c.tab_col[2]] = "'" + league_str + "'"
                    res[c.tab_col[0]] = "'https://www.etipos.sk'"
                    results.append(res)
            
            if results:
                print(results[-1][c.tab_col[1]])
                psql.upsert(results)

        psql.close()
