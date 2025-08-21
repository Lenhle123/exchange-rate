import requests
import yfinance as yf
from datetime import datetime, timedelta
import random
import time
from textblob import TextBlob

class ExternalAPIService:
    """Service for integrating with external APIs for exchange rates, news, and sentiment analysis"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Exchange-Rate-Forecasting-App/1.0'
        })
    
    def get_real_exchange_rates(self, pairs):
        """Get real exchange rates using yfinance as a fallback"""
        rates = {}
        
        for pair in pairs:
            try:
                # Convert pair format for yfinance (USD/EUR -> USDEUR=X)
                if '/' in pair:
                    base, quote = pair.split('/')
                    symbol = f"{base}{quote}=X"
                else:
                    symbol = pair
                
                # Get data from yfinance
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d", interval="1m")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[0] if len(hist) > 1 else current_price
                    change = current_price - prev_price
                    
                    rates[pair] = {
                        'rate': round(float(current_price), 4),
                        'change': round(float(change), 4),
                        'timestamp': datetime.utcnow().isoformat(),
                        'source': 'yfinance'
                    }
                else:
                    # Fallback to simulated data
                    rates[pair] = self._get_simulated_rate(pair)
                    
            except Exception as e:
                print(f"Error fetching rate for {pair}: {e}")
                # Fallback to simulated data
                rates[pair] = self._get_simulated_rate(pair)
        
        return rates
    
    def _get_simulated_rate(self, pair):
        """Generate simulated exchange rate data"""
        base_rates = {
            'USD/EUR': 1.0545,
            'USD/GBP': 0.7823,
            'USD/JPY': 149.85,
            'EUR/GBP': 0.8412,
            'EUR/JPY': 142.15,
            'GBP/JPY': 191.58
        }
        
        base_rate = base_rates.get(pair, 1.0000)
        variation = random.uniform(-0.01, 0.01)
        current_rate = base_rate + variation
        change = random.uniform(-0.005, 0.005)
        
        return {
            'rate': round(current_rate, 4),
            'change': round(change, 4),
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'simulated'
        }
    
    def get_historical_rates(self, pair, period='1mo'):
        """Get historical exchange rate data"""
        try:
            if '/' in pair:
                base, quote = pair.split('/')
                symbol = f"{base}{quote}=X"
            else:
                symbol = pair
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval="1h")
            
            if not hist.empty:
                historical_data = []
                for index, row in hist.iterrows():
                    historical_data.append({
                        'timestamp': index.isoformat(),
                        'rate': round(float(row['Close']), 4),
                        'high': round(float(row['High']), 4),
                        'low': round(float(row['Low']), 4),
                        'open': round(float(row['Open']), 4),
                        'volume': int(row['Volume']) if row['Volume'] > 0 else random.randint(1000000, 5000000)
                    })
                
                return historical_data
            else:
                return self._generate_simulated_history(pair, period)
                
        except Exception as e:
            print(f"Error fetching historical data for {pair}: {e}")
            return self._generate_simulated_history(pair, period)
    
    def _generate_simulated_history(self, pair, period):
        """Generate simulated historical data"""
        base_rates = {
            'USD/EUR': 1.0545,
            'USD/GBP': 0.7823,
            'USD/JPY': 149.85,
            'EUR/GBP': 0.8412,
            'EUR/JPY': 142.15,
            'GBP/JPY': 191.58
        }
        
        base_rate = base_rates.get(pair, 1.0000)
        
        # Determine number of data points based on period
        if period == '1d':
            hours = 24
        elif period == '1w' or period == '7d':
            hours = 168
        elif period == '1mo':
            hours = 720
        else:
            hours = 168
        
        historical_data = []
        for i in range(hours):
            timestamp = datetime.utcnow() - timedelta(hours=hours-i)
            variation = random.uniform(-0.02, 0.02)
            rate = base_rate + variation
            
            historical_data.append({
                'timestamp': timestamp.isoformat(),
                'rate': round(rate, 4),
                'high': round(rate + random.uniform(0, 0.01), 4),
                'low': round(rate - random.uniform(0, 0.01), 4),
                'open': round(rate + random.uniform(-0.005, 0.005), 4),
                'volume': random.randint(1000000, 5000000)
            })
        
        return historical_data
    
    def get_financial_news(self, query, limit=10):
        """Get financial news (simulated for demo)"""
        # In a real implementation, this would use NewsAPI, Finnhub, or similar
        sample_headlines = [
            "Federal Reserve Signals Potential Rate Changes",
            "European Central Bank Maintains Current Policy Stance",
            "GDP Growth Exceeds Expectations in Major Economies",
            "Trade Relations Show Signs of Improvement",
            "Inflation Data Suggests Cooling Trend",
            "Central Bank Intervention Stabilizes Currency Markets",
            "Economic Indicators Point to Continued Growth",
            "Market Volatility Increases Amid Uncertainty",
            "Currency Traders React to Latest Economic Data",
            "International Trade Agreements Boost Market Confidence"
        ]
        
        news_articles = []
        for i in range(min(limit, len(sample_headlines))):
            headline = sample_headlines[i]
            
            # Generate content
            content = f"Recent developments in {query} markets have shown significant activity. {headline.lower()} according to latest reports from financial institutions. Market analysts are closely monitoring the situation as it develops."
            
            # Simple sentiment analysis using TextBlob
            blob = TextBlob(content)
            sentiment_score = blob.sentiment.polarity
            
            if sentiment_score > 0.1:
                sentiment_label = 'positive'
            elif sentiment_score < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            article = {
                'id': f'news_{i+1}',
                'title': headline,
                'content': content,
                'source': random.choice(['Reuters', 'Bloomberg', 'Financial Times', 'Wall Street Journal', 'CNBC']),
                'url': f'https://example.com/news/{i+1}',
                'timestamp': (datetime.utcnow() - timedelta(hours=random.randint(1, 48))).isoformat(),
                'sentiment': {
                    'score': round(sentiment_score, 3),
                    'label': sentiment_label,
                    'confidence': round(abs(sentiment_score) + 0.5, 2)
                },
                'relevance': round(random.uniform(0.6, 1.0), 2),
                'impact': random.choice(['high', 'medium', 'low'])
            }
            
            news_articles.append(article)
        
        return news_articles
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text using TextBlob"""
        try:
            blob = TextBlob(text)
            sentiment_score = blob.sentiment.polarity
            
            if sentiment_score > 0.1:
                label = 'positive'
            elif sentiment_score < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'score': round(sentiment_score, 3),
                'label': label,
                'confidence': round(abs(sentiment_score) + 0.5, 2)
            }
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'score': 0.0,
                'label': 'neutral',
                'confidence': 0.5
            }
    
    def get_economic_indicators(self, country='US'):
        """Get economic indicators (simulated for demo)"""
        indicators = {
            'US': {
                'gdp_growth': round(random.uniform(1.5, 3.5), 2),
                'inflation_rate': round(random.uniform(2.0, 4.0), 2),
                'unemployment_rate': round(random.uniform(3.0, 6.0), 2),
                'interest_rate': round(random.uniform(0.5, 5.0), 2),
                'consumer_confidence': round(random.uniform(80, 120), 1)
            },
            'EU': {
                'gdp_growth': round(random.uniform(0.5, 2.5), 2),
                'inflation_rate': round(random.uniform(1.5, 3.5), 2),
                'unemployment_rate': round(random.uniform(6.0, 9.0), 2),
                'interest_rate': round(random.uniform(0.0, 3.0), 2),
                'consumer_confidence': round(random.uniform(70, 110), 1)
            },
            'UK': {
                'gdp_growth': round(random.uniform(0.0, 2.0), 2),
                'inflation_rate': round(random.uniform(2.0, 5.0), 2),
                'unemployment_rate': round(random.uniform(3.5, 6.5), 2),
                'interest_rate': round(random.uniform(1.0, 6.0), 2),
                'consumer_confidence': round(random.uniform(75, 115), 1)
            },
            'JP': {
                'gdp_growth': round(random.uniform(-0.5, 1.5), 2),
                'inflation_rate': round(random.uniform(0.0, 2.0), 2),
                'unemployment_rate': round(random.uniform(2.0, 4.0), 2),
                'interest_rate': round(random.uniform(-0.5, 1.0), 2),
                'consumer_confidence': round(random.uniform(85, 125), 1)
            }
        }
        
        return indicators.get(country, indicators['US'])
    
    def check_api_health(self):
        """Check the health of external APIs"""
        health_status = {
            'yfinance': self._check_yfinance_health(),
            'news_service': {'status': 'simulated', 'response_time': 0.1},
            'sentiment_service': {'status': 'active', 'response_time': 0.05}
        }
        
        return health_status
    
    def _check_yfinance_health(self):
        """Check yfinance API health"""
        try:
            start_time = time.time()
            ticker = yf.Ticker("EURUSD=X")
            info = ticker.info
            response_time = time.time() - start_time
            
            return {
                'status': 'active' if info else 'degraded',
                'response_time': round(response_time, 3)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'response_time': None
            }

# Global instance
external_api_service = ExternalAPIService()

