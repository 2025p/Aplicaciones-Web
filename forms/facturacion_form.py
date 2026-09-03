from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class FacturacionForm(FlaskForm):
    nombre = StringField('Nombre Completo', validators=[
        DataRequired(message="El nombre es obligatorio."),
        Length(min=3, max=100)
    ])
    cedula = StringField('Identificación / Cédula', validators=[
        DataRequired(message="La cédula es obligatoria."),
        Length(min=10, max=13)
    ])
    direccion = StringField('Dirección Exacta', validators=[
        DataRequired(message="La dirección es obligatoria.")
    ])
    telefono = StringField('Número de Contacto', validators=[
        DataRequired(message="El teléfono es obligatorio.")
    ])
    
    # Campos opcionales para la prenda elegida
    producto = StringField('Producto')
    cantidad = StringField('Cantidad')
    talla = StringField('Talla')
    
    submit = SubmitField('Confirmar y Enviar Pedido 🚀')