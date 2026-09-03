
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
    // Escuchar cuando el usuario cambia de opinión o sale del campo (Acciones del profesor)
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
    renderizarCatalogo();
});


// 3. FUNCIONES DE VALIDACIÓN (BORDES EN ROJO / VERDE)

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

// Pintar el campo de rojo y poner el aviso abajo
function mostrarError(elemento, mensaje) {
    if(!elemento) return;
    elemento.classList.remove('is-valid');
    elemento.classList.add('is-invalid');
    const feedback = elemento.nextElementSibling; // Captura el <div class="invalid-feedback">
    if (feedback && feedback.classList.contains('invalid-feedback')) {
        feedback.textContent = mensaje;
    }
}

// Pintar el campo de verde si todo está bien
function mostrarExito(elemento) {
    if(!elemento) return;
    elemento.classList.remove('is-invalid');
    elemento.classList.add('is-valid');
}


// 4. MANEJO DEL ENVÍO DEL PRODUCTO

function manejarEnvio(evento) {
    evento.preventDefault();

    // Forzar la validación de todos los campos al dar clic en enviar
    const nValido = validarNombre();
    const qValido = validarCantidad();
    const cValido = validarCategoria();

    // Solo si todos están aprobados (en verde) pasa al catálogo
    if (nValido && qValido && cValido) {
        const nuevaPrenda = {
            id: Date.now(),
            nombre: inputNombre.value,
            cantidad: inputCantidad.value,
            categoria: selectCategoria.value
        };

        catalogoPrendas.push(nuevaPrenda);
        renderizarCatalogo(); // Actualiza el indicador y las tarjetas al instante
        
        // Limpieza de estados visuales del formulario principal
        form.reset();
        inputNombre.classList.remove('is-valid');
        inputCantidad.classList.remove('is-valid');
        selectCategoria.classList.remove('is-valid');

        // Levantar el primer modal de confirmación
        const modalElement = document.getElementById('modalCompra');
        if (modalElement) {
            const miModal = new bootstrap.Modal(modalElement);
            miModal.show();
        }
    }
}


// 5. RENDERIZADO Y CONTADORES EN TIEMPO REAL

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
                        <h5 class="card-title fw-bold text-dark mb-1">${prenda.nombre}</h5>
                        <p class="card-text text-muted small mb-0">Pedido: <strong>${prenda.cantidad}</strong></p>
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


// 6. FLUJO POST-COMPRA (DATOS DE ENVÍO)

window.cerrarCompra = function() {
    const modalElement = document.getElementById('modalCompra');
    if (modalElement) {
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) modalInstance.hide();
    }

    // Abrir de inmediato el modal de registro de datos de envío
    setTimeout(() => {
        const modalEnvioElement = document.getElementById('modalDatosEnvio');
        if (modalEnvioElement) {
            const modalEnvio = new bootstrap.Modal(modalEnvioElement);
            modalEnvio.show();
        }
    }, 400); 
};

// Capturar el envío definitivo del cliente
document.addEventListener('DOMContentLoaded', () => {
    const formEnvio = document.getElementById('form-datos-envio');
    if (formEnvio) {
        formEnvio.addEventListener('submit', (e) => {
            e.preventDefault();

            const nombreCli = document.getElementById('envio-nombre').value;
            const idCli = document.getElementById('envio-id').value;
            const dirCli = document.getElementById('envio-direccion').value;
            const telCli = document.getElementById('envio-telefono').value;

            let resumenPrendas = catalogoPrendas.map(p => `- ${p.nombre} (${p.cantidad})`).join('\n');

            alert(
                `🚀 ¡ENVÍO PROGRAMADO CON ÉXITO!\n\n` +
                `👤 Destinatario: ${nombreCli}\n` +
                `🆔 Cédula: ${idCli}\n` +
                `📍 Dirección: ${dirCli}\n` +
                `📞 Teléfono: ${telCli}\n` +
                `-----------------------------------------\n` +
                `📦 DETALLE DEL PEDIDO:\n${resumenPrendas}\n\n` +
                `¡Tu orden de compra ha sido procesada!`
            );

            formEnvio.reset();
            const modalEnvioElement = document.getElementById('modalDatosEnvio');
            if (modalEnvioElement) {
                const modalInstance = bootstrap.Modal.getInstance(modalEnvioElement);
                if (modalInstance) modalInstance.hide();
            }

            // Limpiar la lista tras completarse la transacción
            catalogoPrendas = [];
            renderizarCatalogo();
        });
    }
});
document.getElementById('form-contacto').addEventListener('submit', function(event) {
    const form = event.target;
    
    // Validar campos vacíos
    if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
        form.classList.add('was-validated');
    } else {
        event.preventDefault(); // Evita el envío real para mostrar el mensaje
        
        // Mostrar mensaje de éxito
        const msgEnvio = document.getElementById('mensaje-envio');
        msgEnvio.classList.remove('d-none');
        
        // Ocultar mensaje después de 3 segundos
        setTimeout(() => {
            msgEnvio.classList.add('d-none');
            form.reset();
            form.classList.remove('was-validated');
        }, 3000);
    }
});
