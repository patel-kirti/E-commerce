from flask import render_template,session, request,redirect,url_for,flash
from shop import app,db,bcrypt
from .forms import RegistrationForm,Loginform
from .models import User
from shop.products.models import Addproducts,Brand,Category
import os
from flask_login import login_required, current_user, logout_user, login_user



@app.route('/admin')
def admin():
    print(session)
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    products=Addproducts.query.all()
    return render_template('admin/index.html', title='Admin page',products=products)

@app.route('/brands')
def brands():
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    brands=Brand.query.order_by(Brand.id.desc()).all()
    return render_template('admin/brand.html',title='Brand page',brands=brands)

@app.route('/category')
def category():
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    categories=Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/brand.html',title='Category page',categories=categories)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = User(name=form.name.data,username=form.username.data, email=form.email.data,
                    password=hash_password)
        db.session.add(user)
        flash(f'welcome {form.name.data} Thanks for registering','success')
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('admin/register.html',title='Register user', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    form = Loginform()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            flash(f'welcome {form.email.data} you are logedin now','success')
            return redirect(url_for('admin'))
        else:
            flash(f'Wrong email and password', 'warning')
            return redirect(url_for('login'))
    return render_template('admin/login.html',title='Login page',form=form)


@app.route('/admin/logout')
def admin_logout():
    logout_user()
    return redirect(url_for('home'))