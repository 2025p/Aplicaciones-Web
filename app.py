import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# Importación de formularios desde la carpeta /forms
from forms.producto_form import ProductoForm
from forms.facturacion_form import FacturacionForm

# Importación centralizada de la conexión a PostgreSQL
from conexion.conexion import obtener_conexion

app = Flask(__name__)

# Clave obligatoria para la seguridad CSRF y Flask-WTF
app.config['SECRET_KEY'] = 'mi_clave_secreta_1234'


def init_db():
    """Inicializa la base de datos PostgreSQL y crea las tablas requeridas si no existen."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        # Tabla de Proveedores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proveedores (
                id_proveedor SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                telefono VARCHAR(20),
                correo VARCHAR(100)
            );
        ''')

        # Tabla de Productos / Ropa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                precio NUMERIC(10, 2) NOT NULL,
                stock INT NOT NULL,
                id_proveedor INT REFERENCES proveedores(id_proveedor) ON DELETE SET NULL
            );
        ''')

        # Tabla de Pedidos / Compras
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                cedula VARCHAR(20) NOT NULL,
                direccion TEXT NOT NULL,
                telefono VARCHAR(20) NOT NULL,
                producto VARCHAR(100),
                cantidad VARCHAR(50),
                talla VARCHAR(10),
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # Tabla de Contacto / Mensajes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contactos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                correo VARCHAR(100) NOT NULL,
                asunto VARCHAR(150),
                mensaje TEXT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # Tabla de Stock (Registros de Prendas)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock (
                id SERIAL PRIMARY KEY,
                prenda VARCHAR(100) NOT NULL,
                cantidad VARCHAR(50) NOT NULL,
                categoria VARCHAR(50) NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        conn.commit()
        cursor.close()
        conn.close()
        print("¡Base de datos inicializada correctamente!")
    except Exception as e:
        mensaje_error = str(e).encode('utf-8', errors='ignore').decode('utf-8')
        print(f"\n================ ERROR DE CONEXIÓN ================\n{mensaje_error}\n===================================================\n")


# Inicializar base de datos al arrancar la aplicación
init_db()


# RUTAS DE NAVEGACIÓN Y VISTAS


@app.route('/')
@app.route('/inicio')
def inicio():
    """Página principal de la tienda."""
    return render_template('index.html')


@app.route('/productos')
def productos():
    """Lista los productos almacenados en PostgreSQL (SELECT)."""
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, precio, stock FROM productos ORDER BY id ASC')
    lista_productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('productos.html', productos=lista_productos)


@app.route('/catalogo')
def catalogo():
    """Muestra el catálogo con el modal de facturación/pedido listo."""
    form = FacturacionForm()
    return render_template('catalogo.html', form=form)


@app.route('/stock')
def stock():
    """Muestra la vista de stock/inventario desde la tabla stock o productos."""
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT id, prenda, cantidad, categoria, fecha_registro FROM stock ORDER BY id DESC')
    lista_stock = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('stock.html', productos=lista_stock)


@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    """Muestra la vista de contacto y guarda los mensajes recibidos."""
    if request.method == 'POST':
        # Permite recibir tanto JSON (fetch/AJAX) como Formulario HTML tradicional
        data = request.get_json(silent=True) or request.form

        nombre = data.get('nombre')
        correo = data.get('correo')
        asunto = data.get('asunto')
        mensaje = data.get('mensaje')

        if nombre and correo and mensaje:
            conn = None
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()
                
                # INSERT con fecha actual explícita (NOW())
                cursor.execute('''
                    INSERT INTO contactos (nombre, correo, asunto, mensaje, fecha)
                    VALUES (%s, %s, %s, %s, NOW())
                ''', (nombre, correo, asunto, mensaje))
                
                conn.commit()
                cursor.close()

                # Si la petición vino por AJAX / JSON, responde JSON
                if request.is_json:
                    return jsonify({'success': True, 'message': '¡Gracias por contactarnos! Tu mensaje ha sido enviado.'})

                flash('¡Gracias por contactarnos! Tu mensaje ha sido enviado.', 'success')
            except Exception as e:
                if conn:
                    conn.rollback()
                print("Error en base de datos al guardar contacto:", e) # Ver error en la terminal de Python
                
                if request.is_json:
                    return jsonify({'success': False, 'message': f'Error al enviar mensaje: {str(e)}'}), 500

                flash(f'Error al enviar el mensaje: {e}', 'danger')
            finally:
                if conn:
                    conn.close()

            return redirect(url_for('contacto'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Por favor, completa todos los campos obligatorios.'}), 400
            
            flash('Por favor, completa todos los campos obligatorios.', 'warning')

    return render_template('contacto.html')


# RUTAS DE GESTIÓN (CRUD COMPLETO SOBRE POSTGRESQL)


@app.route('/guardar_stock', methods=['POST'])
def guardar_stock():
    """Guarda en lote las prendas ingresadas desde la interfaz de Stock."""
    datos = request.get_json()
    prendas = datos.get('prendas', [])
    
    if not prendas:
        return jsonify({'success': False, 'message': 'No hay prendas enviadas'}), 400

    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        for p in prendas:
            cursor.execute('''
                INSERT INTO stock (prenda, cantidad, categoria)
                VALUES (%s, %s, %s)
            ''', (p.get('prenda'), p.get('cantidad'), p.get('categoria')))
            
        conn.commit()
        cursor.close()
        return jsonify({'success': True, 'message': 'Prendas guardadas exitosamente en PostgreSQL.'})
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if conn:
            conn.close()


@app.route('/formulario_producto', methods=['GET', 'POST'])
def formulario_producto():
    """Agrega un nuevo producto mediante WTForms y PostgreSQL (INSERT)."""
    form = ProductoForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        precio = form.precio.data
        stock = form.stock.data

        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s)',
            (nombre, precio, stock)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash('¡Producto guardado exitosamente en PostgreSQL!', 'success')
        return redirect(url_for('productos'))

    return render_template('formulario_producto.html', form=form)


@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    """Edita un producto existente (UPDATE)."""
    conn = obtener_conexion()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT id, nombre, precio, stock FROM productos WHERE id = %s', (id,))
        prod = cursor.fetchone()
        cursor.close()
        conn.close()

        if prod:
            form = ProductoForm(data=prod)
            return render_template('formulario_producto.html', form=form, editando=True)
        
        flash('El producto solicitado no existe.', 'warning')
        return redirect(url_for('productos'))

    form = ProductoForm()
    if form.validate_on_submit():
        cursor.execute(
            'UPDATE productos SET nombre = %s, precio = %s, stock = %s WHERE id = %s',
            (form.nombre.data, form.precio.data, form.stock.data, id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash('¡Producto actualizado exitosamente!', 'info')
        return redirect(url_for('productos'))

    cursor.close()
    conn.close()
    return render_template('formulario_producto.html', form=form, editando=True)


@app.route('/eliminar_producto/<int:id>', methods=['POST'])
def eliminar_producto(id):
    """Elimina un producto por su ID (DELETE)."""
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM productos WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('¡Producto eliminado exitosamente!', 'danger')
    return redirect(url_for('productos'))


@app.route('/guardar_pedido', methods=['POST'])
def guardar_pedido():
    """Procesa y guarda los datos del pedido enviado desde el modal (INSERT)."""
    nombre = request.form.get('nombre')
    cedula = request.form.get('cedula')
    direccion = request.form.get('direccion')
    telefono = request.form.get('telefono')
    producto = request.form.get('producto', '')
    cantidad = request.form.get('cantidad', '')
    talla = request.form.get('talla', '')

    if nombre and cedula and direccion and telefono:
        conn = None
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO pedidos (nombre, cedula, direccion, telefono, producto, cantidad, talla) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (nombre, cedula, direccion, telefono, producto, cantidad, talla))

            conn.commit()
            cursor.close()
            flash('¡Pedido registrado y enviado a entrega con éxito!', 'success')
        except Exception as e:
            if conn:
                conn.rollback()
            flash(f'Error al registrar el pedido: {e}', 'danger')
        finally:
            if conn:
                conn.close()
        return redirect(url_for('catalogo'))

    flash('Hubo un error al procesar tu pedido. Verifica que los campos obligatorios estén llenos.', 'danger')
    return redirect(url_for('catalogo'))


@app.route('/pedidos')
def ver_pedidos():
    """Lista todos los pedidos recibidos (SELECT)."""
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, cedula, direccion, telefono, producto, cantidad, talla, fecha FROM pedidos ORDER BY id DESC')
    lista_pedidos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('pedidos.html', pedidos=lista_pedidos)


if __name__ == '__main__':
    app.run(debug=True)