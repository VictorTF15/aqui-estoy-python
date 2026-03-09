const authService = {
    async login(correo, contrasena) {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/auth/token/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ correo, contrasena }),
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                return { success: true, data };
            } else {
                const error = await response.json();
                return { success: false, error: error.detail || 'Credenciales incorrectas' };
            }
        } catch (error) {
            console.error('Error en login:', error);
            return { success: false, error: 'Error de conexión' };
        }
    },

    async register(userData) {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/usuarios/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
            });

            if (response.ok) {
                const data = await response.json();
                return { success: true, data };
            } else {
                const error = await response.json();
                return { success: false, error };
            }
        } catch (error) {
            console.error('Error en registro:', error);
            return { success: false, error: 'Error de conexión' };
        }
    },

    async getProfile() {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                return { success: false, error: 'No hay sesión activa' };
            }

            const response = await fetch('http://127.0.0.1:8000/api/usuarios/me/', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                const data = await response.json();
                return { success: true, data };
            } else {
                return { success: false, error: 'No se pudo obtener el perfil' };
            }
        } catch (error) {
            console.error('Error obteniendo perfil:', error);
            return { success: false, error: 'Error de conexión' };
        }
    },

    async updateProfile(userData) {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('http://127.0.0.1:8000/api/usuarios/me/', {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
            });

            if (response.ok) {
                const data = await response.json();
                return { success: true, data };
            } else {
                const error = await response.json();
                return { success: false, error };
            }
        } catch (error) {
            console.error('Error actualizando perfil:', error);
            return { success: false, error: 'Error de conexión' };
        }
    },

    async changePassword(oldPassword, newPassword) {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('http://127.0.0.1:8000/api/usuarios/change-password/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    old_password: oldPassword,
                    new_password: newPassword,
                }),
            });

            if (response.ok) {
                return { success: true };
            } else {
                const error = await response.json();
                return { success: false, error };
            }
        } catch (error) {
            console.error('Error cambiando contraseña:', error);
            return { success: false, error: 'Error de conexión' };
        }
    },

    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/web/login/';
    },

    isAuthenticated() {
        return !!localStorage.getItem('access_token');
    }
};