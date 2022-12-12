import telebot
from pprint import pprint
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import re

from const import GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS, Session, bot

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

    

def get_perenosi(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS, dbeg):
    # сессия - сеанс подключения к БД
    s = Session()

    # запускаем скрипт (запрос чтобы вытащить переносы)
    rows = s.execute(f"""
    SELECT s.groups as groups_id, q.type, s.groups_verbose, s.teachers, s.teachers_verbose, s.discipline_verbose
    FROM schedule_v2 s
    JOIN queries q on s.query_id = q.id
    WHERE q.type in (2, 3,4) and s.dbeg = '{dbeg}'
    """)

    rows = list(rows)

    groups_info = {}
    teachers_info = {}

    for row in rows:
        # надо сделать цикл по groups_id чтобы учитывал все группы которые в groups_id
        if row.groups_id[0] not in groups_info: # проверяем есть ли group_id в словарике groups_info
            groups_info[row.groups_id[0]] = [] # если нет то инициализируем пустым списком
        
        # добавляем сообщение о переносе группе 
        groups_info[row.groups_id[0]].append(remove_tags(row.discipline_verbose))

    for row in rows:
        if row.teachers[0] not in teachers_info:
            teachers_info[row.teachers[0]] = []

        # добавляем сообщение о переносе преподавателю 
        teachers_info [row.teachers[0]].append(remove_tags(row.discipline_verbose))



    # красивый вывод словарика
    pprint(groups_info)

    # рассылка сообщений в бот по данным словарика groups_info
    for group_id in groups_info:
        # вытащили список переносов для данной группы group_id
        perenosi = groups_info[group_id]

        # вытащили список подписчиков данной группы group_id
        telegram_ids = GROUPS_TO_TELEGRAMS_IDS.get(group_id, [])

        # рассылаем сообщения об переносах студентам
        for user_id in telegram_ids:
            message = '	&#128308;' "<b>Сообщение о переносе для группы: </b>" '&#128221;' + " \n".join(perenosi) # склейка сообщений в одно сообщение
            bot.send_message (user_id, message, parse_mode='HTML')

    for teacher_id in teachers_info:
        perenosi = teachers_info[teacher_id]

        telegram_ids = TEACHERS_TO_TELEGRAMS_IDS.get(teacher_id, [])

        # рассылаем сообщения об переносах преподавателям
        for user_id in telegram_ids:
            message = '	&#128308;' "<b>Сообщение о переносе для преподавателя: </b>" '&#128221;' + " \n".join(perenosi)
            bot.send_message (user_id, message, parse_mode='HTML')


get_perenosi(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS, "2022-09-26")