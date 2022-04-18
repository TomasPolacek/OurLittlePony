import datetime
import sys
import src.scrappers.scrapper_doxxbet as scr_doxx
import src.scrappers.scrapper_fortuna as scr_fortuna
import src.scrappers.scrapper_nike as scr_nike
import src.scrappers.scrapper_etipos as scr_etipos
import src.arbitrage as arbi

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
    ############################################################################################
    ##################################### Scrappers ############################################
    ############################################################################################
    # # Doxxbet scrapper
    # try: 
    #     ct = datetime.datetime.now()
    #     print("-----------------------------")
    #     print("Start Doxxbet script execution: ",ct)
    #     scr_doxx.scrape()
    # except Exception as e:
    #     print("ERROR: " + str(e))
    #     print("End Doxxbet script execution on error: ", datetime.datetime.now())
    # else:
    #     print("End Doxxbet script execution on success: ", datetime.datetime.now())    
    # print("Script execution: ", datetime.datetime.now() - ct)

    # # Nike scrapper
    # ct = datetime.datetime.now()
    # print("-----------------------------")
    # print("Start Nike script execution: ",ct)
    # try: 
    #     scr_nike.scrape()
    # except Exception as e:
    #     print("ERROR: " + str(e))
    #     print("End Nike script execution on error: ", datetime.datetime.now())
    # else:
    #     print("End Nike script execution on success: ", datetime.datetime.now())    
    # print("Script execution: ", datetime.datetime.now() - ct)

    # # Fortuna scrapper
    # ct = datetime.datetime.now()
    # print("-----------------------------")
    # print("Start Fortuna script execution: ",ct)
        
    # try: 
    #     scr_fortuna.scrape()
    # except Exception as e:
    #     print("ERROR: " + str(e))
    #     print("End Fortuna script execution on error: ", datetime.datetime.now())
    # else:
    #     print("End Fortuna  script execution on success: ", datetime.datetime.now())    
    # print("Script execution: ", datetime.datetime.now() - ct)

    # eTipos scrapper
    ct = datetime.datetime.now()
    print("-----------------------------")
    print("Start eTipos script execution: ",ct)
        
    try: 
        scr_etipos.scrape()
    except Exception as e:
        print("ERROR: " + str(e))
        print("End eTipos script execution on error: ", datetime.datetime.now())
    else:
        print("End eTipos  script execution on success: ", datetime.datetime.now())    
    print("Script execution: ", datetime.datetime.now() - ct)


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


