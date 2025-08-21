from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random

news_bp = Blueprint('news', __name__)

# Sample news data
SAMPLE_NEWS = [
    {
        'title': 'Federal Reserve Signals Potential Rate Changes',
        'content': 'The Federal Reserve indicated potential monetary policy adjustments that could significantly impact currency markets in the coming months...',
        'source': 'Financial Times',
        'category': 'monetary_policy',
        'impact_level': 'high'
    },
    {
        'title': 'European Central Bank Maintains Current Policy Stance',
        'content': 'The ECB decided to keep interest rates unchanged while monitoring inflation trends across the eurozone...',
        'source': 'Reuters',
        'category': 'monetary_policy',
        'impact_level': 'medium'
    },
    {
        'title': 'GDP Growth Exceeds Expectations in Major Economies',
        'content': 'Recent economic data shows stronger than expected growth in several major economies, boosting currency confidence...',
        'source': 'Bloomberg',
        'category': 'economic_data',
        'impact_level': 'high'
    },
    {
        'title': 'Trade Relations Show Signs of Improvement',
        'content': 'Diplomatic efforts have led to improved trade relations between major economic partners, reducing market uncertainty...',
        'source': 'Wall Street Journal',
        'category': 'trade',
        'impact_level': 'medium'
    },
    {
        'title': 'Inflation Data Suggests Cooling Trend',
        'content': 'Latest inflation figures indicate a gradual cooling of price pressures, potentially influencing central bank decisions...',
        'source': 'CNBC',
        'category': 'economic_data',
        'impact_level': 'high'
    }
]

@news_bp.route('/news/<pair>')
def get_news_for_pair(pair):
    """Get news articles relevant to a currency pair"""
    limit = int(request.args.get('limit', 10))
    sentiment_filter = request.args.get('sentiment')  # positive, negative, neutral
    impact_filter = request.args.get('impact')  # high, medium, low
    
    # Generate news articles
    articles = []
    for i in range(min(limit, len(SAMPLE_NEWS) * 2)):
        base_article = SAMPLE_NEWS[i % len(SAMPLE_NEWS)]
        
        # Generate sentiment
        sentiment_score = random.uniform(-0.5, 0.5)
        if sentiment_score > 0.1:
            sentiment_label = 'positive'
        elif sentiment_score < -0.1:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        # Apply sentiment filter
        if sentiment_filter and sentiment_label != sentiment_filter:
            continue
        
        # Apply impact filter
        if impact_filter and base_article['impact_level'] != impact_filter:
            continue
        
        article = {
            'id': f'news_{i+1}',
            'title': base_article['title'].replace('Major Economies', pair.replace('/', ' and ')),
            'content': base_article['content'],
            'source': base_article['source'],
            'url': f'https://example.com/news/{i+1}',
            'timestamp': (datetime.utcnow() - timedelta(hours=random.randint(1, 48))).isoformat(),
            'category': base_article['category'],
            'sentiment': {
                'score': round(sentiment_score, 3),
                'label': sentiment_label,
                'confidence': round(random.uniform(0.7, 0.95), 2)
            },
            'relevance': {
                'score': round(random.uniform(0.6, 1.0), 2),
                'keywords': get_keywords_for_pair(pair),
                'entities': extract_entities(pair)
            },
            'impact': base_article['impact_level'],
            'read_time': random.randint(2, 8)
        }
        
        articles.append(article)
    
    # Calculate sentiment summary
    if articles:
        sentiment_scores = [a['sentiment']['score'] for a in articles]
        positive_count = sum(1 for a in articles if a['sentiment']['label'] == 'positive')
        neutral_count = sum(1 for a in articles if a['sentiment']['label'] == 'neutral')
        negative_count = sum(1 for a in articles if a['sentiment']['label'] == 'negative')
        
        sentiment_summary = {
            'overall_sentiment': round(sum(sentiment_scores) / len(sentiment_scores), 3),
            'positive_count': positive_count,
            'neutral_count': neutral_count,
            'negative_count': negative_count,
            'total_articles': len(articles),
            'trending_topics': get_trending_topics(pair),
            'sentiment_distribution': {
                'positive': round(positive_count / len(articles), 2),
                'neutral': round(neutral_count / len(articles), 2),
                'negative': round(negative_count / len(articles), 2)
            }
        }
    else:
        sentiment_summary = {
            'overall_sentiment': 0.0,
            'positive_count': 0,
            'neutral_count': 0,
            'negative_count': 0,
            'total_articles': 0,
            'trending_topics': [],
            'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0}
        }
    
    return jsonify({
        'pair': pair,
        'articles': articles,
        'sentiment_summary': sentiment_summary,
        'filters_applied': {
            'sentiment': sentiment_filter,
            'impact': impact_filter,
            'limit': limit
        },
        'last_updated': datetime.utcnow().isoformat()
    })

@news_bp.route('/sentiment/<pair>')
def get_sentiment_analysis(pair):
    """Get detailed sentiment analysis for a currency pair"""
    period = request.args.get('period', '24h')
    
    # Generate sentiment timeline
    if period == '1h':
        intervals = 12
        delta_minutes = 5
    elif period == '24h':
        intervals = 24
        delta_minutes = 60
    elif period == '7d':
        intervals = 7
        delta_minutes = 1440  # daily
    else:
        intervals = 24
        delta_minutes = 60
    
    sentiment_timeline = []
    for i in range(intervals):
        timestamp = datetime.utcnow() - timedelta(minutes=i * delta_minutes)
        sentiment_score = random.uniform(-0.4, 0.4)
        
        sentiment_timeline.append({
            'timestamp': timestamp.isoformat(),
            'sentiment': round(sentiment_score, 3),
            'article_count': random.randint(5, 25),
            'confidence': round(random.uniform(0.7, 0.9), 2),
            'volume': random.randint(100, 1000)  # Social media mentions, etc.
        })
    
    sentiment_timeline.reverse()  # Chronological order
    
    # Key factors affecting sentiment
    key_factors = [
        {
            'factor': 'monetary_policy',
            'impact': round(random.uniform(0.6, 1.0), 2),
            'sentiment': round(random.uniform(-0.3, 0.3), 3),
            'confidence': round(random.uniform(0.8, 0.95), 2),
            'articles': random.randint(15, 40)
        },
        {
            'factor': 'economic_indicators',
            'impact': round(random.uniform(0.5, 0.9), 2),
            'sentiment': round(random.uniform(-0.2, 0.4), 3),
            'confidence': round(random.uniform(0.7, 0.9), 2),
            'articles': random.randint(10, 30)
        },
        {
            'factor': 'geopolitical_events',
            'impact': round(random.uniform(0.3, 0.8), 2),
            'sentiment': round(random.uniform(-0.5, 0.2), 3),
            'confidence': round(random.uniform(0.6, 0.85), 2),
            'articles': random.randint(5, 20)
        },
        {
            'factor': 'trade_relations',
            'impact': round(random.uniform(0.4, 0.7), 2),
            'sentiment': round(random.uniform(-0.2, 0.3), 3),
            'confidence': round(random.uniform(0.7, 0.9), 2),
            'articles': random.randint(8, 25)
        }
    ]
    
    # Overall sentiment distribution
    sentiment_distribution = {
        'very_positive': round(random.uniform(0.05, 0.15), 2),
        'positive': round(random.uniform(0.20, 0.35), 2),
        'neutral': round(random.uniform(0.30, 0.50), 2),
        'negative': round(random.uniform(0.15, 0.30), 2),
        'very_negative': round(random.uniform(0.02, 0.10), 2)
    }
    
    return jsonify({
        'pair': pair,
        'period': period,
        'sentiment_timeline': sentiment_timeline,
        'sentiment_distribution': sentiment_distribution,
        'key_factors': key_factors,
        'summary': {
            'current_sentiment': sentiment_timeline[-1]['sentiment'] if sentiment_timeline else 0.0,
            'trend': 'improving' if len(sentiment_timeline) > 1 and sentiment_timeline[-1]['sentiment'] > sentiment_timeline[-2]['sentiment'] else 'declining',
            'volatility': round(random.uniform(0.1, 0.4), 2),
            'reliability': round(random.uniform(0.7, 0.9), 2)
        },
        'generated_at': datetime.utcnow().isoformat()
    })

@news_bp.route('/news/sources')
def get_news_sources():
    """Get available news sources and their reliability scores"""
    sources = [
        {
            'name': 'Financial Times',
            'reliability': 0.95,
            'bias': 0.1,
            'coverage': ['monetary_policy', 'economic_data', 'market_analysis'],
            'update_frequency': 'real-time'
        },
        {
            'name': 'Reuters',
            'reliability': 0.93,
            'bias': 0.05,
            'coverage': ['breaking_news', 'economic_data', 'central_banks'],
            'update_frequency': 'real-time'
        },
        {
            'name': 'Bloomberg',
            'reliability': 0.92,
            'bias': 0.15,
            'coverage': ['market_data', 'economic_indicators', 'trading'],
            'update_frequency': 'real-time'
        },
        {
            'name': 'Wall Street Journal',
            'reliability': 0.90,
            'bias': 0.2,
            'coverage': ['market_analysis', 'economic_policy', 'business'],
            'update_frequency': 'hourly'
        },
        {
            'name': 'CNBC',
            'reliability': 0.85,
            'bias': 0.25,
            'coverage': ['market_news', 'economic_data', 'trading'],
            'update_frequency': 'real-time'
        }
    ]
    
    return jsonify({
        'sources': sources,
        'total_sources': len(sources),
        'average_reliability': round(sum(s['reliability'] for s in sources) / len(sources), 2)
    })

def get_keywords_for_pair(pair):
    """Get relevant keywords for a currency pair"""
    base_keywords = ['exchange_rate', 'currency', 'forex', 'monetary_policy']
    
    currencies = pair.split('/')
    currency_keywords = []
    
    for currency in currencies:
        if currency == 'USD':
            currency_keywords.extend(['federal_reserve', 'dollar', 'us_economy'])
        elif currency == 'EUR':
            currency_keywords.extend(['ecb', 'euro', 'eurozone'])
        elif currency == 'GBP':
            currency_keywords.extend(['bank_of_england', 'pound', 'uk_economy'])
        elif currency == 'JPY':
            currency_keywords.extend(['bank_of_japan', 'yen', 'japan_economy'])
    
    return base_keywords + currency_keywords

def extract_entities(pair):
    """Extract relevant entities for a currency pair"""
    entities = ['central_banks', 'government_officials', 'economic_indicators']
    
    currencies = pair.split('/')
    for currency in currencies:
        if currency == 'USD':
            entities.extend(['Federal Reserve', 'Jerome Powell', 'US Treasury'])
        elif currency == 'EUR':
            entities.extend(['European Central Bank', 'Christine Lagarde', 'European Commission'])
        elif currency == 'GBP':
            entities.extend(['Bank of England', 'Andrew Bailey', 'UK Treasury'])
        elif currency == 'JPY':
            entities.extend(['Bank of Japan', 'Kazuo Ueda', 'Ministry of Finance'])
    
    return entities

def get_trending_topics(pair):
    """Get trending topics for a currency pair"""
    general_topics = ['inflation', 'interest_rates', 'economic_growth', 'employment']
    
    # Add pair-specific topics
    if 'USD' in pair:
        general_topics.extend(['fed_policy', 'dollar_strength'])
    if 'EUR' in pair:
        general_topics.extend(['ecb_policy', 'eurozone_stability'])
    if 'GBP' in pair:
        general_topics.extend(['brexit_impact', 'uk_politics'])
    if 'JPY' in pair:
        general_topics.extend(['boj_intervention', 'japan_trade'])
    
    return random.sample(general_topics, min(5, len(general_topics)))

