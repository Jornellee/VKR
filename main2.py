from const import Session
import telebot
from pprint import pprint
from const import GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS, Session, bot
import re


s = Session()
        
    
# запускаем скрипт (показывает когда было/стало)
rows = s.execute(f"""
SELECT discipline_verbose
, groups
, teachers
, nt
, array_agg(day ORDER BY dbeg, everyweek, day, para) as day
, array_agg(para ORDER BY dbeg, everyweek, day, para) as para
, array_agg(everyweek ORDER BY dbeg, everyweek, day, para) as everyweek
, array_agg(schedule_id ORDER BY dbeg, everyweek, day, para) as schedule_id
FROM schedule_v2
WHERE dbeg in ('2022.09.26', '2022.10.03')
and 464289 = any (groups)
and type = 'day'
GROUP BY discipline_verbose, groups, teachers, nt
""")

for r in rows:
    if r['day'][0] != r['day'][1]:
        print(r)

