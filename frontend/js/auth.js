// js/auth.js
import { API_ENDPOINTS, TOKEN_KEY } from './config.js';
import { apiCall, saveToken, removeTokens } from './api.js';

// Form switching
document.getElementById('showRegister')?.addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('registerForm').classList.remove('hidden');
    clearMessage();
});

document.getElementById('showLogin')?.addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('registerForm').classList.add('hidden');
    document.getElementById('loginForm').classList.remove('hidden');
    clearMessage();
});

// Login form
document.getElementById('login')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        showMessage('Logging in...', 'success');
        
        const data = await apiCall(API_ENDPOINTS.LOGIN, {
            method: 'POST',
            body: JSON.stringify({ email, password }),
            skipAuth: true
        });
        
        saveToken(data.access_token, data.refresh_token);
        showMessage('Login successful! Redirecting...', 'success');
        
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
        
    } catch (error) {
        showMessage(error.message || 'Login failed. Please check your credentials.', 'error');
    }
});

// Register form
document.getElementById('register')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('registerEmail').value;
    const username = document.getElementById('registerUsername').value;
    const fullName = document.getElementById('registerFullName').value;
    const password = document.getElementById('registerPassword').value;
    
    if (password.length < 8) {
        showMessage('Password must be at least 8 characters', 'error');
        return;
    }
    
    try {
        showMessage('Creating account...', 'success');
        
        await apiCall(API_ENDPOINTS.REGISTER, {
            method: 'POST',
            body: JSON.stringify({
                email,
                username,
                full_name: fullName || null,
                password,
                is_active: true,
                is_verified: false,
                role: 'user'
            }),
            skipAuth: true
        });
        
        showMessage('Account created! Please login.', 'success');
        
        setTimeout(() => {
            document.getElementById('registerForm').classList.add('hidden');
            document.getElementById('loginForm').classList.remove('hidden');
            document.getElementById('loginEmail').value = email;
        }, 1500);
        
    } catch (error) {
        showMessage(error.message || 'Registration failed. Please try again.', 'error');
    }
});

function showMessage(message, type) {
    const messageEl = document.getElementById('message');
    messageEl.textContent = message;
    messageEl.className = `message ${type}`;
}

function clearMessage() {
    const messageEl = document.getElementById('message');
    messageEl.className = 'message';
    messageEl.textContent = '';
}