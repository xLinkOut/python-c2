#-*- coding:utf-8 -*-

import hashlib
import sqlite3

databaseFile = "Database.db"

def MD5(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()

class DB():
    def selectQuery(query,params=[]):
        DB = sqlite3.connect(databaseFile)
        c = DB.cursor()
        c.execute(query,params)
        resultSet = c.fetchall()
        DB.close()
        if len(resultSet) == 0:
            return None
        elif len(resultSet) == 1:
            return resultSet[0]
        else:
            return resultSet

    def executeQuery(query,params=[]):
        DB = sqlite3.connect(databaseFile)
        c = DB.cursor()
        c.execute(query,params)
        DB.commit()
        DB.close()
        if c.rowcount >= 1:
            return True
        else:
            return False