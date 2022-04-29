import datetime
import sys

import src.arbitrage as arbi
from src.scrappers.scrapper_doxxbet import ScraperDoxxbet
from src.scrappers.scrapper_etipos import ScraperEtipos
from src.scrappers.scrapper_fortuna import ScraperFortuna
from src.scrappers.scrapper_nike import ScraperNike


class Logger(object):
    def __init__(self, name):
        self.terminal = sys.stdout
        self.log = open("logs/" + name + ".txt", "w", encoding="utf-8")
   
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        pass    

if __name__ == "__main__":
    sys.stdout = Logger("log")
    scrapers = [ScraperEtipos(), ScraperFortuna(), ScraperNike(), ScraperDoxxbet()]

    ############################################################################################
    ####################################### Scrape #############################################
    ############################################################################################

    for scraper in scrapers:
        ct = datetime.datetime.now()
        try: 
            print("-----------------------------")
            print(f"Start {scraper.name} script execution: {ct}")
            scraper.scrape()
        except Exception as e:
            print("ERROR: " + str(e))
            print(f"End {scraper.name} script execution on error: {datetime.datetime.now()}")
        else:
            print(f"End {scraper.name} script execution on success: {datetime.datetime.now()}")    
        print(f"Script execution: {datetime.datetime.now() - ct}")

    ############################################################################################
    ################################### Evaluate bets ##########################################
    ############################################################################################
    ct = datetime.datetime.now()
    print("-----------------------------")
    print("Start arbitrage script execution: ",ct)
        
    try: 
        arbi.evaluate_bets()
    except Exception as e:
        print("ERROR: " + str(e))
        print("End arbitrage script execution on error: ", datetime.datetime.now())
    else:
        print("End arbitrage  script execution on success: ", datetime.datetime.now())    
    print("Script execution: ", datetime.datetime.now() - ct)


