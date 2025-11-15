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
const refreshAllBtn = document.getElementById('refreshAllBtn');
const addTickerBtn = document.getElementById('addTickerBtn');
const tickersContainer = document.getElementById('tickersContainer');
const loadingState = document.getElementById('loadingState');
const emptyState = document.getElementById('emptyState');
const errorMessage = document.getElementById('errorMessage');

// Modal Elements
const addTickerModal = document.getElementById('addTickerModal');
const closeModal = document.getElementById('closeModal');
const addTickerForm = document.getElementById('addTickerForm');
const tickerSymbolInput = document.getElementById('tickerSymbol');
const submitTickerBtn = document.getElementById('submitTickerBtn');
const modalError = document.getElementById('modalError');
const modalSuccess = document.getElementById('modalSuccess');

// Logout handler
logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
});

// Refresh all tickers
refreshAllBtn.addEventListener('click', async () => {
    refreshAllBtn.disabled = true;
    refreshAllBtn.textContent = 'Refreshing...';
    await loadDashboard();
    refreshAllBtn.disabled = false;
    refreshAllBtn.textContent = 'Refresh All';
});

// Modal handlers
addTickerBtn.addEventListener('click', () => {
    addTickerModal.classList.add('show');
    tickerSymbolInput.focus();
});

closeModal.addEventListener('click', () => {
    addTickerModal.classList.remove('show');
    clearModalMessages();
    addTickerForm.reset();
});

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if (e.target === addTickerModal) {
        addTickerModal.classList.remove('show');
        clearModalMessages();
        addTickerForm.reset();
    }
});

// Clear modal messages
function clearModalMessages() {
    modalError.classList.remove('show');
    modalSuccess.classList.remove('show');
}

// Show modal error
function showModalError(message) {
    clearModalMessages();
    modalError.textContent = message;
    modalError.classList.add('show');
}

// Show modal success
function showModalSuccess(message) {
    clearModalMessages();
    modalSuccess.textContent = message;
    modalSuccess.classList.add('show');
}

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
    setTimeout(() => {
        errorMessage.classList.remove('show');
    }, 5000);
}

// Add ticker form handler
addTickerForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const symbol = tickerSymbolInput.value.trim().toUpperCase();
    if (!symbol) {
        showModalError('Please enter a ticker symbol');
        return;
    }

    submitTickerBtn.disabled = true;
    submitTickerBtn.textContent = 'Adding...';
    clearModalMessages();

    try {
        const response = await fetch('/api/tickers/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                symbol: symbol,
                name: symbol,
                type: 'stock'
            })
        });

        const data = await response.json();

        if (response.ok) {
            showModalSuccess(`${symbol} added successfully!`);
            addTickerForm.reset();

            // Close modal and reload dashboard after 1.5 seconds
            setTimeout(() => {
                addTickerModal.classList.remove('show');
                clearModalMessages();
                loadDashboard();
            }, 1500);
        } else {
            showModalError(data.detail || `Failed to add ${symbol}. Please check the symbol and try again.`);
        }
    } catch (error) {
        showModalError('An error occurred. Please try again.');
        console.error('Add ticker error:', error);
    } finally {
        submitTickerBtn.disabled = false;
        submitTickerBtn.textContent = 'Add Ticker';
    }
});

// Remove ticker function
async function removeTicker(symbol) {
    if (!confirm(`Are you sure you want to remove ${symbol} from your dashboard?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/tickers/remove/${symbol}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            // Reload dashboard
            await loadDashboard();
        } else {
            const data = await response.json();
            showError(data.detail || `Failed to remove ${symbol}`);
        }
    } catch (error) {
        showError('An error occurred while removing the ticker.');
        console.error('Remove ticker error:', error);
    }
}

// Format date to relative time
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
}

// Create AI insight card
function createInsightCard(insight) {
    const card = document.createElement('div');
    card.className = 'insight-card';

    const header = document.createElement('div');
    header.className = 'insight-header';

    const type = document.createElement('div');
    type.className = 'insight-type';
    type.textContent = insight.insight_type;

    const confidence = document.createElement('div');
    confidence.className = 'insight-confidence';
    if (insight.confidence_score !== null) {
        confidence.textContent = `${Math.round(insight.confidence_score * 100)}% confidence`;
    } else {
        confidence.textContent = 'AI Analysis';
    }

    header.appendChild(type);
    header.appendChild(confidence);

    const content = document.createElement('div');
    content.className = 'insight-content';
    content.textContent = insight.content;

    const meta = document.createElement('div');
    meta.className = 'insight-meta';

    if (insight.sentiment) {
        const sentiment = document.createElement('span');
        sentiment.textContent = `Sentiment: ${insight.sentiment}`;
        meta.appendChild(sentiment);
    }

    if (insight.sources_analyzed) {
        const sources = document.createElement('span');
        sources.textContent = `${insight.sources_analyzed} sources analyzed`;
        meta.appendChild(sources);
    }

    card.appendChild(header);
    card.appendChild(content);
    if (meta.children.length > 0) {
        card.appendChild(meta);
    }

    return card;
}

// Create news article card
function createNewsCard(article) {
    const card = document.createElement('div');
    card.className = 'news-card';
    card.onclick = () => {
        if (article.url) {
            window.open(article.url, '_blank');
        }
    };

    const title = document.createElement('div');
    title.className = 'news-title';
    title.textContent = article.title;

    if (article.summary) {
        const summary = document.createElement('div');
        summary.className = 'news-summary';
        summary.textContent = article.summary;
        card.appendChild(title);
        card.appendChild(summary);
    } else {
        card.appendChild(title);
    }

    const meta = document.createElement('div');
    meta.className = 'news-meta';

    const leftMeta = document.createElement('div');
    const source = document.createElement('span');
    source.className = 'news-source';
    source.textContent = article.news_provider || article.source || 'Unknown';
    leftMeta.appendChild(source);
    leftMeta.appendChild(document.createTextNode(' • '));
    leftMeta.appendChild(document.createTextNode(formatDate(article.published_at)));

    meta.appendChild(leftMeta);

    if (article.sentiment_score !== null) {
        const sentiment = document.createElement('span');
        sentiment.className = 'news-sentiment';
        const score = article.sentiment_score;
        if (score > 0.1) {
            sentiment.textContent = '📈 Positive';
            sentiment.style.background = '#d4edda';
            sentiment.style.color = '#155724';
        } else if (score < -0.1) {
            sentiment.textContent = '📉 Negative';
            sentiment.style.background = '#f8d7da';
            sentiment.style.color = '#721c24';
        } else {
            sentiment.textContent = '➡️ Neutral';
            sentiment.style.background = '#fff3cd';
            sentiment.style.color = '#856404';
        }
        meta.appendChild(sentiment);
    }

    card.appendChild(meta);
    return card;
}

// Create ticker dashboard card
function createTickerDashboardCard(tickerData) {
    const card = document.createElement('div');
    card.className = 'ticker-dashboard-card';

    // Ticker Header
    const header = document.createElement('div');
    header.className = 'ticker-header';

    const info = document.createElement('div');
    info.className = 'ticker-info';

    const symbol = document.createElement('div');
    symbol.className = 'ticker-main-symbol';
    symbol.textContent = tickerData.ticker_symbol;

    const details = document.createElement('div');
    details.className = 'ticker-details';

    const name = document.createElement('div');
    name.className = 'ticker-main-name';
    name.textContent = tickerData.ticker_name;

    const badges = document.createElement('div');
    badges.className = 'ticker-badges';

    const typeBadge = document.createElement('span');
    typeBadge.className = 'ticker-type-badge';
    typeBadge.textContent = tickerData.ticker_type;
    typeBadge.style.background = tickerData.ticker_type === 'crypto' ? '#f59e0b' : '#667eea';

    const sentimentBadge = document.createElement('span');
    sentimentBadge.className = `sentiment-badge sentiment-${tickerData.overall_sentiment}`;
    sentimentBadge.textContent = tickerData.overall_sentiment;

    const sourcesBadge = document.createElement('span');
    sourcesBadge.className = 'news-sources-badge';
    sourcesBadge.textContent = `${tickerData.news_sources_count} sources`;

    badges.appendChild(typeBadge);
    badges.appendChild(sentimentBadge);
    badges.appendChild(sourcesBadge);

    details.appendChild(name);
    details.appendChild(badges);

    info.appendChild(symbol);
    info.appendChild(details);
    header.appendChild(info);

    // Add remove button
    const removeBtn = document.createElement('button');
    removeBtn.className = 'remove-ticker-btn';
    removeBtn.textContent = 'Remove';
    removeBtn.onclick = () => removeTicker(tickerData.ticker_symbol);
    header.appendChild(removeBtn);

    card.appendChild(header);

    // AI Insights Section
    const insightsSection = document.createElement('div');
    insightsSection.className = 'ai-insights-section';

    const insightsTitle = document.createElement('h3');
    insightsTitle.textContent = 'AI Insights';

    insightsSection.appendChild(insightsTitle);

    if (tickerData.ai_insights && tickerData.ai_insights.length > 0) {
        const insightsGrid = document.createElement('div');
        insightsGrid.className = 'insights-grid';

        tickerData.ai_insights.forEach(insight => {
            const insightCard = createInsightCard(insight);
            insightsGrid.appendChild(insightCard);
        });

        insightsSection.appendChild(insightsGrid);
    } else {
        const noInsights = document.createElement('div');
        noInsights.className = 'no-insights';
        noInsights.textContent = 'No AI insights available yet. News is being analyzed...';
        insightsSection.appendChild(noInsights);
    }

    card.appendChild(insightsSection);

    // News Section
    const newsSection = document.createElement('div');
    newsSection.className = 'news-section';

    const newsTitle = document.createElement('h3');
    newsTitle.textContent = 'Latest News';

    newsSection.appendChild(newsTitle);

    if (tickerData.latest_news && tickerData.latest_news.length > 0) {
        const newsGrid = document.createElement('div');
        newsGrid.className = 'news-grid';

        tickerData.latest_news.forEach(article => {
            const newsCard = createNewsCard(article);
            newsGrid.appendChild(newsCard);
        });

        newsSection.appendChild(newsGrid);
    } else {
        const noNews = document.createElement('div');
        noNews.className = 'no-news';
        noNews.textContent = 'No recent news articles available.';
        newsSection.appendChild(noNews);
    }

    card.appendChild(newsSection);

    return card;
}

// Fetch user info
async function loadUserInfo() {
    try {
        const response = await fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
            return null;
        }

        if (!response.ok) {
            throw new Error('Failed to load user info');
        }

        const user = await response.json();

        // Display user info
        const firstLetter = user.username.charAt(0).toUpperCase();
        userAvatar.textContent = firstLetter;
        userName.textContent = `Welcome, ${user.username}!`;
        userEmail.textContent = user.email;

        return user;
    } catch (error) {
        console.error('User info error:', error);
        return null;
    }
}

// Fetch and display dashboard data with news
async function loadDashboard() {
    try {
        // Load user info if not already loaded
        if (!userName.textContent || userName.textContent === 'Loading...') {
            await loadUserInfo();
        }

        const response = await fetch('/api/news/dashboard-news?hours=24', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
            return;
        }

        if (!response.ok) {
            throw new Error('Failed to load dashboard data');
        }

        const tickersData = await response.json();

        // Hide loading state
        loadingState.style.display = 'none';

        // Display tickers with news
        if (tickersData && tickersData.length > 0) {
            tickersContainer.style.display = 'flex';
            emptyState.style.display = 'none';

            tickersContainer.innerHTML = '';
            tickersData.forEach(tickerData => {
                const card = createTickerDashboardCard(tickerData);
                tickersContainer.appendChild(card);
            });
        } else {
            tickersContainer.style.display = 'none';
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

// Refresh dashboard every 2 minutes
setInterval(loadDashboard, 120000);
