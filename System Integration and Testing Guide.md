# System Integration and Testing Guide

## Overview

This guide covers the complete integration and testing of the Exchange Rate Forecasting system, including frontend-backend connectivity, end-to-end testing procedures, performance optimization, and comprehensive error handling strategies.

## System Architecture Integration

### Component Integration Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │    │   Flask Backend  │    │  MongoDB Cloud  │
│                 │    │                  │    │                 │
│ • Dashboard     │◄──►│ • REST API       │◄──►│ • Exchange Data │
│ • Real-time UI  │    │ • WebSocket      │    │ • News Data     │
│ • Charts        │    │ • ML Models      │    │ • Model Data    │
│ • Controls      │    │ • Data Pipeline  │    │ • User Data     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  External APIs  │    │   ML Pipeline    │    │   Data Sources  │
│                 │    │                  │    │                 │
│ • ExchangeRate  │    │ • Feature Eng.   │    │ • News APIs     │
│ • NewsAPI       │    │ • Model Training │    │ • Sentiment API │
│ • Sentiment API │    │ • Predictions    │    │ • Market Data   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Frontend-Backend Integration

### 1. API Configuration

#### Frontend API Service Configuration
```javascript
// src/services/api.js
const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  WS_URL: process.env.REACT_APP_WS_URL || 'ws://localhost:5000',
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3
}

class ApiService {
  constructor() {
    this.baseURL = API_CONFIG.BASE_URL
    this.wsURL = API_CONFIG.WS_URL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    }

    try {
      const response = await fetch(url, config)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      return await response.json()
    } catch (error) {
      console.error('API Request failed:', error)
      throw error
    }
  }

  // Exchange rate endpoints
  async getExchangeRates(pair) {
    return this.request(`/api/rates/${pair}`)
  }

  async getHistoricalRates(pair, period) {
    return this.request(`/api/rates/${pair}/history?period=${period}`)
  }

  // Forecasting endpoints
  async generateForecast(pair, model, horizon) {
    return this.request('/api/forecast', {
      method: 'POST',
      body: JSON.stringify({ pair, model, horizon })
    })
  }

  async getForecastHistory(pair) {
    return this.request(`/api/forecast/${pair}/history`)
  }

  // News and sentiment endpoints
  async getNews(pair, limit = 10) {
    return this.request(`/api/news/${pair}?limit=${limit}`)
  }

  async getSentimentAnalysis(pair) {
    return this.request(`/api/sentiment/${pair}`)
  }

  // Model endpoints
  async getModelPerformance() {
    return this.request('/api/models/performance')
  }

  async getModelStatus() {
    return this.request('/api/models/status')
  }

  async retrainModel(modelType) {
    return this.request('/api/models/retrain', {
      method: 'POST',
      body: JSON.stringify({ model: modelType })
    })
  }
}

export const apiService = new ApiService()
```

#### WebSocket Integration
```javascript
// src/hooks/useWebSocket.js
import { useState, useEffect, useRef, useCallback } from 'react'

export function useWebSocket(url, options = {}) {
  const [socket, setSocket] = useState(null)
  const [lastMessage, setLastMessage] = useState(null)
  const [readyState, setReadyState] = useState(0)
  const [error, setError] = useState(null)
  const reconnectTimeoutRef = useRef(null)
  const reconnectAttemptsRef = useRef(0)

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url)
      
      ws.onopen = () => {
        console.log('WebSocket connected')
        setReadyState(1)
        setSocket(ws)
        setError(null)
        reconnectAttemptsRef.current = 0
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          setLastMessage(data)
          options.onMessage?.(data)
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setError(error)
        options.onError?.(error)
      }
      
      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason)
        setReadyState(3)
        setSocket(null)
        options.onClose?.(event)
        
        // Auto-reconnect logic
        if (options.autoReconnect && reconnectAttemptsRef.current < 5) {
          const delay = Math.pow(2, reconnectAttemptsRef.current) * 1000
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++
            connect()
          }, delay)
        }
      }
      
      setSocket(ws)
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err)
      setError(err)
    }
  }, [url, options])

  useEffect(() => {
    connect()
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (socket) {
        socket.close()
      }
    }
  }, [connect])

  const sendMessage = useCallback((message) => {
    if (socket && readyState === 1) {
      socket.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected, message not sent:', message)
    }
  }, [socket, readyState])

  return { socket, lastMessage, readyState, error, sendMessage, reconnect: connect }
}
```

### 2. Backend CORS Configuration

#### Flask CORS Setup
```python
# app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

def create_app():
    app = Flask(__name__)
    
    # CORS configuration for frontend integration
    CORS(app, origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "https://your-frontend-domain.com"  # Production frontend
    ], supports_credentials=True)
    
    # SocketIO for real-time communication
    socketio = SocketIO(app, cors_allowed_origins="*", 
                       async_mode='threading')
    
    # Register blueprints
    from app.api.v1 import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app, socketio

app, socketio = create_app()
```

#### Real-time Data Streaming
```python
# app/services/websocket_service.py
from flask_socketio import emit, join_room, leave_room
from app import socketio
import threading
import time
import json

class WebSocketService:
    def __init__(self):
        self.active_connections = {}
        self.data_streams = {}
        
    def start_rate_stream(self, pair):
        """Start real-time exchange rate streaming for a currency pair"""
        if pair not in self.data_streams:
            thread = threading.Thread(
                target=self._rate_stream_worker, 
                args=(pair,),
                daemon=True
            )
            thread.start()
            self.data_streams[pair] = thread
    
    def _rate_stream_worker(self, pair):
        """Worker thread for streaming exchange rate data"""
        while pair in self.data_streams:
            try:
                # Fetch latest rate data
                rate_data = self.get_latest_rate(pair)
                
                # Emit to all clients subscribed to this pair
                socketio.emit('rate_update', {
                    'pair': pair,
                    'rate': rate_data['rate'],
                    'change': rate_data['change'],
                    'timestamp': rate_data['timestamp']
                }, room=f'rates_{pair}')
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print(f"Error in rate stream for {pair}: {e}")
                time.sleep(10)  # Wait longer on error
    
    def get_latest_rate(self, pair):
        """Fetch latest exchange rate from data source"""
        # Implementation to fetch from external API or database
        pass

ws_service = WebSocketService()

@socketio.on('subscribe_rates')
def handle_rate_subscription(data):
    pair = data.get('pair')
    if pair:
        join_room(f'rates_{pair}')
        ws_service.start_rate_stream(pair)
        emit('subscription_confirmed', {'pair': pair})

@socketio.on('unsubscribe_rates')
def handle_rate_unsubscription(data):
    pair = data.get('pair')
    if pair:
        leave_room(f'rates_{pair}')
        emit('unsubscription_confirmed', {'pair': pair})
```

## End-to-End Testing

### 1. Integration Test Suite

#### Frontend Integration Tests
```javascript
// src/tests/integration/dashboard.test.js
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { rest } from 'msw'
import { setupServer } from 'msw/node'
import App from '../App'

// Mock API server
const server = setupServer(
  rest.get('/api/rates/USD/EUR', (req, res, ctx) => {
    return res(ctx.json({
      current: { rate: 1.0545, change: 0.0007, timestamp: '2025-01-08T10:00:00Z' },
      history: [
        { rate: 1.0538, timestamp: '2025-01-08T09:55:00Z' },
        { rate: 1.0545, timestamp: '2025-01-08T10:00:00Z' }
      ]
    }))
  }),
  
  rest.post('/api/forecast', (req, res, ctx) => {
    return res(ctx.json({
      predictions: [
        { timestamp: '2025-01-08T11:00:00Z', predicted: 1.0550, confidence: 0.85 },
        { timestamp: '2025-01-08T12:00:00Z', predicted: 1.0565, confidence: 0.82 }
      ],
      model: 'ensemble',
      accuracy: 0.847
    }))
  })
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('Dashboard Integration', () => {
  test('loads exchange rate data and displays dashboard', async () => {
    render(<App />)
    
    // Check if dashboard loads
    expect(screen.getByText('Exchange Rate Forecasting')).toBeInTheDocument()
    
    // Wait for API data to load
    await waitFor(() => {
      expect(screen.getByText('1.0545')).toBeInTheDocument()
    })
    
    // Check if metrics are displayed
    expect(screen.getByText('Current Rate')).toBeInTheDocument()
    expect(screen.getByText('24h Change')).toBeInTheDocument()
  })
  
  test('generates forecast when button clicked', async () => {
    const user = userEvent.setup()
    render(<App />)
    
    // Click generate forecast button
    const forecastButton = screen.getByText('Generate Forecast')
    await user.click(forecastButton)
    
    // Wait for forecast data
    await waitFor(() => {
      expect(screen.getByText('1.0550')).toBeInTheDocument()
    })
  })
  
  test('switches between currency pairs', async () => {
    const user = userEvent.setup()
    render(<App />)
    
    // Change currency pair
    const pairSelect = screen.getByRole('combobox')
    await user.click(pairSelect)
    await user.click(screen.getByText('USD/GBP'))
    
    // Verify API call with new pair
    await waitFor(() => {
      expect(screen.getByText('USD/GBP')).toBeInTheDocument()
    })
  })
})
```

#### Backend Integration Tests
```python
# tests/integration/test_api_integration.py
import pytest
import json
from app import create_app
from app.models import ExchangeRate, NewsArticle
from app.services.ml_service import MLService

@pytest.fixture
def client():
    app, _ = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_data():
    return {
        'exchange_rates': [
            {'pair': 'USD/EUR', 'rate': 1.0545, 'timestamp': '2025-01-08T10:00:00Z'},
            {'pair': 'USD/EUR', 'rate': 1.0538, 'timestamp': '2025-01-08T09:55:00Z'}
        ],
        'news': [
            {
                'title': 'Fed Signals Rate Changes',
                'content': 'Federal Reserve indicates potential policy shifts...',
                'sentiment': 0.2,
                'relevance': 0.9,
                'timestamp': '2025-01-08T09:30:00Z'
            }
        ]
    }

class TestAPIIntegration:
    def test_get_exchange_rates(self, client, sample_data):
        """Test exchange rate API endpoint"""
        response = client.get('/api/rates/USD/EUR')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'current' in data
        assert 'history' in data
        assert data['current']['rate'] > 0
    
    def test_generate_forecast(self, client):
        """Test forecast generation endpoint"""
        payload = {
            'pair': 'USD/EUR',
            'model': 'ensemble',
            'horizon': 24
        }
        
        response = client.post('/api/forecast', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'predictions' in data
        assert len(data['predictions']) > 0
        assert data['model'] == 'ensemble'
    
    def test_news_sentiment_integration(self, client):
        """Test news and sentiment analysis integration"""
        response = client.get('/api/news/USD/EUR')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'articles' in data
        assert 'sentiment_summary' in data
        
        for article in data['articles']:
            assert 'sentiment' in article
            assert 'relevance' in article
    
    def test_model_performance_endpoint(self, client):
        """Test model performance monitoring"""
        response = client.get('/api/models/performance')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'models' in data
        
        for model in data['models']:
            assert 'accuracy' in model
            assert 'mse' in model
            assert 'last_updated' in model
    
    def test_websocket_connection(self, client):
        """Test WebSocket real-time functionality"""
        # This would require a WebSocket test client
        # Implementation depends on your WebSocket library
        pass
```

### 2. Performance Testing

#### Load Testing Script
```python
# tests/performance/load_test.py
import asyncio
import aiohttp
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

class LoadTester:
    def __init__(self, base_url, concurrent_users=10):
        self.base_url = base_url
        self.concurrent_users = concurrent_users
        self.results = []
    
    async def make_request(self, session, endpoint):
        """Make a single HTTP request and measure response time"""
        start_time = time.time()
        try:
            async with session.get(f"{self.base_url}{endpoint}") as response:
                await response.text()
                end_time = time.time()
                return {
                    'endpoint': endpoint,
                    'status': response.status,
                    'response_time': end_time - start_time,
                    'success': response.status == 200
                }
        except Exception as e:
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'status': 0,
                'response_time': end_time - start_time,
                'success': False,
                'error': str(e)
            }
    
    async def run_load_test(self, endpoints, duration_seconds=60):
        """Run load test for specified duration"""
        print(f"Starting load test with {self.concurrent_users} concurrent users for {duration_seconds} seconds")
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            tasks = []
            
            while time.time() - start_time < duration_seconds:
                for endpoint in endpoints:
                    for _ in range(self.concurrent_users):
                        task = asyncio.create_task(self.make_request(session, endpoint))
                        tasks.append(task)
                
                # Wait a bit before next batch
                await asyncio.sleep(1)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            self.results.extend([r for r in results if not isinstance(r, Exception)])
    
    def generate_report(self):
        """Generate performance test report"""
        if not self.results:
            print("No results to report")
            return
        
        successful_requests = [r for r in self.results if r['success']]
        failed_requests = [r for r in self.results if not r['success']]
        
        response_times = [r['response_time'] for r in successful_requests]
        
        print("\n=== LOAD TEST REPORT ===")
        print(f"Total requests: {len(self.results)}")
        print(f"Successful requests: {len(successful_requests)}")
        print(f"Failed requests: {len(failed_requests)}")
        print(f"Success rate: {len(successful_requests)/len(self.results)*100:.2f}%")
        
        if response_times:
            print(f"\nResponse Time Statistics:")
            print(f"Average: {statistics.mean(response_times):.3f}s")
            print(f"Median: {statistics.median(response_times):.3f}s")
            print(f"Min: {min(response_times):.3f}s")
            print(f"Max: {max(response_times):.3f}s")
            print(f"95th percentile: {statistics.quantiles(response_times, n=20)[18]:.3f}s")

# Usage
async def main():
    tester = LoadTester("http://localhost:5000", concurrent_users=20)
    
    endpoints = [
        "/api/rates/USD/EUR",
        "/api/forecast",
        "/api/news/USD/EUR",
        "/api/models/performance"
    ]
    
    await tester.run_load_test(endpoints, duration_seconds=120)
    tester.generate_report()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Database Performance Testing

#### MongoDB Performance Tests
```python
# tests/performance/db_performance.py
import time
import pymongo
from pymongo import MongoClient
import statistics
import threading
from datetime import datetime, timedelta

class DatabasePerformanceTester:
    def __init__(self, connection_string):
        self.client = MongoClient(connection_string)
        self.db = self.client.exchange_forecast
        self.results = []
    
    def test_insert_performance(self, num_records=1000):
        """Test bulk insert performance"""
        print(f"Testing insert performance with {num_records} records...")
        
        # Generate test data
        test_data = []
        for i in range(num_records):
            test_data.append({
                'pair': 'USD/EUR',
                'rate': 1.0500 + (i * 0.0001),
                'timestamp': datetime.utcnow() - timedelta(minutes=i),
                'volume': 1000000 + i,
                'source': 'test'
            })
        
        # Measure insert time
        start_time = time.time()
        result = self.db.exchange_rates.insert_many(test_data)
        end_time = time.time()
        
        insert_time = end_time - start_time
        records_per_second = num_records / insert_time
        
        print(f"Inserted {len(result.inserted_ids)} records in {insert_time:.3f}s")
        print(f"Insert rate: {records_per_second:.2f} records/second")
        
        return {
            'operation': 'insert',
            'records': num_records,
            'time': insert_time,
            'rate': records_per_second
        }
    
    def test_query_performance(self, num_queries=100):
        """Test query performance"""
        print(f"Testing query performance with {num_queries} queries...")
        
        query_times = []
        
        for i in range(num_queries):
            start_time = time.time()
            
            # Test different query patterns
            if i % 3 == 0:
                # Time range query
                result = list(self.db.exchange_rates.find({
                    'pair': 'USD/EUR',
                    'timestamp': {
                        '$gte': datetime.utcnow() - timedelta(hours=1)
                    }
                }).limit(100))
            elif i % 3 == 1:
                # Aggregation query
                result = list(self.db.exchange_rates.aggregate([
                    {'$match': {'pair': 'USD/EUR'}},
                    {'$group': {
                        '_id': None,
                        'avg_rate': {'$avg': '$rate'},
                        'count': {'$sum': 1}
                    }}
                ]))
            else:
                # Index-based query
                result = list(self.db.exchange_rates.find({
                    'pair': 'USD/EUR'
                }).sort('timestamp', -1).limit(10))
            
            end_time = time.time()
            query_times.append(end_time - start_time)
        
        avg_query_time = statistics.mean(query_times)
        queries_per_second = 1 / avg_query_time
        
        print(f"Average query time: {avg_query_time:.3f}s")
        print(f"Query rate: {queries_per_second:.2f} queries/second")
        
        return {
            'operation': 'query',
            'queries': num_queries,
            'avg_time': avg_query_time,
            'rate': queries_per_second
        }
    
    def test_concurrent_operations(self, num_threads=10, operations_per_thread=50):
        """Test concurrent database operations"""
        print(f"Testing concurrent operations with {num_threads} threads...")
        
        results = []
        threads = []
        
        def worker():
            thread_results = []
            for _ in range(operations_per_thread):
                start_time = time.time()
                
                # Mix of read and write operations
                if time.time() % 2 < 1:
                    # Write operation
                    self.db.exchange_rates.insert_one({
                        'pair': 'USD/EUR',
                        'rate': 1.0500,
                        'timestamp': datetime.utcnow(),
                        'thread_id': threading.current_thread().ident
                    })
                else:
                    # Read operation
                    list(self.db.exchange_rates.find({'pair': 'USD/EUR'}).limit(10))
                
                end_time = time.time()
                thread_results.append(end_time - start_time)
            
            results.extend(thread_results)
        
        # Start threads
        start_time = time.time()
        for _ in range(num_threads):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        total_operations = num_threads * operations_per_thread
        total_time = end_time - start_time
        operations_per_second = total_operations / total_time
        
        print(f"Completed {total_operations} concurrent operations in {total_time:.3f}s")
        print(f"Throughput: {operations_per_second:.2f} operations/second")
        
        return {
            'operation': 'concurrent',
            'total_operations': total_operations,
            'time': total_time,
            'throughput': operations_per_second
        }

# Usage
def run_db_performance_tests():
    tester = DatabasePerformanceTester("mongodb://localhost:27017/")
    
    # Run tests
    insert_results = tester.test_insert_performance(1000)
    query_results = tester.test_query_performance(100)
    concurrent_results = tester.test_concurrent_operations(10, 50)
    
    print("\n=== DATABASE PERFORMANCE SUMMARY ===")
    print(f"Insert rate: {insert_results['rate']:.2f} records/second")
    print(f"Query rate: {query_results['rate']:.2f} queries/second")
    print(f"Concurrent throughput: {concurrent_results['throughput']:.2f} ops/second")

if __name__ == "__main__":
    run_db_performance_tests()
```

## Error Handling and Monitoring

### 1. Frontend Error Handling

#### Error Boundary Component
```jsx
// src/components/ErrorBoundary.jsx
import React from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    })
    
    // Log error to monitoring service
    console.error('Error caught by boundary:', error, errorInfo)
    
    // Send to error tracking service (e.g., Sentry)
    if (window.Sentry) {
      window.Sentry.captureException(error, {
        contexts: { errorInfo }
      })
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <Card className="max-w-md mx-auto">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-red-600">
                <AlertTriangle className="h-5 w-5" />
                <span>Something went wrong</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-600">
                We're sorry, but something unexpected happened. Please try refreshing the page.
              </p>
              
              {process.env.NODE_ENV === 'development' && (
                <details className="text-sm">
                  <summary className="cursor-pointer text-gray-500">Error details</summary>
                  <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
                    {this.state.error && this.state.error.toString()}
                    {this.state.errorInfo.componentStack}
                  </pre>
                </details>
              )}
              
              <div className="flex space-x-2">
                <Button 
                  onClick={() => window.location.reload()}
                  className="flex items-center space-x-2"
                >
                  <RefreshCw className="h-4 w-4" />
                  <span>Refresh Page</span>
                </Button>
                
                <Button 
                  variant="outline"
                  onClick={() => this.setState({ hasError: false, error: null, errorInfo: null })}
                >
                  Try Again
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
```

#### API Error Handling
```javascript
// src/hooks/useApiError.js
import { useState, useCallback } from 'react'
import { toast } from 'sonner'

export function useApiError() {
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleApiCall = useCallback(async (apiCall, options = {}) => {
    const { 
      showToast = true, 
      retries = 3, 
      retryDelay = 1000,
      onError,
      onSuccess 
    } = options

    setIsLoading(true)
    setError(null)

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const result = await apiCall()
        setIsLoading(false)
        onSuccess?.(result)
        return result
      } catch (err) {
        console.error(`API call attempt ${attempt} failed:`, err)
        
        if (attempt === retries) {
          setError(err)
          setIsLoading(false)
          
          if (showToast) {
            toast.error(err.message || 'An unexpected error occurred')
          }
          
          onError?.(err)
          throw err
        }
        
        // Wait before retry
        if (attempt < retries) {
          await new Promise(resolve => setTimeout(resolve, retryDelay * attempt))
        }
      }
    }
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return { error, isLoading, handleApiCall, clearError }
}
```

### 2. Backend Error Handling

#### Global Error Handler
```python
# app/error_handlers.py
from flask import jsonify, request
from werkzeug.exceptions import HTTPException
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the error
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        
        # If it's an HTTP exception, return the appropriate response
        if isinstance(e, HTTPException):
            return jsonify({
                'error': e.description,
                'status_code': e.code,
                'timestamp': datetime.utcnow().isoformat()
            }), e.code
        
        # For non-HTTP exceptions, return 500
        return jsonify({
            'error': 'Internal server error',
            'status_code': 500,
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': getattr(request, 'id', None)
        }), 500
    
    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({
            'error': 'Bad request',
            'message': str(e.description),
            'status_code': 400,
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({
            'error': 'Resource not found',
            'status_code': 404,
            'timestamp': datetime.utcnow().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        return jsonify({
            'error': 'Internal server error',
            'status_code': 500,
            'timestamp': datetime.utcnow().isoformat()
        }), 500
```

#### Custom Exception Classes
```python
# app/exceptions.py
class ExchangeRateAPIException(Exception):
    """Base exception for exchange rate API errors"""
    def __init__(self, message, status_code=500, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

class DataSourceException(ExchangeRateAPIException):
    """Exception for data source errors"""
    def __init__(self, source, message):
        super().__init__(f"Data source '{source}' error: {message}", 503)
        self.source = source

class ModelException(ExchangeRateAPIException):
    """Exception for ML model errors"""
    def __init__(self, model, message):
        super().__init__(f"Model '{model}' error: {message}", 500)
        self.model = model

class ValidationException(ExchangeRateAPIException):
    """Exception for input validation errors"""
    def __init__(self, field, message):
        super().__init__(f"Validation error for '{field}': {message}", 400)
        self.field = field
```

### 3. System Monitoring

#### Health Check Endpoint
```python
# app/api/v1/health.py
from flask import Blueprint, jsonify
from datetime import datetime
import psutil
import pymongo
from app.services.ml_service import MLService
from app.services.data_service import DataService

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Comprehensive system health check"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {},
        'system': {}
    }
    
    # Check database connectivity
    try:
        # MongoDB health check
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.server_info()
        health_status['services']['database'] = {'status': 'healthy', 'type': 'mongodb'}
    except Exception as e:
        health_status['services']['database'] = {'status': 'unhealthy', 'error': str(e)}
        health_status['status'] = 'degraded'
    
    # Check ML models
    try:
        ml_service = MLService()
        model_status = ml_service.get_model_health()
        health_status['services']['ml_models'] = model_status
    except Exception as e:
        health_status['services']['ml_models'] = {'status': 'unhealthy', 'error': str(e)}
        health_status['status'] = 'degraded'
    
    # Check external APIs
    try:
        data_service = DataService()
        api_status = data_service.check_external_apis()
        health_status['services']['external_apis'] = api_status
    except Exception as e:
        health_status['services']['external_apis'] = {'status': 'unhealthy', 'error': str(e)}
        health_status['status'] = 'degraded'
    
    # System metrics
    health_status['system'] = {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'uptime': datetime.utcnow().isoformat()  # Would be actual uptime in production
    }
    
    # Determine overall status
    if health_status['status'] == 'healthy':
        status_code = 200
    else:
        status_code = 503
    
    return jsonify(health_status), status_code

@health_bp.route('/health/ready')
def readiness_check():
    """Kubernetes readiness probe"""
    # Check if all critical services are ready
    try:
        # Quick checks for readiness
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        
        return jsonify({'status': 'ready'}), 200
    except Exception:
        return jsonify({'status': 'not ready'}), 503

@health_bp.route('/health/live')
def liveness_check():
    """Kubernetes liveness probe"""
    # Basic liveness check
    return jsonify({'status': 'alive'}), 200
```

## Performance Optimization

### 1. Frontend Optimizations

#### Code Splitting and Lazy Loading
```javascript
// src/App.jsx
import { lazy, Suspense } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import LoadingSpinner from './components/LoadingSpinner'

// Lazy load components
const Dashboard = lazy(() => import('./components/Dashboard'))
const ForecastingPage = lazy(() => import('./pages/ForecastingPage'))
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'))
const NewsPage = lazy(() => import('./pages/NewsPage'))

function App() {
  return (
    <Router>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/forecasting" element={<ForecastingPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/news" element={<NewsPage />} />
        </Routes>
      </Suspense>
    </Router>
  )
}
```

#### Data Caching Strategy
```javascript
// src/hooks/useCache.js
import { useState, useEffect, useRef } from 'react'

export function useCache(key, fetchFn, options = {}) {
  const { ttl = 300000, staleWhileRevalidate = true } = options // 5 minutes default TTL
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const cacheRef = useRef(new Map())
  const timestampRef = useRef(new Map())

  useEffect(() => {
    const fetchData = async () => {
      const cached = cacheRef.current.get(key)
      const timestamp = timestampRef.current.get(key)
      const now = Date.now()

      // Return cached data if still fresh
      if (cached && timestamp && (now - timestamp) < ttl) {
        setData(cached)
        setLoading(false)
        return
      }

      // Return stale data immediately, then fetch fresh data
      if (cached && staleWhileRevalidate) {
        setData(cached)
        setLoading(false)
      }

      try {
        const freshData = await fetchFn()
        cacheRef.current.set(key, freshData)
        timestampRef.current.set(key, now)
        setData(freshData)
        setError(null)
      } catch (err) {
        setError(err)
        // Keep stale data on error if available
        if (!cached) {
          setData(null)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [key, fetchFn, ttl, staleWhileRevalidate])

  return { data, loading, error }
}
```

### 2. Backend Optimizations

#### Database Query Optimization
```python
# app/services/optimized_data_service.py
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor

class OptimizedDataService:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client.exchange_forecast
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Ensure indexes for optimal query performance
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create database indexes for optimal query performance"""
        # Exchange rates indexes
        self.db.exchange_rates.create_index([
            ('pair', ASCENDING),
            ('timestamp', DESCENDING)
        ])
        
        self.db.exchange_rates.create_index([
            ('timestamp', DESCENDING)
        ])
        
        # News articles indexes
        self.db.news_articles.create_index([
            ('relevance_pairs', ASCENDING),
            ('timestamp', DESCENDING)
        ])
        
        self.db.news_articles.create_index([
            ('sentiment', ASCENDING),
            ('timestamp', DESCENDING)
        ])
        
        # Predictions indexes
        self.db.predictions.create_index([
            ('pair', ASCENDING),
            ('model', ASCENDING),
            ('timestamp', DESCENDING)
        ])
    
    async def get_exchange_rates_optimized(self, pair, limit=100):
        """Optimized exchange rate retrieval with caching"""
        loop = asyncio.get_event_loop()
        
        # Use thread pool for database operations
        def fetch_rates():
            return list(self.db.exchange_rates.find(
                {'pair': pair},
                {'_id': 0}  # Exclude _id field for better performance
            ).sort('timestamp', -1).limit(limit))
        
        rates = await loop.run_in_executor(self.executor, fetch_rates)
        return rates
    
    async def get_aggregated_data(self, pair, period_hours=24):
        """Get aggregated data using MongoDB aggregation pipeline"""
        loop = asyncio.get_event_loop()
        
        def aggregate_data():
            pipeline = [
                {
                    '$match': {
                        'pair': pair,
                        'timestamp': {
                            '$gte': datetime.utcnow() - timedelta(hours=period_hours)
                        }
                    }
                },
                {
                    '$group': {
                        '_id': {
                            'hour': {'$hour': '$timestamp'},
                            'day': {'$dayOfMonth': '$timestamp'}
                        },
                        'avg_rate': {'$avg': '$rate'},
                        'min_rate': {'$min': '$rate'},
                        'max_rate': {'$max': '$rate'},
                        'count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'_id': 1}
                }
            ]
            
            return list(self.db.exchange_rates.aggregate(pipeline))
        
        return await loop.run_in_executor(self.executor, aggregate_data)
```

#### Caching Layer
```python
# app/services/cache_service.py
import redis
import json
import pickle
from datetime import timedelta
from functools import wraps

class CacheService:
    def __init__(self, redis_url='redis://localhost:6379'):
        self.redis_client = redis.from_url(redis_url)
        self.default_ttl = 300  # 5 minutes
    
    def get(self, key):
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
    
    def set(self, key, value, ttl=None):
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            serialized = pickle.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            print(f"Cache set error: {e}")
    
    def delete(self, key):
        """Delete value from cache"""
        try:
            self.redis_client.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
    
    def cache_result(self, key_prefix, ttl=None):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result
            
            return wrapper
        return decorator

# Usage example
cache_service = CacheService()

@cache_service.cache_result('exchange_rates', ttl=60)
def get_exchange_rates(pair):
    # Expensive database operation
    return fetch_rates_from_db(pair)
```

This comprehensive integration and testing guide provides a robust framework for ensuring the exchange rate forecasting system works reliably in production with proper error handling, monitoring, and performance optimization.

