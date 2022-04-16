from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from random import randint
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
import re
import config as c
from db_handler import DB_Handler

def scrape():

    web_url = "https://www.doxxbet.sk/"

    # Install Chrome driver
    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument("--start-maximized")
    browser_service=Service(ChromeDriverManager().install())

    # Open browser
    driver = webdriver.Chrome(service=browser_service, options=browser_options)
    driver.get(web_url)
    sleep(randint(5,12))

    # DB handler, connect to postgres DB
    psql = DB_Handler()

    # Delete old records
    psql.delete_older()

    # Extract element of each sport 
    sports_bar = driver.find_element(by=By.XPATH, value ='//*[@id="mCSB_12_container"]/nav/ul').get_attribute('innerHTML')
    sports_soup = BeautifulSoup(sports_bar, 'html.parser')
    sports = [s for s in sports_soup.find_all('li', {'ng-repeat':"Sport in Sidebar.Sports track by Sport.ID+Sport.Typ"})]

    for sport in sports:
        # Extract sport name
            bs_sport = BeautifulSoup(str(sport), 'html.parser')
            sport_link = str(bs_sport.find('a', href=True)['href'])
            sport_str = sport_link.split('/')[2]
            print("Sport category: " + sport_str)

            if sport_str == "zlata-liga":
                print("Skipping " + sport_str)
                continue

            # Go to new page
            print("Switching url")   
            driver.get(web_url + sport_link)
            sleep(randint(5,12))
            content_html = driver.page_source

            # Load all bets by collapsing Sport menu
            element = driver.find_element(by=By.XPATH, value ='//*[@id="offers-nonlive"]/div[2]/div/div[1]')
            element.click()

            # Wait unti all data is loaded
            while True:
                try:
                    print("Waiting for page to load data")
                    sleep(2)
                    element_loading = driver.find_element(by=By.XPATH, value ='//*[@id="offers-nonlive"]/div[2]/img')
                except:
                    break
            
            print("Parsing data")
            # Table of leagues
            leagues_table = driver.find_element(by=By.XPATH, value ='//*[@id="offers-nonlive"]/div[2]/div/div[2]/div[1]').get_attribute('innerHTML')
            leagues_table_soup = BeautifulSoup(leagues_table, 'html.parser')
            leagues = [le for le in leagues_table_soup.find_all('div', {'ng-repeat':"league in region.leagues"})]

            print("Found", len(leagues), " possible leagues")

            results = []
            for league in leagues:

                league_bs = BeautifulSoup(str(league), 'html.parser')
                league_header = league_bs.find("span", class_="label").getText().strip()

                if " - Celkovo" in league_header:
                    print("Skipping - " + league_header)
                    continue
                
                dates = [d for d in league_bs.find_all('div', {'ng-repeat':"date in league.dates"})]
                
                for date in dates:
                    date_bs = BeautifulSoup(str(date), 'html.parser')

                    res_date = date_bs.find('div', {'class':"td--heading"}).getText().strip().split(" - ")[0]

                    rows = date_bs.find_all('div', {'class':"offer__row"})
                    print("Found", len(rows), "matches in - " + sport_str + " " + league_header)
                    for row in rows:
                        res = {}
                        row_bs = BeautifulSoup(str(row), 'html.parser')

                        is_live = row_bs.find('div', {'class':"td--time"})['ng-if'] == "event.isLive"
                        if is_live:
                            print("Skipping live match...")
                            continue

                        res_time = str(row_bs.find('div', {'class':"td--time"}).getText().strip()).split("\n")

                        res_bets = row_bs.find_all('div', {'ng-click':"toggleOdd(event.masterChanceType.odds[mark].ID)"})

                        if len(res_bets) == 6:
                            # 1, 0, 2, 10, 12, 20
                            res[c.tab_col[5]] = res_bets[0].getText().strip() if res_bets[0].getText().strip() != '-' else '1'
                            res[c.tab_col[7]] = res_bets[1].getText().strip() if res_bets[1].getText().strip() != '-' else '1'
                            res[c.tab_col[6]] = res_bets[2].getText().strip() if res_bets[2].getText().strip() != '-' else '1'
                            res[c.tab_col[8]] = res_bets[3].getText().strip() if res_bets[3].getText().strip() != '-' else '1'
                            res[c.tab_col[10]] = res_bets[4].getText().strip() if res_bets[4].getText().strip() != '-' else '1'
                            res[c.tab_col[9]] = res_bets[5].getText().strip() if res_bets[5].getText().strip() != '-' else '1'

                        elif len(res_bets) == 5:
                            # 1, 0, 2, 10, 20
                            res[c.tab_col[5]] = res_bets[0].getText().strip() if res_bets[0].getText().strip() != '-' else '1'
                            res[c.tab_col[7]] = res_bets[1].getText().strip() if res_bets[1].getText().strip() != '-' else '1'
                            res[c.tab_col[6]] = res_bets[2].getText().strip() if res_bets[2].getText().strip() != '-' else '1'
                            res[c.tab_col[8]] = res_bets[3].getText().strip() if res_bets[3].getText().strip() != '-' else '1'
                            res[c.tab_col[9]] = res_bets[5].getText().strip() if res_bets[5].getText().strip() != '-' else '1'
                                

                        elif len(res_bets) == 2:
                            # 1, 2
                            res[c.tab_col[5]] = res_bets[0].getText().strip() if res_bets[0].getText().strip() != '-' else '1'
                            res[c.tab_col[6]] = res_bets[1].getText().strip() if res_bets[1].getText().strip() != '-' else '1'

                        else:
                            break

                        res_op = row_bs.find('div', {'class':"td--match"}).getText().strip().split("\n")
                        res[c.tab_col[3]] = "'" + res_op[0].strip().replace("'","''") +"'"
                        res[c.tab_col[4]] = "'" + res_op[-1].strip().replace("'","''") + "'"

                        # Time & date
                        if len(res_time) == 2:
                            time_in_row = res_date + " " + res_time[1]
                        else:
                            time_in_row = res_date + " " + res_time[0]
                        res[c.tab_col[11]] = "'" + str(datetime.strptime(time_in_row, '%d.%m.%Y %H:%M')) + "'"

                        try:
                            res[c.tab_col[1]] = "'" + c.sport[sport_str] + "'"
                        except:
                            print(f"New sport category detected: {sport_str}, add it to config later!")
                            res[c.tab_col[1]] = "'" + sport_str + "'"
                            
                        res[c.tab_col[2]] = "'" + league_header.replace("'","''") + "'"

                        res[c.tab_col[0]] = "'" + web_url + "'"
                        results.append(res)
            
            if results:
                psql.upsert(results)
                    
    psql.close()