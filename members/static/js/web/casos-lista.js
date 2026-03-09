let todosLosCasos = [];
let casosFiltrados = [];
let paginaActual = 1;
const casosPorPagina = 9;

document.addEventListener('DOMContentLoaded', async function() {
    await loadCategorias();
    await loadEstados();
    await loadCasos();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('searchInput').addEventListener('input', filtrarCasos);
    document.getElementById('categoriaFilter').addEventListener('change', filtrarCasos);
    document.getElementById('estadoFilter').addEventListener('change', filtrarCasos);
}

async function loadCategorias() {
    try {
        const response = await apiClient.get('/categorias/');
        const categorias = response.data || [];
        
        const select = document.getElementById('categoriaFilter');
        categorias.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = cat.nombre;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error cargando categorías:', error);
    }
}

async function loadEstados() {
    try {
        const response = await apiClient.get('/estados-caso/');
        const estados = response.data || [];
        
        const select = document.getElementById('estadoFilter');
        estados.forEach(estado => {
            const option = document.createElement('option');
            option.value = estado.id;
            option.textContent = estado.nombre;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error cargando estados:', error);
    }
}

async function loadCasos() {
    try {
        const response = await apiClient.get('/casos/');
        todosLosCasos = response.data || [];
        casosFiltrados = [...todosLosCasos];
        
        renderCasos();
    } catch (error) {
        console.error('Error cargando casos:', error);
        mostrarError('Error al cargar los casos');
    }
}

function filtrarCasos() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const categoriaId = document.getElementById('categoriaFilter').value;
    const estadoId = document.getElementById('estadoFilter').value;

    casosFiltrados = todosLosCasos.filter(caso => {
        const matchSearch = !searchTerm || 
            caso.titulo.toLowerCase().includes(searchTerm) ||
            caso.descripcion.toLowerCase().includes(searchTerm);
        
        const matchCategoria = !categoriaId || 
            (caso.categorias && caso.categorias.some(cat => cat.id == categoriaId));
        
        const matchEstado = !estadoId || caso.estado?.id == estadoId;

        return matchSearch && matchCategoria && matchEstado;
    });

    paginaActual = 1;
    renderCasos();
}

function renderCasos() {
    const container = document.getElementById('casosContainer');
    const totalCasos = casosFiltrados.length;
    
    document.getElementById('totalCasos').textContent = totalCasos;

    if (totalCasos === 0) {
        container.innerHTML = `
            <div class="col-span-full text-center py-12">
                <svg class="w-20 h-20 text-sky-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                </svg>
                <p class="text-sky-600 text-lg">No se encontraron casos</p>
                <p class="text-sky-500 text-sm mt-2">Intenta con otros filtros</p>
            </div>
        `;
        document.getElementById('paginationContainer').innerHTML = '';
        return;
    }

    // Calcular casos para la página actual
    const inicio = (paginaActual - 1) * casosPorPagina;
    const fin = inicio + casosPorPagina;
    const casosPagina = casosFiltrados.slice(inicio, fin);

    // Renderizar casos
    container.innerHTML = '';
    casosPagina.forEach(caso => {
        const casoCard = renderCasoCard(caso);
        container.appendChild(casoCard);
    });

    // Renderizar paginación
    renderPaginacion(totalCasos);
}

function renderCasoCard(caso) {
    const div = document.createElement('div');
    div.className = 'bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-sky-100';
    
    const imagen = caso.imagen1 || '';
    const categorias = Array.isArray(caso.categorias) ? caso.categorias : [];
    const estadoBadge = caso.estado ? caso.estado.nombre : 'Sin estado';
    
    div.innerHTML = `
        <div class="relative h-48 overflow-hidden bg-gradient-to-br from-sky-100 to-blue-100">
            ${imagen ? 
                `<img src="${imagen}" alt="${caso.titulo}" class="w-full h-full object-cover">` :
                `<div class="w-full h-full flex items-center justify-center">
                    <svg class="w-20 h-20 text-sky-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                </div>`
            }
            <div class="absolute top-2 right-2">
                <span class="px-3 py-1 text-xs font-semibold rounded-full bg-white text-sky-700 shadow">
                    ${estadoBadge}
                </span>
            </div>
        </div>

        <div class="p-5">
            <h3 class="text-lg font-bold text-sky-800 mb-2 line-clamp-2">${caso.titulo}</h3>
            <p class="text-sm text-sky-600 mb-4 line-clamp-3">${caso.descripcion || ''}</p>

            <div class="flex flex-wrap gap-2 mb-4">
                ${categorias.map(cat => `
                    <span class="px-2 py-1 text-xs font-medium bg-sky-100 text-sky-700 rounded">
                        ${cat.nombre || cat}
                    </span>
                `).join('')}
            </div>

            <div class="flex items-center justify-between text-xs text-sky-500 mb-4">
                <div class="flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    </svg>
                    <span>${caso.colonia || 'Sin ubicación'}</span>
                </div>
                <div class="flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                    </svg>
                    <span>${caso.vistas || 0}</span>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-2">
                <a href="/web/casos/${caso.id}/" 
                   class="py-2 px-4 bg-sky-600 hover:bg-sky-700 text-white text-sm font-semibold rounded-md text-center transition">
                    Ver más
                </a>
                <button onclick="donar(${caso.id})" 
                        class="py-2 px-4 bg-white hover:bg-sky-50 text-sky-700 border border-sky-300 text-sm font-semibold rounded-md transition">
                    Donar
                </button>
            </div>
        </div>
    `;
    
    return div;
}

function renderPaginacion(total) {
    const totalPaginas = Math.ceil(total / casosPorPagina);
    const container = document.getElementById('paginationContainer');
    
    if (totalPaginas <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '<div class="flex items-center space-x-2">';
    
    // Botón anterior
    html += `
        <button onclick="cambiarPagina(${paginaActual - 1})" 
                ${paginaActual === 1 ? 'disabled' : ''}
                class="px-4 py-2 text-sm font-medium rounded-md transition
                       ${paginaActual === 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-sky-700 border border-sky-300 hover:bg-sky-50'}">
            Anterior
        </button>
    `;

    // Números de página
    for (let i = 1; i <= totalPaginas; i++) {
        if (i === 1 || i === totalPaginas || (i >= paginaActual - 2 && i <= paginaActual + 2)) {
            html += `
                <button onclick="cambiarPagina(${i})" 
                        class="px-4 py-2 text-sm font-medium rounded-md transition
                               ${i === paginaActual ? 'bg-sky-600 text-white' : 'bg-white text-sky-700 border border-sky-300 hover:bg-sky-50'}">
                    ${i}
                </button>
            `;
        } else if (i === paginaActual - 3 || i === paginaActual + 3) {
            html += '<span class="px-2 text-sky-600">...</span>';
        }
    }

    // Botón siguiente
    html += `
        <button onclick="cambiarPagina(${paginaActual + 1})" 
                ${paginaActual === totalPaginas ? 'disabled' : ''}
                class="px-4 py-2 text-sm font-medium rounded-md transition
                       ${paginaActual === totalPaginas ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-sky-700 border border-sky-300 hover:bg-sky-50'}">
            Siguiente
        </button>
    `;

    html += '</div>';
    container.innerHTML = html;
}

function cambiarPagina(pagina) {
    paginaActual = pagina;
    renderCasos();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function limpiarFiltros() {
    document.getElementById('searchInput').value = '';
    document.getElementById('categoriaFilter').value = '';
    document.getElementById('estadoFilter').value = '';
    filtrarCasos();
}

function donar(casoId) {
    window.location.href = `/web/donaciones/crear/${casoId}/`;
}

function compartirCaso(casoId) {
    const url = `${window.location.origin}/web/casos/${casoId}/`;
    
    if (navigator.share) {
        navigator.share({
            title: 'Aqui Estoy! - Caso',
            url: url
        });
    } else {
        navigator.clipboard.writeText(url);
        alert('Enlace copiado al portapapeles');
    }
}

function mostrarError(mensaje) {
    const container = document.getElementById('casosContainer');
    container.innerHTML = `
        <div class="col-span-full">
            <div class="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                <svg class="w-12 h-12 text-red-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p class="text-red-800 font-medium">${mensaje}</p>
            </div>
        </div>
    `;
}