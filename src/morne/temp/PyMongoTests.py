import pymongo

conn=pymongo.MongoClient('MySqlDbServer', 27017)

doc = {
        "id" : "getNextSequence('test_table')",
        "name": "Name 1",
        "surname": "Surname 1",
        "age": 42
      }
conn.test_db.test_table2.insert(doc)

print conn.test_db.test_table.aggregate(
    [
        { "$match": {"id": { "$gt": 0, "$lt": 100}}},
        {
            "$group": {
                "_id": 1,
                "maxFloat1": {"$max": "$index_1"}
            }
        }
    ]
).next()

#print Json.dumps(conn.admin.command({ "serverStatus": 1 }))
