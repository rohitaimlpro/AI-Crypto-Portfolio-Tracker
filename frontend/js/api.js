// js/api.js
import { TOKEN_KEY } from './config.js';

export async function apiCall(url, options = {}) {
    const token = localStorage.getItem(TOKEN_KEY);
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token && !options.skipAuth) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || data.detail || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

export function saveToken(token, refreshToken) {
    localStorage.setItem(TOKEN_KEY, token);
    if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
    }
}

export function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

export function removeTokens() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem('refresh_token');
}

export function isAuthenticated() {
    return !!getToken();
}