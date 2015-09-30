__author__ = 'jbosley2'

import MySQLdb
import datetime

# ================== [ SQL SERVER SETTINGS ] =================
settings = []
with open('server_settings.txt') as fp:
    for line in fp:
        line = line.split("=")
        settings.append(line[1].strip('\n'))
fp.close()

HOST = settings[0]
PORT = int(settings[1])
BLOCK = int(settings[2])
SQL_ADDR = settings[3]
SQL_USER = settings[4]
SQL_PASS = settings[5]
SQL_DB = settings[6]
settings = []
# ===========================================================


def db_update(query):
    db = MySQLdb.connect(SQL_ADDR, SQL_USER, SQL_PASS, SQL_DB)
    return_code = 1
    cursor = db.cursor()
    try:
        cursor.execute(query)
        db.commit()
    except:
        db.rollback()
        return_code = -1
        db.close()
    return return_code


def db_fetch(query):
    db = MySQLdb.connect(SQL_ADDR, SQL_USER, SQL_PASS, SQL_DB)
    cursor = db.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
    except:
        results = -1
    db.close()
    return results


def output_update_to_screen(message):

    message = ("\n %s \t : \t\t %s") % (message, datetime.datetime.now())

    print message

    return