from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from random import randint
from time import sleep
from bs4 import BeautifulSoup
import re
from datetime import datetime

web_url = "https://www.nike.sk"

# Install Chrome driver
browser_options = webdriver.ChromeOptions()
browser_options.add_argument("--start-maximized")
browser_service=Service(ChromeDriverManager().install())

# Open browser
driver = webdriver.Chrome(service=browser_service, options=browser_options)
driver.get(web_url)

sleep(randint(5,12))

# Extract element of each sport 
sports_bar = driver.find_element(by=By.XPATH, value ='//*[@id="left-column"]/div/div/div/div/div[4]/div').get_attribute('innerHTML')
sports_soup = BeautifulSoup(sports_bar, 'html.parser')
sports = [s for s in sports_soup.find_all('div', class_="menu-item menu-item-0")]

for idx_sport, sport in enumerate(sports):

    # Uncollapse sport to show leagues
    bs_sport = BeautifulSoup(str(sport), 'html.parser')
    link = bs_sport.find('a', href=True)['href']
    sleep(randint(5,12))
    click = driver.find_element(by=By.XPATH, value ='//*[@id="left-column"]/div/div/div/div/div[4]/div/div[' + str(idx_sport + 1) + ']/div[1]/a[1]').click()
    sleep(randint(1,2))

    # Extract element of each league
    leagues_bar =driver.find_element(by=By.XPATH, value ='//*[@id="left-column"]/div/div/div/div/div[4]/div/div[' + str(idx_sport + 1) + ']/div[2]').get_attribute('innerHTML') 
    league_soup = BeautifulSoup(leagues_bar, 'html.parser')
    leagues = [le for le in league_soup.find_all('div', class_="menu-item menu-item-1")]

    results = []

    for league in leagues:

        # Parse link from league element
        bs_league = BeautifulSoup(str(league), 'html.parser')
        link_league = bs_league.find('a', href=True)['href']

        # Go to new page
        sleep(randint(5,12))    
        driver.get(web_url + link_league)
        content_html = driver.page_source

        content_soup = BeautifulSoup(content_html, 'html.parser')
        rows = content_soup.find_all("div", class_="flex bet-view-prematch-row")

        for row in rows:
            res = {}
            row_bs = BeautifulSoup(str(row).replace("\n", ""), 'html.parser')

            # Numbers
            possible_num = row_bs.find_all("span", class_="bet-center")
            if len(possible_num) == 6:
                # 1, 0, 2, 10, 12, 20
                res["1"] = possible_num[0].getText().strip() if possible_num[0].getText().strip() != "" else 0
                res["0"] = possible_num[1].getText().strip() if possible_num[1].getText().strip() != "" else 0
                res["2"] = possible_num[2].getText().strip() if possible_num[2].getText().strip() != "" else 0
                res["10"] = possible_num[3].getText().strip() if possible_num[3].getText().strip() != "" else 0
                res["12"] = possible_num[4].getText().strip() if possible_num[4].getText().strip() != "" else 0
                res["20"] = possible_num[5].getText().strip() if possible_num[5].getText().strip() != "" else 0

            elif len(possible_num) == 5:
                # 1, 0, 2, 10, 20
                res["1"] = possible_num[0].getText().strip() if possible_num[0].getText().strip() != "" else 0
                res["0"] = possible_num[1].getText().strip() if possible_num[1].getText().strip() != "" else 0
                res["2"] = possible_num[2].getText().strip() if possible_num[2].getText().strip() != "" else 0
                res["10"] = possible_num[3].getText().strip() if possible_num[3].getText().strip() != "" else 0
                res["20"] = possible_num[4].getText().strip() if possible_num[4].getText().strip() != "" else 0

            elif len(possible_num) == 2:
                # 1, 2
                res["1"] = possible_num[0].getText().strip() if possible_num[0].getText().strip() != "" else 0
                res["2"] = possible_num[1].getText().strip() if possible_num[1].getText().strip() != "" else 0

            else:
                break

            # Oponents
            oponents = row_bs.find("button", class_="bets-opponents ellipsis flex items-center").find_all("div")
            res["name1"] = oponents[0].getText().strip()
            res["name2"] = oponents[2].getText().strip()

            # Time & date
            time_in_row =str(re.findall("\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}", str(row_bs))[0]) 
            res["date"] = datetime.strptime(time_in_row, '%d.%m.%Y %H:%M')

            # Sport category and league (/tipovanie/futbal/anglicko/anglicko-i-liga)
            parsed_link = link_league.split('/')
            res["sport"] = parsed_link[2]
            res["league"] = parsed_link[-1]

            res["site"] = web_url

            results.append(res)
            print(res)