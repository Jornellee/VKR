#сделать запрос к БД с пользователями и сгруппировать подписчиков по группам и преподам (как в конст GROUPS_TO_TELEGRAMS_IDS)
#
import pymongo
client = pymongo.MongoClient("localhost", 27017)
db = client.schedule
result = db.users.find()
for r in result: 
    print (r)

    