# Data Collection and Preprocessing Pipeline Implementation

**Author:** Manus AI  
**Date:** July 8, 2025  
**Version:** 1.0

## Executive Summary

This comprehensive implementation guide provides detailed code and procedures for building a robust data collection and preprocessing pipeline for the exchange rate forecasting system. The pipeline handles real-time data ingestion from multiple sources including exchange rate APIs, news feeds, and sentiment analysis services, with sophisticated preprocessing and quality assurance mechanisms.

The implementation follows enterprise-grade practices with error handling, retry logic, data validation, and monitoring capabilities. The pipeline is designed to handle high-volume data streams while maintaining data quality and system reliability. All components are built using Python with Flask for API services and include comprehensive logging and monitoring features.

## Table of Contents

1. [Pipeline Architecture Overview](#pipeline-architecture-overview)
2. [Exchange Rate Data Collection](#exchange-rate-data-collection)
3. [News Data Collection](#news-data-collection)
4. [Sentiment Analysis Pipeline](#sentiment-analysis-pipeline)
5. [Data Preprocessing and Validation](#data-preprocessing-and-validation)
6. [Real-Time Streaming Implementation](#real-time-streaming-implementation)
7. [Error Handling and Retry Logic](#error-handling-and-retry-logic)
8. [Data Quality Monitoring](#data-quality-monitoring)
9. [Configuration Management](#configuration-management)
10. [Deployment and Scaling](#deployment-and-scaling)

## Pipeline Architecture Overview

The data collection and preprocessing pipeline implements a modular, event-driven architecture that can handle multiple data sources simultaneously while maintaining data consistency and quality. The architecture separates concerns between data collection, processing, and storage, enabling independent scaling and maintenance of each component.

### Core Components Architecture

The pipeline consists of several interconnected components that work together to provide comprehensive data processing capabilities. The **Data Collectors** component handles communication with external APIs and data sources, implementing robust error handling and rate limiting compliance. The **Data Processors** component applies transformations, validations, and enrichment to raw data before storage. The **Event System** coordinates communication between components using message queues and event-driven patterns.

The **Storage Layer** manages data persistence to MongoDB with optimized schemas and indexing strategies. The **Monitoring System** tracks pipeline performance, data quality, and system health with comprehensive alerting capabilities. The **Configuration Manager** handles environment-specific settings and API credentials with secure storage and rotation capabilities.

### Data Flow Architecture

Data flows through the pipeline in a structured manner that ensures consistency and reliability. Raw data enters through **Collection Endpoints** that interface with external APIs and data sources. The **Validation Layer** performs initial data quality checks and format validation before processing. The **Processing Engine** applies transformations, enrichment, and analysis to prepare data for storage and consumption.

The **Quality Assurance System** monitors data quality throughout the pipeline and triggers alerts for anomalies or issues. The **Storage Interface** handles optimized data persistence with appropriate indexing and partitioning strategies. The **Event Publishing System** notifies downstream consumers of new data availability and processing completion.

### Scalability and Performance Design

The pipeline architecture supports horizontal scaling through containerization and microservices patterns. Each component can be scaled independently based on load patterns and resource requirements. The **Load Balancing System** distributes incoming requests across multiple instances of data collectors and processors.

The **Caching Layer** reduces external API calls and improves response times for frequently accessed data. The **Batch Processing System** handles large-volume data operations efficiently while maintaining real-time capabilities for urgent updates. The **Resource Management System** monitors and optimizes resource utilization across all pipeline components.

## Exchange Rate Data Collection

Exchange rate data collection implements robust mechanisms for gathering real-time and historical currency exchange data from multiple providers with comprehensive error handling and data validation.

### API Integration Framework

The API integration framework provides a unified interface for connecting to different exchange rate providers while handling their specific requirements and limitations.

```python
import requests
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

class APIProvider(Enum):
    """Enumeration of supported exchange rate API providers."""
    EXCHANGERATE_API = "exchangerate-api"
    FIXER_IO = "fixer-io"
    CURRENCYLAYER = "currencylayer"
    OPENEXCHANGERATES = "openexchangerates"

@dataclass
class ExchangeRateData:
    """Data structure for exchange rate information."""
    base_currency: str
    target_currency: str
    rate: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    timestamp: datetime = None
    source: str = None
    volume: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    change_24h: Optional[float] = None

class ExchangeRateCollector:
    """Unified exchange rate data collector supporting multiple providers."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Configure retry strategy
        self.session.mount('https://', requests.adapters.HTTPAdapter(
            max_retries=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        ))
        
        # API configurations
        self.api_configs = {
            APIProvider.EXCHANGERATE_API: {
                'base_url': 'https://v6.exchangerate-api.com/v6',
                'rate_limit': 1500,  # requests per month for free tier
                'requires_auth': True
            },
            APIProvider.FIXER_IO: {
                'base_url': 'http://data.fixer.io/api',
                'rate_limit': 1000,  # requests per month for free tier
                'requires_auth': True
            },
            APIProvider.CURRENCYLAYER: {
                'base_url': 'http://api.currencylayer.com',
                'rate_limit': 1000,  # requests per month for free tier
                'requires_auth': True
            }
        }
        
        # Rate limiting tracking
        self.rate_limits = {}
        self.last_request_times = {}
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def collect_current_rates(self, currency_pairs: List[Tuple[str, str]], 
                            provider: APIProvider = APIProvider.EXCHANGERATE_API) -> List[ExchangeRateData]:
        """Collect current exchange rates for specified currency pairs."""
        try:
            self._check_rate_limit(provider)
            
            if provider == APIProvider.EXCHANGERATE_API:
                return self._collect_exchangerate_api(currency_pairs)
            elif provider == APIProvider.FIXER_IO:
                return self._collect_fixer_io(currency_pairs)
            elif provider == APIProvider.CURRENCYLAYER:
                return self._collect_currencylayer(currency_pairs)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            self.logger.error(f"Error collecting rates from {provider}: {e}")
            raise
    
    def _collect_exchangerate_api(self, currency_pairs: List[Tuple[str, str]]) -> List[ExchangeRateData]:
        """Collect data from ExchangeRate-API."""
        results = []
        api_key = self.config['exchangerate_api']['api_key']
        
        # Group by base currency to minimize API calls
        base_currencies = {}
        for base, target in currency_pairs:
            if base not in base_currencies:
                base_currencies[base] = []
            base_currencies[base].append(target)
        
        for base_currency, target_currencies in base_currencies.items():
            url = f"{self.api_configs[APIProvider.EXCHANGERATE_API]['base_url']}/{api_key}/latest/{base_currency}"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if data['result'] != 'success':
                raise Exception(f"API error: {data.get('error-type', 'Unknown error')}")
            
            timestamp = datetime.fromtimestamp(data['time_last_update_unix'])
            
            for target_currency in target_currencies:
                if target_currency in data['conversion_rates']:
                    rate_data = ExchangeRateData(
                        base_currency=base_currency,
                        target_currency=target_currency,
                        rate=data['conversion_rates'][target_currency],
                        timestamp=timestamp,
                        source='exchangerate-api'
                    )
                    results.append(rate_data)
            
            # Respect rate limits
            time.sleep(1)  # 1 second between requests
        
        return results
    
    def _collect_fixer_io(self, currency_pairs: List[Tuple[str, str]]) -> List[ExchangeRateData]:
        """Collect data from Fixer.io API."""
        results = []
        api_key = self.config['fixer_io']['api_key']
        
        # Fixer.io uses EUR as base currency in free tier
        symbols = set()
        for base, target in currency_pairs:
            symbols.add(base)
            symbols.add(target)
        
        url = f"{self.api_configs[APIProvider.FIXER_IO]['base_url']}/latest"
        params = {
            'access_key': api_key,
            'symbols': ','.join(symbols)
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if not data['success']:
            raise Exception(f"Fixer.io API error: {data.get('error', {}).get('info', 'Unknown error')}")
        
        timestamp = datetime.fromtimestamp(data['timestamp'])
        base_currency = data['base']  # Usually EUR
        rates = data['rates']
        
        # Convert rates for requested currency pairs
        for req_base, req_target in currency_pairs:
            if req_base in rates and req_target in rates:
                # Calculate cross rate: (EUR/target) / (EUR/base) = base/target
                if req_base == base_currency:
                    rate = rates[req_target]
                elif req_target == base_currency:
                    rate = 1.0 / rates[req_base]
                else:
                    rate = rates[req_target] / rates[req_base]
                
                rate_data = ExchangeRateData(
                    base_currency=req_base,
                    target_currency=req_target,
                    rate=rate,
                    timestamp=timestamp,
                    source='fixer-io'
                )
                results.append(rate_data)
        
        return results
    
    def _check_rate_limit(self, provider: APIProvider):
        """Check and enforce rate limits for API provider."""
        current_time = time.time()
        provider_key = provider.value
        
        if provider_key not in self.last_request_times:
            self.last_request_times[provider_key] = 0
        
        time_since_last = current_time - self.last_request_times[provider_key]
        min_interval = 1.0  # Minimum 1 second between requests
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_times[provider_key] = time.time()
    
    async def collect_rates_async(self, currency_pairs: List[Tuple[str, str]], 
                                providers: List[APIProvider]) -> Dict[APIProvider, List[ExchangeRateData]]:
        """Collect rates from multiple providers asynchronously."""
        async def collect_from_provider(provider):
            try:
                return provider, await self._collect_async_provider(currency_pairs, provider)
            except Exception as e:
                self.logger.error(f"Error collecting from {provider}: {e}")
                return provider, []
        
        tasks = [collect_from_provider(provider) for provider in providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {provider: data for provider, data in results if not isinstance(data, Exception)}
    
    async def _collect_async_provider(self, currency_pairs: List[Tuple[str, str]], 
                                    provider: APIProvider) -> List[ExchangeRateData]:
        """Asynchronous collection from a single provider."""
        async with aiohttp.ClientSession() as session:
            if provider == APIProvider.EXCHANGERATE_API:
                return await self._collect_exchangerate_api_async(session, currency_pairs)
            # Add other providers as needed
            return []
    
    def validate_rate_data(self, rate_data: ExchangeRateData) -> bool:
        """Validate exchange rate data for quality and consistency."""
        try:
            # Basic validation
            if rate_data.rate <= 0:
                self.logger.warning(f"Invalid rate value: {rate_data.rate}")
                return False
            
            if rate_data.rate > 1000000:  # Sanity check for extremely high rates
                self.logger.warning(f"Suspiciously high rate: {rate_data.rate}")
                return False
            
            # Currency code validation
            if len(rate_data.base_currency) != 3 or len(rate_data.target_currency) != 3:
                self.logger.warning(f"Invalid currency codes: {rate_data.base_currency}/{rate_data.target_currency}")
                return False
            
            # Timestamp validation
            if rate_data.timestamp:
                age_hours = (datetime.utcnow() - rate_data.timestamp).total_seconds() / 3600
                if age_hours > 24:  # Data older than 24 hours
                    self.logger.warning(f"Stale data: {age_hours} hours old")
                    return False
            
            # Bid/Ask spread validation
            if rate_data.bid and rate_data.ask:
                spread = rate_data.ask - rate_data.bid
                if spread < 0:
                    self.logger.warning(f"Invalid bid/ask spread: bid={rate_data.bid}, ask={rate_data.ask}")
                    return False
                
                spread_percentage = (spread / rate_data.rate) * 100
                if spread_percentage > 5:  # Spread larger than 5%
                    self.logger.warning(f"Large bid/ask spread: {spread_percentage}%")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating rate data: {e}")
            return False
```

### Historical Data Collection

Historical data collection implements efficient mechanisms for gathering large volumes of historical exchange rate data with proper pagination and data integrity checks.

```python
class HistoricalDataCollector:
    """Collector for historical exchange rate data."""
    
    def __init__(self, config: Dict, db_manager):
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.rate_collector = ExchangeRateCollector(config)
    
    def collect_historical_range(self, currency_pair: Tuple[str, str], 
                               start_date: datetime, end_date: datetime,
                               provider: APIProvider = APIProvider.EXCHANGERATE_API) -> List[ExchangeRateData]:
        """Collect historical data for a date range."""
        try:
            base_currency, target_currency = currency_pair
            historical_data = []
            
            current_date = start_date
            while current_date <= end_date:
                try:
                    daily_data = self._collect_historical_day(
                        currency_pair, current_date, provider
                    )
                    
                    if daily_data:
                        historical_data.extend(daily_data)
                        self.logger.info(f"Collected {len(daily_data)} records for {current_date.date()}")
                    
                    # Store data in batches to avoid memory issues
                    if len(historical_data) >= 1000:
                        self._store_historical_batch(historical_data)
                        historical_data = []
                    
                    current_date += timedelta(days=1)
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    self.logger.error(f"Error collecting data for {current_date.date()}: {e}")
                    current_date += timedelta(days=1)
                    continue
            
            # Store remaining data
            if historical_data:
                self._store_historical_batch(historical_data)
            
            return historical_data
            
        except Exception as e:
            self.logger.error(f"Error in historical data collection: {e}")
            raise
    
    def _collect_historical_day(self, currency_pair: Tuple[str, str], 
                              date: datetime, provider: APIProvider) -> List[ExchangeRateData]:
        """Collect historical data for a specific day."""
        if provider == APIProvider.EXCHANGERATE_API:
            return self._collect_exchangerate_historical(currency_pair, date)
        else:
            raise NotImplementedError(f"Historical data not implemented for {provider}")
    
    def _collect_exchangerate_historical(self, currency_pair: Tuple[str, str], 
                                       date: datetime) -> List[ExchangeRateData]:
        """Collect historical data from ExchangeRate-API."""
        base_currency, target_currency = currency_pair
        api_key = self.config['exchangerate_api']['api_key']
        
        date_str = date.strftime('%Y-%m-%d')
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/history/{base_currency}/{date_str}"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data['result'] != 'success':
            raise Exception(f"API error: {data.get('error-type', 'Unknown error')}")
        
        if target_currency not in data['conversion_rates']:
            return []
        
        rate_data = ExchangeRateData(
            base_currency=base_currency,
            target_currency=target_currency,
            rate=data['conversion_rates'][target_currency],
            timestamp=datetime.strptime(date_str, '%Y-%m-%d'),
            source='exchangerate-api'
        )
        
        return [rate_data]
    
    def _store_historical_batch(self, historical_data: List[ExchangeRateData]):
        """Store batch of historical data to database."""
        try:
            db = self.db_manager.databases['exchange_rates']
            documents = []
            
            for rate_data in historical_data:
                document = {
                    'currency_pair': {
                        'base': rate_data.base_currency,
                        'target': rate_data.target_currency,
                        'symbol': f"{rate_data.base_currency}_{rate_data.target_currency}"
                    },
                    'rate': {
                        'value': rate_data.rate,
                        'bid': rate_data.bid,
                        'ask': rate_data.ask,
                        'timestamp': rate_data.timestamp
                    },
                    'source': {
                        'provider': rate_data.source,
                        'collection_type': 'historical'
                    },
                    'metadata': {
                        'collection_timestamp': datetime.utcnow(),
                        'data_quality_score': 1.0 if self.rate_collector.validate_rate_data(rate_data) else 0.5
                    }
                }
                documents.append(document)
            
            if documents:
                result = db.historical_rates.insert_many(documents)
                self.logger.info(f"Stored {len(result.inserted_ids)} historical records")
            
        except Exception as e:
            self.logger.error(f"Error storing historical batch: {e}")
            raise
    
    def backfill_missing_data(self, currency_pairs: List[Tuple[str, str]], 
                            days_back: int = 30) -> Dict[str, int]:
        """Backfill missing historical data for currency pairs."""
        results = {}
        end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=days_back)
        
        for currency_pair in currency_pairs:
            try:
                pair_key = f"{currency_pair[0]}_{currency_pair[1]}"
                
                # Check for missing dates
                missing_dates = self._find_missing_dates(currency_pair, start_date, end_date)
                
                if missing_dates:
                    self.logger.info(f"Found {len(missing_dates)} missing dates for {pair_key}")
                    
                    collected_count = 0
                    for missing_date in missing_dates:
                        try:
                            daily_data = self._collect_historical_day(
                                currency_pair, missing_date, APIProvider.EXCHANGERATE_API
                            )
                            
                            if daily_data:
                                self._store_historical_batch(daily_data)
                                collected_count += len(daily_data)
                            
                            time.sleep(1)  # Rate limiting
                            
                        except Exception as e:
                            self.logger.error(f"Error backfilling {missing_date}: {e}")
                            continue
                    
                    results[pair_key] = collected_count
                else:
                    results[pair_key] = 0
                    
            except Exception as e:
                self.logger.error(f"Error in backfill for {currency_pair}: {e}")
                results[f"{currency_pair[0]}_{currency_pair[1]}"] = -1
        
        return results
    
    def _find_missing_dates(self, currency_pair: Tuple[str, str], 
                          start_date: datetime, end_date: datetime) -> List[datetime]:
        """Find dates with missing data in the specified range."""
        try:
            db = self.db_manager.databases['exchange_rates']
            pair_symbol = f"{currency_pair[0]}_{currency_pair[1]}"
            
            # Get existing dates from database
            existing_dates = set()
            cursor = db.historical_rates.find(
                {
                    'currency_pair.symbol': pair_symbol,
                    'rate.timestamp': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                },
                {'rate.timestamp': 1}
            )
            
            for doc in cursor:
                date_only = doc['rate']['timestamp'].replace(hour=0, minute=0, second=0, microsecond=0)
                existing_dates.add(date_only)
            
            # Generate list of all dates in range
            all_dates = []
            current_date = start_date
            while current_date <= end_date:
                all_dates.append(current_date)
                current_date += timedelta(days=1)
            
            # Find missing dates
            missing_dates = [date for date in all_dates if date not in existing_dates]
            
            return missing_dates
            
        except Exception as e:
            self.logger.error(f"Error finding missing dates: {e}")
            return []
```


## News Data Collection

News data collection implements comprehensive mechanisms for gathering financial news from multiple sources with content filtering, deduplication, and relevance scoring for currency market analysis.

### News API Integration

The news API integration framework provides unified access to multiple news sources while handling different API formats and rate limiting requirements.

```python
import feedparser
import hashlib
from urllib.parse import urlparse
from textblob import TextBlob
import re
from typing import Set

class NewsProvider(Enum):
    """Enumeration of supported news API providers."""
    NEWSAPI = "newsapi"
    FINNHUB = "finnhub"
    ALPHA_VANTAGE = "alpha_vantage"
    RSS_FEEDS = "rss_feeds"

@dataclass
class NewsArticle:
    """Data structure for news article information."""
    title: str
    content: str
    url: str
    source: str
    published_at: datetime
    author: Optional[str] = None
    category: Optional[str] = None
    language: str = 'en'
    summary: Optional[str] = None
    word_count: int = 0
    relevance_score: float = 0.0
    content_hash: Optional[str] = None

class NewsCollector:
    """Unified news data collector supporting multiple providers."""
    
    def __init__(self, config: Dict, db_manager):
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Financial keywords for relevance filtering
        self.financial_keywords = {
            'currency': ['currency', 'exchange rate', 'forex', 'fx', 'dollar', 'euro', 'pound', 'yen'],
            'economic': ['economy', 'economic', 'gdp', 'inflation', 'interest rate', 'central bank'],
            'monetary': ['monetary policy', 'federal reserve', 'ecb', 'bank of england', 'boj'],
            'trade': ['trade', 'import', 'export', 'tariff', 'trade war', 'trade deal'],
            'market': ['market', 'financial', 'investment', 'stock', 'bond', 'commodity']
        }
        
        # RSS feed sources for financial news
        self.rss_feeds = [
            'https://feeds.reuters.com/reuters/businessNews',
            'https://feeds.bloomberg.com/markets/news.rss',
            'https://rss.cnn.com/rss/money_news_international.rss',
            'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'https://www.ft.com/rss/home/uk'
        ]
        
        # Content deduplication tracking
        self.seen_hashes = set()
        self._load_existing_hashes()
    
    def collect_recent_news(self, hours_back: int = 6, 
                          providers: List[NewsProvider] = None) -> List[NewsArticle]:
        """Collect recent financial news from multiple providers."""
        if providers is None:
            providers = [NewsProvider.NEWSAPI, NewsProvider.RSS_FEEDS]
        
        all_articles = []
        
        for provider in providers:
            try:
                articles = self._collect_from_provider(provider, hours_back)
                filtered_articles = self._filter_relevant_articles(articles)
                deduplicated_articles = self._deduplicate_articles(filtered_articles)
                
                all_articles.extend(deduplicated_articles)
                self.logger.info(f"Collected {len(deduplicated_articles)} articles from {provider.value}")
                
            except Exception as e:
                self.logger.error(f"Error collecting from {provider.value}: {e}")
                continue
        
        # Sort by relevance and recency
        all_articles.sort(key=lambda x: (x.relevance_score, x.published_at), reverse=True)
        
        return all_articles
    
    def _collect_from_provider(self, provider: NewsProvider, hours_back: int) -> List[NewsArticle]:
        """Collect articles from a specific provider."""
        if provider == NewsProvider.NEWSAPI:
            return self._collect_newsapi(hours_back)
        elif provider == NewsProvider.FINNHUB:
            return self._collect_finnhub(hours_back)
        elif provider == NewsProvider.RSS_FEEDS:
            return self._collect_rss_feeds(hours_back)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _collect_newsapi(self, hours_back: int) -> List[NewsArticle]:
        """Collect articles from NewsAPI."""
        api_key = self.config['newsapi']['api_key']
        
        # Calculate time range
        from_time = datetime.utcnow() - timedelta(hours=hours_back)
        from_str = from_time.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Search for financial news
        url = 'https://newsapi.org/v2/everything'
        params = {
            'apiKey': api_key,
            'q': 'currency OR forex OR "exchange rate" OR "central bank" OR economy',
            'language': 'en',
            'sortBy': 'publishedAt',
            'from': from_str,
            'pageSize': 100
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] != 'ok':
            raise Exception(f"NewsAPI error: {data.get('message', 'Unknown error')}")
        
        articles = []
        for article_data in data['articles']:
            try:
                # Skip articles without content
                if not article_data.get('content') or article_data['content'] == '[Removed]':
                    continue
                
                article = NewsArticle(
                    title=article_data['title'],
                    content=article_data['content'],
                    url=article_data['url'],
                    source=article_data['source']['name'],
                    published_at=datetime.fromisoformat(article_data['publishedAt'].replace('Z', '+00:00')),
                    author=article_data.get('author'),
                    summary=article_data.get('description'),
                    word_count=len(article_data['content'].split())
                )
                
                article.content_hash = self._calculate_content_hash(article)
                articles.append(article)
                
            except Exception as e:
                self.logger.warning(f"Error parsing NewsAPI article: {e}")
                continue
        
        return articles
    
    def _collect_finnhub(self, hours_back: int) -> List[NewsArticle]:
        """Collect articles from Finnhub."""
        api_key = self.config['finnhub']['api_key']
        
        # Calculate time range (Finnhub uses Unix timestamps)
        from_time = datetime.utcnow() - timedelta(hours=hours_back)
        to_time = datetime.utcnow()
        
        url = 'https://finnhub.io/api/v1/news'
        params = {
            'token': api_key,
            'category': 'forex',
            'from': int(from_time.timestamp()),
            'to': int(to_time.timestamp())
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        articles = []
        for article_data in data:
            try:
                article = NewsArticle(
                    title=article_data['headline'],
                    content=article_data['summary'],
                    url=article_data['url'],
                    source=article_data['source'],
                    published_at=datetime.fromtimestamp(article_data['datetime']),
                    category='forex',
                    summary=article_data['summary'][:200] + '...' if len(article_data['summary']) > 200 else article_data['summary'],
                    word_count=len(article_data['summary'].split())
                )
                
                article.content_hash = self._calculate_content_hash(article)
                articles.append(article)
                
            except Exception as e:
                self.logger.warning(f"Error parsing Finnhub article: {e}")
                continue
        
        return articles
    
    def _collect_rss_feeds(self, hours_back: int) -> List[NewsArticle]:
        """Collect articles from RSS feeds."""
        articles = []
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    try:
                        # Parse publication date
                        if hasattr(entry, 'published_parsed'):
                            pub_date = datetime(*entry.published_parsed[:6])
                        elif hasattr(entry, 'updated_parsed'):
                            pub_date = datetime(*entry.updated_parsed[:6])
                        else:
                            pub_date = datetime.utcnow()
                        
                        # Skip old articles
                        if pub_date < cutoff_time:
                            continue
                        
                        # Extract content
                        content = ''
                        if hasattr(entry, 'content'):
                            content = entry.content[0].value
                        elif hasattr(entry, 'summary'):
                            content = entry.summary
                        elif hasattr(entry, 'description'):
                            content = entry.description
                        
                        if not content:
                            continue
                        
                        # Clean HTML tags
                        content = re.sub(r'<[^>]+>', '', content)
                        content = re.sub(r'\s+', ' ', content).strip()
                        
                        article = NewsArticle(
                            title=entry.title,
                            content=content,
                            url=entry.link,
                            source=urlparse(feed_url).netloc,
                            published_at=pub_date,
                            author=getattr(entry, 'author', None),
                            summary=content[:200] + '...' if len(content) > 200 else content,
                            word_count=len(content.split())
                        )
                        
                        article.content_hash = self._calculate_content_hash(article)
                        articles.append(article)
                        
                    except Exception as e:
                        self.logger.warning(f"Error parsing RSS entry: {e}")
                        continue
                
                time.sleep(1)  # Rate limiting between feeds
                
            except Exception as e:
                self.logger.error(f"Error fetching RSS feed {feed_url}: {e}")
                continue
        
        return articles
    
    def _filter_relevant_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Filter articles for financial relevance."""
        relevant_articles = []
        
        for article in articles:
            try:
                relevance_score = self._calculate_relevance_score(article)
                article.relevance_score = relevance_score
                
                # Keep articles with relevance score above threshold
                if relevance_score >= 0.3:
                    relevant_articles.append(article)
                
            except Exception as e:
                self.logger.warning(f"Error calculating relevance for article: {e}")
                continue
        
        return relevant_articles
    
    def _calculate_relevance_score(self, article: NewsArticle) -> float:
        """Calculate relevance score for financial content."""
        try:
            # Combine title and content for analysis
            text = f"{article.title} {article.content}".lower()
            
            # Count keyword matches by category
            category_scores = {}
            total_words = len(text.split())
            
            for category, keywords in self.financial_keywords.items():
                matches = 0
                for keyword in keywords:
                    matches += text.count(keyword.lower())
                
                # Normalize by text length
                category_scores[category] = matches / max(total_words, 1)
            
            # Calculate weighted relevance score
            weights = {
                'currency': 0.3,
                'economic': 0.25,
                'monetary': 0.25,
                'trade': 0.1,
                'market': 0.1
            }
            
            relevance_score = sum(
                category_scores.get(category, 0) * weight
                for category, weight in weights.items()
            )
            
            # Boost score for recent articles
            age_hours = (datetime.utcnow() - article.published_at).total_seconds() / 3600
            recency_boost = max(0, 1 - (age_hours / 24))  # Boost decreases over 24 hours
            
            final_score = min(1.0, relevance_score * 10 + recency_boost * 0.1)
            
            return final_score
            
        except Exception as e:
            self.logger.error(f"Error calculating relevance score: {e}")
            return 0.0
    
    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on content hash."""
        unique_articles = []
        
        for article in articles:
            if article.content_hash not in self.seen_hashes:
                unique_articles.append(article)
                self.seen_hashes.add(article.content_hash)
        
        return unique_articles
    
    def _calculate_content_hash(self, article: NewsArticle) -> str:
        """Calculate hash for article content deduplication."""
        # Normalize content for hashing
        normalized_content = re.sub(r'\s+', ' ', article.content.lower().strip())
        normalized_title = re.sub(r'\s+', ' ', article.title.lower().strip())
        
        # Create hash from title and content
        content_string = f"{normalized_title}|{normalized_content}"
        return hashlib.md5(content_string.encode()).hexdigest()
    
    def _load_existing_hashes(self):
        """Load existing content hashes from database to prevent duplicates."""
        try:
            db = self.db_manager.databases['news_sentiment']
            
            # Get hashes from recent articles (last 7 days)
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            
            cursor = db.news_articles.find(
                {'collected_at': {'$gte': cutoff_date}},
                {'processing_metadata.content_hash': 1}
            )
            
            for doc in cursor:
                content_hash = doc.get('processing_metadata', {}).get('content_hash')
                if content_hash:
                    self.seen_hashes.add(content_hash)
            
            self.logger.info(f"Loaded {len(self.seen_hashes)} existing content hashes")
            
        except Exception as e:
            self.logger.error(f"Error loading existing hashes: {e}")
    
    def store_articles(self, articles: List[NewsArticle]) -> List[str]:
        """Store articles in database."""
        try:
            db = self.db_manager.databases['news_sentiment']
            documents = []
            
            for article in articles:
                document = {
                    'article_info': {
                        'title': article.title,
                        'content': article.content,
                        'summary': article.summary,
                        'word_count': article.word_count,
                        'language': article.language
                    },
                    'source': {
                        'name': article.source,
                        'url': article.url,
                        'author': article.author
                    },
                    'publication': {
                        'published_at': article.published_at,
                        'collected_at': datetime.utcnow()
                    },
                    'categorization': {
                        'primary_category': article.category or 'finance',
                        'relevance_score': article.relevance_score
                    },
                    'processing_metadata': {
                        'content_hash': article.content_hash,
                        'processing_status': 'pending_sentiment',
                        'collection_version': '1.0'
                    }
                }
                documents.append(document)
            
            if documents:
                result = db.news_articles.insert_many(documents)
                self.logger.info(f"Stored {len(result.inserted_ids)} articles")
                return [str(id) for id in result.inserted_ids]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error storing articles: {e}")
            raise
```

## Sentiment Analysis Pipeline

The sentiment analysis pipeline processes news articles to extract sentiment scores, entity sentiment, and market impact indicators using multiple analysis methods and validation techniques.

### Sentiment Analysis Framework

```python
from google.cloud import language_v1
import openai
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import spacy
from typing import NamedTuple

class SentimentScore(NamedTuple):
    """Structured sentiment score with confidence metrics."""
    score: float  # -1.0 to 1.0
    magnitude: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    classification: str  # very_negative, negative, neutral, positive, very_positive

class EntitySentiment(NamedTuple):
    """Entity-specific sentiment information."""
    entity: str
    entity_type: str
    mentions: int
    sentiment: float
    confidence: float
    relevance: float

class SentimentAnalyzer:
    """Multi-method sentiment analysis with financial domain specialization."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize Google Cloud Natural Language client
        if 'google_cloud' in config:
            self.google_client = language_v1.LanguageServiceClient()
        else:
            self.google_client = None
        
        # Initialize OpenAI client
        if 'openai' in config:
            openai.api_key = config['openai']['api_key']
        
        # Initialize Hugging Face transformers
        self.financial_model = None
        self._load_financial_model()
        
        # Initialize spaCy for entity extraction
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.logger.warning("spaCy model not found. Entity extraction will be limited.")
            self.nlp = None
        
        # Financial entity patterns
        self.financial_entities = {
            'central_banks': ['federal reserve', 'fed', 'ecb', 'european central bank', 'bank of england', 'boe', 'bank of japan', 'boj'],
            'currencies': ['dollar', 'usd', 'euro', 'eur', 'pound', 'gbp', 'yen', 'jpy', 'franc', 'chf'],
            'economic_indicators': ['gdp', 'inflation', 'cpi', 'unemployment', 'interest rate', 'yield'],
            'financial_institutions': ['goldman sachs', 'jp morgan', 'morgan stanley', 'citigroup', 'bank of america']
        }
    
    def _load_financial_model(self):
        """Load specialized financial sentiment model."""
        try:
            # Use FinBERT or similar financial domain model
            model_name = "ProsusAI/finbert"
            self.financial_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.financial_model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.financial_pipeline = pipeline(
                "sentiment-analysis",
                model=self.financial_model,
                tokenizer=self.financial_tokenizer,
                device=-1  # Use CPU
            )
            self.logger.info("Loaded FinBERT model for financial sentiment analysis")
        except Exception as e:
            self.logger.warning(f"Could not load financial model: {e}")
            self.financial_pipeline = None
    
    def analyze_article_sentiment(self, article: NewsArticle) -> Dict:
        """Comprehensive sentiment analysis of news article."""
        try:
            # Combine title and content for analysis
            full_text = f"{article.title}. {article.content}"
            
            # Get sentiment from multiple sources
            sentiment_results = {}
            
            # Google Cloud Natural Language
            if self.google_client:
                sentiment_results['google'] = self._analyze_google_sentiment(full_text)
            
            # Financial domain model (FinBERT)
            if self.financial_pipeline:
                sentiment_results['finbert'] = self._analyze_finbert_sentiment(full_text)
            
            # OpenAI GPT analysis
            if 'openai' in self.config:
                sentiment_results['openai'] = self._analyze_openai_sentiment(full_text)
            
            # Entity sentiment analysis
            entity_sentiments = self._analyze_entity_sentiment(full_text)
            
            # Combine results into final sentiment
            final_sentiment = self._combine_sentiment_results(sentiment_results)
            
            # Calculate currency relevance
            currency_relevance = self._calculate_currency_relevance(full_text, entity_sentiments)
            
            return {
                'overall_sentiment': final_sentiment,
                'entity_sentiments': entity_sentiments,
                'currency_relevance': currency_relevance,
                'method_results': sentiment_results,
                'processed_at': datetime.utcnow(),
                'processor_version': '2.0'
            }
            
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {e}")
            return self._create_fallback_sentiment()
    
    def _analyze_google_sentiment(self, text: str) -> SentimentScore:
        """Analyze sentiment using Google Cloud Natural Language API."""
        try:
            document = language_v1.Document(
                content=text,
                type_=language_v1.Document.Type.PLAIN_TEXT
            )
            
            response = self.google_client.analyze_sentiment(
                request={'document': document}
            )
            
            sentiment = response.document_sentiment
            
            # Classify sentiment
            if sentiment.score >= 0.25:
                classification = 'positive' if sentiment.score < 0.75 else 'very_positive'
            elif sentiment.score <= -0.25:
                classification = 'negative' if sentiment.score > -0.75 else 'very_negative'
            else:
                classification = 'neutral'
            
            return SentimentScore(
                score=sentiment.score,
                magnitude=sentiment.magnitude,
                confidence=min(sentiment.magnitude, 1.0),
                classification=classification
            )
            
        except Exception as e:
            self.logger.error(f"Error in Google sentiment analysis: {e}")
            return SentimentScore(0.0, 0.0, 0.0, 'neutral')
    
    def _analyze_finbert_sentiment(self, text: str) -> SentimentScore:
        """Analyze sentiment using FinBERT financial model."""
        try:
            # Truncate text to model's maximum length
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]
            
            result = self.financial_pipeline(text)[0]
            
            # Convert FinBERT labels to standardized scores
            label_mapping = {
                'positive': 0.5,
                'negative': -0.5,
                'neutral': 0.0
            }
            
            score = label_mapping.get(result['label'].lower(), 0.0)
            confidence = result['score']
            
            # Adjust score based on confidence
            adjusted_score = score * confidence
            
            # Classify sentiment
            if adjusted_score >= 0.25:
                classification = 'positive' if adjusted_score < 0.75 else 'very_positive'
            elif adjusted_score <= -0.25:
                classification = 'negative' if adjusted_score > -0.75 else 'very_negative'
            else:
                classification = 'neutral'
            
            return SentimentScore(
                score=adjusted_score,
                magnitude=abs(adjusted_score),
                confidence=confidence,
                classification=classification
            )
            
        except Exception as e:
            self.logger.error(f"Error in FinBERT sentiment analysis: {e}")
            return SentimentScore(0.0, 0.0, 0.0, 'neutral')
    
    def _analyze_openai_sentiment(self, text: str) -> SentimentScore:
        """Analyze sentiment using OpenAI GPT model."""
        try:
            prompt = f"""
            Analyze the sentiment of this financial news article and provide:
            1. Sentiment score (-1.0 to 1.0, where -1 is very negative, 0 is neutral, 1 is very positive)
            2. Confidence level (0.0 to 1.0)
            3. Brief explanation
            
            Article: {text[:1000]}...
            
            Response format:
            Score: [number]
            Confidence: [number]
            Explanation: [brief explanation]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            
            # Parse response
            score = 0.0
            confidence = 0.0
            
            for line in content.split('\n'):
                if line.startswith('Score:'):
                    try:
                        score = float(line.split(':')[1].strip())
                    except:
                        pass
                elif line.startswith('Confidence:'):
                    try:
                        confidence = float(line.split(':')[1].strip())
                    except:
                        pass
            
            # Classify sentiment
            if score >= 0.25:
                classification = 'positive' if score < 0.75 else 'very_positive'
            elif score <= -0.25:
                classification = 'negative' if score > -0.75 else 'very_negative'
            else:
                classification = 'neutral'
            
            return SentimentScore(
                score=score,
                magnitude=abs(score),
                confidence=confidence,
                classification=classification
            )
            
        except Exception as e:
            self.logger.error(f"Error in OpenAI sentiment analysis: {e}")
            return SentimentScore(0.0, 0.0, 0.0, 'neutral')
    
    def _analyze_entity_sentiment(self, text: str) -> List[EntitySentiment]:
        """Extract entities and analyze their sentiment."""
        entity_sentiments = []
        
        try:
            if not self.nlp:
                return entity_sentiments
            
            doc = self.nlp(text)
            
            # Extract named entities
            entities = {}
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'MONEY']:
                    entity_text = ent.text.lower()
                    if entity_text not in entities:
                        entities[entity_text] = {
                            'type': ent.label_,
                            'mentions': 0,
                            'contexts': []
                        }
                    entities[entity_text]['mentions'] += 1
                    
                    # Get context around entity
                    start = max(0, ent.start - 10)
                    end = min(len(doc), ent.end + 10)
                    context = doc[start:end].text
                    entities[entity_text]['contexts'].append(context)
            
            # Add financial entities
            for category, entity_list in self.financial_entities.items():
                for entity in entity_list:
                    if entity.lower() in text.lower():
                        if entity not in entities:
                            entities[entity] = {
                                'type': category,
                                'mentions': 0,
                                'contexts': []
                            }
                        entities[entity]['mentions'] += text.lower().count(entity.lower())
            
            # Analyze sentiment for each entity
            for entity, info in entities.items():
                if info['mentions'] > 0:
                    # Analyze sentiment of contexts
                    context_sentiments = []
                    for context in info['contexts']:
                        if self.google_client:
                            context_sentiment = self._analyze_google_sentiment(context)
                            context_sentiments.append(context_sentiment.score)
                    
                    # Calculate average sentiment
                    avg_sentiment = sum(context_sentiments) / len(context_sentiments) if context_sentiments else 0.0
                    
                    # Calculate relevance based on mentions and entity type
                    relevance = min(1.0, info['mentions'] * 0.1)
                    if info['type'] in ['central_banks', 'currencies']:
                        relevance *= 1.5  # Boost relevance for important financial entities
                    
                    entity_sentiment = EntitySentiment(
                        entity=entity,
                        entity_type=info['type'],
                        mentions=info['mentions'],
                        sentiment=avg_sentiment,
                        confidence=min(1.0, info['mentions'] * 0.2),
                        relevance=min(1.0, relevance)
                    )
                    
                    entity_sentiments.append(entity_sentiment)
            
        except Exception as e:
            self.logger.error(f"Error in entity sentiment analysis: {e}")
        
        return entity_sentiments
    
    def _combine_sentiment_results(self, sentiment_results: Dict) -> SentimentScore:
        """Combine sentiment results from multiple methods."""
        if not sentiment_results:
            return SentimentScore(0.0, 0.0, 0.0, 'neutral')
        
        # Weight different methods
        method_weights = {
            'google': 0.4,
            'finbert': 0.4,
            'openai': 0.2
        }
        
        weighted_score = 0.0
        weighted_magnitude = 0.0
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for method, result in sentiment_results.items():
            weight = method_weights.get(method, 0.1)
            weighted_score += result.score * weight
            weighted_magnitude += result.magnitude * weight
            weighted_confidence += result.confidence * weight
            total_weight += weight
        
        if total_weight > 0:
            final_score = weighted_score / total_weight
            final_magnitude = weighted_magnitude / total_weight
            final_confidence = weighted_confidence / total_weight
        else:
            final_score = final_magnitude = final_confidence = 0.0
        
        # Classify final sentiment
        if final_score >= 0.25:
            classification = 'positive' if final_score < 0.75 else 'very_positive'
        elif final_score <= -0.25:
            classification = 'negative' if final_score > -0.75 else 'very_negative'
        else:
            classification = 'neutral'
        
        return SentimentScore(
            score=final_score,
            magnitude=final_magnitude,
            confidence=final_confidence,
            classification=classification
        )
    
    def _calculate_currency_relevance(self, text: str, entity_sentiments: List[EntitySentiment]) -> Dict[str, Dict]:
        """Calculate relevance scores for different currency pairs."""
        currency_pairs = ['USD_EUR', 'USD_GBP', 'USD_JPY', 'EUR_GBP', 'EUR_JPY', 'GBP_JPY']
        relevance_scores = {}
        
        for pair in currency_pairs:
            base, target = pair.split('_')
            
            # Calculate relevance based on currency mentions
            base_mentions = text.lower().count(base.lower()) + text.lower().count(self._get_currency_name(base).lower())
            target_mentions = text.lower().count(target.lower()) + text.lower().count(self._get_currency_name(target).lower())
            
            # Factor in entity sentiments
            entity_relevance = 0.0
            for entity_sentiment in entity_sentiments:
                if entity_sentiment.entity_type == 'currencies':
                    if base.lower() in entity_sentiment.entity.lower() or target.lower() in entity_sentiment.entity.lower():
                        entity_relevance += entity_sentiment.relevance
            
            # Calculate overall relevance
            mention_score = min(1.0, (base_mentions + target_mentions) * 0.1)
            entity_score = min(1.0, entity_relevance)
            
            # Combine scores
            relevance_score = (mention_score * 0.6 + entity_score * 0.4)
            
            # Determine impact prediction
            if relevance_score > 0.7:
                impact = 'high'
            elif relevance_score > 0.4:
                impact = 'moderate'
            elif relevance_score > 0.2:
                impact = 'low'
            else:
                impact = 'minimal'
            
            relevance_scores[pair] = {
                'relevance_score': relevance_score,
                'impact_prediction': impact,
                'confidence': min(1.0, relevance_score * 1.2)
            }
        
        return relevance_scores
    
    def _get_currency_name(self, currency_code: str) -> str:
        """Get full currency name from code."""
        currency_names = {
            'USD': 'dollar',
            'EUR': 'euro',
            'GBP': 'pound',
            'JPY': 'yen',
            'CHF': 'franc',
            'CAD': 'canadian dollar',
            'AUD': 'australian dollar'
        }
        return currency_names.get(currency_code, currency_code.lower())
    
    def _create_fallback_sentiment(self) -> Dict:
        """Create fallback sentiment result when analysis fails."""
        return {
            'overall_sentiment': SentimentScore(0.0, 0.0, 0.0, 'neutral'),
            'entity_sentiments': [],
            'currency_relevance': {},
            'method_results': {},
            'processed_at': datetime.utcnow(),
            'processor_version': '2.0',
            'error': 'Analysis failed, using fallback'
        }
    
    def process_article_batch(self, article_ids: List[str]) -> Dict[str, Dict]:
        """Process sentiment analysis for a batch of articles."""
        results = {}
        db = self.db_manager.databases['news_sentiment']
        
        try:
            # Fetch articles from database
            articles = list(db.news_articles.find(
                {'_id': {'$in': [ObjectId(id) for id in article_ids]}},
                {
                    'article_info': 1,
                    'processing_metadata.processing_status': 1
                }
            ))
            
            for article_doc in articles:
                try:
                    # Skip already processed articles
                    if article_doc.get('processing_metadata', {}).get('processing_status') == 'completed':
                        continue
                    
                    # Create NewsArticle object
                    article_info = article_doc['article_info']
                    article = NewsArticle(
                        title=article_info['title'],
                        content=article_info['content'],
                        url='',  # Not needed for sentiment analysis
                        source='',  # Not needed for sentiment analysis
                        published_at=datetime.utcnow()  # Not needed for sentiment analysis
                    )
                    
                    # Analyze sentiment
                    sentiment_result = self.analyze_article_sentiment(article)
                    
                    # Update article in database
                    update_result = db.news_articles.update_one(
                        {'_id': article_doc['_id']},
                        {
                            '$set': {
                                'sentiment_analysis': sentiment_result,
                                'processing_metadata.processing_status': 'completed',
                                'processing_metadata.processed_at': datetime.utcnow()
                            }
                        }
                    )
                    
                    if update_result.modified_count > 0:
                        results[str(article_doc['_id'])] = sentiment_result
                        self.logger.info(f"Processed sentiment for article {article_doc['_id']}")
                    
                except Exception as e:
                    self.logger.error(f"Error processing article {article_doc['_id']}: {e}")
                    results[str(article_doc['_id'])] = {'error': str(e)}
                    continue
            
        except Exception as e:
            self.logger.error(f"Error in batch sentiment processing: {e}")
            raise
        
        return results
```


## Data Preprocessing and Validation

Data preprocessing ensures that all collected data meets quality standards and is properly formatted for machine learning and analysis. The preprocessing pipeline includes data cleaning, normalization, feature extraction, and validation.

### Data Cleaning and Normalization

```python
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import re
from typing import Union

class DataPreprocessor:
    """Comprehensive data preprocessing for exchange rate forecasting."""
    
    def __init__(self, config: Dict, db_manager):
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize scalers
        self.rate_scaler = StandardScaler()
        self.sentiment_scaler = MinMaxScaler()
        
        # Data quality thresholds
        self.quality_thresholds = {
            'rate_deviation_threshold': 3.0,  # Standard deviations
            'sentiment_confidence_threshold': 0.5,
            'news_relevance_threshold': 0.3,
            'data_freshness_hours': 24,
            'minimum_daily_rates': 50,
            'minimum_daily_news': 10
        }
    
    def preprocess_exchange_rates(self, currency_pair: str, days_back: int = 30) -> pd.DataFrame:
        """Preprocess exchange rate data for analysis and modeling."""
        try:
            # Fetch raw data
            raw_data = self._fetch_exchange_rate_data(currency_pair, days_back)
            
            if raw_data.empty:
                self.logger.warning(f"No exchange rate data found for {currency_pair}")
                return pd.DataFrame()
            
            # Clean and validate data
            cleaned_data = self._clean_exchange_rate_data(raw_data)
            
            # Handle missing values
            filled_data = self._handle_missing_rates(cleaned_data)
            
            # Detect and handle outliers
            outlier_free_data = self._handle_rate_outliers(filled_data)
            
            # Generate technical indicators
            enriched_data = self._generate_technical_indicators(outlier_free_data)
            
            # Normalize data
            normalized_data = self._normalize_rate_data(enriched_data)
            
            self.logger.info(f"Preprocessed {len(normalized_data)} exchange rate records for {currency_pair}")
            
            return normalized_data
            
        except Exception as e:
            self.logger.error(f"Error preprocessing exchange rates for {currency_pair}: {e}")
            raise
    
    def _fetch_exchange_rate_data(self, currency_pair: str, days_back: int) -> pd.DataFrame:
        """Fetch exchange rate data from database."""
        try:
            db = self.db_manager.databases['exchange_rates']
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            cursor = db.current_rates.find(
                {
                    'currency_pair.symbol': currency_pair,
                    'rate.timestamp': {'$gte': cutoff_date}
                },
                {
                    'rate.timestamp': 1,
                    'rate.value': 1,
                    'rate.bid': 1,
                    'rate.ask': 1,
                    'market_data.volume_24h': 1,
                    'market_data.high_24h': 1,
                    'market_data.low_24h': 1,
                    'source.provider': 1,
                    'metadata.data_quality_score': 1
                }
            ).sort('rate.timestamp', 1)
            
            data = []
            for doc in cursor:
                rate_info = doc['rate']
                market_data = doc.get('market_data', {})
                metadata = doc.get('metadata', {})
                
                data.append({
                    'timestamp': rate_info['timestamp'],
                    'rate': rate_info['value'],
                    'bid': rate_info.get('bid'),
                    'ask': rate_info.get('ask'),
                    'volume': market_data.get('volume_24h'),
                    'high': market_data.get('high_24h'),
                    'low': market_data.get('low_24h'),
                    'source': doc.get('source', {}).get('provider'),
                    'quality_score': metadata.get('data_quality_score', 1.0)
                })
            
            df = pd.DataFrame(data)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                df.sort_index(inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching exchange rate data: {e}")
            return pd.DataFrame()
    
    def _clean_exchange_rate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean exchange rate data by removing invalid values."""
        if df.empty:
            return df
        
        original_count = len(df)
        
        # Remove rows with invalid rates
        df = df[df['rate'] > 0]
        df = df[df['rate'] < 1000000]  # Sanity check
        
        # Remove rows with invalid bid/ask spreads
        valid_spread_mask = (
            (df['bid'].isna()) | (df['ask'].isna()) |
            ((df['ask'] >= df['bid']) & ((df['ask'] - df['bid']) / df['rate'] <= 0.05))
        )
        df = df[valid_spread_mask]
        
        # Remove low quality data
        df = df[df['quality_score'] >= 0.5]
        
        # Remove duplicate timestamps (keep the highest quality)
        df = df.sort_values('quality_score', ascending=False)
        df = df[~df.index.duplicated(keep='first')]
        df = df.sort_index()
        
        cleaned_count = len(df)
        removed_count = original_count - cleaned_count
        
        if removed_count > 0:
            self.logger.info(f"Removed {removed_count} invalid records during cleaning")
        
        return df
    
    def _handle_missing_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in exchange rate data."""
        if df.empty:
            return df
        
        # Create complete time index (1-minute intervals)
        start_time = df.index.min()
        end_time = df.index.max()
        complete_index = pd.date_range(start=start_time, end=end_time, freq='1min')
        
        # Reindex to complete time series
        df = df.reindex(complete_index)
        
        # Forward fill missing rates (up to 5 minutes)
        df['rate'] = df['rate'].fillna(method='ffill', limit=5)
        
        # Interpolate remaining missing values
        df['rate'] = df['rate'].interpolate(method='time', limit=10)
        
        # Fill bid/ask based on rate if missing
        df['bid'] = df['bid'].fillna(df['rate'] * 0.9995)  # Approximate spread
        df['ask'] = df['ask'].fillna(df['rate'] * 1.0005)
        
        # Drop rows that still have missing critical values
        df = df.dropna(subset=['rate'])
        
        return df
    
    def _handle_rate_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect and handle outliers in exchange rate data."""
        if df.empty or len(df) < 10:
            return df
        
        # Calculate rolling statistics
        df['rate_ma_24h'] = df['rate'].rolling(window=1440, min_periods=100).mean()  # 24 hours
        df['rate_std_24h'] = df['rate'].rolling(window=1440, min_periods=100).std()
        
        # Identify outliers using z-score
        df['z_score'] = np.abs((df['rate'] - df['rate_ma_24h']) / df['rate_std_24h'])
        
        # Mark outliers
        outlier_threshold = self.quality_thresholds['rate_deviation_threshold']
        outlier_mask = df['z_score'] > outlier_threshold
        
        outlier_count = outlier_mask.sum()
        if outlier_count > 0:
            self.logger.warning(f"Detected {outlier_count} outliers in exchange rate data")
            
            # Replace outliers with interpolated values
            df.loc[outlier_mask, 'rate'] = np.nan
            df['rate'] = df['rate'].interpolate(method='time')
            
            # Update bid/ask for corrected rates
            corrected_mask = outlier_mask & df['rate'].notna()
            df.loc[corrected_mask, 'bid'] = df.loc[corrected_mask, 'rate'] * 0.9995
            df.loc[corrected_mask, 'ask'] = df.loc[corrected_mask, 'rate'] * 1.0005
        
        # Clean up temporary columns
        df = df.drop(['rate_ma_24h', 'rate_std_24h', 'z_score'], axis=1)
        
        return df
    
    def _generate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate technical indicators for exchange rate data."""
        if df.empty or len(df) < 50:
            return df
        
        try:
            # Moving averages
            df['ma_5min'] = df['rate'].rolling(window=5).mean()
            df['ma_15min'] = df['rate'].rolling(window=15).mean()
            df['ma_1h'] = df['rate'].rolling(window=60).mean()
            df['ma_4h'] = df['rate'].rolling(window=240).mean()
            df['ma_24h'] = df['rate'].rolling(window=1440).mean()
            
            # Exponential moving averages
            df['ema_5min'] = df['rate'].ewm(span=5).mean()
            df['ema_15min'] = df['rate'].ewm(span=15).mean()
            df['ema_1h'] = df['rate'].ewm(span=60).mean()
            
            # Volatility measures
            df['volatility_1h'] = df['rate'].rolling(window=60).std()
            df['volatility_4h'] = df['rate'].rolling(window=240).std()
            df['volatility_24h'] = df['rate'].rolling(window=1440).std()
            
            # Rate of change
            df['roc_5min'] = df['rate'].pct_change(periods=5)
            df['roc_15min'] = df['rate'].pct_change(periods=15)
            df['roc_1h'] = df['rate'].pct_change(periods=60)
            
            # Bollinger Bands
            bb_window = 60
            bb_std = 2
            df['bb_middle'] = df['rate'].rolling(window=bb_window).mean()
            df['bb_std'] = df['rate'].rolling(window=bb_window).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * df['bb_std'])
            df['bb_lower'] = df['bb_middle'] - (bb_std * df['bb_std'])
            df['bb_position'] = (df['rate'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # RSI (Relative Strength Index)
            df['rsi'] = self._calculate_rsi(df['rate'], window=14)
            
            # MACD
            df['macd'], df['macd_signal'], df['macd_histogram'] = self._calculate_macd(df['rate'])
            
            # Support and resistance levels
            df['support_1h'] = df['rate'].rolling(window=60).min()
            df['resistance_1h'] = df['rate'].rolling(window=60).max()
            
            # Trend indicators
            df['trend_5min'] = np.where(df['ma_5min'] > df['ma_5min'].shift(1), 1, -1)
            df['trend_1h'] = np.where(df['ma_1h'] > df['ma_1h'].shift(1), 1, -1)
            
            # Clean up intermediate columns
            df = df.drop(['bb_std'], axis=1)
            
            self.logger.info(f"Generated {len([col for col in df.columns if col not in ['rate', 'bid', 'ask', 'volume', 'high', 'low', 'source', 'quality_score']])} technical indicators")
            
        except Exception as e:
            self.logger.error(f"Error generating technical indicators: {e}")
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """Calculate MACD indicator."""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        macd_histogram = macd - macd_signal
        return macd, macd_signal, macd_histogram
    
    def _normalize_rate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize exchange rate data for machine learning."""
        if df.empty:
            return df
        
        # Identify numeric columns for normalization
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        # Separate rate and technical indicator columns
        rate_columns = ['rate', 'bid', 'ask', 'high', 'low']
        indicator_columns = [col for col in numeric_columns if col not in rate_columns + ['volume', 'quality_score']]
        
        # Normalize rate columns using StandardScaler
        if any(col in df.columns for col in rate_columns):
            rate_data = df[rate_columns].dropna()
            if not rate_data.empty:
                normalized_rates = pd.DataFrame(
                    self.rate_scaler.fit_transform(rate_data),
                    index=rate_data.index,
                    columns=rate_data.columns
                )
                df[rate_columns] = normalized_rates
        
        # Normalize technical indicators
        if indicator_columns:
            indicator_data = df[indicator_columns].dropna()
            if not indicator_data.empty:
                # Use robust scaling for technical indicators
                scaler = StandardScaler()
                normalized_indicators = pd.DataFrame(
                    scaler.fit_transform(indicator_data),
                    index=indicator_data.index,
                    columns=indicator_data.columns
                )
                df[indicator_columns] = normalized_indicators
        
        return df
    
    def preprocess_sentiment_data(self, currency_pair: str, days_back: int = 7) -> pd.DataFrame:
        """Preprocess sentiment data for analysis and modeling."""
        try:
            # Fetch raw sentiment data
            raw_data = self._fetch_sentiment_data(currency_pair, days_back)
            
            if raw_data.empty:
                self.logger.warning(f"No sentiment data found for {currency_pair}")
                return pd.DataFrame()
            
            # Clean and validate sentiment data
            cleaned_data = self._clean_sentiment_data(raw_data)
            
            # Aggregate sentiment by time windows
            aggregated_data = self._aggregate_sentiment_data(cleaned_data)
            
            # Generate sentiment features
            enriched_data = self._generate_sentiment_features(aggregated_data)
            
            # Normalize sentiment data
            normalized_data = self._normalize_sentiment_data(enriched_data)
            
            self.logger.info(f"Preprocessed sentiment data for {currency_pair}: {len(normalized_data)} time windows")
            
            return normalized_data
            
        except Exception as e:
            self.logger.error(f"Error preprocessing sentiment data for {currency_pair}: {e}")
            raise
    
    def _fetch_sentiment_data(self, currency_pair: str, days_back: int) -> pd.DataFrame:
        """Fetch sentiment data from database."""
        try:
            db = self.db_manager.databases['news_sentiment']
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            cursor = db.news_articles.find(
                {
                    f'currency_relevance.{currency_pair}.relevance_score': {'$gte': self.quality_thresholds['news_relevance_threshold']},
                    'publication.published_at': {'$gte': cutoff_date},
                    'sentiment_analysis.overall_sentiment': {'$exists': True}
                },
                {
                    'publication.published_at': 1,
                    'sentiment_analysis.overall_sentiment': 1,
                    'sentiment_analysis.entity_sentiments': 1,
                    f'currency_relevance.{currency_pair}': 1,
                    'source.name': 1,
                    'article_info.word_count': 1
                }
            ).sort('publication.published_at', 1)
            
            data = []
            for doc in cursor:
                sentiment = doc['sentiment_analysis']['overall_sentiment']
                relevance = doc['currency_relevance'][currency_pair]
                
                data.append({
                    'timestamp': doc['publication']['published_at'],
                    'sentiment_score': sentiment['score'],
                    'sentiment_magnitude': sentiment['magnitude'],
                    'sentiment_confidence': sentiment['confidence'],
                    'relevance_score': relevance['relevance_score'],
                    'impact_prediction': relevance['impact_prediction'],
                    'source': doc['source']['name'],
                    'word_count': doc['article_info']['word_count']
                })
            
            df = pd.DataFrame(data)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                df.sort_index(inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching sentiment data: {e}")
            return pd.DataFrame()
    
    def _clean_sentiment_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean sentiment data by removing invalid values."""
        if df.empty:
            return df
        
        original_count = len(df)
        
        # Remove rows with invalid sentiment scores
        df = df[(df['sentiment_score'] >= -1.0) & (df['sentiment_score'] <= 1.0)]
        df = df[(df['sentiment_magnitude'] >= 0.0) & (df['sentiment_magnitude'] <= 1.0)]
        df = df[df['sentiment_confidence'] >= self.quality_thresholds['sentiment_confidence_threshold']]
        
        # Remove rows with low relevance
        df = df[df['relevance_score'] >= self.quality_thresholds['news_relevance_threshold']]
        
        cleaned_count = len(df)
        removed_count = original_count - cleaned_count
        
        if removed_count > 0:
            self.logger.info(f"Removed {removed_count} invalid sentiment records during cleaning")
        
        return df
    
    def _aggregate_sentiment_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate sentiment data by time windows."""
        if df.empty:
            return df
        
        # Define aggregation windows
        windows = ['15min', '1h', '4h', '24h']
        aggregated_data = []
        
        for window in windows:
            try:
                # Group by time window
                grouped = df.groupby(pd.Grouper(freq=window))
                
                for timestamp, group in grouped:
                    if group.empty:
                        continue
                    
                    # Calculate weighted averages
                    weights = group['relevance_score'] * group['sentiment_confidence']
                    
                    if weights.sum() > 0:
                        weighted_sentiment = (group['sentiment_score'] * weights).sum() / weights.sum()
                        weighted_magnitude = (group['sentiment_magnitude'] * weights).sum() / weights.sum()
                    else:
                        weighted_sentiment = group['sentiment_score'].mean()
                        weighted_magnitude = group['sentiment_magnitude'].mean()
                    
                    aggregated_data.append({
                        'timestamp': timestamp,
                        'window': window,
                        'sentiment_score': weighted_sentiment,
                        'sentiment_magnitude': weighted_magnitude,
                        'article_count': len(group),
                        'avg_relevance': group['relevance_score'].mean(),
                        'avg_confidence': group['sentiment_confidence'].mean(),
                        'source_diversity': group['source'].nunique(),
                        'total_word_count': group['word_count'].sum()
                    })
            
            except Exception as e:
                self.logger.error(f"Error aggregating sentiment data for window {window}: {e}")
                continue
        
        agg_df = pd.DataFrame(aggregated_data)
        if not agg_df.empty:
            agg_df['timestamp'] = pd.to_datetime(agg_df['timestamp'])
            agg_df.set_index('timestamp', inplace=True)
        
        return agg_df
    
    def _generate_sentiment_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate sentiment features for machine learning."""
        if df.empty:
            return df
        
        try:
            # Pivot by window to create features for each time window
            pivot_df = df.pivot(columns='window', values=['sentiment_score', 'sentiment_magnitude', 'article_count'])
            
            # Flatten column names
            pivot_df.columns = [f"{col[0]}_{col[1]}" for col in pivot_df.columns]
            
            # Calculate sentiment trends
            for window in ['15min', '1h', '4h']:
                if f'sentiment_score_{window}' in pivot_df.columns:
                    pivot_df[f'sentiment_trend_{window}'] = pivot_df[f'sentiment_score_{window}'].diff()
                    pivot_df[f'sentiment_momentum_{window}'] = pivot_df[f'sentiment_score_{window}'].rolling(window=4).mean()
            
            # Calculate sentiment volatility
            for window in ['1h', '4h']:
                if f'sentiment_score_{window}' in pivot_df.columns:
                    pivot_df[f'sentiment_volatility_{window}'] = pivot_df[f'sentiment_score_{window}'].rolling(window=6).std()
            
            # Fill missing values
            pivot_df = pivot_df.fillna(method='ffill').fillna(0)
            
            return pivot_df
            
        except Exception as e:
            self.logger.error(f"Error generating sentiment features: {e}")
            return df
    
    def _normalize_sentiment_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize sentiment data for machine learning."""
        if df.empty:
            return df
        
        # Identify numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) > 0:
            # Use MinMaxScaler for sentiment data to preserve interpretability
            normalized_data = pd.DataFrame(
                self.sentiment_scaler.fit_transform(df[numeric_columns]),
                index=df.index,
                columns=numeric_columns
            )
            
            # Replace original columns with normalized versions
            df[numeric_columns] = normalized_data
        
        return df
    
    def validate_processed_data(self, rate_data: pd.DataFrame, sentiment_data: pd.DataFrame) -> Dict[str, bool]:
        """Validate processed data quality."""
        validation_results = {
            'rate_data_valid': False,
            'sentiment_data_valid': False,
            'data_alignment_valid': False,
            'sufficient_data_volume': False
        }
        
        try:
            # Validate rate data
            if not rate_data.empty:
                rate_checks = [
                    len(rate_data) >= self.quality_thresholds['minimum_daily_rates'],
                    rate_data['rate'].notna().sum() / len(rate_data) >= 0.95,  # 95% completeness
                    not rate_data['rate'].isin([np.inf, -np.inf]).any(),  # No infinite values
                    (rate_data['rate'].std() > 0)  # Has variation
                ]
                validation_results['rate_data_valid'] = all(rate_checks)
            
            # Validate sentiment data
            if not sentiment_data.empty:
                sentiment_checks = [
                    len(sentiment_data) >= self.quality_thresholds['minimum_daily_news'],
                    sentiment_data.notna().sum().sum() / (len(sentiment_data) * len(sentiment_data.columns)) >= 0.90,  # 90% completeness
                    not sentiment_data.isin([np.inf, -np.inf]).any().any()  # No infinite values
                ]
                validation_results['sentiment_data_valid'] = all(sentiment_checks)
            
            # Validate data alignment
            if not rate_data.empty and not sentiment_data.empty:
                # Check time overlap
                rate_start, rate_end = rate_data.index.min(), rate_data.index.max()
                sentiment_start, sentiment_end = sentiment_data.index.min(), sentiment_data.index.max()
                
                overlap_start = max(rate_start, sentiment_start)
                overlap_end = min(rate_end, sentiment_end)
                
                if overlap_start < overlap_end:
                    overlap_hours = (overlap_end - overlap_start).total_seconds() / 3600
                    validation_results['data_alignment_valid'] = overlap_hours >= 24  # At least 24 hours overlap
            
            # Check sufficient data volume
            total_rate_points = len(rate_data) if not rate_data.empty else 0
            total_sentiment_points = len(sentiment_data) if not sentiment_data.empty else 0
            
            validation_results['sufficient_data_volume'] = (
                total_rate_points >= 1000 and total_sentiment_points >= 50
            )
            
        except Exception as e:
            self.logger.error(f"Error in data validation: {e}")
        
        return validation_results

class DataQualityMonitor:
    """Monitor data quality and generate quality reports."""
    
    def __init__(self, config: Dict, db_manager):
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def generate_quality_report(self, currency_pairs: List[str]) -> Dict:
        """Generate comprehensive data quality report."""
        report = {
            'timestamp': datetime.utcnow(),
            'currency_pairs': {},
            'overall_status': 'healthy',
            'issues': [],
            'recommendations': []
        }
        
        for pair in currency_pairs:
            try:
                pair_report = self._analyze_pair_quality(pair)
                report['currency_pairs'][pair] = pair_report
                
                # Check for issues
                if pair_report['rate_data_quality'] < 0.8:
                    report['issues'].append(f"Low rate data quality for {pair}: {pair_report['rate_data_quality']:.2f}")
                    report['overall_status'] = 'degraded'
                
                if pair_report['sentiment_data_quality'] < 0.7:
                    report['issues'].append(f"Low sentiment data quality for {pair}: {pair_report['sentiment_data_quality']:.2f}")
                    report['overall_status'] = 'degraded'
                
                if pair_report['data_freshness_hours'] > 2:
                    report['issues'].append(f"Stale data for {pair}: {pair_report['data_freshness_hours']:.1f} hours old")
                    if report['overall_status'] == 'healthy':
                        report['overall_status'] = 'degraded'
                
            except Exception as e:
                self.logger.error(f"Error analyzing quality for {pair}: {e}")
                report['issues'].append(f"Analysis failed for {pair}: {str(e)}")
                report['overall_status'] = 'degraded'
        
        # Generate recommendations
        if report['issues']:
            report['recommendations'] = self._generate_recommendations(report['issues'])
        
        return report
    
    def _analyze_pair_quality(self, currency_pair: str) -> Dict:
        """Analyze data quality for a specific currency pair."""
        try:
            # Analyze rate data quality
            rate_quality = self._analyze_rate_data_quality(currency_pair)
            
            # Analyze sentiment data quality
            sentiment_quality = self._analyze_sentiment_data_quality(currency_pair)
            
            # Check data freshness
            freshness = self._check_data_freshness(currency_pair)
            
            return {
                'rate_data_quality': rate_quality['quality_score'],
                'rate_data_completeness': rate_quality['completeness'],
                'rate_data_consistency': rate_quality['consistency'],
                'sentiment_data_quality': sentiment_quality['quality_score'],
                'sentiment_data_completeness': sentiment_quality['completeness'],
                'sentiment_data_relevance': sentiment_quality['relevance'],
                'data_freshness_hours': freshness['hours_since_last_update'],
                'total_rate_records': rate_quality['total_records'],
                'total_sentiment_records': sentiment_quality['total_records']
            }
            
        except Exception as e:
            self.logger.error(f"Error in pair quality analysis: {e}")
            return {
                'rate_data_quality': 0.0,
                'sentiment_data_quality': 0.0,
                'data_freshness_hours': 999,
                'error': str(e)
            }
    
    def _analyze_rate_data_quality(self, currency_pair: str) -> Dict:
        """Analyze exchange rate data quality."""
        try:
            db = self.db_manager.databases['exchange_rates']
            
            # Get recent data (last 24 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            cursor = db.current_rates.find(
                {
                    'currency_pair.symbol': currency_pair,
                    'rate.timestamp': {'$gte': cutoff_time}
                },
                {
                    'rate.value': 1,
                    'rate.timestamp': 1,
                    'metadata.data_quality_score': 1
                }
            )
            
            data = list(cursor)
            total_records = len(data)
            
            if total_records == 0:
                return {
                    'quality_score': 0.0,
                    'completeness': 0.0,
                    'consistency': 0.0,
                    'total_records': 0
                }
            
            # Calculate completeness (expected vs actual records)
            expected_records = 24 * 60  # 1 record per minute for 24 hours
            completeness = min(1.0, total_records / expected_records)
            
            # Calculate consistency (quality scores)
            quality_scores = [doc.get('metadata', {}).get('data_quality_score', 1.0) for doc in data]
            avg_quality = sum(quality_scores) / len(quality_scores)
            
            # Calculate overall quality score
            overall_quality = (completeness * 0.4 + avg_quality * 0.6)
            
            return {
                'quality_score': overall_quality,
                'completeness': completeness,
                'consistency': avg_quality,
                'total_records': total_records
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing rate data quality: {e}")
            return {
                'quality_score': 0.0,
                'completeness': 0.0,
                'consistency': 0.0,
                'total_records': 0
            }
    
    def _analyze_sentiment_data_quality(self, currency_pair: str) -> Dict:
        """Analyze sentiment data quality."""
        try:
            db = self.db_manager.databases['news_sentiment']
            
            # Get recent data (last 24 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            cursor = db.news_articles.find(
                {
                    f'currency_relevance.{currency_pair}.relevance_score': {'$gte': 0.3},
                    'publication.published_at': {'$gte': cutoff_time},
                    'sentiment_analysis': {'$exists': True}
                },
                {
                    'sentiment_analysis.overall_sentiment.confidence': 1,
                    f'currency_relevance.{currency_pair}.relevance_score': 1
                }
            )
            
            data = list(cursor)
            total_records = len(data)
            
            if total_records == 0:
                return {
                    'quality_score': 0.0,
                    'completeness': 0.0,
                    'relevance': 0.0,
                    'total_records': 0
                }
            
            # Calculate average confidence
            confidences = [
                doc['sentiment_analysis']['overall_sentiment']['confidence']
                for doc in data
            ]
            avg_confidence = sum(confidences) / len(confidences)
            
            # Calculate average relevance
            relevances = [
                doc['currency_relevance'][currency_pair]['relevance_score']
                for doc in data
            ]
            avg_relevance = sum(relevances) / len(relevances)
            
            # Calculate completeness (minimum expected articles per day)
            expected_articles = 20  # Minimum expected articles per day
            completeness = min(1.0, total_records / expected_articles)
            
            # Calculate overall quality
            overall_quality = (completeness * 0.3 + avg_confidence * 0.4 + avg_relevance * 0.3)
            
            return {
                'quality_score': overall_quality,
                'completeness': completeness,
                'relevance': avg_relevance,
                'total_records': total_records
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment data quality: {e}")
            return {
                'quality_score': 0.0,
                'completeness': 0.0,
                'relevance': 0.0,
                'total_records': 0
            }
    
    def _check_data_freshness(self, currency_pair: str) -> Dict:
        """Check data freshness for currency pair."""
        try:
            db_rates = self.db_manager.databases['exchange_rates']
            db_sentiment = self.db_manager.databases['news_sentiment']
            
            # Check latest rate data
            latest_rate = db_rates.current_rates.find_one(
                {'currency_pair.symbol': currency_pair},
                sort=[('rate.timestamp', -1)]
            )
            
            # Check latest sentiment data
            latest_sentiment = db_sentiment.news_articles.find_one(
                {f'currency_relevance.{currency_pair}.relevance_score': {'$gte': 0.3}},
                sort=[('publication.published_at', -1)]
            )
            
            current_time = datetime.utcnow()
            
            rate_age_hours = 999
            if latest_rate:
                rate_age = current_time - latest_rate['rate']['timestamp']
                rate_age_hours = rate_age.total_seconds() / 3600
            
            sentiment_age_hours = 999
            if latest_sentiment:
                sentiment_age = current_time - latest_sentiment['publication']['published_at']
                sentiment_age_hours = sentiment_age.total_seconds() / 3600
            
            return {
                'hours_since_last_update': max(rate_age_hours, sentiment_age_hours),
                'rate_age_hours': rate_age_hours,
                'sentiment_age_hours': sentiment_age_hours
            }
            
        except Exception as e:
            self.logger.error(f"Error checking data freshness: {e}")
            return {
                'hours_since_last_update': 999,
                'rate_age_hours': 999,
                'sentiment_age_hours': 999
            }
    
    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on identified issues."""
        recommendations = []
        
        for issue in issues:
            if 'rate data quality' in issue.lower():
                recommendations.append("Increase exchange rate data collection frequency")
                recommendations.append("Verify API provider reliability and consider backup sources")
            
            if 'sentiment data quality' in issue.lower():
                recommendations.append("Expand news source coverage")
                recommendations.append("Improve sentiment analysis confidence thresholds")
            
            if 'stale data' in issue.lower():
                recommendations.append("Check data collection pipeline status")
                recommendations.append("Verify API connectivity and rate limits")
            
            if 'analysis failed' in issue.lower():
                recommendations.append("Investigate system errors and logs")
                recommendations.append("Check database connectivity and performance")
        
        # Remove duplicates
        return list(set(recommendations))
```

## Real-Time Streaming Implementation

Real-time streaming enables immediate processing and distribution of data updates as they become available, supporting live dashboards and real-time decision making.

### Event-Driven Streaming Architecture

```python
import asyncio
import websockets
import json
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import redis
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue

class StreamingManager:
    """Manage real-time data streaming and event processing."""
    
    def __init__(self, config: Dict, db_manager):
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize message queue (Kafka)
        self.producer = None
        self.consumers = {}
        self._init_kafka()
        
        # Initialize Redis for caching and pub/sub
        self.redis_client = None
        self._init_redis()
        
        # WebSocket connections
        self.websocket_clients = set()
        
        # Event processing
        self.event_queue = Queue()
        self.processing_threads = []
        self.running = False
        
        # Data collectors
        self.rate_collector = ExchangeRateCollector(config)
        self.news_collector = NewsCollector(config, db_manager)
        self.sentiment_analyzer = SentimentAnalyzer(config)
    
    def _init_kafka(self):
        """Initialize Kafka producer and consumers."""
        try:
            kafka_config = self.config.get('kafka', {})
            
            if kafka_config:
                self.producer = KafkaProducer(
                    bootstrap_servers=kafka_config['bootstrap_servers'],
                    value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None,
                    acks='all',
                    retries=3,
                    batch_size=16384,
                    linger_ms=10
                )
                
                self.logger.info("Kafka producer initialized")
            else:
                self.logger.warning("Kafka configuration not found, using in-memory queues")
                
        except Exception as e:
            self.logger.error(f"Error initializing Kafka: {e}")
    
    def _init_redis(self):
        """Initialize Redis client."""
        try:
            redis_config = self.config.get('redis', {})
            
            if redis_config:
                self.redis_client = redis.Redis(
                    host=redis_config['host'],
                    port=redis_config['port'],
                    db=redis_config['db'],
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                
                # Test connection
                self.redis_client.ping()
                self.logger.info("Redis client initialized")
            else:
                self.logger.warning("Redis configuration not found")
                
        except Exception as e:
            self.logger.error(f"Error initializing Redis: {e}")
            self.redis_client = None
    
    def start_streaming(self):
        """Start real-time streaming services."""
        try:
            self.running = True
            
            # Start event processing threads
            for i in range(4):  # 4 processing threads
                thread = threading.Thread(target=self._process_events, daemon=True)
                thread.start()
                self.processing_threads.append(thread)
            
            # Start data collection tasks
            asyncio.create_task(self._collect_exchange_rates())
            asyncio.create_task(self._collect_news_data())
            asyncio.create_task(self._process_sentiment_queue())
            
            # Start Kafka consumers
            if self.producer:
                self._start_kafka_consumers()
            
            self.logger.info("Real-time streaming started")
            
        except Exception as e:
            self.logger.error(f"Error starting streaming: {e}")
            raise
    
    def stop_streaming(self):
        """Stop real-time streaming services."""
        try:
            self.running = False
            
            # Stop Kafka producer
            if self.producer:
                self.producer.close()
            
            # Stop consumers
            for consumer in self.consumers.values():
                consumer.close()
            
            # Close Redis connection
            if self.redis_client:
                self.redis_client.close()
            
            self.logger.info("Real-time streaming stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping streaming: {e}")
    
    async def _collect_exchange_rates(self):
        """Continuously collect exchange rate data."""
        currency_pairs = [('USD', 'EUR'), ('USD', 'GBP'), ('USD', 'JPY'), ('EUR', 'GBP')]
        
        while self.running:
            try:
                # Collect current rates
                rates = self.rate_collector.collect_current_rates(currency_pairs)
                
                for rate_data in rates:
                    # Create event
                    event = {
                        'type': 'exchange_rate_update',
                        'timestamp': datetime.utcnow(),
                        'data': {
                            'currency_pair': f"{rate_data.base_currency}_{rate_data.target_currency}",
                            'rate': rate_data.rate,
                            'bid': rate_data.bid,
                            'ask': rate_data.ask,
                            'source': rate_data.source,
                            'timestamp': rate_data.timestamp
                        }
                    }
                    
                    # Publish event
                    await self._publish_event(event)
                    
                    # Store in database
                    await self._store_rate_data(rate_data)
                
                # Wait before next collection
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                self.logger.error(f"Error in exchange rate collection: {e}")
                await asyncio.sleep(30)  # Wait before retry
    
    async def _collect_news_data(self):
        """Continuously collect news data."""
        while self.running:
            try:
                # Collect recent news
                articles = self.news_collector.collect_recent_news(hours_back=1)
                
                for article in articles:
                    # Create event
                    event = {
                        'type': 'news_article',
                        'timestamp': datetime.utcnow(),
                        'data': {
                            'title': article.title,
                            'source': article.source,
                            'published_at': article.published_at,
                            'relevance_score': article.relevance_score,
                            'url': article.url,
                            'content_hash': article.content_hash
                        }
                    }
                    
                    # Publish event
                    await self._publish_event(event)
                    
                    # Queue for sentiment analysis
                    await self._queue_sentiment_analysis(article)
                
                # Wait before next collection
                await asyncio.sleep(300)  # Collect every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in news collection: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    async def _process_sentiment_queue(self):
        """Process sentiment analysis queue."""
        while self.running:
            try:
                if self.redis_client:
                    # Get articles from sentiment queue
                    article_data = self.redis_client.lpop('sentiment_queue')
                    
                    if article_data:
                        article_info = json.loads(article_data)
                        
                        # Create NewsArticle object
                        article = NewsArticle(
                            title=article_info['title'],
                            content=article_info['content'],
                            url=article_info['url'],
                            source=article_info['source'],
                            published_at=datetime.fromisoformat(article_info['published_at'])
                        )
                        
                        # Analyze sentiment
                        sentiment_result = self.sentiment_analyzer.analyze_article_sentiment(article)
                        
                        # Create sentiment event
                        event = {
                            'type': 'sentiment_analysis',
                            'timestamp': datetime.utcnow(),
                            'data': {
                                'article_id': article_info['id'],
                                'sentiment': sentiment_result['overall_sentiment'],
                                'currency_relevance': sentiment_result['currency_relevance']
                            }
                        }
                        
                        # Publish event
                        await self._publish_event(event)
                        
                        # Update database
                        await self._update_article_sentiment(article_info['id'], sentiment_result)
                
                await asyncio.sleep(1)  # Check queue every second
                
            except Exception as e:
                self.logger.error(f"Error in sentiment processing: {e}")
                await asyncio.sleep(5)
    
    async def _publish_event(self, event: Dict):
        """Publish event to message queue and WebSocket clients."""
        try:
            # Publish to Kafka
            if self.producer:
                topic = f"exchange_rate_{event['type']}"
                self.producer.send(topic, value=event, key=event['type'])
            
            # Publish to Redis pub/sub
            if self.redis_client:
                channel = f"realtime:{event['type']}"
                self.redis_client.publish(channel, json.dumps(event, default=str))
            
            # Send to WebSocket clients
            await self._broadcast_to_websockets(event)
            
            # Add to processing queue
            self.event_queue.put(event)
            
        except Exception as e:
            self.logger.error(f"Error publishing event: {e}")
    
    async def _broadcast_to_websockets(self, event: Dict):
        """Broadcast event to connected WebSocket clients."""
        if not self.websocket_clients:
            return
        
        message = json.dumps(event, default=str)
        disconnected_clients = set()
        
        for client in self.websocket_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                self.logger.warning(f"Error sending to WebSocket client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.websocket_clients -= disconnected_clients
    
    def _process_events(self):
        """Process events from the event queue."""
        while self.running:
            try:
                event = self.event_queue.get(timeout=1)
                
                # Process based on event type
                if event['type'] == 'exchange_rate_update':
                    self._process_rate_update(event)
                elif event['type'] == 'news_article':
                    self._process_news_article(event)
                elif event['type'] == 'sentiment_analysis':
                    self._process_sentiment_update(event)
                
                self.event_queue.task_done()
                
            except:
                continue  # Timeout or other error, continue processing
    
    def _process_rate_update(self, event: Dict):
        """Process exchange rate update event."""
        try:
            rate_data = event['data']
            currency_pair = rate_data['currency_pair']
            
            # Update cache
            if self.redis_client:
                cache_key = f"current_rate:{currency_pair}"
                self.redis_client.setex(cache_key, 300, json.dumps(rate_data, default=str))  # 5 minute expiry
            
            # Check for significant changes
            previous_rate = self._get_previous_rate(currency_pair)
            if previous_rate:
                change_percent = abs((rate_data['rate'] - previous_rate) / previous_rate) * 100
                
                if change_percent > 0.5:  # 0.5% change threshold
                    alert_event = {
                        'type': 'rate_alert',
                        'timestamp': datetime.utcnow(),
                        'data': {
                            'currency_pair': currency_pair,
                            'current_rate': rate_data['rate'],
                            'previous_rate': previous_rate,
                            'change_percent': change_percent,
                            'alert_level': 'high' if change_percent > 1.0 else 'medium'
                        }
                    }
                    
                    # Publish alert
                    asyncio.create_task(self._publish_event(alert_event))
            
        except Exception as e:
            self.logger.error(f"Error processing rate update: {e}")
    
    def _process_news_article(self, event: Dict):
        """Process news article event."""
        try:
            article_data = event['data']
            
            # Check relevance threshold
            if article_data['relevance_score'] > 0.7:
                # High relevance article - create alert
                alert_event = {
                    'type': 'news_alert',
                    'timestamp': datetime.utcnow(),
                    'data': {
                        'title': article_data['title'],
                        'source': article_data['source'],
                        'relevance_score': article_data['relevance_score'],
                        'url': article_data['url']
                    }
                }
                
                # Publish alert
                asyncio.create_task(self._publish_event(alert_event))
            
        except Exception as e:
            self.logger.error(f"Error processing news article: {e}")
    
    def _process_sentiment_update(self, event: Dict):
        """Process sentiment analysis update event."""
        try:
            sentiment_data = event['data']
            
            # Update sentiment cache
            if self.redis_client:
                for currency_pair, relevance_info in sentiment_data['currency_relevance'].items():
                    if relevance_info['relevance_score'] > 0.5:
                        cache_key = f"sentiment:{currency_pair}"
                        
                        # Get existing sentiment data
                        existing_data = self.redis_client.get(cache_key)
                        if existing_data:
                            existing_sentiment = json.loads(existing_data)
                            
                            # Calculate weighted average
                            new_weight = relevance_info['relevance_score']
                            existing_weight = existing_sentiment.get('weight', 1.0)
                            
                            total_weight = new_weight + existing_weight
                            weighted_sentiment = (
                                (sentiment_data['sentiment']['score'] * new_weight +
                                 existing_sentiment['sentiment'] * existing_weight) / total_weight
                            )
                            
                            sentiment_cache = {
                                'sentiment': weighted_sentiment,
                                'weight': total_weight,
                                'last_updated': datetime.utcnow().isoformat(),
                                'article_count': existing_sentiment.get('article_count', 0) + 1
                            }
                        else:
                            sentiment_cache = {
                                'sentiment': sentiment_data['sentiment']['score'],
                                'weight': relevance_info['relevance_score'],
                                'last_updated': datetime.utcnow().isoformat(),
                                'article_count': 1
                            }
                        
                        self.redis_client.setex(cache_key, 3600, json.dumps(sentiment_cache, default=str))  # 1 hour expiry
            
        except Exception as e:
            self.logger.error(f"Error processing sentiment update: {e}")
    
    async def _store_rate_data(self, rate_data: ExchangeRateData):
        """Store exchange rate data in database."""
        try:
            db = self.db_manager.databases['exchange_rates']
            
            document = {
                'currency_pair': {
                    'base': rate_data.base_currency,
                    'target': rate_data.target_currency,
                    'symbol': f"{rate_data.base_currency}_{rate_data.target_currency}"
                },
                'rate': {
                    'value': rate_data.rate,
                    'bid': rate_data.bid,
                    'ask': rate_data.ask,
                    'timestamp': rate_data.timestamp
                },
                'source': {
                    'provider': rate_data.source,
                    'collection_type': 'real_time'
                },
                'metadata': {
                    'collection_timestamp': datetime.utcnow(),
                    'data_quality_score': 1.0 if self.rate_collector.validate_rate_data(rate_data) else 0.5
                }
            }
            
            await asyncio.get_event_loop().run_in_executor(
                None, db.current_rates.insert_one, document
            )
            
        except Exception as e:
            self.logger.error(f"Error storing rate data: {e}")
    
    async def _queue_sentiment_analysis(self, article: NewsArticle):
        """Queue article for sentiment analysis."""
        try:
            if self.redis_client:
                # Store article in database first
                article_ids = self.news_collector.store_articles([article])
                
                if article_ids:
                    article_data = {
                        'id': article_ids[0],
                        'title': article.title,
                        'content': article.content,
                        'url': article.url,
                        'source': article.source,
                        'published_at': article.published_at.isoformat()
                    }
                    
                    self.redis_client.rpush('sentiment_queue', json.dumps(article_data, default=str))
            
        except Exception as e:
            self.logger.error(f"Error queuing sentiment analysis: {e}")
    
    async def _update_article_sentiment(self, article_id: str, sentiment_result: Dict):
        """Update article with sentiment analysis results."""
        try:
            db = self.db_manager.databases['news_sentiment']
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                db.news_articles.update_one,
                {'_id': ObjectId(article_id)},
                {
                    '$set': {
                        'sentiment_analysis': sentiment_result,
                        'processing_metadata.processing_status': 'completed',
                        'processing_metadata.processed_at': datetime.utcnow()
                    }
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error updating article sentiment: {e}")
    
    def _get_previous_rate(self, currency_pair: str) -> Optional[float]:
        """Get previous rate for comparison."""
        try:
            if self.redis_client:
                cache_key = f"current_rate:{currency_pair}"
                cached_data = self.redis_client.get(cache_key)
                
                if cached_data:
                    rate_data = json.loads(cached_data)
                    return rate_data.get('rate')
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting previous rate: {e}")
            return None
    
    def _start_kafka_consumers(self):
        """Start Kafka consumers for different topics."""
        try:
            kafka_config = self.config.get('kafka', {})
            
            topics = ['exchange_rate_exchange_rate_update', 'exchange_rate_news_article', 'exchange_rate_sentiment_analysis']
            
            for topic in topics:
                consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=kafka_config['bootstrap_servers'],
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    group_id=f"exchange_rate_consumer_{topic}",
                    auto_offset_reset='latest'
                )
                
                self.consumers[topic] = consumer
                
                # Start consumer thread
                thread = threading.Thread(
                    target=self._consume_kafka_messages,
                    args=(consumer, topic),
                    daemon=True
                )
                thread.start()
            
            self.logger.info(f"Started {len(topics)} Kafka consumers")
            
        except Exception as e:
            self.logger.error(f"Error starting Kafka consumers: {e}")
    
    def _consume_kafka_messages(self, consumer: KafkaConsumer, topic: str):
        """Consume messages from Kafka topic."""
        while self.running:
            try:
                for message in consumer:
                    if not self.running:
                        break
                    
                    # Process message based on topic
                    self._handle_kafka_message(message.value, topic)
                    
            except Exception as e:
                self.logger.error(f"Error consuming Kafka messages from {topic}: {e}")
                time.sleep(5)  # Wait before retry
    
    def _handle_kafka_message(self, message: Dict, topic: str):
        """Handle incoming Kafka message."""
        try:
            # Add message to processing queue
            self.event_queue.put(message)
            
        except Exception as e:
            self.logger.error(f"Error handling Kafka message: {e}")

# WebSocket server for real-time client connections
class WebSocketServer:
    """WebSocket server for real-time data streaming to clients."""
    
    def __init__(self, streaming_manager: StreamingManager, port: int = 8765):
        self.streaming_manager = streaming_manager
        self.port = port
        self.logger = logging.getLogger(__name__)
    
    async def register_client(self, websocket, path):
        """Register new WebSocket client."""
        try:
            self.streaming_manager.websocket_clients.add(websocket)
            self.logger.info(f"WebSocket client connected: {websocket.remote_address}")
            
            # Send welcome message
            welcome_message = {
                'type': 'connection_established',
                'timestamp': datetime.utcnow(),
                'message': 'Connected to exchange rate streaming service'
            }
            
            await websocket.send(json.dumps(welcome_message, default=str))
            
            # Keep connection alive
            await websocket.wait_closed()
            
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            self.logger.error(f"Error in WebSocket connection: {e}")
        finally:
            self.streaming_manager.websocket_clients.discard(websocket)
            self.logger.info("WebSocket client disconnected")
    
    def start_server(self):
        """Start WebSocket server."""
        return websockets.serve(self.register_client, "0.0.0.0", self.port)
```

This comprehensive data pipeline implementation provides all the necessary components for collecting, processing, and streaming real-time exchange rate and news data. The implementation includes robust error handling, data quality monitoring, and scalable streaming architecture that can handle high-volume data flows while maintaining reliability and performance.

---

## References

[1] ExchangeRate-API Documentation: https://exchangerate-api.com/docs
[2] NewsAPI Documentation: https://newsapi.org/docs
[3] Google Cloud Natural Language API: https://cloud.google.com/natural-language/docs
[4] Finnhub API Documentation: https://finnhub.io/docs/api
[5] Apache Kafka Documentation: https://kafka.apache.org/documentation/
[6] Redis Documentation: https://redis.io/documentation
[7] WebSocket Protocol Specification: https://tools.ietf.org/html/rfc6455
[8] Pandas Documentation: https://pandas.pydata.org/docs/
[9] Scikit-learn Documentation: https://scikit-learn.org/stable/
[10] Transformers Library Documentation: https://huggingface.co/docs/transformers/

