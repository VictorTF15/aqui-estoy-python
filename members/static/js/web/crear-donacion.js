let caso = null;
let usuarioActual = null;

document.addEventListener('DOMContentLoaded', async function() {
    // Verificar autenticación
    const profile = await authService.getProfile();
    if (!profile.success) {
        window.location.href = '/login/';
        return;
    }
    
    usuarioActual = profile.data;
    await cargarCaso();
    setupFormulario();
    setupMontoListener();
});

async function cargarCaso() {
    try {
        const response = await apiClient.get(`/casos/${casoId}/`);
        caso = response.data;
        renderCasoInfo();
    } catch (error) {
        console.error('Error cargando caso:', error);
        showAlert('Error al cargar la información del caso', 'danger');
    }
}

function renderCasoInfo() {
    // Imagen
    const imgContainer = document.getElementById('casoImagen');
    if (caso.imagen_principal) {
        imgContainer.innerHTML = `<img src="${caso.imagen_principal}" alt="${caso.titulo}" class="w-full h-full object-cover rounded-lg">`;
    } else {
        imgContainer.innerHTML = `
            <svg class="w-full h-full text-sky-400 p-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
        `;
    }
    
    // Título
    document.getElementById('casoTitulo').textContent = caso.titulo;
    
    // Meta
    const montoRecaudado = parseFloat(caso.monto_recaudado || 0);
    const metaEconomica = parseFloat(caso.meta_economica || 1);
    const porcentaje = (montoRecaudado / metaEconomica * 100).toFixed(0);
    
    document.getElementById('casoMeta').textContent = 
        `$${montoRecaudado.toFixed(2)} de $${metaEconomica.toFixed(2)}`;
    
    // Progreso
    document.getElementById('casoProgreso').style.width = `${Math.min(porcentaje, 100)}%`;
}

function seleccionarMonto(monto) {
    // Remover clase active de todos los botones
    document.querySelectorAll('.amount-option').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Activar el botón clickeado
    event.target.classList.add('active');
    
    // Establecer el valor en el input
    document.getElementById('monto').value = monto;
    
    // Actualizar resumen
    actualizarResumen();
}

function setupMontoListener() {
    const montoInput = document.getElementById('monto');
    
    montoInput.addEventListener('input', function() {
        // Remover active de botones predefinidos
        document.querySelectorAll('.amount-option').forEach(btn => {
            btn.classList.remove('active');
        });
        
        actualizarResumen();
    });
}

function actualizarResumen() {
    const monto = parseFloat(document.getElementById('monto').value) || 0;
    const comision = 0; // Sin comisión
    const total = monto + comision;
    
    document.getElementById('resumenMonto').textContent = `$${monto.toFixed(2)}`;
    document.getElementById('resumenTotal').textContent = `$${total.toFixed(2)}`;
}

function setupFormulario() {
    const form = document.getElementById('formDonacion');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validar monto mínimo
        const monto = parseFloat(document.getElementById('monto').value);
        if (monto < 10) {
            showAlert('El monto mínimo es $10.00', 'warning');
            return;
        }
        
        // Validar método de pago
        const metodoPago = document.querySelector('input[name="metodo_pago"]:checked');
        if (!metodoPago) {
            showAlert('Por favor selecciona un método de pago', 'warning');
            return;
        }
        
        // Validar términos
        const aceptoTerminos = document.getElementById('acepto_terminos').checked;
        if (!aceptoTerminos) {
            showAlert('Debes aceptar los términos y condiciones', 'warning');
            return;
        }
        
        // Preparar datos
        const donacionData = {
            caso: casoId,
            monto: monto,
            metodo_pago: metodoPago.value,
            comentario: document.getElementById('comentario').value.trim() || null,
            anonima: document.getElementById('anonima').checked,
            estado_donacion: 'Pendiente',
            fecha_compromiso: new Date().toISOString().split('T')[0]
        };
        
        // Enviar donación
        const btnEnviar = document.getElementById('btnEnviar');
        btnEnviar.disabled = true;
        btnEnviar.innerHTML = `
            <svg class="animate-spin h-5 w-5 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
        `;
        
        try {
            const response = await apiClient.post('/donaciones/', donacionData);
            
            if (response && response.id) {
                // Mostrar modal de éxito
                mostrarModalExito();
            } else {
                showAlert('Error al procesar la donación', 'danger');
                btnEnviar.disabled = false;
                btnEnviar.textContent = 'Realizar Donación';
            }
        } catch (error) {
            console.error('Error creando donación:', error);
            showAlert(error.message || 'Error al procesar la donación', 'danger');
            btnEnviar.disabled = false;
            btnEnviar.textContent = 'Realizar Donación';
        }
    });
}

function mostrarModalExito() {
    const modal = document.getElementById('modalConfirmacion');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    
    // Opcional: redirigir automáticamente después de unos segundos
    setTimeout(() => {
        window.location.href = '/donaciones/';
    }, 5000);
}

function showAlert(message, type = 'danger') {
    const alertContainer = document.getElementById('alertContainer');
    
    const colorClasses = {
        'success': 'bg-green-50 text-green-800 border-green-200',
        'danger': 'bg-red-50 text-red-800 border-red-200',
        'warning': 'bg-yellow-50 text-yellow-800 border-yellow-200',
        'info': 'bg-blue-50 text-blue-800 border-blue-200'
    };
    
    const icons = {
        'success': '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
        'danger': '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
        'warning': '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>',
        'info': '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
    };
    
    const alert = `
        <div class="flex items-center p-4 rounded-md border ${colorClasses[type]} animate-fade-in">
            <div class="flex-shrink-0 mr-3">${icons[type]}</div>
            <p class="text-sm font-medium">${message}</p>
        </div>
    `;
    
    alertContainer.innerHTML = alert;
    
    setTimeout(() => {
        alertContainer.innerHTML = '';
    }, 5000);
}
