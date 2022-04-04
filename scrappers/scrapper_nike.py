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

def scrape(opt:int = 0, only_sport:str = "", only_league:str = ""):
    '''
    Scrape https://www.nike.sk for odds for each event

    Arguments:

    opt : 0 = Start scraping from the beginning
          1 = Continue scraping from last execution
    '''
    # Get last scrapped link
    try:
        f = open("last_link.txt", "r", encoding = 'utf-8')       
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
    
    for idx_sport, sport in enumerate(sports):
        
        # Extract sport name
        bs_sport = BeautifulSoup(str(sport), 'html.parser')
        sport_str = str(bs_sport.find('a', href=True)['href']).split('/')[2]
        print("Sport category: " + sport_str)

        if sport_str != only_sport and only_sport != "":
            continue
        
        print("Getting league sub links..."),
        # Uncollapse sport to show leagues
        if (not start_scrape and sport_str == prev_sport) or start_scrape:   
            sleep(randint(3,6))
            element = driver.find_element(by=By.XPATH, value ='//*[@id="left-column"]/div/div/div/div/div[4]/div/div[' + str(idx_sport + 1) + ']/div[1]/a[1]')
            driver.execute_script('arguments[0].scrollIntoView({behavior: "smooth"})', element)
            sleep(1)
            element.click()
            
            
            # Extract element of each league
            leagues_bar =driver.find_element(by=By.XPATH, value ='//*[@id="left-column"]/div/div/div/div/div[4]/div/div[' + str(idx_sport + 1) + ']/div[2]').get_attribute('innerHTML') 
            league_soup = BeautifulSoup(leagues_bar, 'html.parser')
            leagues = [le for le in league_soup.find_all('div', class_="menu-item menu-item-1")]

            league_links = []

            for idx_league, league_link in enumerate(leagues):
                bs_league = BeautifulSoup(str(league_link), 'html.parser')
                hrefs = bs_league.find_all('a', href=True)

                # League bar contains aditional submenu
                if len(hrefs) > 2:

                    # Scroll element to top
                    element = driver.find_element(by=By.XPATH, value ='//*[@id="left-column"]/div/div/div/div/div[4]/div/div[' + str(idx_sport + 1) + ']/div[2]/div[' + str(idx_league + 1) + ']/div[1]/a[1]')
                    driver.execute_script('arguments[0].scrollIntoView({behavior: "smooth"})', element)
                    sleep(1)

                    # Uncollapse submenu
                    element.click()
                    sleep(randint(3,4))

                    # Get submenu content
                    subleague_bar = driver.find_element(by=By.XPATH, value ='//*[@id="left-column"]/div/div/div/div/div[4]/div/div[' + str(idx_sport + 1) + ']/div[2]/div[' + str(idx_league + 1) + ']/div[2]').get_attribute('innerHTML')
                    subleague_soup = BeautifulSoup(subleague_bar, 'html.parser')
                    subleagues = [sle for sle in subleague_soup.find_all('div', class_="menu-item menu-item-2")]

                    # Collapse submenu
                    element.click()

                    for subleague in subleagues:
                        bs_subleague = BeautifulSoup(str(subleague), 'html.parser')
                        subleague_link = bs_subleague.find('a', href=True)['href']
                        if subleague_link != "/tipovanie":
                            league_links.append(subleague_link)
                else:
                    league_links.append(hrefs[0]['href'])

            print("Found", len(league_links), "league sub links")
            # League and subleague links
            print("Iterating...")
            for league in league_links:

                league_str = league.split('/')[-1]
                print(league)

                if league_str != only_league and only_league != "":
                    continue

                if not start_scrape and prev_league == league_str:
                    start_scrape = True

                if start_scrape:

                    # Go to new page
                    print("Switching url")   
                    driver.get(web_url + league)
                    sleep(randint(5,12))
                    content_html = driver.page_source

                    content_soup = BeautifulSoup(content_html, 'html.parser')
                    rows = content_soup.find_all("div", class_="bet-view-prematch-row")
                    # save last visited link
                    f = open("last_link.txt","w", encoding = 'utf-8')
                    f.write(league)
                    f.close()
                    print("Found", len(rows), " possible rows") 
                    for row in rows:
                        res = {}
                        row_bs = BeautifulSoup(str(row).replace("\n", ""), 'html.parser')

                        # Numbers
                        if sport_str == "box":
                            possible_num = row_bs.find_all("span", class_="bet-right")
                        else:
                            possible_num = row_bs.find_all("span", class_="bet-center")
                        if len(possible_num) == 6:
                            # 1, 0, 2, 10, 12, 20
                            res[c.tab_col[5]] = possible_num[0].getText().strip() if possible_num[0].getText().strip() != "" else "0"
                            res[c.tab_col[7]] = possible_num[1].getText().strip() if possible_num[1].getText().strip() != "" else "0"
                            res[c.tab_col[6]] = possible_num[2].getText().strip() if possible_num[2].getText().strip() != "" else "0"
                            res[c.tab_col[8]] = possible_num[3].getText().strip() if possible_num[3].getText().strip() != "" else "0"
                            res[c.tab_col[10]] = possible_num[4].getText().strip() if possible_num[4].getText().strip() != "" else "0"
                            res[c.tab_col[9]] = possible_num[5].getText().strip() if possible_num[5].getText().strip() != "" else "0"

                        elif len(possible_num) == 5:
                            # 1, 0, 2, 10, 20
                            res[c.tab_col[5]] = possible_num[0].getText().strip() if possible_num[0].getText().strip() != "" else "0"
                            res[c.tab_col[7]] = possible_num[1].getText().strip() if possible_num[1].getText().strip() != "" else "0"
                            res[c.tab_col[6]] = possible_num[2].getText().strip() if possible_num[2].getText().strip() != "" else "0"
                            res[c.tab_col[8]] = possible_num[3].getText().strip() if possible_num[3].getText().strip() != "" else "0"
                            res[c.tab_col[10]] = "0"
                            res[c.tab_col[9]] = possible_num[4].getText().strip() if possible_num[4].getText().strip() != "" else "0"
                            

                        elif len(possible_num) == 2:
                            # 1, 2
                            res[c.tab_col[5]] = possible_num[0].getText().strip() if possible_num[0].getText().strip() != "" else "0"
                            res[c.tab_col[7]] = "0"
                            res[c.tab_col[6]] = possible_num[1].getText().strip() if possible_num[1].getText().strip() != "" else "0"
                            res[c.tab_col[8]] = "0"
                            res[c.tab_col[10]] = "0"
                            res[c.tab_col[9]] = "0"

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

                        psql.upsert(res)

    psql.close()