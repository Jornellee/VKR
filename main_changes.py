import telebot
from pprint import pprint
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import re

from const import GROUPS_TO_TELEGRAMS_IDS, PARAS, TEACHERS_TO_TELEGRAMS_IDS, Session, bot

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

def get_changes(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS):
    # сессия - сеанс подключения к БД
    s = Session()

    # запускаем скрипт (показывает когда было/стало)
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
    and 464439 = any (groups)
    and type = 'day'
    GROUP BY discipline_verbose, groups, teachers, nt
    """)

    rows = list(rows)

    for r in rows:
        if r['day'][0] != r['day'][1]:
            print(r)

    groups_info = {}
    teachers_info = {}
    
    for row in rows:
        # надо сделать цикл по groups_id чтобы учитывал все группы которые в groups_id
        if row.groups_id[0] not in groups_info: # проверяем есть ли group_id в словарике groups_info
            groups_info[row.groups_id[0]] = [] # если нет то инициализируем пустым списком
        
        # добавляем сообщение об изменениях группе 
        if row.day[0] != row.day[1] or row.para[0] != row.para[1] or row.everyweek[0] != row.everyweek[1]:
            pprint (row)
            groups_info[row.groups_id[0]].append(row)

    for row in rows:
        if row.teachers[0] not in teachers_info:
            teachers_info[row.teachers[0]] = []

        # добавляем сообщение об изменениях преподавателю 
        teachers_info [row.teachers[0]].append(row)



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

            real_changes = [] 
            for row in changes: 
                text = row.discipline_verbose

                if row.day[0] != row.day[1]: 
                    text += f'\n ---- Перенос дня с  {row.day[0]} на {row.day[1]}'

                if row.para[0] != row.para[1]: 
                    text += f'\n ---- Перенос пары с {PARAS[row.para[0]]} на {PARAS[row.para[1]]}'

                if row.everyweek[0] != row.everyweek[1]: 
                    if row.everyweek[1] == 2:
                        text += f'\n ---- Пара стала еженедельной'
                    if row.everyweek[1] == 1:
                        text += f'\n ---- Пара стала через неделю'


                real_changes.append(text)
            
            message = f' &#128309; <b>Сообщение об изменениях для группы:</b>\n&#10024; {", ".join(real_changes)}'  # склейка сообщений в одно сообщение
            bot.send_message (user_id, message, parse_mode='HTML')

    '''for teacher_id in teachers_info:
        changes = teachers_info[teacher_id]

        telegram_ids = TEACHERS_TO_TELEGRAMS_IDS.get(teacher_id, [])

        # рассылаем сообщения об изменениях преподавателям
        for user_id in telegram_ids:
            message = '	&#128309;' "<b>Сообщение об изменениях для преподавателя: </b>" '&#10024;' + " \n".join(changes)
            bot.send_message (user_id, message, parse_mode='HTML')'''


get_changes(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS)