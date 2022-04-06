from db_handler import DB_Handler
from difflib import SequenceMatcher
from datetime import datetime

# DB handler, connect to postgres DB
psql = DB_Handler()

# Delete old records
psql.delete_older()

nike = psql.get_from_date("https://www.nike.sk")
doxx = psql.get_from_date("https://www.doxxbet.sk/")

res = []
for i1,m1 in enumerate(nike):
    top_ratio = 0
    res.append(('',''))
    for i2,m2 in enumerate(doxx):
        s = SequenceMatcher(None, str(m1[1:5] + m1[11:12]), str(m2[1:5] + m2[11:12]))
        if s.ratio() > 0.5 and  s.ratio() > top_ratio:
            top_ratio = s.ratio()
            res[i1] = (m1,m2)
    print('---------------')
    print(res[i1][0][0:11])
    print(res[i1][1][0:11])
    print('---------------')
