import datetime
import sys

import scrappers.scrapper_doxxbet as scr_doxx
import scrappers.scrapper_fortuna as scr_fortuna
import scrappers.scrapper_nike as scr_nike

if __name__ == "__main__":
    
    # ct stores current time
    sys.stdout = open('log.txt', 'w', encoding="utf-8")

    # # Doxxbet scrapper
    # try: 
    #     ct = datetime.datetime.now()
    #     print("-----------------------------")
    #     print("Start Nike script execution: ",ct)
    #     scr_doxx.scrape(0)
    # except Exception as e:
    #     print("ERROR: " + str(e))
    #     print("End Nike script execution on error: ", datetime.datetime.now())
    # else:
    #     print("End Nike script execution on success: ", datetime.datetime.now())    
    # print("Script execution: ", datetime.datetime.now() - ct)

    
    # # Nike scrapper
    # try: 
    #     ct = datetime.datetime.now()
    #     print("-----------------------------")
    #     print("Start Nike script execution: ",ct)
    #     scr_nike.scrape(0)
    # except Exception as e:
    #     print("ERROR: " + str(e))
    #     print("End Nike script execution on error: ", datetime.datetime.now())
    # else:
    #     print("End Nike script execution on success: ", datetime.datetime.now())    
    # print("Script execution: ", datetime.datetime.now() - ct)

    # Fortuna scrapper
    try: 
        ct = datetime.datetime.now()
        print("-----------------------------")
        print("Start Fortuna script execution: ",ct)
        scr_fortuna.scrape(0)
    except Exception as e:
        print("ERROR: " + str(e))
        print("End Fortuna script execution on error: ", datetime.datetime.now())
    else:
        print("End Fortuna  script execution on success: ", datetime.datetime.now())    
    print("Script execution: ", datetime.datetime.now() - ct)



    sys.stdout.close()
