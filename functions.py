#!/usr/local/bin/python2.7

'''

Written Spring 2019
Hala Lotfy
'''
import sys
import MySQLdb

def getConn(db):
    conn = MySQLdb.connect(host='localhost',
                           user='ubuntu',
                           passwd='',
                           db=db)
    return conn
    
#### QUESTION: DO WE NEED THIS? (Scott seems like he didn't check if the uid is in the db)
def login(conn,uid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from staff where uid=%s',(uid,))
    user = curs.fetchone()
    print(user)
    if user:
        return user['uid']
    return False # check if the user exists in the staff database

def getAllOutstandingBalance(conn):
    '''Returns a list of rows, as dictionaries. selects all movies in the database'''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from user where balanceOwed > 0')
    return curs.fetchall()
    
def getAllUsers(conn):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from user')
    return curs.fetchall()

def updateUserBalance(conn,user):
# works but I'm wondering if there is a better way to do this
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('update user, payments, orders set balanceOwed = (select sum(menuItem.price) from orders inner join menuItem on orders.miid = menuItem.miid where orders.username=user.username) - (select sum(payments.amount) from payments where payments.username = user.username) where user.username = %s; select balanceOwed from user where username=%s',(user,user,))
    return curs.fetchall()

def searchUser(conn,form):
    '''returns all movie information using title'''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    form = '%' + form + '%'
    curs.execute('select * from user where username like %s',(form,))
    return curs.fetchall()
    
def addOrder(conn,form):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('insert into orders(dt,username,miid) values(now(),%s,(select miid from menuItem where name=%s))',(form['username'],form['menuItem']))
    conn.commit()
    return updateUserBalance(conn,form['username'])

if __name__ == '__main__':
    conn = getConn('tabtracker')
    
   