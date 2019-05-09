#!/usr/local/bin/python2.7

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
#from werkzeug imdport secure_filename
app = Flask(__name__)

from datetime import timedelta
import sys,os,random,functions
from werkzeug.datastructures import ImmutableMultiDict

app.secret_key = 'asdflsgflawiewurhe'

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# @app.before_request
# def make_session_permanent():
#     session.permanent = True
#     app.permanent_session_lifetime = timedelta(minutes=1)

@app.route('/')
# the index page of the app, which includes the staff login form
def index():
    conn = functions.getConn('tabtracker')
    return render_template('index.html')

@app.route('/staff_login',  methods = ['POST'])
# route which processes the staff login and adds the username to the session
def staff_login():
    conn = functions.getConn('tabtracker')
    #form = request.form
    #print form
    staffId = request.form['staffId']
    isStaff = functions.login(conn,staffId)
    if isStaff:
        session['staffId'] = staffId
        flash("login successful! welcome ", staffId)
        return redirect(url_for('tabs'))
    else:
        flash("login unsuccessful!")
        return redirect(url_for('index'))
    
@app.route('/staff_logout', methods = ['POST'])
# rotue which processes the staff logout and removes the username from the session
def staff_logout():
    conn = functions.getConn('tabtracker')
    session.pop('staffId')
    print "Logging Out of Staff Account"
    return redirect(url_for('index'))

@app.route('/tabs/')
# route which renders the user tabs page which all current usernames
def tabs():
    if session.get('username'):
        print leave_tab()
    conn = functions.getConn('tabtracker')
    users = functions.getAllUsers(conn)
    return render_template('userTabs.html', users=users)
    
@app.route('/menu/', methods = ['POST', 'GET'])
#route which renders the menu page which all current menu items
def order():
    conn = functions.getConn('tabtracker')
    items = functions.getAllMenuItems(conn)
    return render_template('order_form.html', items=items)

@app.route('/access_tab', methods = ['POST'])
# route which processes access to the selected user's tab, adding the username to the session and creating a sesion id for the session
def access_tab(username):
    print username
    conn = functions.getConn('tabtracker')
    #sessId = functions.newSession(conn,username)
    session['username'] = username
    #session['sessId'] = sessId
    menu = functions.getAllMenuItems(conn)
    session['cart'] = {}
    cart = session['cart']
    print cart
    print "accessing the tab of " + session['username'] + "!"
    return redirect(url_for('recent_orders', username=session['username']))

@app.route('/leave_tab', methods = ['POST'])
def leave_tab():
    conn = functions.getConn('tabtracker')
    if session.get('username'):
        session.pop('username')
        print "leaving user tab!"
    return redirect(url_for('tabs'))

@app.route('/<username>/recent_orders/',  methods = ['POST', 'GET'])
# creates order, adds selected menu items to cart
# add safeguard so you don't create an order with no order items
# delete orders with no order items
def recent_orders(username):
    conn = functions.getConn('tabtracker')
    if not session.get('username'):
        access_tab(username)
    if request.method == 'POST':
        
        form = request.form.to_dict(flat=False)
        if form:
            print form
            form = [{form.keys()[j]: form.values()[j][i] for j in range(len(form))} for i in range(len(form.values()[0]))]
            print form
            
            functions.addOrder(conn,form,username)
            orders = functions.getRecentOrders(conn,username)
            items = functions.getOrderItems(conn,username)
            user = functions.getUser(conn,username)
            clearCart()
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
    conn = functions.getConn('tabtracker')
    cart  = session['cart']
    if request.method == 'POST':
        cart  = session['cart']
        print session['cart']
        # form = request.form[0] #.to_dict(flat=True)
        # print form
        miid = request.form.get('miid')
        # name = request.form.get('name')
        # price = request.form.get('price')
        item = functions.getMenuItem(conn,miid)
        if miid in cart:
            cart[miid]['quantity'] += 1
        else:
            cart[miid] = item
        print cart
        # item = functions.getMenuItem(conn,miid)
        session['cart'] = cart
        return jsonify(item)
    # else:
        # cartCont = {}
        # for item in session['cart']:
        #     cartCont[item] = functions
    
    return render_template('shopping_cart_page.html')
    
@app.route('/clearCart', methods=['POST'])
def clearCart():
    conn = functions.getConn('tabtracker')
    menu = functions.getAllMenuItems(conn)
    session['cart'] = {}
    return redirect(request.referrer)

@app.route('/<username>/payment/', methods=['GET','POST'])
# accesses payment history for selected user and allows payments to be made to user's tab balance
def payment(username):
    conn = functions.getConn('tabtracker')
    user = functions.getUser(conn,username)
    if request.method == 'GET':
        payments = functions.getRecentPayments(conn,username)
            
        return render_template('payment_page.html', payments=payments, user=user)
        
    else: #method must be 'POST'
        #get the payment amount and method
        amount = request.form.get('amount')
        method = request.form.get('method')
        dt = request.form.get('dt')
        print "request dt: ", dt
        
        try:
            # convert to float to type check and to insert into database
            amount = float(amount)
        except ValueError:
            return jsonify({'error':True, 'err':"Please enter an number."})
            
        # make sure the employee enters a payment method
        if method == '':
            return jsonify({'error':True, 'err': "Please select a payment method."})
            
        #calculates the user's new balance and updates the database
        newBalance = functions.makePayment(conn,username,method,amount)
        name = functions.getUser(conn,username)['name']
        payments = functions.getRecentPayments(conn,username)

        try:
            method=request.form.get('method')
            amount=request.form.get('amount')
            print(method,amount)
            return jsonify({'error':False,'method':method,'amount':amount,'newBalance':newBalance,'user':name,'dt':dt})
        except Exception as err:
            return jsonify({'error':True, 'err':str(err)})
        
                           
if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)

