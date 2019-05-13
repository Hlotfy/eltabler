#!/usr/local/bin/python2.7

'''

Written Spring 2019
Dee Dee Lennon-Jones, Hala Lotfy
'''
import sys
import MySQLdb

def getConn(db):
    conn = MySQLdb.connect(host='localhost',
                           user='ubuntu',
                           passwd='',
                           db=db)
    return conn

# returns the user's username if they are a staff member, else returns None
def login(conn,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select hashed from staff where username=%s',(username,))
    return curs.fetchone()

def addStaffMember(conn,username,hashed):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('SELECT username FROM staff WHERE username = %s',
                     [username])
    row = curs.fetchone()
    if row is not None:
        return False
    curs.execute('INSERT into staff(username,hashed) \
                            VALUES(%s,%s) \
                            on duplicate key update \
                            hashed = %s',
                 (username, hashed, hashed))
    curs.commit()
    curs.execute('SELECT username FROM staff WHERE username = %s',
                     [username])
    return curs.fetchone()
    
# gets every user's username and name
def getAllUsers(conn):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select username,name from user;')
    return curs.fetchall()
    
# get all menu items of a certain category
def getMenuItemByKind(conn,kind):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select miid,name,price from menuItem where kind = %s;', (kind,))
    return curs.fetchall()

# Gets all menu items
def getAllMenuItems(conn):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from menuItem;')
    return curs.fetchall()

def getMenuItem(conn,miid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from menuItem where miid=%s',(miid,))
    return curs.fetchone()
    
def getAllIngredients(conn):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from ingredient')
    return curs.fetchall()

# Gets the ingredients of a given menu item
def getIngredients(conn, menuItemId):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from ingredient inner join recipe using (iid) where miid = %s', (menuItemId,))
    return curs.fetchall()

# Updates the payments table, and the user's current balance in the user table
def makePayment(conn,username,method,amount,dt):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    #update the user's balance owed atomically :)
    curs.execute('update user set balanceOwed = (select * from (select balanceOwed - %s from user where username=%s) as t1) where username = %s;',(amount,username,username,))
    curs.execute('select balanceOwed from user where username = %s',(username,))
    newBalance = curs.fetchone()['balanceOwed']
    #update their payments
    curs.execute('insert into payments(username,dt,method,amount) values (%s,%s,%s,%s)', (username,dt,method,amount,))
    conn.commit()
    return newBalance
    
# gets a user's name, username, and balance based on their username
def getUser(conn,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from user where username = %s',(username,))
    return curs.fetchone()

# adds an order to the orders table, and updates the user's balance
def addOrder(conn,form,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('insert into orders(dt,username) values(now(),%s)',(username,))
    conn.commit()
    curs.execute('select max(oid) as "oid" from orders where username=%s',(username,))
    oid = curs.fetchone()['oid']
    #print(oid)
    for item in form:
        addOrderItems(conn,item,oid)
    curs.execute('select sum(menuItem.price * orderItem.quantity) as total from orders inner join orderItem on (orders.oid=orderItem.oid) inner join menuItem on (orderItem.miid=menuItem.miid) where orders.username=%s and orderItem.oid=%s',(username,oid))
    orderTotal = curs.fetchone()['total']
    print orderTotal
    curs.execute('update user set balanceOwed = balanceOwed + %s where username=%s',(orderTotal,username))
    conn.commit()
    return getRecentOrders(conn,username)
 
# adds each individual order item to orderItem
def addOrderItems(conn,item,oid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    print item
    curs.execute('insert into orderItem(oid,miid,quantity) values(%s,%s,%s)',(oid,item['miid'],item['quantity']))
    conn.commit()
    return True
    
# fetches a user's recent orders based on their username
def getRecentOrders(conn, user):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select orders.oid, orders.dt, count(orderItem.miid) as item_num, sum(menuItem.price * orderItem.quantity) as "total" from orders inner join orderItem on (orders.oid=orderItem.oid) inner join menuItem on (orderItem.miid=menuItem.miid) where orders.username=%s group by orders.oid order by orders.oid DESC',(user,))
    return curs.fetchall()
    
# fetches order items associated with a user based on their username
def getOrderItems(conn,user):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select orders.oid, menuItem.name, menuItem.price, orderItem.quantity, (menuItem.price * orderItem.quantity) as "item_total" from orders inner join orderItem on (orders.oid=orderItem.oid) inner join menuItem on (orderItem.miid=menuItem.miid) where orders.username=%s order by orders.oid DESC',(user,))
    return curs.fetchall()

# fetches a user's payment history, based on their username
def getRecentPayments(conn,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select * from payments where username = %s order by dt DESC;',(username,))
    return curs.fetchall()

# creates new session for selected user tab
def newSession(conn,username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('insert into session (username) values (%s)',(username,))
    conn.commit()
    curs.execute('select max(sid) as "sid" from session')
    return curs.fetchone()

# for use in short testing
if __name__ == '__main__':
    conn = getConn('tabtracker')
    
