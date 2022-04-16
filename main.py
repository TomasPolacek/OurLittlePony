import datetime
import sys
import os
import scrappers.scrapper_doxxbet as scr_doxx
import scrappers.scrapper_fortuna as scr_fortuna
import scrappers.scrapper_nike as scr_nike

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("log.txt", "w", encoding="utf-8")
   
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        pass    

if __name__ == "__main__":
    

    sys.stdout = Logger()

    # Doxxbet scrapper
    try: 
        ct = datetime.datetime.now()
        print("-----------------------------")
        print("Start Nike script execution: ",ct)
        scr_doxx.scrape()
    except Exception as e:
        print("ERROR: " + str(e))
        print("End Nike script execution on error: ", datetime.datetime.now())
    else:
        print("End Nike script execution on success: ", datetime.datetime.now())    
    print("Script execution: ", datetime.datetime.now() - ct)

    
    # Nike scrapper
    ct = datetime.datetime.now()
    print("-----------------------------")
    print("Start Nike script execution: ",ct)
    try: 
        scr_nike.scrape()
    except Exception as e:
        print("ERROR: " + str(e))
        print("End Nike script execution on error: ", datetime.datetime.now())
    else:
        print("End Nike script execution on success: ", datetime.datetime.now())    
    print("Script execution: ", datetime.datetime.now() - ct)


    # Fortuna scrapper
    ct = datetime.datetime.now()
    print("-----------------------------")
    print("Start Fortuna script execution: ",ct)
        
    try: 
        scr_fortuna.scrape()
    except Exception as e:
        print("ERROR: " + str(e))
        print("End Fortuna script execution on error: ", datetime.datetime.now())
    else:
        print("End Fortuna  script execution on success: ", datetime.datetime.now())    
    print("Script execution: ", datetime.datetime.now() - ct)
