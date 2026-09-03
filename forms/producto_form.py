from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del Producto', validators=[
        DataRequired(message="El nombre es obligatorio."),
        Length(min=2, max=100, message="Debe tener entre 2 y 100 caracteres.")
    ])
    precio = FloatField('Precio ($)', validators=[
        DataRequired(message="Ingrese un precio válido."),
        NumberRange(min=0.01, message="El precio debe ser positivo.")
    ])
    stock = IntegerField('Stock', validators=[
        DataRequired(message="Ingrese la cantidad."),
        NumberRange(min=0, message="El stock no puede ser negativo.")
    ])
    submit = SubmitField('Guardar Producto')