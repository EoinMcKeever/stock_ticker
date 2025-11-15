import yfinance as yf
import anthropic
import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict
import os
from app.models import Ticker, NewsArticle, AIInsight


class NewsService:
    def __init__(self):
        self.anthropic_client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.alphavantage_key = os.getenv("ALPHAVANTAGE_API_KEY")
        self.finnhub_key = os.getenv("FINNHUB_API_KEY")
        self.marketaux_key = os.getenv("MARKETAUX_API_KEY")

    def fetch_yfinance_news(self, ticker_symbol: str) -> List[Dict]:
        """Fetch news from Yahoo Finance"""
        try:
            ticker = yf.Ticker(ticker_symbol)
            news = ticker.news

            parsed_news = []
            for article in news[:10]:
                parsed_news.append({
                    'title': article.get('title', ''),
                    'summary': article.get('summary', ''),
                    'url': article.get('link', ''),
                    'source': article.get('publisher', ''),
                    'provider': 'yfinance',
                    'published_at': datetime.fromtimestamp(article.get('providerPublishTime', 0)),
                    'sentiment': None
                })
            return parsed_news
        except Exception as e:
            print(f"Error fetching yfinance news for {ticker_symbol}: {e}")
            return []

    def fetch_alphavantage_news(self, ticker_symbol: str) -> List[Dict]:
        """Fetch news from Alpha Vantage with sentiment"""
        if not self.alphavantage_key:
            return []

        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': ticker_symbol,
                'apikey': self.alphavantage_key,
                'limit': 50
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if 'feed' not in data:
                return []

            parsed_news = []
            for article in data['feed'][:10]:
                sentiment_score = None
                for ticker_sentiment in article.get('ticker_sentiment', []):
                    if ticker_sentiment.get('ticker') == ticker_symbol:
                        sentiment_score = float(ticker_sentiment.get('ticker_sentiment_score', 0))
                        break

                parsed_news.append({
                    'title': article.get('title', ''),
                    'summary': article.get('summary', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', ''),
                    'provider': 'alphavantage',
                    'published_at': datetime.strptime(article.get('time_published', ''), '%Y%m%dT%H%M%S'),
                    'sentiment': sentiment_score
                })
            return parsed_news
        except Exception as e:
            print(f"Error fetching Alpha Vantage news: {e}")
            return []

    def fetch_finnhub_news(self, ticker_symbol: str) -> List[Dict]:
        """Fetch news from Finnhub"""
        if not self.finnhub_key:
            return []

        try:
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')

            url = "https://finnhub.io/api/v1/company-news"
            params = {
                'symbol': ticker_symbol,
                'from': from_date,
                'to': to_date,
                'token': self.finnhub_key
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            parsed_news = []
            for article in data[:10]:
                parsed_news.append({
                    'title': article.get('headline', ''),
                    'summary': article.get('summary', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', ''),
                    'provider': 'finnhub',
                    'published_at': datetime.fromtimestamp(article.get('datetime', 0)),
                    'sentiment': None
                })
            return parsed_news
        except Exception as e:
            print(f"Error fetching Finnhub news: {e}")
            return []

    def fetch_marketaux_news(self, ticker_symbol: str) -> List[Dict]:
        """Fetch news from Marketaux with sentiment"""
        if not self.marketaux_key:
            return []

        try:
            url = "https://api.marketaux.com/v1/news/all"
            params = {
                'symbols': ticker_symbol,
                'filter_entities': 'true',
                'language': 'en',
                'api_token': self.marketaux_key,
                'limit': 10
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if 'data' not in data:
                return []

            parsed_news = []
            for article in data['data']:
                sentiment_score = None
                for entity in article.get('entities', []):
                    if entity.get('symbol') == ticker_symbol:
                        sentiment = entity.get('sentiment_score')
                        if sentiment:
                            sentiment_score = float(sentiment)
                        break

                parsed_news.append({
                    'title': article.get('title', ''),
                    'summary': article.get('description', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', ''),
                    'provider': 'marketaux',
                    'published_at': datetime.fromisoformat(article.get('published_at', '').replace('Z', '+00:00')),
                    'sentiment': sentiment_score
                })
            return parsed_news
        except Exception as e:
            print(f"Error fetching Marketaux news: {e}")
            return []

    def fetch_all_news(self, ticker_symbol: str) -> List[Dict]:
        """Fetch news from all available sources"""
        all_news = []
        all_news.extend(self.fetch_yfinance_news(ticker_symbol))
        all_news.extend(self.fetch_alphavantage_news(ticker_symbol))
        all_news.extend(self.fetch_finnhub_news(ticker_symbol))
        all_news.extend(self.fetch_marketaux_news(ticker_symbol))

        all_news.sort(key=lambda x: x['published_at'], reverse=True)

        # Remove duplicates
        unique_news = []
        seen_titles = set()
        for article in all_news:
            title_lower = article['title'].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_news.append(article)

        return unique_news[:20]

    def analyze_news_with_ai(self, ticker_symbol: str, news_articles: List[Dict]) -> Dict:
        """Use Claude to analyze news articles from multiple sources"""
        sources_context = {}
        for article in news_articles[:15]:
            provider = article['provider']
            if provider not in sources_context:
                sources_context[provider] = []

            sources_context[provider].append({
                'title': article['title'],
                'summary': article['summary'],
                'source': article['source'],
                'date': article['published_at'].strftime('%Y-%m-%d'),
                'sentiment': article.get('sentiment')
            })

        news_context = ""
        for provider, articles in sources_context.items():
            news_context += f"\n\n--- {provider.upper()} NEWS ---\n"
            for article in articles:
                sentiment_str = f" (Sentiment: {article['sentiment']:.2f})" if article['sentiment'] else ""
                news_context += f"\nTitle: {article['title']}{sentiment_str}\nSummary: {article['summary']}\nSource: {article['source']}\nDate: {article['date']}\n"

        prompt = f"""You are a financial analyst providing unbiased insights on {ticker_symbol}.

Recent news from multiple sources:
{news_context}

Provide comprehensive analysis:
1. **Summary**: Key developments (3-4 sentences), consensus vs conflicts
2. **Sentiment**: Overall (bullish/bearish/neutral) with reasoning
3. **Impact**: Short-term and long-term
4. **Risks & Opportunities**: Key points from multiple sources
5. **Confidence Score** (0-100): Based on source agreement

Be objective. Highlight disagreements. Avoid hype.

Format as JSON: summary, sentiment, sentiment_reasoning, short_term_impact, long_term_impact, risks, opportunities, source_agreement, confidence_score"""

        try:
            message = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text

            import json
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            return json.loads(response_text)
        except Exception as e:
            print(f"Error analyzing news: {e}")
            return {
                "summary": "Analysis unavailable",
                "sentiment": "neutral",
                "sentiment_reasoning": "Error occurred",
                "short_term_impact": "Unknown",
                "long_term_impact": "Unknown",
                "risks": "Analysis unavailable",
                "opportunities": "Analysis unavailable",
                "source_agreement": "Unknown",
                "confidence_score": 0
            }

    def save_news_and_insights(self, ticker_id: int, ticker_symbol: str, db: Session):
        """Fetch news, analyze, and save to database"""
        news_articles = self.fetch_all_news(ticker_symbol)

        if not news_articles:
            print(f"No news for {ticker_symbol}")
            return

        print(f"Found {len(news_articles)} articles for {ticker_symbol}")

        saved_count = 0
        for article in news_articles:
            existing = db.query(NewsArticle).filter(
                NewsArticle.url == article['url']
            ).first()

            if not existing:
                news_obj = NewsArticle(
                    ticker_id=ticker_id,
                    title=article['title'],
                    summary=article['summary'],
                    url=article['url'],
                    source=article['source'],
                    news_provider=article['provider'],
                    published_at=article['published_at'],
                    sentiment_score=article.get('sentiment')
                )
                db.add(news_obj)
                saved_count += 1

        db.commit()
        print(f"Saved {saved_count} new articles")

        ai_analysis = self.analyze_news_with_ai(ticker_symbol, news_articles)
        sources_count = len(set(a['provider'] for a in news_articles))

        sentiment_map = {
            'bullish': 0.7, 'bearish': -0.7, 'neutral': 0.0,
            'very_bullish': 0.9, 'very_bearish': -0.9
        }

        insight_content = f"""**Summary:**
{ai_analysis.get('summary', '')}

**Sentiment Reasoning:**
{ai_analysis.get('sentiment_reasoning', '')}

**Short-term Impact:**
{ai_analysis.get('short_term_impact', '')}

**Long-term Impact:**
{ai_analysis.get('long_term_impact', '')}

**Risks:**
{ai_analysis.get('risks', '')}

**Opportunities:**
{ai_analysis.get('opportunities', '')}

**Source Agreement:**
{ai_analysis.get('source_agreement', '')}"""

        insight = AIInsight(
            ticker_id=ticker_id,
            insight_type='market_analysis',
            content=insight_content,
            sentiment=ai_analysis.get('sentiment', 'neutral'),
            confidence_score=ai_analysis.get('confidence_score', 0) / 100.0,
            sources_analyzed=sources_count
        )
        db.add(insight)
        db.commit()
        print(f"Saved AI insight for {ticker_symbol}")