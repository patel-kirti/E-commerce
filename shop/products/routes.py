from shop.admin.routes import brands
from flask import render_template, request, redirect, url_for, flash, session, current_app
from shop import db, app, photos, search
from .models import Brand, Category, Addproducts
from .forms import Addproduct
import secrets, os

def brands():
    brands=Brand.query.join(Addproducts,(Brand.id==Addproducts.brand_id)).all()
    return brands

def cat():
    cat=Category.query.join(Addproducts,(Category.id==Addproducts.category_id)).all()
    return cat

@app.route('/')
def home():
    page=request.args.get('page',1,type=int)
    products=Addproducts.query.filter(Addproducts.stock>0).order_by(Addproducts.id.desc()).paginate(page=page, per_page=8)
    return render_template('products/index.html',title='Home page',products=products,brands=brands(),cat=cat())

@app.route('/result')
def result():
    searchword=request.args.get('q')
    products=Addproducts.query.msearch(searchword,fields=['name','description'], limit=3)
    return render_template('products/result.html',title='Search result',products=products,brands=brands(),cat=cat())

@app.route('/product/<int:id>')
def single_page(id):
    product=Addproducts.query.get_or_404(id)
    return render_template('products/single_page.html',product=product,brands=brands(),cat=cat())

@app.route('/brand/<int:id>')
def get_brand(id):
    get_b=Brand.query.filter_by(id=id).first_or_404()
    page=request.args.get('page',1,type=int)
    brand=Addproducts.query.filter_by(brand=get_b).order_by(Addproducts.id.desc()).paginate(page=page, per_page=4)
    return render_template('products/index.html',title='Brand',brand=brand,brands=brands(),cat=cat(),get_b=get_b)
    
@app.route('/category/<int:id>')
def get_caregory(id):
    get_cat=Category.query.filter_by(id=id).first_or_404()
    page=request.args.get('page',1,type=int)
    get_pro=Addproducts.query.filter_by(category=get_cat).order_by(Addproducts.id.desc()).paginate(page=page, per_page=4)
    return render_template('products/index.html',title='Categorys',get_pro=get_pro,cat=cat(),brands=brands(),get_cat=get_cat)

@app.route('/addbrand', methods=['GET', 'POST'])
def addbrand():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        getbrand = request.form.get('brand')
        brand = Brand(name=getbrand)
        db.session.add(brand)
        flash(f'The Brand {getbrand} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addbrand'))
    return render_template('products/addbrand.html', brand='brand')


@app.route('/addcat', methods=['GET', 'POST'])
def addcat():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        getcat = request.form.get('category')
        cat = Category(name=getcat)
        print(cat)
        db.session.add(cat)
        flash(f'The Brand {getcat} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addcat'))
    return render_template('products/addbrand.html')


@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
    brand = Brand.query.all()
    category = Category.query.all()
    form = Addproduct(request.form)
    if request.method == "POST":
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        color = form.color.data
        description = form.description.data
        brand = request.form.get('brand')
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")

        addpro = Addproducts(name=name, price=price, discount=discount, stock=stock, color=color, description=description,
                             brand_id=brand, category_id=category, image_1=image_1, image_2=image_2, image_3=image_3)
        db.session.add(addpro)
        flash(f'The Product {name} has been added to your database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))

    return render_template('products/addproduct.html', title='Add Product', form=form, brand=brand, category=category)


@app.route('/updatebrand/<int:id>', methods=['GET', 'POST'])
def updatebrand(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method == "POST":
        updatebrand.name = brand
        flash(f'Your brand has been updated', 'success')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('products/updatebrand.html', title='Update Brand', updatebrand=updatebrand)


@app.route('/updatecategory/<int:id>', methods=['GET', 'POST'])
def updatecategory(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    updatecategory = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method == "POST":
        updatecategory.name = category
        flash(f'Your brand has been updated', 'success')
        db.session.commit()
        return redirect(url_for('category'))
    return render_template('products/updatebrand.html', title='Update Brand', updatecategory=updatecategory)


@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    brand = Brand.query.all()
    category = Category.query.all()
    product = Addproducts.query.get_or_404(id)
    
    brands = request.form.get('brand')
    categories = request.form.get('category')

    form = Addproduct(request.form)
    if request.method=="POST":
        product.name=form.name.data
        product.price=form.price.data
        product.discount=form.discount.data
        product.brand_id=brands
        product.category_id=categories
        product.stock=form.stock.data
        product.color=form.color.data
        product.description=form.description.data
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path,"static/images/"+product.image_1))
                product.image_1=photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1=photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
    
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path,"static/images/"+product.image_2))
                product.image_1=photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1=photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path,"static/images/"+product.image_3))
                product.image_1=photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1=photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")  
       
        db.session.commit()
        flash(f'Your product has been updated','success')
        return redirect(url_for('admin'))
        
    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.color.data = product.color
    form.description.data = product.description

    return render_template('products/updateproduct.html', title='Update Product', form=form, brand=brand, category=category, product=product)


@app.route('/deletebrand/<int:id>', methods=['GET','POST'])
def deletebrand(id):
    brands=Brand.query.get_or_404(id)
    if request.method=="POST":
        db.session.delete(brands)
        flash(f'The brand {brands.name} was deleted from your database','success')
        db.session.commit()
        return redirect(url_for('brand'))
    flash(f'The brand {brands.name} cant be deleted','warning')
    return render_template('products/deletebrand.html')
             
            
@app.route('/deletecategory/<int:id>', methods=['POST','GET'])
def deletecategory(id):
    category=Category.query.get_or_404(id)
    if request.method=="POST":
        db.session.delete(category)
        flash(f'The brand {category.name} was deleted from your database','success')
        db.session.commit()
        return redirect(url_for('category'))
    flash(f'The brand {category.name} cant be deleted','warning')
    # return redirect(url_for('admin'))          
    return render_template('products/deletebrand.html')
      
            
            
@app.route('/deleteproduct/<int:id>', methods=['POST','GET'])
def deleteproduct(id):
    product=Addproducts.query.get_or_404(id)
    if request.method=="POST":
        try:
            os.unlink(os.path.join(current_app.root_path,"static/images/"+product.image_1))
            os.unlink(os.path.join(current_app.root_path,"static/images/"+product.image_2))
            os.unlink(os.path.join(current_app.root_path,"static/images/"+product.image_3))
        except Exception as e:
            print(e)
        db.session.delete(product)
        db.session.commit()
        flash(f'The product {product.name} was deleted from your database','success')
        return redirect(url_for('admin'))
    flash(f'The product {product.name} can not be deleted','warning')
    # return redirect(url_for('admin'))
    return render_template('products/deleteproduct.html')
    
    