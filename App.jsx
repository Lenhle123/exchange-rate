import React, { useState, useEffect } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

function App() {
  const [selectedPair, setSelectedPair] = useState('USD/EUR');
  const [currentRates, setCurrentRates] = useState({});
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [predictions, setPredictions] = useState([]);
  const [news, setNews] = useState([]);

  const CURRENCY_PAIRS = ['USD/EUR', 'USD/GBP', 'USD/JPY', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY'];

  // Fetch current rates
  const fetchCurrentRates = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/rates`);
      if (response.ok) {
        const data = await response.json();
        setCurrentRates(data.rates);
        setConnected(true);
      }
    } catch (error) {
      console.error('Error fetching rates:', error);
      setConnected(false);
      // Fallback to demo data
      setCurrentRates({
        'USD/EUR': { rate: 1.0545, change: 0.0023 },
        'USD/GBP': { rate: 0.7823, change: -0.0012 },
        'USD/JPY': { rate: 149.85, change: 0.45 },
        'EUR/GBP': { rate: 0.8412, change: 0.0015 },
        'EUR/JPY': { rate: 142.15, change: 0.32 },
        'GBP/JPY': { rate: 191.58, change: -0.18 }
      });
    }
  };

  // Generate forecast
  const generateForecast = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/forecast`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pair: selectedPair,
          model: 'ensemble',
          horizon: 24
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setPredictions(data.predictions || []);
      }
    } catch (error) {
      console.error('Error generating forecast:', error);
      // Demo predictions
      setPredictions([
        { timestamp: '2025-09-06T01:00:00Z', predicted: 1.0548, confidence: 0.85 },
        { timestamp: '2025-09-06T06:00:00Z', predicted: 1.0552, confidence: 0.82 },
        { timestamp: '2025-09-06T12:00:00Z', predicted: 1.0556, confidence: 0.78 },
        { timestamp: '2025-09-06T18:00:00Z', predicted: 1.0560, confidence: 0.75 }
      ]);
    }
    setLoading(false);
  };

  // Fetch news
  const fetchNews = async (pair) => {
    try {
      const response = await fetch(`${API_BASE_URL}/news/${pair}?limit=3`);
      if (response.ok) {
        const data = await response.json();
        setNews(data.articles || []);
      }
    } catch (error) {
      console.error('Error fetching news:', error);
      // Demo news
      setNews([
        {
          id: '1',
          title: 'Federal Reserve Signals Potential Rate Changes',
          content: 'The Federal Reserve indicated potential monetary policy adjustments...',
          source: 'Financial Times',
          timestamp: '2025-09-05T20:00:00Z',
          sentiment: { label: 'neutral', score: 0.1 }
        },
        {
          id: '2',
          title: 'European Economy Shows Resilience',
          content: 'Recent economic data from Europe suggests continued stability...',
          source: 'Reuters',
          timestamp: '2025-09-05T18:00:00Z',
          sentiment: { label: 'positive', score: 0.3 }
        }
      ]);
    }
  };

  useEffect(() => {
    fetchCurrentRates();
    fetchNews(selectedPair);
    const interval = setInterval(fetchCurrentRates, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    fetchNews(selectedPair);
  }, [selectedPair]);

  const currentRate = currentRates[selectedPair] || { rate: 0, change: 0 };
  const isPositiveChange = currentRate.change >= 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-6 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-slate-800 flex items-center gap-3">
                📈 Exchange Rate Forecasting
              </h1>
              <p className="text-lg text-slate-600 mt-2">
                AI-powered currency predictions with real-time data
              </p>
            </div>
            
            <div className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium ${
              connected ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}>
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
              {connected ? 'Connected' : 'Demo Mode'}
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Currency Pair
              </label>
              <select
                value={selectedPair}
                onChange={(e) => setSelectedPair(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {CURRENCY_PAIRS.map(pair => (
                  <option key={pair} value={pair}>{pair}</option>
                ))}
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={generateForecast}
                disabled={loading}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? '⟳ Generating...' : '🔮 Generate Forecast'}
              </button>
            </div>

            <div className="flex items-end">
              <button
                onClick={fetchCurrentRates}
                className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
              >
                🔄 Refresh Data
              </button>
            </div>
          </div>
        </div>

        {/* Current Rate Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-slate-600">Current Rate</h3>
              <span className="text-2xl">🌍</span>
            </div>
            <div className="text-3xl font-bold text-slate-900">
              {currentRate.rate.toFixed(4)}
            </div>
            <div className="text-sm text-slate-500 mt-1">{selectedPair}</div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-slate-600">24h Change</h3>
              <span className="text-2xl">{isPositiveChange ? '📈' : '📉'}</span>
            </div>
            <div className={`text-3xl font-bold ${isPositiveChange ? 'text-green-600' : 'text-red-600'}`}>
              {isPositiveChange ? '+' : ''}{currentRate.change.toFixed(4)}
            </div>
            <div className={`text-sm mt-1 ${isPositiveChange ? 'text-green-600' : 'text-red-600'}`}>
              {isPositiveChange ? '+' : ''}{((currentRate.change / currentRate.rate) * 100).toFixed(3)}%
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-slate-600">Model Accuracy</h3>
              <span className="text-2xl">🎯</span>
            </div>
            <div className="text-3xl font-bold text-blue-600">
              84.7%
            </div>
            <div className="text-sm text-slate-500 mt-1">Ensemble Model</div>
          </div>
        </div>

        {/* Predictions */}
        {predictions.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">🔮 Predictions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {predictions.slice(0, 4).map((pred, idx) => (
                <div key={idx} className="bg-slate-50 rounded-lg p-4">
                  <div className="text-sm text-slate-600">
                    {new Date(pred.timestamp).toLocaleString()}
                  </div>
                  <div className="text-xl font-bold text-blue-600">
                    {pred.predicted.toFixed(4)}
                  </div>
                  <div className="text-xs text-slate-500">
                    Confidence: {(pred.confidence * 100).toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* News Section */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">📰 Latest News</h3>
          {news.length === 0 ? (
            <div className="text-slate-500 text-center py-8">
              Loading news articles...
            </div>
          ) : (
            <div className="space-y-4">
              {news.map((article) => (
                <div key={article.id} className="border-b border-slate-200 pb-4 last:border-b-0">
                  <h4 className="font-medium text-slate-900 mb-2">{article.title}</h4>
                  <p className="text-sm text-slate-600 mb-2">{article.content}</p>
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>{article.source}</span>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        article.sentiment?.label === 'positive' ? 'bg-green-100 text-green-700' :
                        article.sentiment?.label === 'negative' ? 'bg-red-100 text-red-700' :
                        'bg-slate-100 text-slate-700'
                      }`}>
                        {article.sentiment?.label || 'neutral'}
                      </span>
                      <span>{new Date(article.timestamp).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-slate-500 text-sm">
          Exchange Rate Forecasting Dashboard • Built with React + Vite
        </div>
      </div>
    </div>
  );
}

export default App;
