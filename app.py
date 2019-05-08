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

@app.route('/')
# the index page of the app, which includes the staff login form
def index():
    return render_template('index.html')

@app.route('/staff_login',  methods = ['POST'])
# route which processes the staff login and adds the username to the session
def staff_login():
    form = request.form
    print form
    staffId = request.form['staffId']
    session['staffId'] = staffId
    return redirect(url_for('tabs'))
    
@app.route('/staff_logout', methods = ['POST'])
# rotue which processes the staff logout and removes the username from the session
def staff_logout():
    session.pop('staffId')
    print "Logging Out of Staff Account"
    return redirect(url_for('index'))

@app.route('/tabs/')
# route which renders the user tabs page which all current usernames
def tabs():
    users = functions.getAllUsers(conn)
    return render_template('userTabs.html', users=users)
    
@app.route('/menu/', methods = ['POST', 'GET'])
#route which renders the menu page which all current menu items
def order():
    items = functions.getAllMenuItems(conn)
    return render_template('order_form.html', items=items)

@app.route('/access_tab', methods = ['POST'])
# route which processes access to the selected user's tab, adding the username to the session and creating a sesion id for the session
def access_tab(username):
    sessId = functions.newSession(conn,username)
    session['username'] = username
    session['sessId'] = sessId
    print "accessing the tab of " + session['username'] + "!"
    return redirect(url_for('recent_orders', username=session['username']))

@app.route('/leave_tab', methods = ['POST'])
def leave_tab():
    session.pop('username')
    print "leaving user tab!"
    return redirect(url_for('tabs'))

@app.route('/<username>/recent_orders/',  methods = ['POST', 'GET'])
# creates order, adds selected menu items to cart
# add safeguard so you don't create an order with no order items
# delete orders with no order items
def recent_orders(username):
    access_tab(username)
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
            return redirect(request.referrer)

    orders = functions.getRecentOrders(conn,username)
    items = functions.getOrderItems(conn,username)
    user = functions.getUser(conn,username)
    return render_template('recent_orders.html',orders=orders, items=items, user=user)

@app.route('/cart/', methods=['GET','POST'])
# keeps track of all selected menu items for current session and renders cart template
def cart():
    form = request.form
    if not form:
        items = functions.getCart(conn,session['username'])
        if not items:
            return redirect(url_for('order'))
        user = functions.getUser(conn,session['username'])
        return render_template('shopping_cart_page.html', items = items, user = user)
    form = form.to_dict(flat=False)['miid']
    functions.addToCart(conn,form,session['username'])
    items = functions.getCart(conn,session['username'])
    user = functions.getUser(conn,session['username'])
    return render_template('shopping_cart_page.html', items = items, user = user)

@app.route('/<username>/payment/', methods=['GET','POST'])
# accesses payment history for selected user and allows payments to be made to user's tab balance
def payment(username):
    
    if request.method == 'GET':
        payments = functions.getRecentPayments(conn,username)
            
        return render_template('payment_page.html', payments=payments, user=username)
        
    else: #method must be 'POST'
        #get the payment amount and method
        amount = request.form.get('amount')
        method = request.form.get('method')
        
        try:
            # convert to float to type check and to insert into database
            amount = float(amount)
        except ValueError:
            return jsonify({'error':True, 'err':"Please enter an number."})
            
        # make sure the employee enters a payment method
        if method == None:
            return jsonify({'error':True, 'err': "Please select a payment method."})
            
        #calculates the user's new balance and updates the database
        newBalance = functions.makePayment(conn,username,method,amount)
        name = functions.getUser(conn,username)['name']
        flash(name + " made a payment of $" + str(amount) + " using " + method + ". Their new balance is $" + str(newBalance) + ".")
        payments = functions.getRecentPayments(conn,username)

        try:
            method=request.form.get('method')
            amount=request.form.get('amount')
            print(method,amount)
            return jsonify({'error':False,'method':method,'amount':amount,})
        except Exception as err:
            return jsonify({'error':True, 'err':str(err)})
        
                           
if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)

