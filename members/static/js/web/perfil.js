let perfilUsuario = null;

document.addEventListener('DOMContentLoaded', async function() {
    await loadPerfil();
    setupForms();
});

async function loadPerfil() {
    try {
        const result = await authService.getProfile();
        if (result.success) {
            perfilUsuario = result.data;
            renderPerfil();
            await loadEstadisticas();
        }
    } catch (error) {
        console.error('Error cargando perfil:', error);
        showAlert('Error al cargar el perfil', 'danger');
    }
}

function renderPerfil() {
    // Sidebar info
    const avatar = perfilUsuario.imagen_perfil || 
        `https://ui-avatars.com/api/?name=${perfilUsuario.nombres}&background=0ea5e9&color=fff`;
    
    document.getElementById('avatarPreview').src = avatar;
    document.getElementById('profileName').textContent = 
        `${perfilUsuario.nombres} ${perfilUsuario.apellido_paterno}`;
    document.getElementById('profileEmail').textContent = perfilUsuario.correo;
    document.getElementById('profileTipo').textContent = perfilUsuario.tipo_usuario || 'Usuario';
    
    // Formulario
    document.getElementById('nombres').value = perfilUsuario.nombres || '';
    document.getElementById('apellido_paterno').value = perfilUsuario.apellido_paterno || '';
    document.getElementById('apellido_materno').value = perfilUsuario.apellido_materno || '';
    document.getElementById('telefono').value = perfilUsuario.telefono || '';
    document.getElementById('ciudad').value = perfilUsuario.ciudad || '';
    document.getElementById('estado').value = perfilUsuario.estado || '';
    document.getElementById('direccion').value = perfilUsuario.direccion || '';
}

async function loadEstadisticas() {
    try {
        // Mis casos
        const casosResponse = await apiClient.get(`/casos/?beneficiario=${perfilUsuario.id}`);
        const casos = casosResponse.data || [];
        document.getElementById('statCasos').textContent = casos.length;
        
        // Mis donaciones
        const donacionesResponse = await apiClient.get(`/donaciones/?donador=${perfilUsuario.id}`);
        const donaciones = donacionesResponse.data || [];
        document.getElementById('statDonaciones').textContent = donaciones.length;
        
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
    }
}

function showTab(tabName) {
    // Ocultar todos los contenidos
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });
    
    // Remover clase active de todos los botones
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active', 'bg-sky-50', 'border-l-4', 'border-sky-600');
    });
    
    // Mostrar contenido seleccionado
    document.getElementById(`content${tabName.charAt(0).toUpperCase() + tabName.slice(1)}`).classList.remove('hidden');
    
    // Activar botón seleccionado
    const activeButton = document.getElementById(`tab${tabName.charAt(0).toUpperCase() + tabName.slice(1)}`);
    activeButton.classList.add('active', 'bg-sky-50', 'border-l-4', 'border-sky-600');
    
    // Cargar datos según el tab
    if (tabName === 'actividad') {
        loadActividad();
    }
}

async function loadActividad() {
    await loadMisCasos();
    await loadMisDonaciones();
}

async function loadMisCasos() {
    try {
        const response = await apiClient.get(`/casos/?beneficiario=${perfilUsuario.id}`);
        const casos = response.data || [];
        
        const container = document.getElementById('misCasosLista');
        
        if (casos.length === 0) {
            container.innerHTML = '<p class="text-center text-sky-500 py-4">No has creado casos aún</p>';
            return;
        }
        
        container.innerHTML = casos.map(caso => `
            <a href="/web/casos/${caso.id}/" 
               class="block p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition border border-sky-100">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h3 class="font-semibold text-sky-800">${caso.titulo}</h3>
                        <p class="text-sm text-sky-600 mt-1 line-clamp-2">${caso.descripcion}</p>
                        <div class="flex items-center gap-4 mt-2 text-xs text-sky-500">
                            <span class="flex items-center">
                                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                                </svg>
                                ${caso.vistas || 0} vistas
                            </span>
                            <span>${formatDate(caso.fecha_creacion)}</span>
                        </div>
                    </div>
                    ${caso.estado ? `
                        <span class="px-3 py-1 text-xs font-semibold rounded-full ${getEstadoColor(caso.estado.nombre)}">
                            ${caso.estado.nombre}
                        </span>
                    ` : ''}
                </div>
            </a>
        `).join('');
        
    } catch (error) {
        console.error('Error cargando casos:', error);
    }
}

async function loadMisDonaciones() {
    try {
        const response = await apiClient.get(`/donaciones/?donador=${perfilUsuario.id}`);
        const donaciones = response.data || [];
        
        const container = document.getElementById('misDonacionesLista');
        
        if (donaciones.length === 0) {
            container.innerHTML = '<p class="text-center text-sky-500 py-4">No has realizado donaciones aún</p>';
            return;
        }
        
        container.innerHTML = donaciones.map(donacion => `
            <div class="p-4 bg-blue-50 rounded-lg border border-sky-100">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h3 class="font-semibold text-sky-800">$${parseFloat(donacion.monto).toFixed(2)}</h3>
                        <p class="text-sm text-sky-600 mt-1">${donacion.caso?.titulo || 'Caso no disponible'}</p>
                        <p class="text-xs text-sky-500 mt-2">${formatDate(donacion.fecha_compromiso)}</p>
                    </div>
                    <span class="px-3 py-1 text-xs font-semibold rounded-full ${getDonacionColor(donacion.estado_donacion)}">
                        ${donacion.estado_donacion || 'Pendiente'}
                    </span>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error cargando donaciones:', error);
    }
}

function setupForms() {
    // Formulario información personal
    const formInfo = document.getElementById('formInfoPersonal');
    formInfo.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const data = {
            nombres: document.getElementById('nombres').value.trim(),
            apellido_paterno: document.getElementById('apellido_paterno').value.trim(),
            apellido_materno: document.getElementById('apellido_materno').value.trim(),
            telefono: document.getElementById('telefono').value.trim(),
            ciudad: document.getElementById('ciudad').value.trim(),
            estado: document.getElementById('estado').value.trim(),
            direccion: document.getElementById('direccion').value.trim()
        };
        
        try {
            const result = await authService.updateProfile(data);
            
            if (result.success) {
                showAlert('Perfil actualizado correctamente', 'success');
                await loadPerfil();
            } else {
                showAlert(result.error || 'Error al actualizar perfil', 'danger');
            }
        } catch (error) {
            console.error('Error actualizando perfil:', error);
            showAlert('Error de conexión', 'danger');
        }
    });
    
    // Formulario cambiar contraseña
    const formPassword = document.getElementById('formCambiarContrasena');
    formPassword.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const contrasenaActual = document.getElementById('contrasena_actual').value;
        const contrasenaNueva = document.getElementById('contrasena_nueva').value;
        const confirmarContrasena = document.getElementById('confirmar_contrasena').value;
        
        if (contrasenaNueva !== confirmarContrasena) {
            showAlert('Las contraseñas no coinciden', 'warning');
            return;
        }
        
        if (contrasenaNueva.length < 8) {
            showAlert('La contraseña debe tener al menos 8 caracteres', 'warning');
            return;
        }
        
        try {
            const result = await authService.changePassword(contrasenaActual, contrasenaNueva, confirmarContrasena);
            
            if (result.success) {
                showAlert('Contraseña actualizada correctamente', 'success');
                formPassword.reset();
            } else {
                showAlert(result.error || 'Error al cambiar contraseña', 'danger');
            }
        } catch (error) {
            console.error('Error cambiando contraseña:', error);
            showAlert('Error de conexión', 'danger');
        }
    });
}

async function cambiarAvatar(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        
        // Validar tamaño (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            showAlert('La imagen no debe superar los 5MB', 'warning');
            return;
        }
        
        // Preview
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('avatarPreview').src = e.target.result;
        };
        reader.readAsDataURL(file);
        
        // Subir imagen
        try {
            const formData = new FormData();
            formData.append('imagen_perfil', file);
            
            const response = await fetch(`${apiClient.baseURL}/usuarios/me/perfil/`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: formData
            });
            
            if (response.ok) {
                showAlert('Foto de perfil actualizada', 'success');
            } else {
                showAlert('Error al subir la imagen', 'danger');
            }
        } catch (error) {
            console.error('Error subiendo avatar:', error);
            showAlert('Error de conexión', 'danger');
        }
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

function getDonacionColor(estado) {
    const colores = {
        'Pendiente': 'bg-yellow-100 text-yellow-800',
        'Completada': 'bg-green-100 text-green-800',
        'Rechazada': 'bg-red-100 text-red-800'
    };
    return colores[estado] || 'bg-gray-100 text-gray-800';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
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
