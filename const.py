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
    1432: [
        "1005181834",
    ]
}

PARAS = {
    1: '8:15',
    5: '15:30',
    7: '18:45',
}