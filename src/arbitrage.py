from src.db_handler import DB_Handler
from fuzzywuzzy import fuzz
import src.webhook.discord_webhook as dw
import src.config as c


def find_arbi(date, res, r1, r2):
    print('---------------')
    text = {}
    for result in res:
        print(result[0:11])
            
    print(f"{date[0]}\nString match ratios: \nr1 = {r1}, \nr2 = {r2}")
    odds = []
    for i in range(3):
        odd_list = [r[5+i] for r in res]
        odd = max(odd_list)
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

    with open("logs/arbi_res.txt", "w", encoding="utf-8") as file:
        file.write("Hehe\n\n\n\n")

    for date in dates:
        nike = psql.get_from_date("https://www.nike.sk",date[0].strftime('%Y/%m/%d'))
        doxx = psql.get_from_date("https://www.doxxbet.sk/",date[0].strftime('%Y/%m/%d'))
        fort = psql.get_from_date("https://www.ifortuna.sk",date[0].strftime('%Y/%m/%d'))
        to_skip = []

        # Compare Nike to Doxx, Fortuna
        for m1 in nike:
            res_to_eval = []

            # Find Nike match in Doxx
            top_ratio_nike_doxx = 0
            found_match2 = None
            for m2 in doxx:
                if m2[1] == c.sport["baseball"]:
                    continue
                ratio = fuzz.partial_ratio(m1[3],m2[3]) + fuzz.partial_ratio(m1[4],m2[4]) # compare opponets
                if ratio > ratio_tresh * 2 and  ratio > top_ratio_nike_doxx and m2[11]==m1[11] and m1[1] in m2[1]:
                    top_ratio_nike_doxx = ratio
                    found_match2 = m2

            # Find Nike match in Fortuna
            top_ratio_nike_fort = 0
            found_match3 = None
            for m3 in fort:
                ratio = fuzz.partial_ratio(m1[3],m3[3]) + fuzz.partial_ratio(m1[4],m3[4]) # compare opponets
                if ratio > ratio_tresh * 2 and  ratio > top_ratio_nike_fort and m3[11]==m1[11] and m1[1] in m3[1]:
                    top_ratio_nike_fort = ratio
                    found_match3 = m3

            if found_match2:
                res_to_eval.append(found_match2)
                to_skip.append(found_match2)

            if found_match3:
                res_to_eval.append(found_match3)
                to_skip.append(found_match3)

            if res_to_eval:
                res_to_eval.append(m1)
                find_arbi(date, res_to_eval, top_ratio_nike_doxx, top_ratio_nike_fort)
            break
                
        # Compare Doxx to Fortuna
        for m1 in doxx:
            
            # skip baseball because doxx has more odds
            if m1 in to_skip or m1[1] == c.sport["baseball"]:
                continue

            res_to_eval = []

            top_ratio_doxx_fort = 0
            found_match2 = None
            for m2 in fort:

                if m2 in to_skip:
                    continue

                ratio = fuzz.partial_ratio(m1[3],m2[3]) + fuzz.partial_ratio(m1[4],m2[4]) # compare opponets
                if ratio > ratio_tresh * 2 and  ratio > top_ratio_doxx_fort and m2[11]==m1[11] and m1[1] in m2[1]:
                    top_ratio_doxx_fort = ratio
                    found_match2 = m2

            if found_match2:
                res_to_eval.append(found_match2)
                to_skip.append(found_match2)
            
            if res_to_eval:
                res_to_eval.append(m1)
                find_arbi(date, res_to_eval, top_ratio_doxx_fort, 0)