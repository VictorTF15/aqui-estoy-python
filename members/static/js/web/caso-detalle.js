let casoActual = null;

document.addEventListener('DOMContentLoaded', async function() {
    await loadCasoDetalle();
    setupFormDonacion();
});

async function loadCasoDetalle() {
    try {
        const response = await apiClient.get(`/casos/${casoId}/`);
        casoActual = response.data;
        
        if (casoActual) {
            renderCasoDetalle();
            await loadCasosSimilares();
            document.getElementById('loadingContainer').classList.add('hidden');
            document.getElementById('casoContainer').classList.remove('hidden');
        } else {
            mostrarError('Caso no encontrado');
        }
    } catch (error) {
        console.error('Error cargando caso:', error);
        mostrarError('Error al cargar el caso');
    }
}

function renderCasoDetalle() {
    // Título y ubicación
    document.getElementById('casoTitulo').textContent = casoActual.titulo;
    document.getElementById('casoUbicacion').textContent = 
        `${casoActual.colonia || ''}, ${casoActual.ciudad || ''}, ${casoActual.estado || ''}`.trim() || 'Sin ubicación';
    
    // Fecha
    const fecha = new Date(casoActual.fecha_creacion);
    document.getElementById('casoFecha').textContent = fecha.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    // Vistas
    document.getElementById('casoVistas').textContent = casoActual.vistas || 0;
    
    // Estado badge
    const estadoBadge = document.getElementById('casoEstadoBadge');
    if (casoActual.estado) {
        estadoBadge.innerHTML = `
            <span class="px-4 py-2 text-sm font-semibold rounded-full ${getEstadoColor(casoActual.estado.nombre)}">
                ${casoActual.estado.nombre}
            </span>
        `;
    }
    
    // Categorías
    const categoriasContainer = document.getElementById('casoCategorias');
    if (casoActual.categorias && casoActual.categorias.length > 0) {
        categoriasContainer.innerHTML = casoActual.categorias.map(cat => `
            <span class="px-3 py-1 text-sm font-medium bg-sky-100 text-sky-700 rounded-full">
                ${cat.nombre || cat}
            </span>
        `).join('');
    }
    
    // Galería
    renderGaleria();
    
    // Descripción
    document.getElementById('casoDescripcion').innerHTML = casoActual.descripcion || '<p class="text-sky-500">Sin descripción</p>';
    
    // Beneficiario
    renderBeneficiario();
    
    // Progreso de donaciones
    renderProgresoDonaciones();
}

function renderGaleria() {
    const galeriaContainer = document.getElementById('galeriaImagenes');
    const imagenes = [];
    
    if (casoActual.imagen1) imagenes.push(casoActual.imagen1);
    if (casoActual.imagen2) imagenes.push(casoActual.imagen2);
    if (casoActual.imagen3) imagenes.push(casoActual.imagen3);
    if (casoActual.imagen4) imagenes.push(casoActual.imagen4);
    
    if (imagenes.length === 0) {
        galeriaContainer.innerHTML = `
            <div class="col-span-2 text-center py-8 bg-blue-50 rounded-lg">
                <svg class="w-16 h-16 text-sky-300 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                <p class="text-sky-500">Sin imágenes</p>
            </div>
        `;
        return;
    }
    
    galeriaContainer.innerHTML = imagenes.map((img, index) => `
        <div class="relative group overflow-hidden rounded-lg border-2 border-sky-100 hover:border-sky-300 transition cursor-pointer" onclick="abrirImagenModal('${img}')">
            <img src="${img}" alt="Imagen ${index + 1}" class="w-full h-48 object-cover">
            <div class="absolute inset-0 bg-sky-900 bg-opacity-0 group-hover:bg-opacity-30 transition flex items-center justify-center">
                <svg class="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path>
                </svg>
            </div>
        </div>
    `).join('');
}

function renderBeneficiario() {
    if (casoActual.beneficiario) {
        const avatar = casoActual.beneficiario.imagen_perfil || 
            `https://ui-avatars.com/api/?name=${casoActual.beneficiario.nombres}&background=0ea5e9&color=fff`;
        
        document.getElementById('beneficiarioAvatar').src = avatar;
        document.getElementById('beneficiarioNombre').textContent = 
            `${casoActual.beneficiario.nombres} ${casoActual.beneficiario.apellido_paterno}`;
        document.getElementById('beneficiarioEmail').textContent = casoActual.beneficiario.correo || 'No disponible';
        document.getElementById('beneficiarioTelefono').textContent = casoActual.beneficiario.telefono || 'No disponible';
    }
}

async function renderProgresoDonaciones() {
    try {
        // Obtener donaciones del caso
        const response = await apiClient.get(`/donaciones/?caso=${casoId}`);
        const donaciones = response.data || [];
        
        const totalRecaudado = donaciones.reduce((sum, d) => sum + parseFloat(d.monto || 0), 0);
        const meta = parseFloat(casoActual.meta_donacion || 0);
        const porcentaje = meta > 0 ? Math.min((totalRecaudado / meta) * 100, 100) : 0;
        
        document.getElementById('metaDonacion').textContent = meta.toFixed(2);
        document.getElementById('recaudadoDonacion').textContent = totalRecaudado.toFixed(2);
        document.getElementById('progresoBarra').style.width = `${porcentaje}%`;
        document.getElementById('porcentajeProgreso').textContent = porcentaje.toFixed(1);
        document.getElementById('totalDonadores').textContent = donaciones.length;
        
        // Calcular días restantes
        if (casoActual.fecha_limite) {
            const fechaLimite = new Date(casoActual.fecha_limite);
            const hoy = new Date();
            const diferencia = Math.ceil((fechaLimite - hoy) / (1000 * 60 * 60 * 24));
            document.getElementById('diasRestantes').textContent = Math.max(0, diferencia);
        }
    } catch (error) {
        console.error('Error cargando donaciones:', error);
    }
}

async function loadCasosSimilares() {
    try {
        const response = await apiClient.get('/casos/');
        const casos = response.data || [];
        
        // Filtrar casos similares (misma categoría, excluyendo el actual)
        const similares = casos.filter(c => 
            c.id !== casoId && 
            c.categorias && casoActual.categorias &&
            c.categorias.some(cat1 => casoActual.categorias.some(cat2 => cat2.id === cat1.id))
        ).slice(0, 3);
        
        const container = document.getElementById('casosSimilares');
        
        if (similares.length === 0) {
            container.innerHTML = '<p class="text-center text-sky-500 text-sm py-4">No hay casos similares</p>';
            return;
        }
        
        container.innerHTML = similares.map(caso => `
            <a href="/web/casos/${caso.id}/" class="block bg-blue-50 rounded-lg p-3 hover:bg-blue-100 transition border border-sky-100">
                <h4 class="text-sm font-semibold text-sky-800 mb-1 line-clamp-2">${caso.titulo}</h4>
                <p class="text-xs text-sky-600 line-clamp-2">${caso.descripcion}</p>
            </a>
        `).join('');
    } catch (error) {
        console.error('Error cargando casos similares:', error);
    }
}

function getEstadoColor(estado) {
    const colores = {
        'Pendiente': 'bg-yellow-100 text-yellow-800',
        'En progreso': 'bg-blue-100 text-blue-800',
        'Completado': 'bg-green-100 text-green-800',
        'Cancelado': 'bg-red-100 text-red-800'
    };
    return colores[estado] || 'bg-gray-100 text-gray-800';
}

// Modal Donación
function abrirModalDonacion() {
    document.getElementById('modalDonacion').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function cerrarModalDonacion() {
    document.getElementById('modalDonacion').classList.add('hidden');
    document.body.style.overflow = 'auto';
    document.getElementById('formDonacion').reset();
}

function setMonto(monto) {
    document.getElementById('montoDonacion').value = monto;
}

function setupFormDonacion() {
    const form = document.getElementById('formDonacion');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const monto = parseFloat(document.getElementById('montoDonacion').value);
        const mensaje = document.getElementById('mensajeDonacion').value;
        const anonima = document.getElementById('donacionAnonima').checked;
        
        if (monto <= 0) {
            alert('Ingresa un monto válido');
            return;
        }
        
        try {
            const donacionData = {
                id_caso: casoId,
                monto: monto,
                mensaje: mensaje || null,
                anonima: anonima
            };
            
            const response = await apiClient.post('/donaciones/', donacionData);
            
            if (response.data) {
                alert('¡Donación realizada con éxito! Gracias por tu apoyo.');
                cerrarModalDonacion();
                await renderProgresoDonaciones();
            }
        } catch (error) {
            console.error('Error realizando donación:', error);
            alert('Error al procesar la donación. Intenta nuevamente.');
        }
    });
}

function compartirCaso() {
    const url = window.location.href;
    const titulo = casoActual.titulo;
    
    if (navigator.share) {
        navigator.share({
            title: `Aqui Estoy! - ${titulo}`,
            text: casoActual.descripcion,
            url: url
        });
    } else {
        navigator.clipboard.writeText(url);
        alert('Enlace copiado al portapapeles');
    }
}

function reportarCaso() {
    const motivo = prompt('¿Por qué deseas reportar este caso?');
    
    if (motivo && motivo.trim()) {
        // Aquí iría la lógica para enviar el reporte
        alert('Reporte enviado. Lo revisaremos pronto.');
    }
}

function abrirImagenModal(src) {
    // Crear modal de imagen
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-90';
    modal.innerHTML = `
        <div class="relative max-w-5xl max-h-screen p-4">
            <button onclick="this.parentElement.parentElement.remove()" 
                    class="absolute top-4 right-4 text-white hover:text-gray-300 z-10">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
            <img src="${src}" class="max-w-full max-h-screen object-contain rounded-lg" onclick="event.stopPropagation()">
        </div>
    `;
    modal.onclick = () => modal.remove();
    document.body.appendChild(modal);
}

function mostrarError(mensaje) {
    document.getElementById('loadingContainer').innerHTML = `
        <div class="text-center py-12">
            <svg class="w-20 h-20 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p class="text-red-600 font-medium text-lg">${mensaje}</p>
            <a href="/web/casos/" class="inline-block mt-4 text-sky-600 hover:text-sky-800 font-medium">
                ← Volver a casos
            </a>
        </div>
    `;
}