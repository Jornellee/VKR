import telebot
from pprint import pprint
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import re
import pendulum

from const import DAYS, GROUPS_TO_TELEGRAMS_IDS, PARAS, TEACHERS_TO_TELEGRAMS_IDS, Session, bot, check, get_day_chenges, get_para_and_day_changes, get_para_chenges, get_split

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

def get_changes(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS):
    # сессия - сеанс подключения к БД
    s = Session()

    today = pendulum.now()
    d1 = today.start_of("week")
    d2 = d1.add(weeks=1)
    d1 = d1.strftime('%Y.%m.%d')
    d2 = d2.strftime('%Y.%m.%d')
    print(d1, d2)

    # запускаем скрипт (показывает когда было/стало)
    rows = s.execute(f"""
   SELECT discipline_verbose
    , groups as groups_id
    , teachers
    , nt
    , array_agg(day ORDER BY dbeg, everyweek, day, para) as day
    , array_agg(para ORDER BY dbeg, everyweek, day, para) as para
    , array_agg(everyweek ORDER BY dbeg, everyweek, day, para) as everyweek
    , array_agg(schedule_id ORDER BY dbeg, everyweek, day, para) as schedule_id
    FROM schedule_v2
    WHERE dbeg in ('2022.09.26', '2022.10.03')
    --and (464332 = any (groups) or -464332 = any (groups))
    and type = 'day'
    GROUP BY discipline_verbose, groups, teachers, nt


    """)

    rows = list(rows)

    groups_info = {}
    teachers_info = {}
    
    for row in rows:
        if row.groups_id[0] not in groups_info: # проверяем есть ли group_id в словарике groups_info
            groups_info[row.groups_id[0]] = [] # если нет то инициализируем пустым списком
        
        if len (row.day) % 2 == 0:
            # добавляем сообщение об изменениях группе 
            if not check(row.day) or not check(row.para) or not check(row.everyweek):
                groups_info[row.groups_id[0]].append(row)
        else:
            groups_info[row.groups_id[0]].append(row)


    for row in rows:
        if not row.teachers:
            continue

        if row.teachers[0] not in teachers_info:
            teachers_info[row.teachers[0]] = []

        # добавляем сообщение об изменениях преподавателю
        if not check(row.day) or not check(row.para) or not check(row.everyweek):
            teachers_info [row.teachers[0]].append(row)



    # красивый вывод словарика
    pprint(groups_info)

    # рассылка сообщений в бот по данным словарика groups_info
    for group_id in groups_info:
        # вытащили список переносов для данной группы group_id
        changes = groups_info[group_id]

        # вытащили список подписчиков данной группы group_id
        telegram_ids = GROUPS_TO_TELEGRAMS_IDS.get(group_id, [])

        # рассылаем сообщения об изменениях студентам
        for user_id in telegram_ids:

            real_changes = [] 
            for row in changes: 
                text = row.discipline_verbose

                if not check (row.day) or not check(row.para): 
                    text += get_para_and_day_changes(row.day,row.para)

                if not check(row.everyweek): 
                    if row.everyweek[1] == 2:
                        text += f'\n ---- Пара стала еженедельной'
                    if row.everyweek[1] == 1:
                        text += f'\n ---- Пара стала через неделю'


                real_changes.append(text)
            
            changes_as_str = "\n ".join(real_changes)
            message = f' &#128309; <b>Сообщение об изменениях для группы:</b>\n&#10024; {changes_as_str}'  # склейка сообщений в одно сообщение
            bot.send_message (user_id, message, parse_mode='HTML')

    for teacher_id in teachers_info:
        changes = teachers_info[teacher_id]

        telegram_ids = TEACHERS_TO_TELEGRAMS_IDS.get(teacher_id, [])

        # рассылаем сообщения об изменениях преподавателям
        for user_id in telegram_ids:

            real_changes = [] 
            for row in changes: 
                text = row.discipline_verbose

                if not check (row.day) or not check(row.para): 
                    text += get_para_and_day_changes(row.day,row.para)

                if not check(row.everyweek): 
                    if row.everyweek[1] == 2:
                        text += f'\n ---- Пара стала еженедельной'
                    if row.everyweek[1] == 1:
                        text += f'\n ---- Пара стала через неделю'


                real_changes.append(text)
            changes_as_str = "\n ".join(real_changes)
            message = f' &#128309; <b>Сообщение об изменениях для преподавателя: </b> &#10024; {changes_as_str}'
            bot.send_message (user_id, message, parse_mode='HTML')


get_changes(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS)