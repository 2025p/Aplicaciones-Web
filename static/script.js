
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-producto');
    const listaProductos = document.getElementById('lista-productos');
    const totalRegistros = document.getElementById('total-registros');
    const mensajeValidacion = document.getElementById('mensaje-validacion');
    
    let contador = 0;

    form.addEventListener('submit', (evento) => {
        evento.preventDefault(); // Evita que se recargue la página

        // Capturar los valores con los nuevos IDs del HTML
        const nombre = document.getElementById('prod-nombre').value.trim();
        const descripcion = document.getElementById('prod-descripcion').value.trim();
        const categoria = document.getElementById('prod-categoria').value;

        // Validación
        if (nombre === '' || descripcion === '' || categoria === '') {
            mostrarAlerta('Todos los campos son obligatorios.', 'danger');
            return;
        }

        mostrarAlerta('¡Prenda agregada al stock con éxito!', 'success');

        // Crear elementos con clases de Bootstrap
        const colDiv = document.createElement('div');
        colDiv.className = 'col-sm-6 mb-3';

        const cardDiv = document.createElement('div');
        cardDiv.className = 'card h-100 border-start border-danger border-3 shadow-sm custom-card';

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body d-flex flex-column justify-content-between';

        cardBody.innerHTML = `
            <div>
                <span class="badge bg-secondary mb-2">${categoria}</span>
                <h5 class="card-title text-dark fw-bold">${nombre}</h5>
                <p class="card-text text-muted small mb-0">${descripcion}</p>
            </div>
        `;

        const botonEliminar = document.createElement('button');
        botonEliminar.className = 'btn btn-outline-danger btn-sm mt-3 align-self-start';
        botonEliminar.innerText = 'Eliminar';

        botonEliminar.addEventListener('click', () => {
            colDiv.remove();
            contador--;
            totalRegistros.innerText = contador;
        });

        cardBody.appendChild(botonEliminar);
        cardDiv.appendChild(cardBody);
        colDiv.appendChild(cardDiv);
        listaProductos.appendChild(colDiv);

        contador++;
        totalRegistros.innerText = contador;

        form.reset();
    });

    function mostrarAlerta(mensaje, tipo) {
        mensajeValidacion.innerHTML = `
            <div class="alert alert-${tipo} alert-dismissible fade show p-2 small" role="alert">
                ${mensaje}
            </div>
        `;
        setTimeout(() => { mensajeValidacion.innerHTML = ''; }, 3000);
    }
    // Evitar que el formulario de contacto recargue la página y borre el stock
    const formContacto = document.getElementById('form-contacto');
    if (formContacto) {
        formContacto.addEventListener('submit', (evento) => {
            evento.preventDefault(); // Detiene la recarga por completo
            alert('¡Gracias por contactarnos! Tu mensaje ha sido simulado con éxito sin reiniciar el catálogo.');
            formContacto.reset();
        });
    }
});