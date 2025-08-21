# Exchange Rate Forecasting Website - Research Findings

## Exchange Rate APIs

### ExchangeRate-API (https://www.exchangerate-api.com/)
**Features:**
- Currency conversion rates for 161 currencies
- Over 14 years of exceptional uptime & support
- Perfect for SaaS, Dashboards & E-Commerce
- High availability infrastructure on AWS
- Long-term support commitment

**Pricing Plans:**
- **Free Plan**: $0/month
  - Updates once per day
  - 1.5K API requests per month
  - Limited features (no historical data, LTS commitment, etc.)

- **Pro Plan**: $10/month
  - Updates every 60 minutes
  - 30K API requests per month
  - High availability infrastructure
  - Historical data access
  - Email support
  - Enriched data
  - Pricing locked in

- **Business Plan**: $30/month
  - Updates every 5 minutes
  - 125K API requests per month
  - All Pro features plus:
  - Priority email support
  - Relaxed quota enforcement

**Key Benefits:**
- Exceptional uptime (>99.99% in 2024)
- Fault tolerant AWS services across multiple availability zones
- Long-term API endpoint support (some endpoints from 2010 still working)
- No breaking changes policy

## News APIs

### NewsAPI.org
- Simple REST API returning JSON search results
- Current and historic news articles
- 150,000+ worldwide sources
- Need to investigate pricing and rate limits

### NewsData.io
- Real-time and 7 years historical news
- 80,000+ sources
- JSON format through API endpoints
- Need to investigate pricing

### Financial News APIs
- Finnhub.io - Real-time market news
- MarketAux.com - Financial and stock market news
- StockNewsAPI.com - Stock market and financial news
- Polygon.io - Financial news with sentiment analysis

## Sentiment Analysis APIs

### Google Cloud Natural Language API
- Sentiment analysis for text
- Identifies emotional opinion within text
- Determines writer's attitude

### AssemblyAI Sentiment Analysis API
- Listed as top choice for sentiment analysis
- Need to investigate features and pricing

### Financial-Specific Sentiment APIs
- Polygon.io - News with sentiment analysis tied to tickers
- Finnhub.io - News sentiment endpoint
- Financial Modeling Prep - Social sentiment API
- Arya.ai - Financial sentiment analysis API

## Next Steps
1. Investigate detailed pricing and features for top news APIs
2. Research sentiment analysis API capabilities and costs
3. Analyze real-time data streaming options
4. Design system architecture based on findings



## Detailed API Analysis

### NewsAPI.org (https://newsapi.org/)
**Features:**
- Simple REST API returning JSON search results
- Current and historic news articles
- 150,000+ worldwide sources
- Search articles and get live top headlines

**Pricing Plans:**
- **Developer Plan**: $0/month
  - For development and testing only
  - Articles have 24-hour delay
  - Search articles up to 1 month old
  - CORS enabled for localhost
  - 100 requests per day
  - No extra requests available
  - Basic support

- **Business Plan**: $449/month (billed monthly)
  - For production and commercial projects
  - Real-time articles (no delay)
  - Search articles up to 5 years old
  - CORS enabled for all origins
  - 250,000 requests per month
  - $0.0018 per extra request
  - Email support

- **Advanced Plan**: $1,749/month (billed monthly)
  - For larger projects requiring exceptional resources
  - All Business features plus:
  - 2,000,000 requests per month
  - $0.0009 per extra request
  - 99.95% uptime SLA
  - Priority email support

- **Enterprise Plan**: Contact for pricing
  - Extra articles and extended source library
  - Articles enriched with 20 additional data points
  - Article & story clustering
  - Custom classifications, tagging & information extraction
  - Unlimited requests
  - Custom SLA & dedicated chat
  - On-premise deployment

**Limitations:**
- Full article content not available (only snippets)
- Developer plan cannot be used in production

### Finnhub.io (https://finnhub.io/)
**Features:**
- Real-time stock API, institutional-grade fundamental and alternative data
- 30+ years of historical data
- Real-time news, Reddit, Twitter sentiment analysis
- Forex API with direct connection to 10+ forex brokers
- Crypto API with access to 15+ crypto brokers
- Technical analysis with precomputed indicators
- ESG data, congressional trading data
- 15+ years of earnings call transcripts

**Pricing Plans:**
- **Free Plan**: $0/month
  - Personal use only
  - 60 API calls/minute
  - US coverage only
  - Company news: 1 year + real-time updates
  - Limited features

- **All-In-One Plan**: $3,000/month (billed annually)
  - Personal use license
  - Market data: 900 API calls/minute
  - Fundamental: 300 API calls/minute
  - Global coverage
  - Company news: 20 years + real-time updates
  - Social sentiment analysis
  - Full alternative data access
  - 30+ years of financial statements
  - Real-time forex and crypto data

**Key Benefits for Our Project:**
- Real-time news with sentiment analysis
- Forex data integration
- Social media sentiment (Reddit, Twitter)
- Comprehensive financial data
- High API rate limits

## Real-Time Data Streaming Options

### WebSocket Support
- **Finnhub**: Provides WebSocket for real-time market data
- **ExchangeRate-API**: Updates every 5 minutes (Business plan) to once per day (Free)
- **NewsAPI**: Real-time news updates available on paid plans

### Data Update Frequencies
- **Exchange Rates**: 
  - ExchangeRate-API: 5 minutes to daily depending on plan
  - Finnhub: Real-time forex data
- **News Data**:
  - NewsAPI: Real-time on paid plans, 24-hour delay on free
  - Finnhub: Real-time news and sentiment updates
- **Sentiment Analysis**: Real-time processing required for incoming news

## Cost Analysis Summary

### For Development/Testing:
- ExchangeRate-API Free: $0 (1.5K requests/month, daily updates)
- NewsAPI Developer: $0 (100 requests/day, 24-hour delay)
- Finnhub Free: $0 (60 calls/minute, limited features)
- **Total Development Cost**: $0/month

### For Production (Small Scale):
- ExchangeRate-API Pro: $10/month (30K requests, hourly updates)
- NewsAPI Business: $449/month (250K requests, real-time)
- Finnhub All-In-One: $3,000/month (comprehensive data)
- **Total Production Cost**: $3,459/month

### For Production (Alternative - Lower Cost):
- ExchangeRate-API Pro: $10/month
- NewsAPI Business: $449/month
- Google Cloud Natural Language API: Pay-per-use sentiment analysis
- **Alternative Production Cost**: ~$500-600/month

## Recommended Data Sources for Our Project

### Exchange Rate Data:
1. **Primary**: ExchangeRate-API Pro ($10/month) - Cost-effective, reliable
2. **Alternative**: Finnhub Forex API (included in All-In-One plan)

### News Data:
1. **Primary**: NewsAPI Business ($449/month) - Comprehensive news coverage
2. **Alternative**: Finnhub News API (included in All-In-One plan)

### Sentiment Analysis:
1. **Primary**: Google Cloud Natural Language API - Pay-per-use, accurate
2. **Alternative**: Finnhub Social Sentiment (included in All-In-One plan)
3. **Budget Option**: Open-source sentiment analysis libraries (VADER, TextBlob)

## Next Research Areas:
1. MongoDB Cloud setup and pricing
2. Real-time data streaming architectures
3. Machine learning frameworks for time series forecasting
4. WebSocket implementation for real-time updates


### Google Cloud Natural Language API (https://cloud.google.com/natural-language/)
**Features:**
- Sentiment Analysis: Understand overall sentiment in text blocks
- Entity Analysis: Identify entities and label by types
- Entity Sentiment Analysis: Understand sentiment for specific entities
- Syntax Analysis: Extract tokens, sentences, parts of speech
- Content Classification: Identify content categories
- Text Moderation: Identify harmful/sensitive content

**Pricing Structure (Pay-as-you-go):**
- **Sentiment Analysis**:
  - First 5K units/month: FREE
  - 5K+ - 1M units: $0.0010 per 1,000-character unit
  - 1M+ - 5M units: $0.00050 per 1,000-character unit
  - 5M+ units: $0.000250 per 1,000-character unit

**Pricing Units:**
- Based on Unicode characters in each request
- Rounded to nearest 1,000 characters for sentiment analysis
- Includes whitespace and markup characters (HTML/XML tags)

**Cost Examples:**
- 100,000 news articles (avg 500 chars each) = 50,000 units
- Monthly cost: First 5K free + 45K units × $0.0010 = $45/month
- For 1M articles/month: ~$450/month for sentiment analysis

**Key Benefits:**
- No upfront commitments
- Generous free tier (5,000 units/month)
- Highly accurate sentiment analysis
- Supports multiple languages
- Scales automatically
- Integration with other Google Cloud services

## Final Recommendations

### Recommended Technology Stack for Exchange Rate Forecasting Website:

**Data Sources:**
1. **Exchange Rates**: ExchangeRate-API Pro ($10/month) - reliable, cost-effective
2. **News Data**: NewsAPI Business ($449/month) - comprehensive real-time news
3. **Sentiment Analysis**: Google Cloud Natural Language API (pay-per-use, ~$50-100/month)

**Alternative Budget-Friendly Stack:**
1. **Exchange Rates**: ExchangeRate-API Free (development) / Pro (production)
2. **News Data**: NewsAPI Developer (development) / Business (production)
3. **Sentiment Analysis**: Open-source libraries (VADER, TextBlob) for development

**Enterprise Stack:**
1. **All Data Sources**: Finnhub All-In-One ($3,000/month) - comprehensive solution
2. **Additional News**: NewsAPI Enterprise for extended coverage
3. **Custom ML**: Build proprietary sentiment analysis models

### Cost Summary by Development Stage:

**Development Phase**: $0/month (all free tiers)
**Small Production**: ~$500-600/month
**Medium Production**: ~$1,000-1,500/month
**Enterprise Production**: $3,000+/month

### Next Steps:
- Design system architecture incorporating these data sources
- Plan MongoDB Cloud integration
- Design real-time data processing pipeline
- Plan machine learning model architecture
- Design frontend and backend components

