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
    
def getAllMenuItems(conn):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from menuItem')
    return curs.fetchall()

def searchUser(conn,form):
    '''returns all movie information using title'''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    form = '%' + form + '%'
    curs.execute('select * from user where username like %s',(form,))
    return curs.fetchall()

def addOrder(conn,form,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('insert into orders(dt,username) values(now(),%s)',(username,))
    conn.commit()
    curs.execute('select max(oid) as "oid" from orders where username=%s',(username,))
    oid = curs.fetchone()['oid']
    #print(oid)
    for item in form:
        addOrderItems(conn,item,oid)
    return getRecentOrders(conn,username)
 

def addOrderItems(conn,form,oid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    print form
    curs.execute('insert into orderItem(oid,miid,quantity) values(%s,%s,1)',(oid,form))
    conn.commit()
    return True
    
def getRecentOrders(conn, user):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select orders.oid, orders.dt, count(orderItem.miid) as item_num, sum(menuItem.price * orderItem.quantity) as "total" from orders inner join orderItem on (orders.oid=orderItem.oid) inner join menuItem on (orderItem.miid=menuItem.miid) where orders.username=%s group by orders.oid order by orders.oid DESC',(user,))
    return curs.fetchall()
    
def getOrderItems(conn,user):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select orders.oid, menuItem.name, menuItem.price, orderItem.quantity, (menuItem.price * orderItem.quantity) as "item_total" from orders inner join orderItem on (orders.oid=orderItem.oid) inner join menuItem on (orderItem.miid=menuItem.miid) where orders.username=%s order by orders.oid DESC',(user,))
    return curs.fetchall()
    
def getUser(conn,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from user where username=%s',(username,))
    return curs.fetchone()

    
# Gets a user's balance, specified by their username
def getUserBalance(conn,user):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select balanceOwed from user where username = %s', (user,))
    return curs.fetchall()

if __name__ == '__main__':
    conn = getConn('tabtracker')
    orders = getRecentOrders(conn,"hlotfy")
    for order in orders:
        print order
    print "----------------------------------"
    items = getOrderItems(conn,"hlotfy")
    for item in items:
        print item
    
