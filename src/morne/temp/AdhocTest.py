import json
#import yaml
import datetime
import json
import uuid

import os
import sys
from decimal import Decimal
import random

print str((random.randint(0, 9999999999))).zfill(10)

print eval("{'Abbreviation': 'None', 'CurrencyCode': 'None', 'Rate': 'None', 'TranGID': 'bcd03a58-42be-11e7-9c2d-000c290d6cb5', 'Surcharge': 60.0}['CurrencyCode']")


def formatField9(rate):
    if rate is None or rate == 0:
        return "00000000"
    else:
        x = 1.0 / rate
        n = 0
        while n < 9 and x < 1000000:
            n = n + 1
            x = x * 10
        return "%s%s" % (n, int(x))

def unpackField9(s):
    if s is None or s == "":
        return None
    else:
        n = int(s[:1])
        v = float(s[1:])
        if v == 0:
            return None
        else:
            return 1.0 / (v / pow(10, n))

print unpackField9("91234567")

for rate in [None, 1, 0.457, 14.49, 259.6485, 810.0005913004316]:
    print "%s : %s : %s" % (rate, formatField9(rate), unpackField9(formatField9(rate)))


exit(1)


d = {'a':123, 'b':[5, 6, 7, {'c':8}]}

class Morne1:
    def __init__(self):
        pass

x = Morne1()
x.__dict__.update(d)
print repr(x)

exit(1)

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
import pymysql

for root, dirs, files in os.walk('c:\\temp'):
    print repr(root)
    print repr(dirs)
    # print repr(files)

class MyClass1:
    def __init__(self):
        self.a = "A"
        self.b = 123

obj = {}
x = uuid.uuid4()
obj["uuid"] = str(uuid.uuid4())
obj["uuid"] = datetime.datetime.now()
print json.dumps(MyClass1())

exit(1)

def EscapeString(data):
    # 2013-10-25 (Buks): The latest version if pymysql has been fixed to escape strings correctly so there is no need to
    # trim the single quotes
    if len(pymysql.escape_string("abc")) == 5:
        return "%s" % pymysql.escape_string(data)[1:-1]
    else:
        return "%s" % pymysql.escape_string(data)

print EscapeString(u"__\u03E6__")

exit(1)

s = "ABCD"
print s[1:]

Base = declarative_base()

class Table1(Base):
    __tablename__ = "table_1"
    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(String)

print repr(Table1.__table__)

engine = sqlalchemy.create_engine("mysql+pymysql://root:xxxxx@localhost/test?host=USERVER2?port=3306")

connection = engine.connect()
print connection.execute("SELECT 1 UNION SELECT 2").fetchall()
connection.close()

Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)

session = Session()
entry = Table1(data='Morne 12356')
session.add(entry)
session.commit()
print entry.id