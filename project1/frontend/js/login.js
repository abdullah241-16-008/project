document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    const messageEl = document.getElementById('message');

    if (messageEl) messageEl.innerText = '';
    
    // Simple validation
    if (!username || !password) {
        showAlert('Please fill in all fields.', 'error');
        return;
    }
    
    if (password.length < 6) {
        showAlert('Password must be at least 6 characters long.', 'error');
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
            
        });

        const data = await res.json().catch(() => ({}));
        const message = data.message || 'Login response received.';

        if (res.ok) {
            showAlert(message, 'success');
            if (messageEl) messageEl.innerText = message;
            setCurrentUser(username);
            if (data.user_id !== undefined) {
                saveToLocalStorage('currentUserId', data.user_id);
            }
            localStorage.setItem('isLoggedIn', 'true');
            setTimeout(() => navigateTo('dashboard.html'), 800);
        } else {
            showAlert(message, 'error');
            if (messageEl) messageEl.innerText = message;
        }
    } catch (err) {
        const fallback = 'Network error. Please try again.';
        showAlert(fallback, 'error');
        if (messageEl) messageEl.innerText = fallback;
    }
});