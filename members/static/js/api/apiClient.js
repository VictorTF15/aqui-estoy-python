const apiClient = {
    baseURL: 'http://127.0.0.1:8000/api', // ← Asegúrate de que sea esta URL
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const token = localStorage.getItem('access_token');
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers,
            });
            
            if (response.status === 401) {
                // Token expirado, intentar refresh
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    // Reintentar la petición original
                    headers['Authorization'] = `Bearer ${localStorage.getItem('access_token')}`;
                    return await fetch(url, { ...options, headers });
                } else {
                    // Redirigir al login
                    window.location.href = '/login/';
                    throw new Error('Sesión expirada');
                }
            }
            
            return response;
        } catch (error) {
            console.error('Error en la petición:', error);
            throw error;
        }
    },
    
    async get(endpoint) {
        const response = await this.request(endpoint, { method: 'GET' });
        return response.json();
    },
    
    async post(endpoint, data) {
        const response = await this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
        return response.json();
    },
    
    async put(endpoint, data) {
        const response = await this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
        return response.json();
    },
    
    async patch(endpoint, data) {
        const response = await this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
        return response.json();
    },
    
    async delete(endpoint) {
        const response = await this.request(endpoint, { method: 'DELETE' });
        return response.ok;
    },
    
    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) return false;
        
        try {
            const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: refreshToken }),
            });
            
            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access);
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }
};