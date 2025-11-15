// Check if user is logged in
const token = localStorage.getItem('access_token');
if (!token) {
    window.location.href = '/login';
}

// DOM Elements
const userAvatar = document.getElementById('userAvatar');
const userName = document.getElementById('userName');
const userEmail = document.getElementById('userEmail');
const logoutBtn = document.getElementById('logoutBtn');
const tickersGrid = document.getElementById('tickersGrid');
const loadingState = document.getElementById('loadingState');
const emptyState = document.getElementById('emptyState');
const errorMessage = document.getElementById('errorMessage');

// Logout handler
logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
});

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
}

// Create ticker card element
function createTickerCard(ticker) {
    const card = document.createElement('div');
    card.className = 'ticker-card';

    const symbol = document.createElement('div');
    symbol.className = 'ticker-symbol';
    symbol.textContent = ticker.symbol;

    const name = document.createElement('div');
    name.className = 'ticker-name';
    name.textContent = ticker.name;

    const type = document.createElement('div');
    type.className = 'ticker-type';
    type.textContent = ticker.type;
    type.style.background = ticker.type === 'crypto' ? '#f59e0b' : '#667eea';

    card.appendChild(symbol);
    card.appendChild(name);
    card.appendChild(type);

    return card;
}

// Fetch and display dashboard data
async function loadDashboard() {
    try {
        const response = await fetch('/api/dashboard/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('access_token');
            window.location.href = '/login';
            return;
        }

        if (!response.ok) {
            throw new Error('Failed to load dashboard data');
        }

        const data = await response.json();

        // Display user info
        const firstLetter = data.user.username.charAt(0).toUpperCase();
        userAvatar.textContent = firstLetter;
        userName.textContent = `Welcome, ${data.user.username}!`;
        userEmail.textContent = data.user.email;

        // Hide loading state
        loadingState.style.display = 'none';

        // Display tickers
        if (data.tickers && data.tickers.length > 0) {
            tickersGrid.style.display = 'grid';
            emptyState.style.display = 'none';

            tickersGrid.innerHTML = '';
            data.tickers.forEach(ticker => {
                const card = createTickerCard(ticker);
                tickersGrid.appendChild(card);
            });
        } else {
            tickersGrid.style.display = 'none';
            emptyState.style.display = 'block';
        }

    } catch (error) {
        loadingState.style.display = 'none';
        showError('Failed to load dashboard. Please try again.');
        console.error('Dashboard error:', error);
    }
}

// Load dashboard on page load
loadDashboard();

// Refresh dashboard every 30 seconds
setInterval(loadDashboard, 30000);
