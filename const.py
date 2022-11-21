import telebot
from pprint import pprint
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import re

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
    466015: [
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

def check(array):
    left, right = array[:len(array)//2], array[len(array)//2:]
    print (left == right)
    return left == right