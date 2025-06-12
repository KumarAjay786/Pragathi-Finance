// frontend/js/app.js
import api from './api.js';

// Example login function
async function login(email, password) {
    try {
        const response = await api.post('/login/', {
            email,
            password
        });

        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);

        console.log('Logged in:', response.data.user);
    } catch (error) {
        console.error('Login failed:', error);
    }
}

// Example protected request
async function getDashboard() {
    try {
        const response = await api.get('/dashboard/user/');
        console.log('Dashboard data:', response.data);
    } catch (error) {
        console.error('Access denied:', error);
    }
}