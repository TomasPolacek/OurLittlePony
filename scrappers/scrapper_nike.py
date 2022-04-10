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

def scrape(opt:int = 0):
    '''
    Scrape https://www.nike.sk for odds for each event

    Arguments:

    opt : 0 = Start scraping from the beginning
          1 = Continue scraping from last execution
    '''
    # Get last scrapped link
    try:
        f = open("last_link_nike.txt", "r", encoding = 'utf-8')       
        start_link_str = f.readline()
        f.close()
    except IOError:
        start_link_str = ""

    if opt == 0: 
        start_link_str = ""
        start_scrape = True
        print("Start scrapping from the beginning")
    elif opt == 1: 
        start_scrape = False
        print("Start scrapping from last script execution: " + start_link_str)

    if not start_scrape and start_link_str != "":
        prev_sport = start_link_str.split('/')[2]
        prev_league = start_link_str.split('/')[-1]
        print("File not found or empty, starting scrapping from the beginning instead.")
    else:
        start_scrape = True

    web_url = "https://www.nike.sk"

    # Install Chrome driver
    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument("--start-maximized")
    browser_service=Service(ChromeDriverManager().install())

    # Open browser
    driver = webdriver.Chrome(service=browser_service, options=browser_options)
    driver.get(web_url)

    # DB handler, connect to postgres DB
    psql = DB_Handler()

    # Delete old records
    psql.delete_older()

    sleep(randint(5,12))

    # Extract element of each sport 
    sports_bar = driver.find_element(by=By.XPATH, value ='//*[@id="left-column"]/div/div/div/div/div[4]/div').get_attribute('innerHTML')
    sports_soup = BeautifulSoup(sports_bar, 'html.parser')
    sports = [s for s in sports_soup.find_all('div', class_="menu-item menu-item-0")]
    
    for sport in sports:
        
        # Extract sport name
        bs_sport = BeautifulSoup(str(sport), 'html.parser')
        sport_link = str(bs_sport.find('a', href=True)['href'])
        sport_str = sport_link.split('/')[2]

        print("Sport category: " + sport_str)

        driver.get(web_url + sport_link)
        sleep(randint(5,7))
        while True:
            try:
                sleep(randint(3,5))
                print("Loading all leagues into page...")
                element = driver.find_element(by=By.XPATH, value ='//*[@id="center-main"]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div/button')
                driver.execute_script('arguments[0].scrollIntoView({behavior: "smooth"})', element)
            except:
                break
        table_element =  driver.find_element(by=By.XPATH, value ='//*[@id="center-main"]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div').get_attribute('innerHTML')
        table_bs = BeautifulSoup(str(table_element), 'html.parser')
        leagues = [l for l in table_bs.find_all('div', {'class':"pl-5"})]
        results = []
        for league in leagues:
            league_bs = BeautifulSoup(str(league), 'html.parser')
            league_str = league_bs.find('div', {'class':"bets-box-header-title"}).get_text()

            rows = league_bs.find_all('div', {'class':"bet-view-prematch-row"})
            print("Found", len(rows), " possible rows")
            for row in rows:
                res = {}
                row_bs = BeautifulSoup(str(row), 'html.parser')

                # Numbers
                if sport_str == "box":
                    possible_num = row_bs.find_all("span", class_="bet-right")
                else:
                    possible_num = row_bs.find_all("span", class_="bet-center")
                if len(possible_num) == 6:
                    # 1, 0, 2, 10, 12, 20
                    res[c.tab_col[5]] = possible_num[0].getText().strip() if possible_num[0].getText().strip() != "" else "1"
                    res[c.tab_col[7]] = possible_num[1].getText().strip() if possible_num[1].getText().strip() != "" else "1"
                    res[c.tab_col[6]] = possible_num[2].getText().strip() if possible_num[2].getText().strip() != "" else "1"
                    res[c.tab_col[8]] = possible_num[3].getText().strip() if possible_num[3].getText().strip() != "" else "1"
                    res[c.tab_col[10]] = possible_num[4].getText().strip() if possible_num[4].getText().strip() != "" else "1"
                    res[c.tab_col[9]] = possible_num[5].getText().strip() if possible_num[5].getText().strip() != "" else "1"

                elif len(possible_num) == 5:
                    # 1, 0, 2, 10, 20
                    res[c.tab_col[5]] = possible_num[0].getText().strip() if possible_num[0].getText().strip() != "" else "1"
                    res[c.tab_col[7]] = possible_num[1].getText().strip() if possible_num[1].getText().strip() != "" else "1"
                    res[c.tab_col[6]] = possible_num[2].getText().strip() if possible_num[2].getText().strip() != "" else "1"
                    res[c.tab_col[8]] = possible_num[3].getText().strip() if possible_num[3].getText().strip() != "" else "1"
                    res[c.tab_col[9]] = possible_num[4].getText().strip() if possible_num[4].getText().strip() != "" else "1"
                    

                elif len(possible_num) == 2:
                    # 1, 2
                    res[c.tab_col[5]] = possible_num[0].getText().strip() if possible_num[0].getText().strip() != "" else "1"
                    res[c.tab_col[6]] = possible_num[1].getText().strip() if possible_num[1].getText().strip() != "" else "1"

                else:
                    break

                # Oponents
                if sport_str == "box":
                    oponents = row_bs.find_all("span", class_="bet-left")
                    res[c.tab_col[3]] = "'" + oponents[0].getText().strip() + "'"
                    res[c.tab_col[4]] = "'" + oponents[1].getText().strip() + "'"
                else:
                    oponents = row_bs.find("button", class_="bets-opponents ellipsis flex items-center").find_all("div")
                    res[c.tab_col[3]] = "'" + oponents[0].getText().strip() + "'"
                    res[c.tab_col[4]] = "'" + oponents[2].getText().strip() + "'"

                # Time & date
                time_in_row =str(re.findall("\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}", str(row_bs))[0]) 
                res[c.tab_col[11]] = "'" + str(datetime.strptime(time_in_row, '%d.%m.%Y %H:%M')) + "'"

                # Sport category and league (/tipovanie/futbal/anglicko/anglicko-i-liga)

                res[c.tab_col[1]] = "'" + sport_str + "'"
                res[c.tab_col[2]] = "'" + league_str + "'"

                res[c.tab_col[0]] = "'" + web_url + "'"

                results.append(res)
        if results:
            psql.upsert(results)

    psql.close()