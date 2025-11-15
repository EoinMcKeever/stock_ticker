"""
Stock News System Diagnostic Test
Run this to test and debug your news fetching system
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")


def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")


def print_section(title):
    print(f"\n{Colors.BLUE}{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}{Colors.END}\n")


# Test 1: Check if API is running
print_section("1. Testing API Connection")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        print_success(f"API is running at {BASE_URL}")
    else:
        print_error(f"API returned status {response.status_code}")
        exit(1)
except Exception as e:
    print_error(f"Cannot connect to API: {e}")
    print_info("Make sure Docker is running: docker-compose up")
    exit(1)

# Test 2: Register/Login User
print_section("2. User Authentication")
username = f"testuser_{int(time.time())}"
password = "testpass123"

try:
    # Try to register
    register_data = {
        "email": f"{username}@test.com",
        "username": username,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    if response.status_code == 201:
        print_success(f"Registered new user: {username}")
    else:
        print_warning(f"Registration returned {response.status_code} (user might exist)")

    # Login
    login_data = {
        "username": username,
        "password": password
    }
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data=login_data
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print_success("Successfully logged in")
        print_info(f"Token: {token[:30]}...")
    else:
        print_error(f"Login failed: {response.text}")
        exit(1)

except Exception as e:
    print_error(f"Authentication error: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Test 3: Add a ticker
print_section("3. Adding Test Ticker")
test_ticker = "AAPL"

try:
    ticker_data = {
        "symbol": test_ticker,
        "name": "Apple Inc.",
        "type": "stock"
    }
    response = requests.post(
        f"{BASE_URL}/api/tickers/create",
        json=ticker_data,
        headers=headers
    )
    if response.status_code in [200, 201]:
        print_success(f"Added ticker: {test_ticker}")
        ticker_result = response.json()
        print_info(f"Ticker ID: {ticker_result.get('id')}")
        print_info(f"Ticker Name: {ticker_result.get('name')}")
    elif response.status_code == 400 and "already" in response.text.lower():
        print_warning(f"Ticker {test_ticker} already exists (this is OK)")
    else:
        print_error(f"Failed to add ticker: {response.status_code} - {response.text}")
        exit(1)
except Exception as e:
    print_error(f"Error adding ticker: {e}")
    exit(1)

# Test 4: Test News Service Directly
print_section("4. Testing News APIs Directly")

# Test yfinance
print_info("Testing yfinance...")
try:
    import yfinance as yf

    ticker = yf.Ticker(test_ticker)
    news = ticker.news
    if news and len(news) > 0:
        print_success(f"yfinance: Found {len(news)} articles")
        print_info(f"  Sample: {news[0].get('title', 'N/A')[:60]}...")
    else:
        print_warning("yfinance: No news found")
except Exception as e:
    print_error(f"yfinance error: {e}")

# Test Alpha Vantage (if key exists)
print_info("\nTesting Alpha Vantage...")
try:
    import os

    av_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if av_key:
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': test_ticker,
            'apikey': av_key,
            'limit': 5
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if 'feed' in data and len(data['feed']) > 0:
            print_success(f"Alpha Vantage: Found {len(data['feed'])} articles")
            print_info(f"  Sample: {data['feed'][0].get('title', 'N/A')[:60]}...")
        else:
            print_warning(f"Alpha Vantage: No news or error: {data.get('Note', data.get('Information', 'Unknown'))}")
    else:
        print_warning("Alpha Vantage: API key not set")
except Exception as e:
    print_error(f"Alpha Vantage error: {e}")

# Test Finnhub
print_info("\nTesting Finnhub...")
try:
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    if finnhub_key:
        from datetime import datetime, timedelta

        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        to_date = datetime.now().strftime('%Y-%m-%d')

        url = "https://finnhub.io/api/v1/company-news"
        params = {
            'symbol': test_ticker,
            'from': from_date,
            'to': to_date,
            'token': finnhub_key
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            print_success(f"Finnhub: Found {len(data)} articles")
            print_info(f"  Sample: {data[0].get('headline', 'N/A')[:60]}...")
        else:
            print_warning(f"Finnhub: No news or error")
    else:
        print_warning("Finnhub: API key not set")
except Exception as e:
    print_error(f"Finnhub error: {e}")

# Test Marketaux
print_info("\nTesting Marketaux...")
try:
    marketaux_key = os.getenv("MARKETAUX_API_KEY")
    if marketaux_key:
        url = "https://api.marketaux.com/v1/news/all"
        params = {
            'symbols': test_ticker,
            'filter_entities': 'true',
            'language': 'en',
            'api_token': marketaux_key,
            'limit': 5
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            print_success(f"Marketaux: Found {len(data['data'])} articles")
            print_info(f"  Sample: {data['data'][0].get('title', 'N/A')[:60]}...")
        else:
            print_warning(f"Marketaux: No news or error")
    else:
        print_warning("Marketaux: API key not set")
except Exception as e:
    print_error(f"Marketaux error: {e}")

# Test 5: Manually Trigger News Refresh
print_section("5. Manually Triggering News Fetch")
try:
    print_info(f"Refreshing news for {test_ticker}...")
    response = requests.post(
        f"{BASE_URL}/api/news/ticker/{test_ticker}/refresh",
        headers=headers
    )
    if response.status_code == 200:
        print_success("News refresh triggered successfully")
    else:
        print_error(f"Refresh failed: {response.status_code} - {response.text}")

    # Wait a bit for processing
    print_info("Waiting 5 seconds for news to be processed...")
    time.sleep(5)

except Exception as e:
    print_error(f"Error triggering refresh: {e}")

# Test 6: Check Database for News
print_section("6. Checking Database for News Articles")
try:
    response = requests.get(
        f"{BASE_URL}/api/news/ticker/{test_ticker}/news?limit=20",
        headers=headers
    )
    if response.status_code == 200:
        news = response.json()
        if len(news) > 0:
            print_success(f"Found {len(news)} news articles in database!")

            # Show breakdown by provider
            providers = {}
            for article in news:
                provider = article.get('news_provider', 'unknown')
                providers[provider] = providers.get(provider, 0) + 1

            print_info("\nArticles by provider:")
            for provider, count in providers.items():
                print(f"  • {provider}: {count} articles")

            # Show sample articles
            print_info("\nSample articles:")
            for article in news[:3]:
                print(f"\n  📰 {article['title'][:70]}...")
                print(f"     Source: {article['news_provider']} - {article['source']}")
                print(f"     Published: {article['published_at']}")
                if article.get('sentiment_score'):
                    print(f"     Sentiment: {article['sentiment_score']:.2f}")
        else:
            print_warning("No news articles found in database")
            print_info("This could mean:")
            print_info("  1. News APIs didn't return data")
            print_info("  2. Background task hasn't run yet")
            print_info("  3. There's an error in the news service")
    elif response.status_code == 404:
        print_error(f"Ticker not found in your list")
    else:
        print_error(f"Failed to get news: {response.status_code} - {response.text}")
except Exception as e:
    print_error(f"Error checking news: {e}")

# Test 7: Check for AI Insights
print_section("7. Checking for AI Insights")
try:
    response = requests.get(
        f"{BASE_URL}/api/news/ticker/{test_ticker}/insights",
        headers=headers
    )
    if response.status_code == 200:
        insights = response.json()
        if len(insights) > 0:
            print_success(f"Found {len(insights)} AI insights!")

            for i, insight in enumerate(insights[:2], 1):
                print(f"\n  🤖 Insight #{i}:")
                print(f"     Sentiment: {insight['sentiment']}")
                print(f"     Confidence: {insight['confidence_score']:.2%}")
                print(f"     Sources analyzed: {insight['sources_analyzed']}")
                print(f"     Created: {insight['created_at']}")
                print(f"     Content preview: {insight['content'][:150]}...")
        else:
            print_warning("No AI insights found")
            print_info("AI insights are generated after news is fetched")
    else:
        print_error(f"Failed to get insights: {response.status_code}")
except Exception as e:
    print_error(f"Error checking insights: {e}")

# Test 8: Check Dashboard
print_section("8. Testing Dashboard Endpoint")
try:
    response = requests.get(
        f"{BASE_URL}/api/news/dashboard-news?hours=24",
        headers=headers
    )
    if response.status_code == 200:
        dashboard = response.json()
        print_success(f"Dashboard loaded with {len(dashboard)} tickers")

        for ticker_data in dashboard:
            print(f"\n  📊 {ticker_data['ticker_symbol']} - {ticker_data['ticker_name']}")
            print(f"     News articles: {len(ticker_data['latest_news'])}")
            print(f"     AI insights: {len(ticker_data['ai_insights'])}")
            print(f"     Overall sentiment: {ticker_data['overall_sentiment']}")
            print(f"     News sources: {ticker_data['news_sources_count']}")
    else:
        print_error(f"Dashboard failed: {response.status_code}")
except Exception as e:
    print_error(f"Error checking dashboard: {e}")

# Test 9: Check Docker Logs
print_section("9. Checking Application Logs")
print_info("To see detailed logs, run:")
print(f"{Colors.YELLOW}docker-compose logs dashboard_app --tail=50{Colors.END}")
print_info("\nLook for these messages:")
print("  • 'News scheduler started'")
print("  • 'Updating news for X tickers'")
print("  • 'Found X articles for TICKER'")
print("  • 'Saved X new articles'")
print("  • 'Saved AI insight for TICKER'")

# Test 10: Environment Check
print_section("10. Environment Variables Check")
print_info("Checking if API keys are set...")
try:
    import subprocess

    result = subprocess.run(
        ["docker", "exec", "dashboard_app", "printenv"],
        capture_output=True,
        text=True
    )
    env_vars = result.stdout

    keys_to_check = [
        "ANTHROPIC_API_KEY",
        "ALPHAVANTAGE_API_KEY",
        "FINNHUB_API_KEY",
        "MARKETAUX_API_KEY"
    ]

    for key in keys_to_check:
        if key in env_vars and f"{key}=" in env_vars:
            value = [line for line in env_vars.split('\n') if line.startswith(f"{key}=")][0]
            if len(value.split('=')[1]) > 5:
                print_success(f"{key} is set")
            else:
                print_warning(f"{key} is set but appears empty")
        else:
            print_warning(f"{key} is NOT set")

except Exception as e:
    print_warning(f"Could not check environment variables: {e}")
    print_info("Manually check with: docker exec dashboard_app printenv | grep API_KEY")

# Final Summary
print_section("Summary & Next Steps")

print_info("If news is NOT showing up, try these steps:")
print("\n1. Check Docker logs:")
print(f"   {Colors.YELLOW}docker-compose logs dashboard_app | grep -i news{Colors.END}")

print("\n2. Verify API keys are in your .env file:")
print(f"   {Colors.YELLOW}cat .env | grep API_KEY{Colors.END}")

print("\n3. Restart containers to pick up .env changes:")
print(f"   {Colors.YELLOW}docker-compose down && docker-compose up --build{Colors.END}")

print("\n4. Manually trigger news refresh:")
print(
    f"   {Colors.YELLOW}curl -X POST http://localhost:8000/api/news/ticker/{test_ticker}/refresh -H 'Authorization: Bearer {token[:20]}...'{Colors.END}")

print("\n5. Check database directly:")
print(
    f"   {Colors.YELLOW}docker exec -it dashboard_db psql -U dashboard_user -d dashboard_db -c 'SELECT COUNT(*) FROM news_articles;'{Colors.END}")

print("\n6. View Swagger UI for interactive testing:")
print(f"   {Colors.YELLOW}http://localhost:8000/docs{Colors.END}")

print(f"\n{Colors.GREEN}Test completed!{Colors.END}\n")