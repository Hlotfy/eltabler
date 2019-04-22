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

@app.route('/tabs/',  methods=['GET','POST'])
def tabs():
    if request.method == 'GET':
        users = functions.getAllUsers(conn)
        return render_template('userTabs.html', users=users)
    
@app.route('/order/', methods = ['POST', 'GET'])
def order():
    items = functions.getAllMenuItems(conn)
    return render_template('order_form.html', items=items)
    
    
@app.route('/menu/')
def menu():
    users = functions.getAllUsers(conn)
    return render_template('menuScreen.html')

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

@app.route('/cart/')
def cart():
    users = functions.getAllUsers(conn)
    return render_template('shoppingCart.html', users=users)

@app.route('/session/cart/', methods=['GET','POST'])
def session_cart():
    users = functions.getAllUsers(conn)
    cart = session.get('cart', {'beer':0, 'wine':0, 'soda':0}) # use these defaults if cart isn't in session
    # ofage = session.get('iam21',False)
    # if request.method == 'POST' and request.form.get('submit') == 'Show Cart':
    #     flash("Showing your cart's contents")
    #     return render_template('cart-template.html',cartContents=True,cart=cart)
    # elif request.method == 'POST':
    #     item = request.form.get('itemid')
    #     if not ofage and item in ['beer','wine']:
    #         flash('Sorry, you are not of age')
    #     else:
    #         cart[item] += 1
    #         flash('Thank you for buying a glass of '+item)
    #         session['cart'] = cart # store the updated cart
    return render_template('shopping-cart-example.html',
                           cartContents=False,
                           cart=cart,
                           users = users)

@app.route('/clearCart/', methods=['POST'])
def clearCart():
    flash('not yet implemented')
    return redirect(url_for('session_cart'))


@app.route('/<username>/payment/', methods=['GET','POST'])
# awesome! idea - maybe we use ajax for this in the alpha/beta version?
def payment(username):
    if request.method == 'GET':
        payments = functions.getRecentPayments(conn,username)
        return render_template('payment_page.html', payments=payments)
        
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
        return render_template('payment_page.html',payments=payments)
    
@app.route('/addToTab/', methods=['POST'])
# should we maybe just redirect to my recent_payments page?
def addToTab():
    flash('not yet implemented')
    return redirect(url_for('session_cart'))
                           
if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)

