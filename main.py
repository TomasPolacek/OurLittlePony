import scrappers.scrapper_doxxbet as scr_doxx
import scrappers.scrapper_nike as scr_nike
import sys
import datetime;
import sys

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("log.txt", "w", encoding="utf-8")
   
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass    


  
if __name__ == "__main__":
    

    sys.stdout = Logger()

    # Doxxbet scrapper
    try: 
        ct = datetime.datetime.now()
        print("-----------------------------")
        print("Start Nike script execution: ",ct)
        scr_doxx.scrape(0)
    except Exception as e:
        print("ERROR: " + str(e))
        print("End Nike script execution on error: ", datetime.datetime.now())
    else:
        print("End Nike script execution on success: ", datetime.datetime.now())    
    print("Script execution: ", datetime.datetime.now() - ct)

    
    # Nike scrapper
    try: 
        ct = datetime.datetime.now()
        print("-----------------------------")
        print("Start Nike script execution: ",ct)
        scr_nike.scrape(0)
    except Exception as e:
        print("ERROR: " + str(e))
        print("End Nike script execution on error: ", datetime.datetime.now())
    else:
        print("End Nike script execution on success: ", datetime.datetime.now())    
    print("Script execution: ", datetime.datetime.now() - ct)
