#!/usr/local/bin/python2.7

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)

from werkzeug import secure_filename
from datetime import timedelta
import sys,os,random,functions
import bcrypt
from werkzeug.datastructures import ImmutableMultiDict

app = Flask(__name__)
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
    if session.get('staffId'):
        session.pop('staffId')
    if session.get('username'):
        session.pop('username')
    return render_template('index.html')

@app.route('/add_staff/',  methods = ['POST','GET'])
def add_staff():
    if not session.get('staffId'):
        return redirect(url_for('index'))
    conn = functions.getConn('tabtracker')
    if request.method=='POST':
        try:
            staffId = request.form.get('username')
            password = request.form.get('password')
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            is_added = functions.addStaffMember(conn,staffId,hashed)
            if staffId == functions.getStaff(conn, staffId)['username']:
                
                return jsonify({'error':False, 'user':staffId})
            else:
                
                return jsonify({'error':False, 'user':staffId})
        except Exception as err:
            flash('form submission error '+str(err))
            return jsonify({'error':True, 'err':err})
    else:
        return render_template('add_staff_page.html')
        

@app.route('/staff_login/',  methods = ['POST'])
# route which processes the staff login and adds the username to the session
def staff_login():
    conn = functions.getConn('tabtracker')
    staffId = request.form['staffId']
    passwd = request.form['pwd']
    row = functions.login(conn,staffId)
    hashed = row['hashed']
    if hashed and bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8')) == hashed:
        flash('successfully logged in as '+staffId)
        session['staffId'] = staffId
        session['currentOrders'] = {}
        return redirect(url_for('tabs'))
    else:
        if not hashed:
            session['staffId'] = staffId
            session['currentOrders'] = {}
            return redirect(url_for('tabs'))
        flash("incorrect login credentials!")
        return redirect(url_for('index'))
    
@app.route('/staff_logout/', methods = ['POST'])
# rotue which processes the staff logout and removes the username from the session
def staff_logout():
    conn = functions.getConn('tabtracker')
    session.pop('staffId')
    print "Logging Out of Staff Account"
    return redirect(url_for('index'))

@app.route('/tabs/')
# route which renders the user tabs page which all current usernames
def tabs():
    if not session.get('staffId'):
        return redirect(url_for('index'))
    if session.get('username'):
        print leave_tab()
    conn = functions.getConn('tabtracker')
    users = functions.getAllUsers(conn)
    return render_template('userTabs.html', users=users)
    
@app.route('/menu/', methods = ['POST', 'GET'])
#route which renders the menu page which all current menu items
def order():
    if not session.get('staffId'):
        return redirect(url_for('index'))
    conn = functions.getConn('tabtracker')
    if request.method=='POST':
        miid = request.form.get('miid')
        ingred = functions.getIngredients(conn,miid)
        print ingred
        extra = functions.getAllIngredients(conn)
        
        return jsonify({'ingred':ingred, 'extra':extra})
    items = functions.getAllMenuItems(conn)
    return render_template('order_form.html', items=items)

@app.route('/access_tab', methods = ['POST'])
# route which processes access to the selected user's tab, adding the username to the session and creating a sesion id for the session
def access_tab(username):
    if not session.get('staffId'):
        return redirect(url_for('index'))
    print username
    conn = functions.getConn('tabtracker')
    #sessId = functions.newSession(conn,username)
    session['username'] = username
    #session['sessId'] = sessId
    menu = functions.getAllMenuItems(conn)
    session['cart'] = {}
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
    if not session.get('staffId'):
        return redirect(url_for('index'))
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
            if session['username'] in session['currentOrders']:
                session['currentOrders'][session['username']].update(session['cart'])
            else:
                session['currentOrders'][session['username']] = session['cart']
            print session['currentOrders'][session['username']]
            clearCart()
            return render_template('recent_orders.html',orders=orders, items=items, user=user)
        else:
            return redirect(request.referrer)

    orders = functions.getRecentOrders(conn,username)
    items = functions.getOrderItems(conn,username)
    user = functions.getUser(conn,username)
    return render_template('recent_orders.html',orders=orders, items=items, user=user)

@app.route('/current_orders/',  methods = ['POST', 'GET'])
# creates order, adds selected menu items to cart
# add safeguard so you don't create an order with no order items
# delete orders with no order items
def current_orders():
    if not session.get('staffId'):
        return redirect(url_for('index'))
    if request.method=="POST":
        username = request.form.get('username')
        print session['currentOrders']
        session['currentOrders'][username].pop()
        print session['currentOrders']
        return jsonify({'success':True})
    print session['currentOrders']
    return render_template('current_orders_page.html')

@app.route('/cart/', methods=['GET','POST'])
# keeps track of all selected menu items for current session and renders cart template
def cart():
    if not session.get('staffId'):
        return redirect(url_for('index'))
    print session['cart']
    conn = functions.getConn('tabtracker')
    cart  = session['cart']
    if request.method == 'POST':
        miid=request.form.get('miid')
        if request.form.get('quantity'):
            newQuantity=request.form.get('quantity')
            if int(newQuantity)==0:
                cart.pop(miid)
                print "item removed from cart!"
                session['cart'] = cart
                return jsonify({'miid':miid,'quantity':True})
            cart[miid]['quantity'] = newQuantity
            cq = cart[miid]['quantity']
            print cart
            session['cart'] = cart
            return jsonify({'miid':miid,'quantity':cq})
        item = functions.getMenuItem(conn,miid)
        if miid in cart:
            cart[miid]['quantity'] += 1
        else:
            #extras = {}
            item['extras'] = {}
            print item
            cart[miid] = item
        print cart
        session['cart'] = cart
        return jsonify(item)
    
    return render_template('shopping_cart_page.html')
    
@app.route('/clearCart/', methods=['POST'])
def clearCart():
    if not session.get('staffId'):
        return redirect(url_for('index'))
    conn = functions.getConn('tabtracker')
    session['cart']={}
    return redirect(url_for('cart'))

@app.route('/<username>/payment/', methods=['GET','POST'])
# accesses payment history for selected user and allows payments to be made to user's tab balance
def payment(username):
    if not session.get('staffId'):
        return redirect(url_for('index'))
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
        if not method:
            return jsonify({'error':True, 'err': "Please select a payment method."})
            
        # make sure new payment will not drop balance below 0
        currentBalance = functions.getUser(conn,username)['balanceOwed']
        if(currentBalance - amount < 0):
            return jsonify({'error':True, 'err': "Please enter an amount that is less than the current balance."})
            
        #calculates the user's new balance and updates the database
        newBalance = functions.makePayment(conn,username,method,amount,dt)
        name = user['name']
        print name
        payments = functions.getRecentPayments(conn,username)

        try:
            method=request.form.get('method')
            amount=request.form.get('amount')
            print(method,amount)
            return jsonify({'error':False,'method':method,'amount':amount,'newBalance':newBalance,'user':name,'dt':dt})
        except Exception as err:
            return jsonify({'error':True, 'err':str(err)})

@app.route('/inventory/', methods = ['GET','POST'])
def inventory():
    conn = functions.getConn('tabtracker')
    categories = functions.getIngredientKinds(conn)
    ingredients = functions.getAllIngredients(conn)
    if request.method == 'GET':
        return render_template('inventory.html',kinds=categories,ingredients=ingredients)
    elif request.method == 'POST':
        ingred_id = request.form.get('ingredient')
        quantity = request.form.get('quantity')
        try:
            # convert to float to type check and to insert into database
            quantity = int(quantity)
        except ValueError:
            return jsonify({'error':True, 'err':"Please enter an integer."})
        # make sure the employee enters an ingredient
        if not ingred_id:
            return jsonify({'error':True, 'err': "Please select an ingredient."})
        
        ingredient = functions.updateQuantity(conn,ingred_id,quantity)
        return jsonify({'error':False,'name':ingredient['name'],'quantity':ingredient['quantity'],'ingred_id':ingredient['iid']})
        
                           
if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8080)

