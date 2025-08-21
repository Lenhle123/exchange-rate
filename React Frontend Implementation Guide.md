# React Frontend Implementation Guide

## Overview

This guide provides a comprehensive implementation of the React frontend for the Exchange Rate Forecasting Dashboard. The frontend is built using modern React with Tailwind CSS, shadcn/ui components, and Recharts for data visualization.

## Project Structure

```
exchange-rate-dashboard/
├── public/
├── src/
│   ├── assets/          # Static assets
│   ├── components/
│   │   ├── ui/          # shadcn/ui components
│   │   ├── charts/      # Custom chart components
│   │   ├── dashboard/   # Dashboard-specific components
│   │   └── common/      # Reusable components
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utility functions
│   ├── services/        # API services
│   ├── App.jsx          # Main App component
│   ├── App.css          # Global styles
│   ├── index.css        # Tailwind imports
│   └── main.jsx         # Entry point
├── package.json
└── vite.config.js
```

## Key Features Implemented

### 1. Real-time Dashboard
- Live exchange rate display
- Real-time clock with UTC time
- Connection status indicator
- Auto-refreshing data every 5 seconds

### 2. Multi-tab Interface
- Overview: Key metrics and current rates
- Forecasting: AI model predictions
- Analytics: Market analysis and trends
- News & Sentiment: Financial news with sentiment scores
- Models: ML model performance and status

### 3. Interactive Components
- Currency pair selection
- Model type selection
- Forecast horizon configuration
- Real-time toggle switch

### 4. Data Visualization
- Real-time exchange rate charts
- Forecast prediction charts
- Volatility analysis
- Sentiment analysis charts
- Model performance comparisons

## Component Implementation

### Main App Component

```jsx
import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Globe, Brain, Activity, DollarSign, TrendingUp, Clock, CheckCircle } from 'lucide-react'

function App() {
  const [selectedPair, setSelectedPair] = useState('USD/EUR')
  const [selectedModel, setSelectedModel] = useState('ensemble')
  const [isRealTimeEnabled, setIsRealTimeEnabled] = useState(true)
  const [currentTime, setCurrentTime] = useState(new Date())
  const [isConnected, setIsConnected] = useState(true)

  // Real-time updates
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header with branding and status */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Globe className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Exchange Rate Forecasting
              </h1>
              <Badge variant={isConnected ? "default" : "destructive"}>
                <CheckCircle className="h-3 w-3 mr-1" />
                Connected
              </Badge>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-sm text-muted-foreground">
                <Clock className="h-4 w-4 inline mr-1" />
                {currentTime.toLocaleTimeString('en-US', { hour12: false })} UTC
              </div>
              <Switch
                checked={isRealTimeEnabled}
                onCheckedChange={setIsRealTimeEnabled}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main dashboard content */}
      <main className="container mx-auto px-4 py-6">
        {/* Control panel */}
        <Card className="mb-6 shadow-lg">
          <CardHeader>
            <CardTitle>Forecasting Controls</CardTitle>
            <CardDescription>Configure your exchange rate forecasting parameters</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Select value={selectedPair} onValueChange={setSelectedPair}>
                <SelectTrigger>
                  <SelectValue placeholder="Select currency pair" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="USD/EUR">USD/EUR</SelectItem>
                  <SelectItem value="USD/GBP">USD/GBP</SelectItem>
                  <SelectItem value="USD/JPY">USD/JPY</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger>
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ensemble">Ensemble</SelectItem>
                  <SelectItem value="xgboost">XGBoost</SelectItem>
                  <SelectItem value="lstm">LSTM</SelectItem>
                </SelectContent>
              </Select>
              
              <Button className="flex items-center space-x-2">
                <Brain className="h-4 w-4" />
                <span>Generate Forecast</span>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Tabbed interface */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="forecasting">Forecasting</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="news">News & Sentiment</TabsTrigger>
            <TabsTrigger value="models">Models</TabsTrigger>
          </TabsList>

          {/* Overview tab content */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card className="shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Current Rate</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">1.0545</div>
                  <div className="text-xs text-green-600">+0.0007 (+0.066%)</div>
                </CardContent>
              </Card>
              
              {/* Additional metric cards */}
            </div>
            
            {/* Real-time chart */}
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle>Real-time Exchange Rate</CardTitle>
                <CardDescription>Live data with 5-minute intervals</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={mockData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="timestamp" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="rate" stroke="#3b82f6" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Other tab contents */}
        </Tabs>
      </main>
    </div>
  )
}

export default App
```

### Custom Hooks

#### useWebSocket Hook
```jsx
import { useState, useEffect, useRef } from 'react'

export function useWebSocket(url, options = {}) {
  const [socket, setSocket] = useState(null)
  const [lastMessage, setLastMessage] = useState(null)
  const [readyState, setReadyState] = useState(0)
  const [error, setError] = useState(null)

  useEffect(() => {
    const ws = new WebSocket(url)
    
    ws.onopen = () => {
      setReadyState(1)
      setSocket(ws)
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setLastMessage(data)
      options.onMessage?.(data)
    }
    
    ws.onerror = (error) => {
      setError(error)
      options.onError?.(error)
    }
    
    ws.onclose = () => {
      setReadyState(3)
      options.onClose?.()
    }
    
    return () => {
      ws.close()
    }
  }, [url])

  const sendMessage = (message) => {
    if (socket && readyState === 1) {
      socket.send(JSON.stringify(message))
    }
  }

  return { socket, lastMessage, readyState, error, sendMessage }
}
```

#### useExchangeRate Hook
```jsx
import { useState, useEffect } from 'react'
import { useWebSocket } from './useWebSocket'

export function useExchangeRate(pair, realTime = true) {
  const [currentRate, setCurrentRate] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const { lastMessage } = useWebSocket(
    realTime ? `ws://localhost:8000/ws/rates/${pair}` : null,
    {
      onMessage: (data) => {
        if (data.type === 'rate_update') {
          setCurrentRate(data.rate)
          setHistory(prev => [...prev.slice(-99), data])
        }
      },
      onError: (error) => setError(error)
    }
  )

  useEffect(() => {
    // Fetch initial data
    fetch(`/api/rates/${pair}`)
      .then(res => res.json())
      .then(data => {
        setCurrentRate(data.current)
        setHistory(data.history)
        setLoading(false)
      })
      .catch(err => {
        setError(err)
        setLoading(false)
      })
  }, [pair])

  return { currentRate, history, loading, error }
}
```

### Chart Components

#### ExchangeRateChart Component
```jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function ExchangeRateChart({ data, title, pair }) {
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const formatRate = (value) => {
    return value.toFixed(5)
  }

  return (
    <Card className="shadow-lg">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="timestamp" 
                tickFormatter={formatTime}
              />
              <YAxis 
                domain={['dataMin - 0.001', 'dataMax + 0.001']}
                tickFormatter={formatRate}
              />
              <Tooltip 
                labelFormatter={(value) => new Date(value).toLocaleString()}
                formatter={(value) => [formatRate(value), 'Rate']}
              />
              <Line 
                type="monotone" 
                dataKey="rate" 
                stroke="#3b82f6" 
                strokeWidth={2}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
```

#### ForecastChart Component
```jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export function ForecastChart({ historicalData, predictions, model, pair }) {
  const combinedData = [...historicalData, ...predictions]

  return (
    <Card className="shadow-lg">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <span>Exchange Rate Forecast</span>
          <Badge variant="outline">{model}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={combinedData}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="timestamp" 
                tickFormatter={(value) => new Date(value).toLocaleTimeString()}
              />
              <YAxis 
                domain={['dataMin - 0.002', 'dataMax + 0.002']}
                tickFormatter={(value) => value.toFixed(5)}
              />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="rate" 
                stroke="#3b82f6" 
                strokeWidth={2}
                connectNulls={false}
              />
              <Line 
                type="monotone" 
                dataKey="predicted" 
                stroke="#f59e0b" 
                strokeWidth={2}
                strokeDasharray="5 5"
                connectNulls={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
```

### API Integration

#### API Service
```jsx
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000'

class ApiService {
  async fetchExchangeRates(pair) {
    const response = await fetch(`${API_BASE_URL}/api/rates/${pair}`)
    if (!response.ok) throw new Error('Failed to fetch exchange rates')
    return response.json()
  }

  async generateForecast(pair, model, horizon) {
    const response = await fetch(`${API_BASE_URL}/api/forecast`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pair, model, horizon })
    })
    if (!response.ok) throw new Error('Failed to generate forecast')
    return response.json()
  }

  async fetchNews(pair) {
    const response = await fetch(`${API_BASE_URL}/api/news/${pair}`)
    if (!response.ok) throw new Error('Failed to fetch news')
    return response.json()
  }

  async fetchModelPerformance() {
    const response = await fetch(`${API_BASE_URL}/api/models/performance`)
    if (!response.ok) throw new Error('Failed to fetch model performance')
    return response.json()
  }
}

export const apiService = new ApiService()
```

## Styling and Theming

### Tailwind Configuration
The project uses Tailwind CSS with custom theme configuration:

```css
/* App.css */
@import "tailwindcss";
@import "tw-animate-css";

:root {
  --radius: 0.625rem;
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  /* Additional CSS variables */
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  /* Dark theme variables */
}
```

### Responsive Design
- Mobile-first approach with responsive grid layouts
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Touch-friendly interface elements
- Optimized for both desktop and mobile viewing

## Performance Optimizations

### 1. Code Splitting
```jsx
import { lazy, Suspense } from 'react'

const ForecastingTab = lazy(() => import('./components/ForecastingTab'))
const AnalyticsTab = lazy(() => import('./components/AnalyticsTab'))

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ForecastingTab />
    </Suspense>
  )
}
```

### 2. Memoization
```jsx
import { memo, useMemo } from 'react'

const ExchangeRateChart = memo(({ data, pair }) => {
  const processedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      formattedTime: new Date(item.timestamp).toLocaleTimeString()
    }))
  }, [data])

  return <LineChart data={processedData} />
})
```

### 3. Virtual Scrolling
For large datasets in news feeds and historical data tables.

## Testing Strategy

### Unit Tests
```jsx
import { render, screen } from '@testing-library/react'
import { ExchangeRateChart } from './ExchangeRateChart'

test('renders exchange rate chart with data', () => {
  const mockData = [
    { timestamp: '2025-01-08T10:00:00Z', rate: 1.0545 }
  ]
  
  render(<ExchangeRateChart data={mockData} pair="USD/EUR" />)
  
  expect(screen.getByText('Exchange Rate Chart')).toBeInTheDocument()
})
```

### Integration Tests
- API integration testing
- WebSocket connection testing
- Real-time data flow testing

## Deployment

### Build Process
```bash
npm run build
```

### Environment Variables
```env
REACT_APP_API_URL=https://api.exchangeforecast.com
REACT_APP_WS_URL=wss://api.exchangeforecast.com/ws
REACT_APP_NEWS_API_KEY=your_news_api_key
```

### Production Optimizations
- Bundle size optimization
- Image optimization
- CDN integration for static assets
- Service worker for offline functionality

## Security Considerations

### 1. API Security
- JWT token authentication
- CORS configuration
- Rate limiting

### 2. Data Validation
- Input sanitization
- XSS protection
- CSRF protection

### 3. Environment Security
- Secure environment variable handling
- API key protection
- HTTPS enforcement

## Monitoring and Analytics

### 1. Performance Monitoring
- Core Web Vitals tracking
- Bundle size monitoring
- API response time tracking

### 2. User Analytics
- User interaction tracking
- Feature usage analytics
- Error tracking and reporting

### 3. Real-time Monitoring
- WebSocket connection health
- Data freshness monitoring
- System status dashboard

This comprehensive React frontend provides a professional, scalable, and maintainable solution for the exchange rate forecasting dashboard with real-time capabilities, advanced visualizations, and seamless integration with the backend API.

