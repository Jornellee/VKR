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

def get_sessia(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS):
    # сессия - сеанс подключения к БД
    s = Session()

    today = pendulum.now()   
    d0 = today.start_of("week").start_of("day")
    d1 = d0.add(weeks=1)
    d2 = d1.add(weeks=1)

    groups_info = {}
    teachers_info = {}

    #скрипт о начале сессии для студентов
    q =  text(f"""
    SELECT unnest(groups) id
    , array_agg (DISTINCT dbeg) weeks 
    FROM schedule_v2
    WHERE dbeg in (:x, :y, :z)
    and type = 'day'
    GROUP BY unnest(groups) 
    """)
    groups_rows = s.execute (q, {"x": d1, "y": d2, "z":d0})

    groups_rows = list(groups_rows)

    for row in groups_rows:
        if len(row.weeks) == 2:
            groups_info [row.id] = "Следующая неделя зачетная"
        elif len(row.weeks) == 1:
            groups_info [row.id] = f" {row.id} Следующая неделя экзаменационная и пар не будет"


    #скрипт о начале сессии для преподавателей
    q =  text(f"""
    SELECT unnest(teachers) id
    , array_agg (DISTINCT dbeg) weeks
    FROM schedule_v2
    WHERE dbeg in (:x, :y, :z)
    and type = 'day'
    GROUP BY unnest(teachers) 
    """)
    teachers_rows = s.execute (q, {"x": d1, "y": d2, "z": d0})

    teachers_rows = list(teachers_rows)

    for row in teachers_rows:
        if len(row.weeks) == 0:
            teachers_info [row.id] = f"{row.id} На следующей неделе пар не будет, проверьте расписание в личном кабинете"


        # рассылаем сообщения о начале сессии
    for group_id in groups_info:
        message = groups_info[group_id]
        # вытащили список подписчиков данной группы group_id
        telegram_ids = GROUPS_TO_TELEGRAMS_IDS.get(group_id, [])
        # рассылаем сообщения о начале сессии
        for user_id in telegram_ids:
             bot.send_message (user_id, message, parse_mode='HTML')

get_sessia(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS)