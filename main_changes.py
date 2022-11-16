import telebot
from pprint import pprint
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import re

from const import GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS, Session, bot

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

def get_changes(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS):
    # сессия - сеанс подключения к БД
    s = Session()

    # запускаем скрипт (запрос чтобы вытащить переносы)
    rows = s.execute(f"""
   SELECT discipline_verbose
    , groups as groups_id
    , teachers as teachers
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


    groups_info = {}
    ##teachers_info = {}

    rows = list(rows)

    for row in rows:
        # надо сделать цикл по groups_id чтобы учитывал все группы которые в groups_id
        if row.groups_id[0] not in groups_info: # проверяем есть ли group_id в словарике groups_info
            groups_info[row.groups_id[0]] = [] # если нет то инициализируем пустым списком
        
        # добавляем сообщение о переносе группе 
        groups_info[row.groups_id[0]].append(remove_tags(row.discipline_verbose))

    '''for row in rows:
        if row.teachers[0] not in teachers_info:
            teachers_info[row.teachers[0]] = []

        # добавляем сообщение о переносе преподавателю 
        teachers_info [row.teachers[0]].append(remove_tags(row.discipline_verbose))'''



    # красивый вывод словарика
    pprint(groups_info)

    # рассылка сообщений в бот по данным словарика groups_info
    for group_id in groups_info:
        # вытащили список переносов для данной группы group_id
        changes = groups_info[group_id]

        # вытащили список подписчиков данной группы group_id
        telegram_ids = GROUPS_TO_TELEGRAMS_IDS.get(group_id, [])

        pprint(group_id)

        # рассылаем сообщения об изменениях студентам
        for user_id in telegram_ids:
            message = '	&#128221;' "<b>Сообщение об изменениях для группы: </b>" '&#10024;' + " \n".join(changes) # склейка сообщений в одно сообщение
            bot.send_message (user_id, message, parse_mode='HTML')

    '''for teacher_id in teachers_info:
        changes = teachers_info[teacher_id]

        telegram_ids = TEACHERS_TO_TELEGRAMS_IDS.get(teacher_id, [])

        # рассылаем сообщения об изменениях преподавателям
        for user_id in telegram_ids:
            message = '	&#128221;' "<b>Сообщение об изменениях для преподавателя: </b>" '&#10024;' + " \n".join(changes)
            bot.send_message (user_id, message, parse_mode='HTML')'''


get_changes(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS)