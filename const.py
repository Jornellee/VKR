import telebot
from pprint import pprint
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import re
import pymorphy2

bot = telebot.TeleBot("5742810421:AAHtH3-j6keBuiceiV640-D6varvokAs2Ds", parse_mode=None)
# bot.send_message (a,"Привет") 

DATABASE_URI = 'postgresql://postgres:123@localhost:5432/schedule new'
engine = db.create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)



# словарик который связывает id группы со списксом телеграм пользователей которые подписаны на группу
GROUPS_TO_TELEGRAMS_IDS = {
    464439: [
        "1005181834",
    ]
,
    464332: [
        "1005181834",
    ]
}

TEACHERS_TO_TELEGRAMS_IDS = {
    4559: [
        "1005181834",
    ]
}

PARAS = {
    1: '8:15',
    2: '10:00',
    3: '11:45',
    4: '13:45',
    5: '15:30',
    6: '17:10',
    7: '18:45',
    8: '20:20',
}

DAYS = {
    1: 'понедельник',
    2: 'вторник',
    3: 'среда',
    4: 'четверг',
    5: 'пятница',
    6: 'суббота',
    8: 'понедельник',
    9: 'вторник',
    10: 'среда',
    11: 'четверг',
    12: 'пятница',
    13: 'суббота',
}

def to(word, padeg):
    morph = pymorphy2.MorphAnalyzer()
    word = morph.parse(word)[0].inflect({'sing', padeg}).word
    return word

def check(array):
    left, right = array[:len(array)//2], array[len(array)//2:]
    print (left == right)
    return left == right

def get_split(everyweek):
    n = sum(everyweek)//2
    print(everyweek)
    print(list(enumerate(everyweek)))
    s = 0;
    j = 0;
    for (i, x) in enumerate(everyweek):
        if s<=n:
            s += x
            j = i

    print(j)
    return j 

def get_day_chenges(day): 
    text = ''
    for i in range(len(day)//2):
        x1 = day[i];
        x2 = day[i+len(day)//2];
        if x1 != x2:
          text += f'\n ---- Перенос дня с {DAYS[x1]} на {DAYS[x2]}'

    return text

print(get_day_chenges([1,2,3,3,2,2]))


def get_para_chenges(para): 
    text = ''
    for i in range(len(para)//2):
        x1 = para[i];
        x2 = para[i+len(para)//2];
        if x1 != x2:
          text += f'\n ---- Перенос пары с {PARAS[x1]} на {PARAS[x2]}'

    return text

print(get_para_chenges([1,2,3,3,2,2]))


def get_para_and_day_changes(day,para):
    text =''
    for i in range(len(para)//2):
        p1 = para[i];
        p2 = para[i+len(para)//2];
        d1 = day[i];
        d2 = day[i+len(day)//2];
        if d1 == d2:
            if p1 != p2:
                text += f'\n ---- Перенос пары в {to(DAYS[d1],"accs")} с {PARAS[p1]} на {PARAS[p2]}'
        else: 
            if p1 != p2:
                text += f'\n ---- Перенос пары с {to(DAYS[d1], "gent")} в {PARAS[p1]} на {to(DAYS[d2], "accs")} в {PARAS[p2]}'
            else:
                 text += f'\n ---- Перенос пары с {to(DAYS[d1], "gent")} в {PARAS[p1]} на {to(DAYS[d2], "accs")} в то же время '
    return text

