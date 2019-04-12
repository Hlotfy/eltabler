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

@app.route('/tabs')
def tabs():
    users = functions.getAllUsers(conn)
    return render_template('userTabs.html', users=users)
    
@app.route('/menu')
def menu():
    users = functions.getAllUsers(conn)
    return render_template('menuScreen.html')
    

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)

