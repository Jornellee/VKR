import telebot
from pprint import pprint
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import re
import pendulum
from sqlalchemy.sql import text

from const import DAYS, GROUPS_TO_TELEGRAMS_IDS, PARAS, TEACHERS_TO_TELEGRAMS_IDS, Session, bot, check, get_changes_weeks_starts, get_day_chenges, get_para_and_day_changes, get_para_chenges, get_split

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

def get_changes(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS):
    # сессия - сеанс подключения к БД
    s = Session()

    today = pendulum.now()   
    d1 = today.add(weeks=1).start_of("week").start_of("day")
    d2 = d1.add(weeks=1)

    #скрипт о начале сессии
    q =  text(f"""
    SELECT unnest(groups)
    , array_agg (DISTINCT dbeg)
    FROM schedule_v2
    WHERE dbeg in (:x, :y)
    and type = 'day'
    GROUP BY unnest(groups) 
    """)

    rows = s.execute (q, {"x": d1, "y": d2})

    rows = list(rows)

    groups_info = {}
    teachers_info = {}

    telegram_ids = TEACHERS_TO_TELEGRAMS_IDS.get(teacher_id, [])

        # рассылаем сообщения о начале сессии
        for user_id in telegram_ids: