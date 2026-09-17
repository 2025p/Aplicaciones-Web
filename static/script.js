// 1. DECLARACIÓN DE VARIABLES GLOBALES

const form = document.getElementById('form-producto');
const inputNombre = document.getElementById('prod-nombre'); 
const inputCantidad = document.getElementById('prod-cantidad'); // Campo de Docenas
const selectCategoria = document.getElementById('prod-categoria');
const listaContenedor = document.getElementById('lista-productos'); 
const totalRegistros = document.getElementById('total-registros'); 

let catalogoPrendas = [];


// 2. INICIALIZACIÓN DE EVENTOS Y VALIDACIONES

document.addEventListener('DOMContentLoaded', () => {
    if(inputNombre) {
        inputNombre.addEventListener('change', validarNombre);
        inputNombre.addEventListener('blur', validarNombre);
    }
    if(inputCantidad) {
        inputCantidad.addEventListener('change', validarCantidad);
        inputCantidad.addEventListener('blur', validarCantidad);
    }
    if(selectCategoria) {
        selectCategoria.addEventListener('change', validarCategoria);
        selectCategoria.addEventListener('blur', validarCategoria);
    }
    if(form) {
        form.addEventListener('submit', manejarEnvio);
    }
    
    // Asignar evento al formulario de envio/pedido si existe
    const formEnvio = document.getElementById('form-datos-envio');
    if (formEnvio) {
        formEnvio.addEventListener('submit', procesarEnvioBaseDatos);
    }

    renderizarCatalogo();
});


// 3. FUNCIONES DE VALIDACIÓN

function validarNombre() {
    if (!inputNombre || inputNombre.value === "") {
        mostrarError(inputNombre, "Debes seleccionar una prenda de la lista.");
        return false;
    }
    mostrarExito(inputNombre);
    return true;
}

function validarCantidad() {
    if (!inputCantidad || inputCantidad.value === "") {
        mostrarError(inputCantidad, "Debes seleccionar la cantidad en docenas.");
        return false;
    }
    mostrarExito(inputCantidad);
    return true;
}

function validarCategoria() {
    if (!selectCategoria || selectCategoria.value === "") {
        mostrarError(selectCategoria, "Por favor, selecciona una categoría.");
        return false;
    }
    mostrarExito(selectCategoria);
    return true;
}

function mostrarError(elemento, mensaje) {
    if(!elemento) return;
    elemento.classList.remove('is-valid');
    elemento.classList.add('is-invalid');
    const feedback = elemento.nextElementSibling;
    if (feedback && feedback.classList.contains('invalid-feedback')) {
        feedback.textContent = mensaje;
    }
}

function mostrarExito(elemento) {
    if(!elemento) return;
    elemento.classList.remove('is-invalid');
    elemento.classList.add('is-valid');
}


// 4. MANEJO DEL ENVÍO DEL PRODUCTO (ALMACENAJE LOCAL TEMPORAL)

function manejarEnvio(evento) {
    evento.preventDefault();

    const nValido = validarNombre();
    const qValido = validarCantidad();
    const cValido = validarCategoria();

    if (nValido && qValido && cValido) {
        const nuevaPrenda = {
            id: Date.now(),
            prenda: inputNombre.value,
            cantidad: inputCantidad.value,
            categoria: selectCategoria.value
        };

        catalogoPrendas.push(nuevaPrenda);
        renderizarCatalogo();
        
        form.reset();
        inputNombre.classList.remove('is-valid');
        inputCantidad.classList.remove('is-valid');
        selectCategoria.classList.remove('is-valid');

        const modalElement = document.getElementById('modalCompra');
        if (modalElement) {
            const miModal = new bootstrap.Modal(modalElement);
            miModal.show();
        }
    }
}


// 5. RENDERIZADO Y CONTADORES

function renderizarCatalogo() {
    if (totalRegistros) {
        totalRegistros.textContent = catalogoPrendas.length;
    }

    if (!listaContenedor) return;
    listaContenedor.innerHTML = "";

    if (catalogoPrendas.length === 0) {
        listaContenedor.innerHTML = `<p class="text-muted text-center py-3">No hay productos ingresados temporalmente.</p>`;
        return;
    }

    catalogoPrendas.forEach(prenda => {
        const div = document.createElement('div');
        div.classList.add('col-md-6', 'col-lg-4', 'mb-3');
        div.innerHTML = `
            <div class="card h-100 shadow-sm border-start border-danger border-3">
                <div class="card-body d-flex flex-column justify-content-between">
                    <div>
                        <span class="badge bg-danger mb-2">${prenda.categoria}</span>
                        <h5 class="card-title fw-bold text-dark mb-1">${prenda.prenda}</h5>
                        <p class="card-text text-muted small mb-0">Cantidad: <strong>${prenda.cantidad}</strong></p>
                    </div>
                    <button class="btn btn-outline-danger btn-sm mt-3 w-100" onclick="eliminarPrenda(${prenda.id})">
                        Eliminar
                    </button>
                </div>
            </div>
        `;
        listaContenedor.appendChild(div);
    });
}

window.eliminarPrenda = function(id) {
    catalogoPrendas = catalogoPrendas.filter(p => p.id !== id);
    renderizarCatalogo();
};


// 6. FLUJO Y GUARDADO EN POSTGRESQL ("CERRAR COMPRA")

window.cerrarCompra = function() {
    if (catalogoPrendas.length === 0) {
        alert("Agrega al menos una prenda antes de cerrar.");
        return;
    }

    // A. Guardar las prendas en la BD PostgreSQL a través del endpoint /guardar_stock
    fetch('/guardar_stock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prendas: catalogoPrendas })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cierra el primer modal
            const modalElement = document.getElementById('modalCompra');
            if (modalElement) {
                const modalInstance = bootstrap.Modal.getInstance(modalElement);
                if (modalInstance) modalInstance.hide();
            }

            // Abre el modal para capturar los datos del cliente
            setTimeout(() => {
                const modalEnvioElement = document.getElementById('modalDatosEnvio');
                if (modalEnvioElement) {
                    const modalEnvio = new bootstrap.Modal(modalEnvioElement);
                    modalEnvio.show();
                }
            }, 400);
        } else {
            alert('Error al guardar el stock: ' + data.message);
        }
    })
    .catch(error => console.error('Error enviando stock:', error));
};


// B. Guardar el pedido final del cliente en PostgreSQL (/guardar_pedido)
function procesarEnvioBaseDatos(e) {
    e.preventDefault();

    const nombreCli = document.getElementById('envio-nombre').value;
    const idCli = document.getElementById('envio-id').value;
    const dirCli = document.getElementById('envio-direccion').value;
    const telCli = document.getElementById('envio-telefono').value;

    let resumenPrendas = catalogoPrendas.map(p => `${p.prenda} (${p.cantidad})`).join(', ');

    // Construir formulario para enviar a Flask
    const formData = new FormData();
    formData.append('nombre', nombreCli);
    formData.append('cedula', idCli);
    formData.append('direccion', dirCli);
    formData.append('telefono', telCli);
    formData.append('producto', resumenPrendas);

    fetch('/guardar_pedido', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            alert('🚀 ¡Pedido e inventario guardados exitosamente en PostgreSQL!');
            
            // Limpiar formulario y cerrar modal
            document.getElementById('form-datos-envio').reset();
            const modalEnvioElement = document.getElementById('modalDatosEnvio');
            if (modalEnvioElement) {
                const modalInstance = bootstrap.Modal.getInstance(modalEnvioElement);
                if (modalInstance) modalInstance.hide();
            }

            catalogoPrendas = [];
            renderizarCatalogo();
        } else {
            alert('Hubo un problema al guardar el pedido en la base de datos.');
        }
    })
    .catch(error => console.error('Error registrando pedido:', error));
}


// 7. ENVÍO DEL FORMULARIO DE CONTACTO A POSTGRESQL

const formContacto = document.getElementById('form-contacto');
if (formContacto) {
    formContacto.addEventListener('submit', function(event) {
        if (!formContacto.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
            formContacto.classList.add('was-validated');
        }
        // Permite que el formulario se envíe a Flask si es válido
    });
}