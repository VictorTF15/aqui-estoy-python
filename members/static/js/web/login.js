document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');
    const loginText = document.getElementById('loginText');
    const loginSpinner = document.getElementById('loginSpinner');
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    const alertContainer = document.getElementById('alertContainer');

    // Toggle mostrar/ocultar contraseña
    togglePassword.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        const icon = this.querySelector('i');
        icon.classList.toggle('bi-eye');
        icon.classList.toggle('bi-eye-slash');
    });

    // Función para mostrar alertas
    function showAlert(message, type = 'danger') {
        const alert = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="bi bi-${type === 'danger' ? 'exclamation-circle' : 'check-circle'}"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        alertContainer.innerHTML = alert;

        // Auto-cerrar después de 5 segundos
        setTimeout(() => {
            const alertElement = alertContainer.querySelector('.alert');
            if (alertElement) {
                alertElement.remove();
            }
        }, 5000);
    }

    // Manejar envío del formulario
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        // Validaciones básicas
        if (!email || !password) {
            showAlert('Por favor completa todos los campos');
            return;
        }

        // Deshabilitar botón y mostrar spinner
        loginBtn.disabled = true;
        loginText.classList.add('d-none');
        loginSpinner.classList.remove('d-none');

        try {
            const result = await authService.login(email, password);

            if (result.success) {
                showAlert('Inicio de sesión exitoso. Redirigiendo...', 'success');
                
                // Redirigir después de 1 segundo
                setTimeout(() => {
                    window.location.href = '/home/';
                }, 1000);
            } else {
                showAlert(result.error || 'Error al iniciar sesión. Verifica tus credenciales.');
                loginBtn.disabled = false;
                loginText.classList.remove('d-none');
                loginSpinner.classList.add('d-none');
            }
        } catch (error) {
            showAlert('Error de conexión. Por favor intenta de nuevo.');
            loginBtn.disabled = false;
            loginText.classList.remove('d-none');
            loginSpinner.classList.add('d-none');
        }
    });

    // Verificar si ya está autenticado
    if (authService.isAuthenticated()) {
        window.location.href = '/home/';
    }
});