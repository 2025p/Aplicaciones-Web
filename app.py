import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

# Importación de formularios desde la carpeta /forms
from forms.producto_form import ProductoForm
from forms.facturacion_form import FacturacionForm

app = Flask(__name__)

# Clave obligatoria para la seguridad CSRF y Flask-WTF
app.config['SECRET_KEY'] = 'mi_clave_secreta_123'

# Configuración de la base de datos SQLite en la carpeta /data
DB_DIR = os.path.join(app.root_path, 'data')
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'tienda_ropa.db')


def init_db():
    """Inicializa la base de datos y crea las tablas requeridas si no existen."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabla de Productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')

    # Tabla de Pedidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT NOT NULL,
            direccion TEXT NOT NULL,
            telefono TEXT NOT NULL,
            producto TEXT,
            cantidad TEXT,
            talla TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabla de Contacto / Mensajes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL,
            asunto TEXT,
            mensaje TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


# Inicializar base de datos al arrancar
init_db()


# -------------------------------------------------------------------------
# RUTAS DE NAVEGACIÓN Y VISTAS
# -------------------------------------------------------------------------

@app.route('/')
@app.route('/inicio')
def inicio():
    """Página principal de la tienda."""
    return render_template('index.html')


@app.route('/productos')
def productos():
    """Lista los productos almacenados en SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, precio, stock FROM productos')
    lista_productos = cursor.fetchall()
    conn.close()
    return render_template('productos.html', productos=lista_productos)


@app.route('/catalogo')
def catalogo():
    """Muestra el catálogo con el modal de facturación/pedido listo."""
    form = FacturacionForm()
    return render_template('catalogo.html', form=form)


@app.route('/stock')
def stock():
    """Muestra la vista de stock/inventario."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, precio, stock FROM productos')
    lista_stock = cursor.fetchall()
    conn.close()
    return render_template('stock.html', productos=lista_stock)


@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    """Muestra la vista de contacto y guarda los mensajes recibidos."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        asunto = request.form.get('asunto')
        mensaje = request.form.get('mensaje')

        if nombre and correo and mensaje:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO contactos (nombre, correo, asunto, mensaje)
                VALUES (?, ?, ?, ?)
            ''', (nombre, correo, asunto, mensaje))
            conn.commit()
            conn.close()

            flash('¡Gracias por contactarnos! Tu mensaje ha sido enviado.', 'success')
            return redirect(url_for('contacto'))
        else:
            flash('Por favor, completa todos los campos obligatorios.', 'warning')

    return render_template('contacto.html')


# -------------------------------------------------------------------------
# RUTAS DE GESTIÓN (FORMULARIOS, PEDIDOS Y ELIMINACIÓN)
# -------------------------------------------------------------------------

@app.route('/formulario_producto', methods=['GET', 'POST'])
def formulario_producto():
    """Agrega un nuevo producto mediante WTForms."""
    form = ProductoForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        precio = form.precio.data
        stock = form.stock.data

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)',
            (nombre, precio, stock)
        )
        conn.commit()
        conn.close()

        flash('¡Producto guardado exitosamente en SQLite!', 'success')
        return redirect(url_for('productos'))

    return render_template('formulario_producto.html', form=form)


@app.route('/eliminar_producto/<int:id>', methods=['POST'])
def eliminar_producto(id):
    """Elimina un producto por su ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM productos WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('¡Producto eliminado exitosamente!', 'danger')
    return redirect(url_for('productos'))


@app.route('/guardar_pedido', methods=['POST'])
def guardar_pedido():
    """Procesa y guarda los datos de la compra/pedido enviado desde el modal."""
    form = FacturacionForm()

    if form.validate_on_submit():
        nombre = form.nombre.data
        cedula = form.cedula.data
        direccion = form.direccion.data
        telefono = form.telefono.data

        # Extracción de campos ocultos del producto
        producto = request.form.get('producto', '')
        cantidad = request.form.get('cantidad', '')
        talla = request.form.get('talla', '')

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pedidos (nombre, cedula, direccion, telefono, producto, cantidad, talla) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, cedula, direccion, telefono, producto, cantidad, talla))

        conn.commit()
        conn.close()

        flash('¡Pedido registrado y enviado a entrega con éxito!', 'success')
        return redirect(url_for('catalogo'))

    flash('Hubo un error al procesar tu pedido. Verifica los datos ingresados.', 'danger')
    return redirect(url_for('catalogo'))


@app.route('/pedidos')
def ver_pedidos():
    """Lista todos los pedidos recibidos."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pedidos ORDER BY id DESC')
    lista_pedidos = cursor.fetchall()
    conn.close()

    return render_template('pedidos.html', pedidos=lista_pedidos)


if __name__ == '__main__':
    app.run(debug=True)