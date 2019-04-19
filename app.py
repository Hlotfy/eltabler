#!/usr/local/bin/python2.7

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
#from werkzeug import secure_filename
app = Flask(__name__)

import sys,os,random,functions

app.secret_key = 'asdflsgflawiewurhe'

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
conn = functions.getConn('tabtracker')


@app.route('/')
def index():
    return redirect( url_for('menu') )
    
@app.route('/tabs')
def tabs():
    users = functions.getAllUsers(conn)
    return render_template('userTabs.html', users=users)
    
@app.route('/menu')
def menu():
    users = functions.getAllUsers(conn)
    return render_template('menuScreen.html')

@app.route('/cart')
def cart():
    users = functions.getAllUsers(conn)
    return render_template('shoppingCart.html', users=users)

@app.route('/session/cart', methods=['GET','POST'])
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

@app.route('/clearCart', methods=['POST'])
def clearCart():
    flash('not yet implemented')
    return redirect(url_for('session_cart'))

@app.route('/addToTab', methods=['POST'])
def addToTab():
    flash('not yet implemented')
    return redirect(url_for('session_cart'))
                           
if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)

