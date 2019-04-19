#!/usr/local/bin/python2.7

import sys, os
import MySQLdb

def getConn(db):
    conn = MySQLdb.connect(host='localhost',
                           user='ubuntu',
                           passwd='',
                           db=db)
    return conn

os.system('mysql-ctl start')

os.system('mysql --local-infile < "./batch/tables.sql"')

conn = getConn('tabtracker')

curs = conn.cursor(MySQLdb.cursors.DictCursor)
