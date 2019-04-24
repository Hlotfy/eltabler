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
def index():
    return render_template('index.html')

@app.route('/tabs/')
def tabs():
    logout()
    users = functions.getAllUsers(conn)
    return render_template('userTabs.html', users=users)
    
@app.route('/menu/', methods = ['POST', 'GET'])
def order():
    print session.get('username')
    items = functions.getAllMenuItems(conn)
    return render_template('order_form.html', items=items, username = session.get('username'))

#@app.route('/logout')
def logout():
    session.pop('username', None)
    print "logged out user!"
    print session.get('username')
    session.clear()
    #flash('''successfully logged out''')
    users = functions.getAllUsers(conn)
    return render_template('userTabs.html',users=users)

#@app.route('/login')
def login(username):
    sid = functions.newSession(conn,username)
    print sid, username
    session['username'] = username
    session['sid'] = sid
    print "logged in as user " + session['username'] + "!"
    return 

@app.route('/<username>/recent_orders/',  methods = ['POST', 'GET'])
# creates order, adds selected menu items to order
# add safeguard so you don't create an order with no order items
# delete orders with no order items
def recent_orders(username):
    login(username)
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
    
    if not session.get('username'):
        session['username'] = username
        print session['username']

    orders = functions.getRecentOrders(conn,username)
    items = functions.getOrderItems(conn,username)
    user = functions.getUser(conn,username)
    return render_template('recent_orders.html',orders=orders, items=items, user=user)

@app.route('/cart/', methods=['GET','POST'])
def cart():
    username= session.get('username')
    if not username:
            return redirect(url_for('tabs'))
    form = request.form
    if form:
        form = form.to_dict(flat=False)['miid']
        print form
        functions.addToCart(conn,form,username)
    items = functions.getCart(conn,username)
    user = functions.getUser(conn,username)
    return render_template('shopping_cart_page.html', items = items, user = user)
           

# @app.route('/clearCart/', methods=['POST'])
# def clearCart():
#     flash('not yet implemented')
#     return redirect(url_for('session_cart'))


@app.route('/<username>/payment/', methods=['GET','POST'])
# awesome! idea - maybe we use ajax for this in the alpha/beta version?
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
            flash("Please enter an number.")
            return render_template("payment_page.html")
            
        # make sure the employee enters a payment method
        if method == None:
            flash("Please select a payment method.")
            return render_template("payment_page.html")
            
        #calculates the user's new balance and updates the database
        newBalance = functions.makePayment(conn,username,method,amount)
        name = functions.getUser(conn,username)['name']
        flash(name + " made a payment of $" + str(amount) + " using " + method + ". Their new balance is $" + str(newBalance) + ".")
        payments = functions.getRecentPayments(conn,username)
        return render_template('payment_page.html', payments=payments, user=username)
                           
if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)

