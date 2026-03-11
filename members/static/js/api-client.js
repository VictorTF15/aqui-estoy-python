const API_BASE_URL = 'http://127.0.0.1:8000/api';

class ApiClient {
    constructor() {
        this.baseUrl = API_BASE_URL;
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
    }

    // Headers con autenticación
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (includeAuth && this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }
        
        return headers;
    }

    // Manejar respuestas
    async handleResponse(response) {
        if (response.status === 401) {
            // Token expirado, intentar refrescar
            const refreshed = await this.refreshAccessToken();
            if (!refreshed) {
                this.logout();
                return null;
            }
        }

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || error.message || 'Error en la petición');
        }

        return response.json();
    }

    // Refrescar token
    async refreshAccessToken() {
        if (!this.refreshToken) return false;

        try {
            const response = await fetch(`${this.baseUrl}/auth/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: this.refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                this.accessToken = data.access;
                localStorage.setItem('access_token', data.access);
                return true;
            }
        } catch (error) {
            console.error('Error al refrescar token:', error);
        }
        
        return false;
    }

    // ========== AUTENTICACIÓN ==========
    
    async login(correo, contrasena) {
        try {
            const response = await fetch(`${this.baseUrl}/auth/login/`, {
                method: 'POST',
                headers: this.getHeaders(false),
                body: JSON.stringify({ correo, contrasena })
            });

            const data = await this.handleResponse(response);
            
            if (data) {
                this.accessToken = data.access;
                this.refreshToken = data.refresh;
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                localStorage.setItem('user', JSON.stringify(data.user));
                return data;
            }
        } catch (error) {
            throw error;
        }
    }

    logout() {
        this.accessToken = null;
        this.refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login/';
    }

    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }

    isAuthenticated() {
        return !!this.accessToken;
    }

    // ========== USUARIOS ==========
    
    async getMiPerfil() {
        const response = await fetch(`${this.baseUrl}/usuarios/me/`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    async actualizarMiPerfil(data) {
        const response = await fetch(`${this.baseUrl}/usuarios/me/perfil/`, {
            method: 'PATCH',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }

    async cambiarContrasena(contrasenaActual, contrasenaNueva) {
        const response = await fetch(`${this.baseUrl}/usuarios/me/contrasena/`, {
            method: 'PATCH',
            headers: this.getHeaders(),
            body: JSON.stringify({
                contrasena_actual: contrasenaActual,
                contrasena_nueva: contrasenaNueva
            })
        });
        return this.handleResponse(response);
    }

    // ========== CASOS ==========
    
    async getCasos(filtros = {}) {
        const params = new URLSearchParams(filtros);
        const response = await fetch(`${this.baseUrl}/casos/?${params}`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    async getCaso(id) {
        const response = await fetch(`${this.baseUrl}/casos/${id}/`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    async crearCaso(data) {
        const response = await fetch(`${this.baseUrl}/casos/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }

    async actualizarCaso(id, data) {
        const response = await fetch(`${this.baseUrl}/casos/${id}/`, {
            method: 'PATCH',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }

    async getMisCasos() {
        const response = await fetch(`${this.baseUrl}/casos/mis-casos/`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    async getCasosMapa() {
        const response = await fetch(`${this.baseUrl}/casos/mapa/`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    async compartirCaso(id, medio, destinatario) {
        const response = await fetch(`${this.baseUrl}/casos/${id}/compartir/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({ medio, destinatario })
        });
        return this.handleResponse(response);
    }

    // ========== CATEGORÍAS ==========
    
    async getCategorias() {
        const response = await fetch(`${this.baseUrl}/categorias/`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    async getCasosPorCategoria(categoriaId) {
        const response = await fetch(`${this.baseUrl}/categorias/${categoriaId}/casos/`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    // ========== DONACIONES ==========
    
    async getDonaciones() {
        const response = await fetch(`${this.baseUrl}/donaciones/`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    async crearDonacion(data) {
        const response = await fetch(`${this.baseUrl}/donaciones/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }

    async getMisDonaciones() {
        const response = await fetch(`${this.baseUrl}/donaciones/mis-donaciones/`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    // ========== CONVERSACIONES ==========
    
    async getConversaciones() {
        const response = await fetch(`${this.baseUrl}/conversaciones/`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    async getMensajes(conversacionId) {
        const response = await fetch(`${this.baseUrl}/conversaciones/${conversacionId}/mensajes/`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    async enviarMensaje(conversacionId, contenido, tipo = null) {
        const response = await fetch(`${this.baseUrl}/conversaciones/${conversacionId}/enviar_mensaje/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({ contenido, tipo })
        });
        return this.handleResponse(response);
    }
}

// Instancia global
const api = new ApiClient();