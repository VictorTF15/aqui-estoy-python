document.addEventListener('DOMContentLoaded', async function() {
    await loadDashboardData();
    await loadCategorias();
    await loadCasosDestacados();
});

async function loadDashboardData() {
    try {
        // Cargar perfil de usuario
        const profileResult = await authService.getProfile();
        if (profileResult.success) {
            document.getElementById('userName').textContent = profileResult.data.nombres;
        }

        // Cargar estadísticas
        const casosResponse = await apiClient.get('/casos/');
        if (casosResponse.data) {
            document.getElementById('casosActivos').textContent = casosResponse.data.length;
        }

        // Cargar mis donaciones
        const donacionesResponse = await apiClient.get('/donaciones/mis-donaciones/');
        if (donacionesResponse.data) {
            const misDonaciones = donacionesResponse.data;
            document.getElementById('misDonaciones').textContent = misDonaciones.length;
            
            const totalDonado = misDonaciones.reduce((sum, d) => sum + parseFloat(d.monto || 0), 0);
            document.getElementById('totalDonado').textContent = totalDonado.toFixed(2);
        }

        // Cargar mis casos
        const misCasosResponse = await apiClient.get('/casos/mis-casos/');
        if (misCasosResponse.data) {
            document.getElementById('misCasos').textContent = misCasosResponse.data.length;
        }

    } catch (error) {
        console.error('Error cargando datos del dashboard:', error);
    }
}

async function loadCategorias() {
    try {
        const response = await apiClient.get('/categorias/');
        const categorias = response.data || [];
        
        const container = document.getElementById('categoriasList');
        container.innerHTML = '';

        if (categorias.length === 0) {
            container.innerHTML = '<p class="text-muted">No hay categorías disponibles</p>';
            return;
        }

        categorias.forEach(categoria => {
            const badge = document.createElement('button');
            badge.className = 'btn btn-outline-primary btn-sm';
            badge.innerHTML = `${categoria.icono || '📁'} ${categoria.nombre}`;
            badge.onclick = () => filtrarPorCategoria(categoria.id);
            container.appendChild(badge);
        });

    } catch (error) {
        console.error('Error cargando categorías:', error);
    }
}

async function loadCasosDestacados() {
    try {
        const response = await apiClient.get('/casos/');
        const casos = response.data || [];
        
        const container = document.getElementById('casosDestacados');
        container.innerHTML = '';

        if (casos.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="bi bi-inbox text-muted" style="font-size: 4rem;"></i>
                    <p class="text-muted mt-3">No hay casos disponibles</p>
                </div>
            `;
            return;
        }

        // Mostrar solo los primeros 6 casos
        casos.slice(0, 6).forEach(caso => {
            const col = document.createElement('div');
            col.className = 'col-md-4';
            col.innerHTML = renderCasoCard(caso);
            container.appendChild(col);
        });

    } catch (error) {
        console.error('Error cargando casos:', error);
        document.getElementById('casosDestacados').innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger">Error al cargar los casos</div>
            </div>
        `;
    }
}

function renderCasoCard(caso) {
    const imagen = caso.imagen1 || 'https://via.placeholder.com/400x300?text=Sin+Imagen';
    const categorias = Array.isArray(caso.categorias) ? caso.categorias : [];
    
    return `
        <div class="card h-100 shadow-sm border-0 caso-card" data-caso-id="${caso.id}">
            <img src="${imagen}" class="card-img-top" alt="${caso.titulo}" style="height: 200px; object-fit: cover;">
            <div class="card-body">
                <h5 class="card-title">${caso.titulo}</h5>
                <p class="card-text text-muted">${truncateText(caso.descripcion, 100)}</p>
                
                <div class="mb-2">
                    ${categorias.map(cat => `<span class="badge bg-primary me-1">${cat}</span>`).join('')}
                </div>
                
                <div class="d-flex justify-content-between align-items-center text-muted small mb-3">
                    <span><i class="bi bi-geo-alt"></i> ${caso.colonia || 'Sin ubicación'}</span>
                    <span><i class="bi bi-eye"></i> ${caso.vistas || 0}</span>
                </div>
            </div>
            
            <div class="card-footer bg-transparent border-0">
                <div class="d-grid gap-2">
                    <a href="/web/casos/${caso.id}/" class="btn btn-primary btn-sm">
                        <i class="bi bi-eye"></i> Ver Detalles
                    </a>
                </div>
            </div>
        </div>
    `;
}

function truncateText(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

function filtrarPorCategoria(categoriaId) {
    window.location.href = `/web/casos/?categoria=${categoriaId}`;
}