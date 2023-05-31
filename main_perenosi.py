import telebot
from pprint import pprint
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import re
import pendulum
from sqlalchemy.sql import text

from const import GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS, Session, bot, get_perenosi_date_range

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

    
def get_group_names(session):
    q =  text(f"""
    SELECT id_7, obozn from real_groups
    WHERE is_active = true""")

    rows = session.execute (q,)
    group_names = {i.id_7: i.obozn for i in rows}

    return group_names

def get_shifts(session, d1, d2):
    # запускаем скрипт (запрос чтобы вытащить переносы)
    q = text (f"""
    SELECT DISTINCT s.groups as groups_id, q.type, s.groups_verbose, s.teachers, s.teachers_verbose, s.discipline_verbose
    FROM schedule_v2 s
    JOIN queries q on s.query_id = q.id
    WHERE q.type in (2, 3,4) and q.dt between :x and :y 
    """)
    rows = session.execute (q, {"x": d1, "y": d2})

    return list(rows)

def add_group_transfer_message(rows, groups_info):
    for row in rows:
        # надо сделать цикл по groups_id чтобы учитывал все группы которые в groups_id
        if row.groups_id[0] not in groups_info: # проверяем есть ли group_id в словарике groups_info
            groups_info[row.groups_id[0]] = [] # если нет то инициализируем пустым списком
        
        # добавляем сообщение о переносе группе 
        groups_info[row.groups_id[0]].append(remove_tags(row.discipline_verbose))

def add_teacher_transfer_message(rows, teachers_info):
    for row in rows:
        if row.teachers[0] not in teachers_info:
            teachers_info[row.teachers[0]] = []

        # добавляем сообщение о переносе преподавателю 
        teachers_info[row.teachers[0]].append(remove_tags(row.discipline_verbose))

def send_transfer_messages_to_students(telegram_ids, group_names, group_id, perenosi):
    # рассылаем сообщения об переносах студентам
    for user_id in telegram_ids:
        message = f"    &#128308; <b>Сообщение о переносе для группы {group_names[group_id]} </b>" '&#128221;' + " \n".join(perenosi) # склейка сообщений в одно сообщение
        bot.send_message (user_id, message, parse_mode='HTML')

def send_transer_messages_to_teachers(telegram_ids, perenosi):
    # рассылаем сообщения об переносах преподавателям
    for user_id in telegram_ids:
        message = ' &#128308;' "<b>Сообщение о переносе для преподавателя: </b>" '&#128221;' + " \n".join(perenosi)
        bot.send_message (user_id, message, parse_mode='HTML')

def send_bot_group_messages(groups_info, group_names, GROUPS_TO_TELEGRAMS_IDS):
    # рассылка сообщений в бот по данным словарика groups_info
    for group_id in groups_info:
        # вытащили список переносов для данной группы group_id
        perenosi = groups_info[group_id]

        # вытащили список подписчиков данной группы group_id
        telegram_ids = GROUPS_TO_TELEGRAMS_IDS.get(group_id, [])

        send_transfer_messages_to_students(telegram_ids, group_names, group_id, perenosi)

def send_bot_teacher_messages(teachers_info, TEACHERS_TO_TELEGRAMS_IDS):
    for teacher_id in teachers_info:
        perenosi = teachers_info[teacher_id]

        telegram_ids = TEACHERS_TO_TELEGRAMS_IDS.get(teacher_id, [])

        send_transer_messages_to_teachers(telegram_ids, perenosi)

def get_perenosi(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS, dbeg):
    # сессия - сеанс подключения к БД
    s = Session()

    group_names = get_group_names(s)

    pendulum.now()
    d1, d2 = get_perenosi_date_range(dbeg)

    print(d1, d2)
    
    shifts = get_shifts(s, d1, d2)

    groups_info = {}
    teachers_info = {}

    add_group_transfer_message(shifts, groups_info)
    add_teacher_transfer_message(shifts, teachers_info)

    # красивый вывод словарика
    pprint(groups_info)

    send_bot_group_messages(groups_info, group_names, GROUPS_TO_TELEGRAMS_IDS)
    send_transer_messages_to_teachers(teachers_info, TEACHERS_TO_TELEGRAMS_IDS)

