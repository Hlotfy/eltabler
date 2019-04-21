#!/usr/local/bin/python2.7

from flask import Flask, render_template, make_response, request, redirect, flash, url_for, session
app = Flask(__name__)

app.secret_key = 'rosebud'

@app.route('/')
def index():
    return redirect( url_for('session_cart') )


@app.route('/session/cart', methods=['GET','POST'])
def session_cart():
    cart = session.get('cart', {'beer':0, 'wine':0, 'soda':0}) # use these defaults if cart isn't in session
    ofage = session.get('iam21',False)
    if request.method == 'POST' and request.form.get('submit') == 'Show Cart':
        flash("Showing your cart's contents")
        return render_template('cart-template.html',cartContents=True,cart=cart)
    elif request.method == 'POST':
        item = request.form.get('itemid')
        if not ofage and item in ['beer','wine']:
            flash('Sorry, you are not of age')
        else:
            cart[item] += 1
            flash('Thank you for buying a glass of '+item)
            session['cart'] = cart # store the updated cart
    return render_template('cart-template.html',
                           cartContents=False,
                           cart=cart)

@app.route('/iam21/', methods=['POST'])
def iam21():
    session['iam21'] = True
    flash('Trusting that you are of age')
    return redirect(url_for('session_cart'))

@app.route('/clearCart', methods=['POST'])
def clearCart():
    session['cart'] = {'beer':0, 'wine':0, 'soda':0}
    session['iam21'] = False
    flash('Cart cleared')
    return redirect(url_for('session_cart'))
    
    


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)
