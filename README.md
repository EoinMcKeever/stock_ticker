# Stock & Crypto Dashboard

> AI-powered stock and cryptocurrency news dashboard with multi-source aggregation and sentiment analysis.

Track your favorite stocks and cryptocurrencies with real-time news from multiple sources, analyzed by Claude AI to give you actionable insights.

## Features

- 📊 **Track Multiple Assets** - Stocks and cryptocurrencies in one dashboard
- 🤖 **AI-Powered Analysis** - Claude Sonnet 4 analyzes news from 4 different sources
- 📰 **Multi-Source News** - Yahoo Finance, Alpha Vantage, Finnhub, Marketaux
- 💡 **Smart Insights** - Sentiment analysis, risk assessment, and confidence scoring
- 🔄 **Auto-Updates** - Background scheduler fetches news every 4 hours
- 🌐 **Web Interface** - Easy-to-use dashboard (no coding required!)

## Quick Start

### 1. Get Your API Keys

**Required:**
- **Anthropic API Key** - Sign up at https://console.anthropic.com
  - New accounts get free credits
  - Pay-as-you-go: ~$0.003 per analysis

**Optional (Free tiers available):**
- Alpha Vantage: https://www.alphavantage.co/support/#api-key
- Finnhub: https://finnhub.io/register
- Marketaux: https://www.marketaux.com/account/signup

### 2. Setup

```bash
# Clone the repository
git clone <repository-url>
cd stock_ticker

# Copy environment file
cp .env.example .env

# Edit .env and add your API keys
# Replace 'your-anthropic-api-key-here' with your actual Anthropic API key
nano .env  # or use your favorite editor
```

**Your `.env` file should look like:**
```bash
SECRET_KEY=generate-a-random-secret-key-here
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-ACTUAL-KEY-HERE
DATABASE_URL=postgresql://dashboard_user:dashboard_pass@db:5432/dashboard_db

# Optional - add these for more news sources
ALPHAVANTAGE_API_KEY=YOUR-KEY-HERE
FINNHUB_API_KEY=YOUR-KEY-HERE
MARKETAUX_API_KEY=YOUR-KEY-HERE
```

### 3. Start the Application

```bash
docker-compose up --build
```

Wait for the services to start (about 30 seconds), then open your browser.

## Using the Dashboard

### Access the Web Interface

Open your browser and go to:
```
http://localhost:8000
```

### First Time Setup

1. **Register an Account**
   - Click "Register here" on the login page
   - Enter your email, username, and password (min 8 characters)
   - Click "Register"

2. **Login**
   - Enter your username and password
   - Click "Login"

### Managing Your Dashboard

#### Add a Ticker

1. Click the **"+ Add Ticker"** button
2. Enter a ticker symbol:
   - **Stocks**: AAPL, GOOGL, TSLA, MSFT
   - **Crypto**: BTC-USD, ETH-USD, ADA-USD
3. Click "Add Ticker"
4. Wait for news to be fetched (happens automatically)

#### View AI Insights

Each ticker card shows:
- **Latest News** - Headlines from multiple sources
- **AI Analysis** - Claude's comprehensive market analysis including:
  - Summary of key developments
  - Overall sentiment (Bullish/Bearish/Neutral)
  - Short-term and long-term impact
  - Risks and opportunities
  - Confidence score based on source agreement
- **Sentiment Indicator** - Visual indicator of market sentiment
- **Source Count** - Number of news sources analyzed

#### Refresh News

- **Refresh All**: Click "Refresh All" to update all your tickers
- **Refresh Single**: Click refresh icon on individual ticker cards

#### Remove a Ticker

- Click the "Remove" button on any ticker card

## API Documentation

If you want to use the API directly (for developers):

**Interactive API Docs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Key Endpoints:**
```bash
# Authentication
POST /api/auth/register    # Create account
POST /api/auth/login       # Login

# Tickers
POST /api/tickers/create   # Add ticker
GET  /api/dashboard        # Get your tickers

# News & AI
GET  /api/news/dashboard-news                # Dashboard with news & AI insights
GET  /api/news/ticker/{symbol}/news          # News for specific ticker
GET  /api/news/ticker/{symbol}/insights      # AI insights for specific ticker
POST /api/news/ticker/{symbol}/refresh       # Manually refresh ticker news
```

## Project Structure

```
stock_ticker/
├── app/
│   ├── routers/          # API endpoints (auth, tickers, news, dashboard)
│   ├── services/         # News aggregation & AI analysis
│   ├── tasks/            # Background scheduler
│   ├── models.py         # Database models
│   └── schemas.py        # API schemas
├── templates/            # Web interface (login, dashboard)
├── static/              # CSS and JavaScript
├── main.py              # Application entry point
├── docker-compose.yml   # Docker configuration
└── .env                 # Your API keys (create from .env.example)
```

## How It Works

1. **You add a ticker** (e.g., AAPL)
2. **System fetches news** from all configured sources
3. **Claude AI analyzes** the aggregated news
4. **Dashboard displays** news + AI insights
5. **Auto-refresh** every 4 hours keeps data fresh

## Troubleshooting

### "AI analysis features not working"
- Check that `ANTHROPIC_API_KEY` is set correctly in `.env`
- Make sure there are no quotes around the key
- Restart: `docker-compose down && docker-compose up --build`

### "No news appearing"
- Wait a few minutes after adding a ticker (news fetches on startup)
- Click "Refresh All" to manually fetch news
- Check logs: `docker-compose logs -f app`

### "Can't login/register"
- Make sure PostgreSQL is running: `docker-compose ps`
- Check database logs: `docker-compose logs db`

### "Getting rate limit errors"
- Free API tiers have limits (5 requests/min for Alpha Vantage)
- Add more API keys to distribute load
- Or wait for the automatic 4-hour refresh cycle

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **AI**: Anthropic Claude Sonnet 4
- **News**: Yahoo Finance, Alpha Vantage, Finnhub, Marketaux
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Background Jobs**: APScheduler
- **Deployment**: Docker & Docker Compose

## Configuration Tips

### For Development
- Set `DEBUG=true` in `.env`
- News refreshes every 4 hours (configurable in `app/tasks/news_tasks.py`)

### For Production
- Change `SECRET_KEY` to a strong random string
- Set `DEBUG=false`
- Use environment variables instead of `.env` file
- Set up proper PostgreSQL with backups
- Consider rate limits on news APIs

## License

[Add your license here]

## Support

For issues and questions, please open an issue in the repository.

---

**Note**: This application uses external APIs that may have rate limits and costs. Monitor your usage on each provider's dashboard.
