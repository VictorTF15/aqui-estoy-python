let donaciones = [];
let donacionesFiltradas = [];
let paginaActual = 1;
const donacionesPorPagina = 10;
let usuarioActual = null;

document.addEventListener('DOMContentLoaded', async function() {
    // Verificar autenticación
    const profile = await authService.getProfile();
    if (!profile.success) {
        window.location.href = '/login/';
        return;
    }
    
    usuarioActual = profile.data;
    await cargarDonaciones();
    setupEventListeners();
});

async function cargarDonaciones() {
    try {
        const response = await apiClient.get(`/donaciones/?donador=${usuarioActual.id}`);
        donaciones = response.data || [];
        donacionesFiltradas = [...donaciones];
        
        calcularEstadisticas();
        renderDonaciones();
        
    } catch (error) {
        console.error('Error cargando donaciones:', error);
        showAlert('Error al cargar las donaciones', 'danger');
        mostrarEstadoVacio();
    }
}

function calcularEstadisticas() {
    const total = donaciones.reduce((sum, d) => sum + parseFloat(d.monto || 0), 0);
    const completadas = donaciones.filter(d => d.estado_donacion === 'Completada').length;
    const casosUnicos = new Set(donaciones.map(d => d.caso?.id).filter(Boolean)).size;
    const promedio = donaciones.length > 0 ? total / donaciones.length : 0;
    
    document.getElementById('statTotal').textContent = `$${total.toFixed(2)}`;
    document.getElementById('statDonaciones').textContent = completadas;
    document.getElementById('statCasos').textContent = casosUnicos;
    document.getElementById('statPromedio').textContent = `$${promedio.toFixed(2)}`;
}

function renderDonaciones() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    const container = document.getElementById('donacionesContainer');
    const emptyState = document.getElementById('emptyState');
    
    loadingSpinner.classList.add('hidden');
    
    if (donacionesFiltradas.length === 0) {
        container.classList.add('hidden');
        emptyState.classList.remove('hidden');
        document.getElementById('paginationContainer').innerHTML = '';
        return;
    }
    
    container.classList.remove('hidden');
    emptyState.classList.add('hidden');
    
    // Paginación
    const inicio = (paginaActual - 1) * donacionesPorPagina;
    const fin = inicio + donacionesPorPagina;
    const donacionesPagina = donacionesFiltradas.slice(inicio, fin);
    
    container.innerHTML = donacionesPagina.map(donacion => `
        <div class="p-6 hover:bg-sky-50 transition cursor-pointer" onclick="verDetalle(${donacion.id})">
            <div class="flex items-start justify-between gap-4">
                <div class="flex-1">
                    <div class="flex items-start gap-4">
                        ${donacion.caso?.imagen_principal ? `
                            <img src="${donacion.caso.imagen_principal}" 
                                 alt="${donacion.caso.titulo}"
                                 class="w-20 h-20 object-cover rounded-lg">
                        ` : `
                            <div class="w-20 h-20 bg-sky-100 rounded-lg flex items-center justify-center">
                                <svg class="w-10 h-10 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                </svg>
                            </div>
                        `}
                        
                        <div class="flex-1">
                            <h3 class="font-semibold text-sky-800 mb-1">${donacion.caso?.titulo || 'Caso no disponible'}</h3>
                            <p class="text-sm text-sky-600 mb-2">${donacion.comentario || 'Sin comentarios'}</p>
                            
                            <div class="flex flex-wrap items-center gap-3 text-xs text-sky-500">
                                <span class="flex items-center">
                                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                    </svg>
                                    ${formatDate(donacion.fecha_compromiso)}
                                </span>
                                
                                ${donacion.anonima ? `
                                    <span class="flex items-center text-sky-400">
                                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path>
                                        </svg>
                                        Anónima
                                    </span>
                                ` : ''}
                                
                                ${donacion.metodo_pago ? `
                                    <span class="flex items-center">
                                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path>
                                        </svg>
                                        ${donacion.metodo_pago}
                                    </span>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="text-right flex flex-col items-end gap-2">
                    <p class="text-2xl font-bold text-sky-800">$${parseFloat(donacion.monto).toFixed(2)}</p>
                    <span class="px-3 py-1 text-xs font-semibold rounded-full ${getEstadoColor(donacion.estado_donacion)}">
                        ${donacion.estado_donacion || 'Pendiente'}
                    </span>
                </div>
            </div>
        </div>
    `).join('');
    
    renderPaginacion();
}

function renderPaginacion() {
    const totalPaginas = Math.ceil(donacionesFiltradas.length / donacionesPorPagina);
    const container = document.getElementById('paginationContainer');
    
    if (totalPaginas <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let html = '<div class="flex items-center gap-2">';
    
    // Botón anterior
    html += `
        <button 
            onclick="cambiarPagina(${paginaActual - 1})"
            ${paginaActual === 1 ? 'disabled' : ''}
            class="px-4 py-2 border border-sky-300 rounded-lg hover:bg-sky-50 disabled:opacity-50 disabled:cursor-not-allowed">
            Anterior
        </button>
    `;
    
    // Números de página
    for (let i = 1; i <= totalPaginas; i++) {
        if (i === 1 || i === totalPaginas || (i >= paginaActual - 2 && i <= paginaActual + 2)) {
            html += `
                <button 
                    onclick="cambiarPagina(${i})"
                    class="px-4 py-2 rounded-lg ${i === paginaActual ? 'bg-sky-600 text-white' : 'border border-sky-300 hover:bg-sky-50'}">
                    ${i}
                </button>
            `;
        } else if (i === paginaActual - 3 || i === paginaActual + 3) {
            html += '<span class="px-2">...</span>';
        }
    }
    
    // Botón siguiente
    html += `
        <button 
            onclick="cambiarPagina(${paginaActual + 1})"
            ${paginaActual === totalPaginas ? 'disabled' : ''}
            class="px-4 py-2 border border-sky-300 rounded-lg hover:bg-sky-50 disabled:opacity-50 disabled:cursor-not-allowed">
            Siguiente
        </button>
    `;
    
    html += '</div>';
    container.innerHTML = html;
}

function cambiarPagina(pagina) {
    const totalPaginas = Math.ceil(donacionesFiltradas.length / donacionesPorPagina);
    if (pagina < 1 || pagina > totalPaginas) return;
    
    paginaActual = pagina;
    renderDonaciones();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function aplicarFiltros() {
    const search = document.getElementById('searchInput').value.toLowerCase().trim();
    const estado = document.getElementById('estadoFilter').value;
    const fechaDesde = document.getElementById('fechaDesde').value;
    const fechaHasta = document.getElementById('fechaHasta').value;
    
    donacionesFiltradas = donaciones.filter(donacion => {
        // Búsqueda por título de caso
        if (search && !donacion.caso?.titulo.toLowerCase().includes(search)) {
            return false;
        }
        
        // Filtro por estado
        if (estado && donacion.estado_donacion !== estado) {
            return false;
        }
        
        // Filtro por fecha desde
        if (fechaDesde && new Date(donacion.fecha_compromiso) < new Date(fechaDesde)) {
            return false;
        }
        
        // Filtro por fecha hasta
        if (fechaHasta && new Date(donacion.fecha_compromiso) > new Date(fechaHasta)) {
            return false;
        }
        
        return true;
    });
    
    paginaActual = 1;
    renderDonaciones();
}

function limpiarFiltros() {
    document.getElementById('searchInput').value = '';
    document.getElementById('estadoFilter').value = '';
    document.getElementById('fechaDesde').value = '';
    document.getElementById('fechaHasta').value = '';
    
    donacionesFiltradas = [...donaciones];
    paginaActual = 1;
    renderDonaciones();
}

async function verDetalle(donacionId) {
    const donacion = donaciones.find(d => d.id === donacionId);
    if (!donacion) return;
    
    const modal = document.getElementById('modalDetalle');
    const content = document.getElementById('modalContent');
    
    content.innerHTML = `
        <div class="space-y-6">
            <!-- Información del Caso -->
            <div>
                <h4 class="text-sm font-semibold text-sky-700 mb-3">Caso Apoyado</h4>
                <div class="flex items-start gap-4 p-4 bg-sky-50 rounded-lg">
                    ${donacion.caso?.imagen_principal ? `
                        <img src="${donacion.caso.imagen_principal}" 
                             alt="${donacion.caso.titulo}"
                             class="w-24 h-24 object-cover rounded-lg">
                    ` : ''}
                    <div class="flex-1">
                        <h5 class="font-semibold text-sky-800 mb-2">${donacion.caso?.titulo || 'N/A'}</h5>
                        <a href="/web/casos/${donacion.caso?.id}/" 
                           class="inline-flex items-center text-sm text-sky-600 hover:text-sky-700">
                            Ver caso completo
                            <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                            </svg>
                        </a>
                    </div>
                </div>
            </div>
            
            <!-- Detalles de la Donación -->
            <div>
                <h4 class="text-sm font-semibold text-sky-700 mb-3">Detalles de la Donación</h4>
                <div class="grid grid-cols-2 gap-4">
                    <div class="p-4 bg-blue-50 rounded-lg">
                        <p class="text-xs text-sky-600 mb-1">Monto</p>
                        <p class="text-xl font-bold text-sky-800">$${parseFloat(donacion.monto).toFixed(2)}</p>
                    </div>
                    
                    <div class="p-4 bg-blue-50 rounded-lg">
                        <p class="text-xs text-sky-600 mb-1">Estado</p>
                        <span class="inline-block px-3 py-1 text-xs font-semibold rounded-full ${getEstadoColor(donacion.estado_donacion)}">
                            ${donacion.estado_donacion || 'Pendiente'}
                        </span>
                    </div>
                    
                    <div class="p-4 bg-blue-50 rounded-lg">
                        <p class="text-xs text-sky-600 mb-1">Fecha de Compromiso</p>
                        <p class="text-sm font-semibold text-sky-800">${formatDate(donacion.fecha_compromiso)}</p>
                    </div>
                    
                    ${donacion.fecha_recepcion ? `
                        <div class="p-4 bg-blue-50 rounded-lg">
                            <p class="text-xs text-sky-600 mb-1">Fecha de Recepción</p>
                            <p class="text-sm font-semibold text-sky-800">${formatDate(donacion.fecha_recepcion)}</p>
                        </div>
                    ` : ''}
                    
                    ${donacion.metodo_pago ? `
                        <div class="p-4 bg-blue-50 rounded-lg">
                            <p class="text-xs text-sky-600 mb-1">Método de Pago</p>
                            <p class="text-sm font-semibold text-sky-800">${donacion.metodo_pago}</p>
                        </div>
                    ` : ''}
                    
                    <div class="p-4 bg-blue-50 rounded-lg">
                        <p class="text-xs text-sky-600 mb-1">Tipo</p>
                        <p class="text-sm font-semibold text-sky-800">
                            ${donacion.anonima ? 'Anónima' : 'Pública'}
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Comentario -->
            ${donacion.comentario ? `
                <div>
                    <h4 class="text-sm font-semibold text-sky-700 mb-3">Tu Mensaje</h4>
                    <div class="p-4 bg-sky-50 rounded-lg">
                        <p class="text-sky-700">${donacion.comentario}</p>
                    </div>
                </div>
            ` : ''}
            
            <!-- Comprobante -->
            ${donacion.comprobante ? `
                <div>
                    <h4 class="text-sm font-semibold text-sky-700 mb-3">Comprobante</h4>
                    <a href="${donacion.comprobante}" 
                       target="_blank"
                       class="inline-flex items-center px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700">
                        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        Descargar Comprobante
                    </a>
                </div>
            ` : ''}
        </div>
    `;
    
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function cerrarModal() {
    const modal = document.getElementById('modalDetalle');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

function setupEventListeners() {
    // Enter en búsqueda
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            aplicarFiltros();
        }
    });
    
    // Cerrar modal con ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            cerrarModal();
        }
    });
    
    // Cerrar modal al hacer clic fuera
    document.getElementById('modalDetalle').addEventListener('click', function(e) {
        if (e.target === this) {
            cerrarModal();
        }
    });
}

function mostrarEstadoVacio() {
    document.getElementById('loadingSpinner').classList.add('hidden');
    document.getElementById('donacionesContainer').classList.add('hidden');
    document.getElementById('emptyState').classList.remove('hidden');
}

function getEstadoColor(estado) {
    const colores = {
        'Completada': 'bg-green-100 text-green-800',
        'Pendiente': 'bg-yellow-100 text-yellow-800',
        'Rechazada': 'bg-red-100 text-red-800'
    };
    return colores[estado] || 'bg-gray-100 text-gray-800';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
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
