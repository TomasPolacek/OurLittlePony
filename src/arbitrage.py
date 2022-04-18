from math import inf
from src.db_handler import DB_Handler
from fuzzywuzzy import fuzz
import src.webhook.discord_webhook as dw
import src.config as c

def max_finite(list):
    max_value = None
    for num in list:
        if (max_value is None or max_value < num) and num < float('inf'):
            max_value = num
    return max_value if max_value else list[0]

def find_arbi(date, res, ratio):
    print('---------------')
    text = {}
    for result in res:
        print(result[0:11])
            
    print(f"{date[0]}\nString match ratios:")
    for idx,r in enumerate(ratio):
        print(f"r{idx+1} = {r}")

    odds = []
    for i in range(3):
        odd_list = [r[5+i] for r in res]   
        odd = max_finite(odd_list)
        source = odd_list.index(odd)
        odds.append((odd,res[source][0]))

    ratios = [1/odd[0] for odd in odds]
    arbitrage_ratio = sum(ratios)

    print(f"Magic number: {arbitrage_ratio}")
    if 0.90 < arbitrage_ratio < 1.0 :
        
        text["desc"] = ""
        for result in res:
            text["desc"] += str(result[0:11]) + "\n"
        text["desc"] += str(res[0][11])
        text["fields"] = []
        for i in range(len(odds)):
            if ratios[i] > 0:
                text["fields"].append({"name":str(f"{100 * ratios[i]:.2f}€"), "value":str(f"on {odds[i][0]} in {odds[i][1]}")})

        text["magic"] = str(f"{(1 - arbitrage_ratio)*100:.2f}%")
        dw.send_msg(text)
        print("!!!!! Arbitrage found !!!!!")
    else:
        print("Nope")
    print('---------------')
    

def evaluate_bets():

    # fuzzy wuzzy match ratio treshold 
    ratio_tresh = 70

    # DB handler, connect to postgres DB
    psql = DB_Handler()

    # Delete old records
    psql.delete_older()

    # Get all dates in table
    dates = psql.get_dates()

    for date in dates:
        bookies = [
            psql.get_from_date("https://www.nike.sk",date[0].strftime('%Y/%m/%d')),
            psql.get_from_date("https://www.doxxbet.sk/",date[0].strftime('%Y/%m/%d')),
            psql.get_from_date("https://www.ifortuna.sk",date[0].strftime('%Y/%m/%d')),
            psql.get_from_date("https://www.etipos.sk",date[0].strftime('%Y/%m/%d'))
        ]
        to_skip = []

        for i,bookie1 in enumerate(bookies[:-1]):
            for event1 in bookie1:
                res_to_eval = []
                ratios = []
                if event1 in to_skip:
                    continue

                for bookie2 in bookies[i+1:]:
                    top_ratio = 0
                    found_match = None

                    for event2 in bookie2:
                        if event2 in to_skip:
                            continue

                        ratio = fuzz.partial_ratio(event1[3],event2[3]) + fuzz.partial_ratio(event1[4],event2[4])
                        if ratio > ratio_tresh * 2 and  ratio > top_ratio and event1[11]==event2[11] and event1[1] in event2[1]:
                            top_ratio = ratio
                            found_match = event2

                    if found_match:
                        res_to_eval.append(found_match)
                        ratios.append(top_ratio)
                        to_skip.append(found_match)

                if res_to_eval:
                    res_to_eval.append(event1)
                    find_arbi(date, res_to_eval, ratios)