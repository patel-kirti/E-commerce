from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import Form, IntegerField, validators, StringField, TextAreaField,DecimalField
from .models import Addproducts,Brand,Category
from flask_wtf import FlaskForm



class Addproduct(FlaskForm):
    name = StringField('Name', [validators.DataRequired()])
    price = DecimalField('Price', [validators.DataRequired()])
    discount = IntegerField('Discount', default=0)
    stock = IntegerField('Stock', [validators.DataRequired()])
    description = TextAreaField('Description', [validators.DataRequired()])
    color = TextAreaField('Color', [validators.DataRequired()])

    image_1 = FileField('Image 1', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'image only please')])
    image_2 = FileField('Image 2', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'image only please')])
    image_3 = FileField('Image 3', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'image only please')])
    

