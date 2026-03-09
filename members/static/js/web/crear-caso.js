document.addEventListener('DOMContentLoaded', async function() {
    await loadCategorias();
    setupForm();
});

async function loadCategorias() {
    try {
        const response = await apiClient.get('/categorias/');
        const categorias = response.data || [];
        
        const select = document.getElementById('id_categoria');
        categorias.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = cat.nombre;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error cargando categorías:', error);
        showAlert('Error cargando categorías', 'danger');
    }
}

function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            preview.classList.add('has-image');
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

function setupForm() {
    const form = document.getElementById('formCrearCaso');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validaciones
        const titulo = document.getElementById('titulo').value.trim();
        const descripcion = document.getElementById('descripcion').value.trim();
        const beneficiario = document.getElementById('beneficiario').value.trim();
        const colonia = document.getElementById('colonia').value.trim();
        const ciudad = document.getElementById('ciudad').value.trim();
        const estado = document.getElementById('estado').value.trim();
        const id_categoria = document.getElementById('id_categoria').value;
        
        if (!titulo || !descripcion || !beneficiario || !colonia || !ciudad || !estado || !id_categoria) {
            showAlert('Por favor completa todos los campos obligatorios', 'warning');
            return;
        }
        
        // Deshabilitar botón
        const btnSubmit = document.getElementById('btnSubmit');
        const submitText = document.getElementById('submitText');
        const submitSpinner = document.getElementById('submitSpinner');
        
        btnSubmit.disabled = true;
        submitText.classList.add('hidden');
        submitSpinner.classList.remove('hidden');
        
        try {
            // Preparar FormData para imágenes
            const formData = new FormData();
            
            // Datos básicos
            formData.append('titulo', titulo);
            formData.append('descripcion', descripcion);
            formData.append('beneficiario', beneficiario);
            formData.append('calle', document.getElementById('calle').value.trim());
            formData.append('numero', document.getElementById('numero').value.trim());
            formData.append('colonia', colonia);
            formData.append('codigo_postal', document.getElementById('codigo_postal').value.trim());
            formData.append('ciudad', ciudad);
            formData.append('estado', estado);
            formData.append('id_categoria', id_categoria);
            
            const metaDonacion = document.getElementById('meta_donacion').value;
            if (metaDonacion) {
                formData.append('meta_donacion', metaDonacion);
            }
            
            // Imágenes
            const imagen1 = document.getElementById('imagen1').files[0];
            const imagen2 = document.getElementById('imagen2').files[0];
            const imagen3 = document.getElementById('imagen3').files[0];
            const imagen4 = document.getElementById('imagen4').files[0];
            
            if (imagen1) formData.append('imagen1', imagen1);
            if (imagen2) formData.append('imagen2', imagen2);
            if (imagen3) formData.append('imagen3', imagen3);
            if (imagen4) formData.append('imagen4', imagen4);
            
            // Enviar
            const response = await fetch(`${apiClient.baseURL}/casos/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                showAlert('¡Caso creado exitosamente!', 'success');
                
                setTimeout(() => {
                    window.location.href = `/web/casos/${data.id}/`;
                }, 2000);
            } else {
                const errorData = await response.json();
                showAlert(errorData.detail || 'Error al crear el caso', 'danger');
                btnSubmit.disabled = false;
                submitText.classList.remove('hidden');
                submitSpinner.classList.add('hidden');
            }
            
        } catch (error) {
            console.error('Error creando caso:', error);
            showAlert('Error de conexión. Por favor intenta de nuevo.', 'danger');
            btnSubmit.disabled = false;
            submitText.classList.remove('hidden');
            submitSpinner.classList.add('hidden');
        }
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
        <div class="flex items-center p-4 mb-4 rounded-md border ${colorClasses[type]} animate-fade-in">
            <div class="flex-shrink-0 mr-3">${icons[type]}</div>
            <p class="text-sm font-medium">${message}</p>
        </div>
    `;
    
    alertContainer.innerHTML = alert;
    
    setTimeout(() => {
        alertContainer.innerHTML = '';
    }, 5000);
}