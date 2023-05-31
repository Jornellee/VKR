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

def get_group_names(session):
    q =  text(f"""
    SELECT id_7, obozn from real_groups
    WHERE is_active = true""")

    rows = session.execute (q,)
    group_names = {i.id_7: i.obozn for i in rows}

def get_schedule_changes(session, dt):
    today = dt 
    d1, d2 = get_changes_weeks_starts(today)

    # запускаем скрипт (показывает когда было/стало)
    q =  text(f"""
   SELECT discipline_verbose
    , array(select abs(unnest(groups))) as groups_id
    , array(select abs(unnest(teachers))) teachers
    , nt
    , array_agg(dbeg) as dbeg
    , array_agg(day ORDER BY dbeg, everyweek, day, para) as day
    , array_agg(para ORDER BY dbeg, everyweek, day, para) as para
    , array_agg(everyweek ORDER BY dbeg, everyweek, day, para) as everyweek
    , array_agg(schedule_id ORDER BY dbeg, everyweek, day, para) as schedule_id
    FROM schedule_v2
    WHERE dbeg in (:x, :y)
    --and (464332 = any (groups) or -464332 = any (groups))
    and type = 'day'
    GROUP BY discipline_verbose, groups, teachers, nt
    """)
    rows = session.execute (q, {"x": d1, "y": d2})

    return list(rows)

def form_groups_changes_messages(groups_info, rows):
    for row in rows:
        if row.groups_id[0] not in groups_info: # проверяем есть ли group_id в словарике groups_info
            groups_info[row.groups_id[0]] = [] # если нет то инициализируем пустым списком
        
        if len (row.day) % 2 == 0:
            # добавляем сообщение об изменениях группе 
            if not check(row.day) or not check(row.para) or not check(row.everyweek):
                groups_info[row.groups_id[0]].append(row)
        else:
            groups_info[row.groups_id[0]].append(row)

def form_teachers_changes_messages(teachers_info, rows):
    for row in rows:
        if not row.teachers:
            continue

        if row.teachers[0] not in teachers_info:
            teachers_info[row.teachers[0]] = []

        # добавляем сообщение об изменениях преподавателю
        if not check(row.day) or not check(row.para) or not check(row.everyweek):
            teachers_info[row.teachers[0]].append(row)

def get_para_frequencies(changes):
    real_changes = [] 
    for row in changes: 
        if len(set(row.dbeg)) <= 1:
            continue
        text1 = row.discipline_verbose

        if not check (row.day) or not check(row.para): 
            text1 += get_para_and_day_changes(row.day,row.para)

        try:
            if not check(row.everyweek): 
                if row.everyweek[1] == 2:
                    text1 += f'\n ---- Пара стала еженедельной'
                if row.everyweek[1] == 1:
                    text1 += f'\n ---- Пара стала через неделю'
        except:
            print(row)
            raise

        real_changes.append(text1)

    return real_changes

def send_group_change_message(real_changes, group_names, group_id, user_id):
    if real_changes:
        changes_as_str = "\n ".join(real_changes)
        message = f' &#128309; <b>Сообщение об изменениях для группы {group_names[group_id]}</b>\n&#10024; {changes_as_str}'  # склейка сообщений в одно сообщение
        bot.send_message (user_id, message, parse_mode='HTML')

def send_teacher_change_message(real_changes, user_id):
    if real_changes:
        changes_as_str = "\n ".join(real_changes)
        message = f' &#128309; <b>Сообщение об изменениях для преподавателя: </b> &#10024; {changes_as_str}'
        bot.send_message (user_id, message, parse_mode='HTML')

def send_bot_groups_changes_messages(groups_info, GROUPS_TO_TELEGRAMS_IDS, group_names):
    # рассылка сообщений в бот по данным словарика groups_info
    for group_id in groups_info:
        # вытащили список переносов для данной группы group_id
        changes = groups_info[group_id]

        # вытащили список подписчиков данной группы group_id
        telegram_ids = GROUPS_TO_TELEGRAMS_IDS.get(group_id, [])

        # рассылаем сообщения об изменениях студентам
        for user_id in telegram_ids:
            real_changes = get_para_frequencies(changes)
            send_group_change_message(real_changes, group_names, group_id, user_id)

def send_bot_teachers_changes_messages(teachers_info, TEACHERS_TO_TELEGRAMS_IDS):
    for teacher_id in teachers_info:
        changes = teachers_info[teacher_id]

        telegram_ids = TEACHERS_TO_TELEGRAMS_IDS.get(teacher_id, [])

        # рассылаем сообщения об изменениях преподавателям
        for user_id in telegram_ids:
            real_changes = get_para_frequencies(changes)
            send_teacher_change_message(real_changes, user_id)
        
def get_changes(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS, dt):
    # сессия - сеанс подключения к БД
    session = Session()

    group_names = get_group_names(session)
	
    schedule_changes = get_schedule_changes(session, dt)

    groups_info = {}
    teachers_info = {}
    
    form_groups_changes_messages(groups_info, schedule_changes)
    form_teachers_changes_messages(teachers_info, schedule_changes)

    # красивый вывод словарика
    pprint(groups_info)

    send_bot_groups_changes_messages(groups_info, GROUPS_TO_TELEGRAMS_IDS, group_names)
    send_bot_teachers_changes_messages(teachers_info, TEACHERS_TO_TELEGRAMS_IDS)

# get_changes(GROUPS_TO_TELEGRAMS_IDS, TEACHERS_TO_TELEGRAMS_IDS, pendulum.now())