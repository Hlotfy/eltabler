'''
A file for testing functions.py

Written by Dee Dee Lennon-Jones spring 2019 for CS304 TabTracker project
'''


import sys
import MySQLdb
import functions

conn = functions.getConn('tabtracker')
######### TESTING login ############## status: pass
print "Login (expected: elennonj): ", functions.login(conn,'elennonj')
print "Login (expected: None): ", functions.login(conn,'hcho5')

######## TESTING getUserBalance ############## status:pass
print "User balance (expected: 0.15): ", functions.getUserBalance(conn,'elennonj')['balanceOwed']

######## TESTING getIngredients ############## status: pass
ingredients = functions.getIngredients(conn,26)
print "Ingredients (expected: 5 items): ", [i['name'] for i in ingredients]

######## TESTING makePayment ############## status: pass (Commented out so my balance doesn't go down crazy)
#balance = functions.makePayment(conn,'elennonj','cash',0.10)
#print "Payment for elennonj results in a balance of (expected 0.05): $", balance

######## TESTING getUser ############## status: pass
user = functions.getUser(conn,'elennonj')
print "User is (expected: Dee Dee Lennon-Jones): ", user['name']

######## TESTING getMenuItemByKind ############## status: pass
items = functions.getMenuItemByKind(conn,'drink')
print "Drinks (expected 3 items): ", [[d['name'],d['price']] for d in items]