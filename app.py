#!/usr/local/bin/python2.7

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
import functions
#from werkzeug import secure_filename
app = Flask(__name__)

import sys,os,random,functions

app.secret_key = 'asdflsgflawiewurhe'

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
conn = functions.getConn('tabtracker')



@app.route('/tabs')
def tabs():
    users = functions.getAllUsers(conn)
    return render_template('userTabs.html', users=users)
    
@app.route('/menu')
def menu():
    users = functions.getAllUsers(conn)
    return render_template('menuScreen.html')
    
@app.route('/<username>/payment/', methods=['GET','POST'])
def payment(username):
    if request.method == 'GET':
        return render_template('payment_page.html')
        
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
    

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)

