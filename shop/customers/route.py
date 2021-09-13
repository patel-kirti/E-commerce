from flask import render_template,session, request,redirect,url_for,flash,current_app,make_response
from flask_login import login_required, current_user, logout_user, login_user
from shop import app, db, bcrypt, login_manager
from .forms import CustomerRegisterForm, CustomerLoginFrom
from .model import Register, CustomerOrder
import secrets
import os,  json
import pdfkit, stripe
from shop.products.models import Addproducts,Brand,Category

def brands():
    brands=Brand.query.join(Addproducts,(Brand.id==Addproducts.brand_id)).all()
    return brands

def cat():
    cat=Category.query.join(Addproducts,(Category.id==Addproducts.category_id)).all()
    return cat


plishable_key = 'pk_test_MaILxTYQ15v5Uhd6NKI9wPdD00qdL0QZSl'

stripe.api_key = 'sk_test_tR3PYbcVNZZ796tH88S4VQ2u'


@app.route('/payment',methods=['POST'])
def payment():
    invoice = request.form.get('invoice')
    amount = request.form.get('amount')
    customer = stripe.Customer.create(
      email=request.form['stripeEmail'],
    #   source=request.form['stripeToken'],
    source="tok_visa",
    )
    charge = stripe.Charge.create(
      customer=customer.id,
      description='Myshop',
      amount=amount,
      currency='inr',
    )
    orders =  CustomerOrder.query.filter_by(customer_id = current_user.id,invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status = 'Paid'
    db.session.commit()
    return redirect(url_for('thanks'))



@app.route('/thanks')
def thanks():
    return render_template('customer/thank.html')
    

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data, username=form.username.data, email=form.email.data, password=hash_password,
                            country=form.country.data, city=form.city.data, contact=form.contact.data, address=form.address.data, zipcode=form.zipcode.data)
        db.session.add(register)
        flash(f'Welcome {form.name.data} Thank you for registering', 'success')
        db.session.commit()
        return redirect(url_for('customerLogin'))
    return render_template('customer/register.html', form=form)


@app.route('/customer/login', methods=['GET', 'POST'])
def customerLogin():
    form = CustomerLoginFrom()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You are login now!', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Incorrect email and password', 'danger')
        return redirect(url_for('customerLogin'))

    return render_template('customer/login.html', form=form)


@app.route('/customer/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('home'))

#Remove un-wanted details from shoping cart
def updateshopingcart():
    for _key, product in session['ShopingCart'].items():
        session.modified=True
        del product['image']
        del product['colors']
    return updateshopingcart

@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        updateshopingcart()
        try:
            order = CustomerOrder(
                invoice=invoice, customer_id=customer_id, orders=session['ShopingCart'])
            db.session.add(order)
            db.session.commit()
            session.pop('ShopingCart')
            flash('Your order has been sent', 'success')
            return redirect(url_for('orders', invoice=invoice,brands=brands(),cat=cat()))
        except Exception as e:
            print(e)
            flash('Some thing went to wrong while get order', 'danger')
            return redirect(url_for('getCart'))


@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(
            customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (product['discount']/100) * float(product['price'])
            subTotal += float(product['price']) * int(product['stock'])
            subTotal -= discount
            tax = ("%.2f" % (.06*float(subTotal)))
            grandTotal = ("%.2f" % (1.06* float(subTotal)))
    else:
        return redirect(url_for('customerLogin'))
    return render_template('customer/order.html', invoice=invoice, tax=tax, subTotal=subTotal, grandTotal=grandTotal, customer=customer, orders=orders,brands=brands(),cat=cat())


@app.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        if request.method =="POST":
            customer = Register.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
            for _key, product in orders.orders.items():
                discount = (product['discount']/100) * float(product['price'])
                subTotal += float(product['price']) * int(product['stock'])
                subTotal -= discount
                tax = ("%.2f" % (.06 * float(subTotal)))
                grandTotal = float("%.2f" % (1.06 * subTotal))
                
            # config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')  
            rendered =  render_template('customer/pdf.html', invoice=invoice, tax=tax,grandTotal=grandTotal,customer=customer,orders=orders)
            pdf = pdfkit.from_string(rendered, False)
            response = make_response(pdf)
            response.headers['Content-Type'] ='application/pdf'
            response.headers['Content-Disposition'] ='inline; filename='+invoice+'.pdf'
            return response
    return request(url_for('orders'))
