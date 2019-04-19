#!/usr/local/bin/python2.7

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
#from werkzeug import secure_filename
app = Flask(__name__)

import sys,os,random,functions
from werkzeug.datastructures import ImmutableMultiDict

app.secret_key = 'asdflsgflawiewurhe'

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
conn = functions.getConn('tabtracker')

@app.route('/tabs/')
def tabs():
    users = functions.getAllUsers(conn)
    return render_template('userTabs.html', users=users)

@app.route('/<username>/recent_orders/',  methods = ['POST', 'GET'])
# creates order, adds selected menu items to order
# add safeguard so you don't create an order with no order items
# delete orders with no order items
def recent_orders(username):
    if request.method == 'POST':
        form = request.form
        if form:
            form = form.to_dict(flat=False)['miid']
            print form
            functions.addOrder(conn,form,username)
            orders = functions.getRecentOrders(conn,username)
            items = functions.getOrderItems(conn,username)
            user = functions.getUser(conn,username)
            return render_template('recent_orders.html',orders=orders, items=items, user=user)
        else:
            flash('''Please select items to add to your order''')
            return redirect(request.referrer)
    
    orders = functions.getRecentOrders(conn,username)
    items = functions.getOrderItems(conn,username)
    user = functions.getUser(conn,username)
    return render_template('recent_orders.html',orders=orders, items=items, user=user)
    

@app.route('/menu/', methods = ['POST', 'GET'])
def menu():
    users = functions.getAllUsers(conn)
    return render_template('menuScreen.html')
    
@app.route('/order/', methods = ['POST', 'GET'])
def menuItems():
    items = functions.getAllMenuItems(conn)
    return render_template('order_form.html', items=items)
    

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)

