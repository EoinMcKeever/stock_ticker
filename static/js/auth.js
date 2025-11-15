// DOM Elements
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const loginContainer = document.querySelector('.container');
const registerContainer = document.getElementById('registerContainer');
const showRegisterLink = document.getElementById('showRegister');
const showLoginLink = document.getElementById('showLogin');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');
const registerErrorMessage = document.getElementById('registerErrorMessage');
const registerSuccessMessage = document.getElementById('registerSuccessMessage');

// Toggle between login and register forms
showRegisterLink.addEventListener('click', (e) => {
    e.preventDefault();
    loginContainer.style.display = 'none';
    registerContainer.style.display = 'block';
    clearMessages();
});

showLoginLink.addEventListener('click', (e) => {
    e.preventDefault();
    registerContainer.style.display = 'none';
    loginContainer.style.display = 'block';
    clearMessages();
});

// Clear all messages
function clearMessages() {
    errorMessage.classList.remove('show');
    successMessage.classList.remove('show');
    registerErrorMessage.classList.remove('show');
    registerSuccessMessage.classList.remove('show');
}

// Show error message
function showError(message, isRegister = false) {
    clearMessages();
    if (isRegister) {
        registerErrorMessage.textContent = message;
        registerErrorMessage.classList.add('show');
    } else {
        errorMessage.textContent = message;
        errorMessage.classList.add('show');
    }
}

// Show success message
function showSuccess(message, isRegister = false) {
    clearMessages();
    if (isRegister) {
        registerSuccessMessage.textContent = message;
        registerSuccessMessage.classList.add('show');
    } else {
        successMessage.textContent = message;
        successMessage.classList.add('show');
    }
}

// Login handler
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginBtn = document.getElementById('loginBtn');

    // Disable button and show loading state
    loginBtn.disabled = true;
    loginBtn.textContent = 'Logging in...';
    clearMessages();

    try {
        // Create form data for OAuth2 login
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            // Store the token
            localStorage.setItem('access_token', data.access_token);

            // Show success message briefly
            showSuccess('Login successful! Redirecting...');

            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            showError(data.detail || 'Login failed. Please check your credentials.');
            loginBtn.disabled = false;
            loginBtn.textContent = 'Login';
        }
    } catch (error) {
        showError('An error occurred. Please try again.');
        loginBtn.disabled = false;
        loginBtn.textContent = 'Login';
    }
});

// Register handler
registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('registerEmail').value;
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    const registerBtn = document.getElementById('registerBtn');

    // Disable button and show loading state
    registerBtn.disabled = true;
    registerBtn.textContent = 'Registering...';
    clearMessages();

    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, username, password })
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess('Registration successful! Please login.', true);

            // Switch to login form after 2 seconds
            setTimeout(() => {
                registerContainer.style.display = 'none';
                loginContainer.style.display = 'block';
                registerForm.reset();
            }, 2000);
        } else {
            showError(data.detail || 'Registration failed. Please try again.', true);
            registerBtn.disabled = false;
            registerBtn.textContent = 'Register';
        }
    } catch (error) {
        showError('An error occurred. Please try again.', true);
        registerBtn.disabled = false;
        registerBtn.textContent = 'Register';
    }
});

// Check if user is already logged in
if (localStorage.getItem('access_token')) {
    // Verify token is still valid
    fetch('/api/auth/me', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    }).then(response => {
        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            localStorage.removeItem('access_token');
        }
    });
}
