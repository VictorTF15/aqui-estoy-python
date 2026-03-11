document.addEventListener('DOMContentLoaded', async function() {
    await loadTiposUsuario();
    setupForm();
});

async function loadTiposUsuario() {
    try {
        const response = await apiClient.get('/tipos-usuario/');
        const tipos = response.data || [];
        
        const select = document.getElementById('id_tipo_usuario');
        tipos.forEach(tipo => {
            // Excluir tipo Administrador del registro público
            if (tipo.nombre !== 'Administrador') {
                const option = document.createElement('option');
                option.value = tipo.id;
                option.textContent = tipo.nombre;
                select.appendChild(option);
            }
        });
    } catch (error) {
        console.error('Error cargando tipos de usuario:', error);
    }
}

function setupForm() {
    const form = document.getElementById('registerForm');
    const registerBtn = document.getElementById('registerBtn');
    const registerText = document.getElementById('registerText');
    const registerSpinner = document.getElementById('registerSpinner');
    const alertContainer = document.getElementById('alertContainer');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Validar campos
        const formData = {
            nombres: document.getElementById('nombres').value.trim(),
            apellido_paterno: document.getElementById('apellido_paterno').value.trim(),
            apellido_materno: document.getElementById('apellido_materno').value.trim(),
            correo: document.getElementById('correo').value.trim(),
            telefono: document.getElementById('telefono').value.trim(),
            ciudad: document.getElementById('ciudad').value.trim(),
            estado: document.getElementById('estado').value.trim(),
            id_tipo_usuario: document.getElementById('id_tipo_usuario').value,
            contrasena: document.getElementById('contrasena').value,
            confirmar_contrasena: document.getElementById('confirmar_contrasena').value
        };

        // Validaciones
        if (!formData.nombres || !formData.apellido_paterno || !formData.correo || 
            !formData.telefono || !formData.ciudad || !formData.estado || 
            !formData.id_tipo_usuario || !formData.contrasena) {
            showAlert('Por favor completa todos los campos obligatorios', 'warning');
            return;
        }

        if (formData.contrasena.length < 8) {
            showAlert('La contraseña debe tener al menos 8 caracteres', 'warning');
            return;
        }

        if (formData.contrasena !== formData.confirmar_contrasena) {
            showAlert('Las contraseñas no coinciden', 'warning');
            return;
        }

        if (!document.getElementById('terminos').checked) {
            showAlert('Debes aceptar los términos y condiciones', 'warning');
            return;
        }

        // Validar email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.correo)) {
            showAlert('El correo electrónico no es válido', 'warning');
            return;
        }

        // Validar teléfono (10 dígitos)
        const phoneRegex = /^\d{10}$/;
        if (!phoneRegex.test(formData.telefono)) {
            showAlert('El teléfono debe tener 10 dígitos', 'warning');
            return;
        }

        // Deshabilitar botón
        registerBtn.disabled = true;
        registerText.classList.add('hidden');
        registerSpinner.classList.remove('hidden');

        try {
            // Remover campo de confirmación antes de enviar
            delete formData.confirmar_contrasena;

            const result = await authService.register(formData);

            if (result.success) {
                showAlert('Cuenta creada exitosamente. Redirigiendo...', 'success');
                
                setTimeout(() => {
                    window.location.href = '/login/';
                }, 2000);
            } else {
                showAlert(result.error || 'Error al crear la cuenta', 'danger');
                registerBtn.disabled = false;
                registerText.classList.remove('hidden');
                registerSpinner.classList.add('hidden');
            }
        } catch (error) {
            showAlert('Error de conexión. Por favor intenta de nuevo.', 'danger');
            registerBtn.disabled = false;
            registerText.classList.remove('hidden');
            registerSpinner.classList.add('hidden');
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

    const alert = `
        <div class="mb-4 p-4 rounded-md border ${colorClasses[type]} animate-fade-in">
            <p class="text-sm font-medium">${message}</p>
        </div>
    `;
    
    alertContainer.innerHTML = alert;

    setTimeout(() => {
        alertContainer.innerHTML = '';
    }, 5000);
}