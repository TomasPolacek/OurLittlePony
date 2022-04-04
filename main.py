import scrappers.scrapper_nike as scr_nike
import sys
import datetime;
  
if __name__ == "__main__":
    
    # ct stores current time
    sys.stdout = open('log.txt', 'w', encoding="utf-8")
    
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


    sys.stdout.close()