import pymongo
import datetime

conn=pymongo.MongoClient('USERVER2', 27017)

start = datetime.datetime.now()

for x in range(0, 1):
    doc = {
        "name": "Name %s" % x,
        "surname": "Surname %s" % x,
        "age": 42

    }
    conn.test_db.test_table.insert(doc)

end = datetime.datetime.now()

print "Time taken: %s" % (end - start)

for cur in conn.morne.col_1.find().sort([("name", pymongo.ASCENDING), ("surname", pymongo.ASCENDING)]).skip(20000).limit(10):
    print cur