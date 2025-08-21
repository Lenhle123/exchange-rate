import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from src.models.user import db
from src.routes.user import user_bp
import threading
import time
import random
from datetime import datetime, timedelta
import json

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'exchange-forecast-secret-key-2025'

# Enable CORS for all routes
CORS(app, origins="*")

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Global variables for real-time data
current_rates = {
    'USD/EUR': {'rate': 1.0545, 'change': 0.0007, 'timestamp': datetime.utcnow().isoformat()},
    'USD/GBP': {'rate': 0.7823, 'change': -0.0012, 'timestamp': datetime.utcnow().isoformat()},
    'USD/JPY': {'rate': 149.85, 'change': 0.45, 'timestamp': datetime.utcnow().isoformat()},
    'EUR/GBP': {'rate': 0.8412, 'change': 0.0023, 'timestamp': datetime.utcnow().isoformat()},
}

# Real-time data simulation
def simulate_rate_updates():
    """Simulate real-time exchange rate updates"""
    while True:
        try:
            for pair in current_rates:
                # Simulate small random changes
                current_rate = current_rates[pair]['rate']
                change = random.uniform(-0.005, 0.005)
                new_rate = current_rate + change
                
                current_rates[pair] = {
                    'rate': round(new_rate, 4),
                    'change': round(change, 4),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Emit to all connected clients
                socketio.emit('rate_update', {
                    'pair': pair,
                    'data': current_rates[pair]
                })
            
            time.sleep(5)  # Update every 5 seconds
        except Exception as e:
            print(f"Error in rate simulation: {e}")
            time.sleep(10)

# Start background thread for rate updates
rate_thread = threading.Thread(target=simulate_rate_updates, daemon=True)
rate_thread.start()

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected to Exchange Rate Server'})
    # Send current rates to new client
    emit('initial_rates', current_rates)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('subscribe_pair')
def handle_subscribe(data):
    pair = data.get('pair')
    if pair in current_rates:
        emit('rate_update', {
            'pair': pair,
            'data': current_rates[pair]
        })

# API Routes
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'api': 'running',
            'websocket': 'running',
            'database': 'connected'
        }
    })

@app.route('/api/rates')
def get_all_rates():
    return jsonify({
        'rates': current_rates,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/rates/<pair>')
def get_rate(pair):
    if pair in current_rates:
        # Generate some historical data
        history = []
        base_rate = current_rates[pair]['rate']
        for i in range(20):
            history.append({
                'rate': round(base_rate + random.uniform(-0.01, 0.01), 4),
                'timestamp': (datetime.utcnow() - timedelta(minutes=i*5)).isoformat()
            })
        
        return jsonify({
            'pair': pair,
            'current': current_rates[pair],
            'history': history[::-1],  # Reverse to get chronological order
            'statistics': {
                'min': round(min(h['rate'] for h in history), 4),
                'max': round(max(h['rate'] for h in history), 4),
                'avg': round(sum(h['rate'] for h in history) / len(history), 4),
                'volatility': round(random.uniform(0.005, 0.02), 4)
            }
        })
    else:
        return jsonify({'error': 'Currency pair not found'}), 404

@app.route('/api/exchange/<pair>/history')
def get_historical_data(pair):
    """Get historical exchange rate data"""
    period = request.args.get('period', '24h')
    limit = int(request.args.get('limit', 100))
    
    # Generate historical data based on period
    if period == '1h':
        intervals = 12  # 5-minute intervals
        delta_minutes = 5
    elif period == '24h':
        intervals = 288  # 5-minute intervals
        delta_minutes = 5
    elif period == '7d':
        intervals = 168  # hourly intervals
        delta_minutes = 60
    elif period == '30d':
        intervals = 720  # hourly intervals
        delta_minutes = 60
    else:
        intervals = 100
        delta_minutes = 5
    
    # Limit the number of data points
    intervals = min(intervals, limit)
    
    # Base rate for the pair
    base_rates = {
        'USD/EUR': 1.0545,
        'USD/GBP': 0.7823,
        'USD/JPY': 149.85,
        'EUR/GBP': 0.8412,
        'EUR/JPY': 142.15,
        'GBP/JPY': 191.58
    }
    
    base_rate = base_rates.get(pair, 1.0000)
    
    # Generate historical data
    history = []
    for i in range(intervals):
        timestamp = datetime.utcnow() - timedelta(minutes=i * delta_minutes)
        # Add some realistic variation
        variation = random.uniform(-0.02, 0.02)
        rate = base_rate + variation
        
        history.append({
            'rate': round(rate, 4),
            'volume': random.randint(1000000, 5000000),
            'timestamp': timestamp.isoformat(),
            'high': round(rate + random.uniform(0, 0.01), 4),
            'low': round(rate - random.uniform(0, 0.01), 4),
            'open': round(rate + random.uniform(-0.005, 0.005), 4),
            'close': round(rate, 4)
        })
    
    # Reverse to get chronological order
    history.reverse()
    
    # Calculate statistics
    rates = [h['rate'] for h in history]
    statistics = {
        'min': round(min(rates), 4),
        'max': round(max(rates), 4),
        'avg': round(sum(rates) / len(rates), 4),
        'volatility': round(random.uniform(0.005, 0.025), 4),
        'volume_avg': sum(h['volume'] for h in history) // len(history)
    }
    
    return jsonify({
        'pair': pair,
        'period': period,
        'data': history,
        'statistics': statistics,
        'count': len(history)
    })

@app.route('/api/forecast', methods=['POST'])
def generate_forecast():
    data = request.get_json()
    pair = data.get('pair', 'USD/EUR')
    model = data.get('model', 'ensemble')
    horizon = data.get('horizon', 24)
    
    # Simulate ML prediction
    current_rate = current_rates.get(pair, {'rate': 1.0545})['rate']
    predictions = []
    
    for i in range(1, min(horizon + 1, 25)):  # Limit to 24 hours
        # Simulate prediction with some trend and noise
        trend = random.uniform(-0.001, 0.001) * i
        noise = random.uniform(-0.002, 0.002)
        predicted_rate = current_rate + trend + noise
        
        predictions.append({
            'timestamp': (datetime.utcnow() + timedelta(hours=i)).isoformat(),
            'predicted': round(predicted_rate, 4),
            'confidence': round(random.uniform(0.75, 0.95), 3),
            'lower_bound': round(predicted_rate - 0.005, 4),
            'upper_bound': round(predicted_rate + 0.005, 4)
        })
    
    return jsonify({
        'pair': pair,
        'model': model,
        'horizon': horizon,
        'predictions': predictions,
        'model_info': {
            'accuracy': round(random.uniform(0.80, 0.90), 3),
            'last_trained': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            'features_used': ['price_history', 'volume', 'news_sentiment', 'technical_indicators']
        }
    })

@app.route('/api/news/<pair>')
def get_news(pair):
    # Simulate news articles
    sample_news = [
        {
            'id': 'news_1',
            'title': f'Federal Reserve Signals Policy Changes Affecting {pair}',
            'content': 'The Federal Reserve indicated potential monetary policy adjustments that could impact currency markets...',
            'source': 'Financial Times',
            'url': 'https://example.com/news/1',
            'timestamp': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            'sentiment': {
                'score': random.uniform(-0.3, 0.3),
                'label': 'neutral',
                'confidence': round(random.uniform(0.7, 0.9), 2)
            },
            'relevance': {
                'score': round(random.uniform(0.8, 1.0), 2),
                'keywords': ['federal_reserve', 'monetary_policy', 'interest_rates']
            },
            'impact': 'high'
        },
        {
            'id': 'news_2',
            'title': f'Economic Indicators Show Strength in {pair.split("/")[0]} Economy',
            'content': 'Recent economic data suggests continued growth in the domestic economy...',
            'source': 'Reuters',
            'url': 'https://example.com/news/2',
            'timestamp': (datetime.utcnow() - timedelta(hours=3)).isoformat(),
            'sentiment': {
                'score': random.uniform(0.1, 0.5),
                'label': 'positive',
                'confidence': round(random.uniform(0.7, 0.9), 2)
            },
            'relevance': {
                'score': round(random.uniform(0.6, 0.9), 2),
                'keywords': ['economic_growth', 'gdp', 'employment']
            },
            'impact': 'medium'
        }
    ]
    
    return jsonify({
        'pair': pair,
        'articles': sample_news,
        'sentiment_summary': {
            'overall_sentiment': round(random.uniform(-0.2, 0.2), 3),
            'positive_count': random.randint(15, 25),
            'neutral_count': random.randint(20, 30),
            'negative_count': random.randint(10, 20),
            'trending_topics': ['fed_policy', 'inflation', 'gdp_growth']
        }
    })

@app.route('/api/models/performance')
def get_model_performance():
    models = [
        {
            'name': 'ensemble',
            'type': 'ensemble',
            'accuracy': round(random.uniform(0.82, 0.88), 3),
            'mse': round(random.uniform(0.0001, 0.0003), 6),
            'directional_accuracy': round(random.uniform(0.70, 0.80), 3),
            'last_trained': (datetime.utcnow() - timedelta(hours=6)).isoformat(),
            'training_data_size': random.randint(45000, 55000),
            'status': 'active'
        },
        {
            'name': 'xgboost',
            'type': 'gradient_boosting',
            'accuracy': round(random.uniform(0.78, 0.85), 3),
            'mse': round(random.uniform(0.0002, 0.0004), 6),
            'directional_accuracy': round(random.uniform(0.65, 0.75), 3),
            'last_trained': (datetime.utcnow() - timedelta(hours=6)).isoformat(),
            'training_data_size': random.randint(45000, 55000),
            'status': 'active'
        },
        {
            'name': 'lstm',
            'type': 'deep_learning',
            'accuracy': round(random.uniform(0.75, 0.82), 3),
            'mse': round(random.uniform(0.0003, 0.0005), 6),
            'directional_accuracy': round(random.uniform(0.68, 0.78), 3),
            'last_trained': (datetime.utcnow() - timedelta(hours=6)).isoformat(),
            'training_data_size': random.randint(45000, 55000),
            'status': 'active'
        }
    ]
    
    return jsonify({
        'models': models,
        'performance_comparison': {
            'best_accuracy': 'ensemble',
            'best_mse': 'ensemble',
            'best_directional': 'ensemble'
        }
    })

# Serve React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'message': 'Exchange Rate Forecasting API',
                'version': '1.0.0',
                'endpoints': {
                    'health': '/api/health',
                    'rates': '/api/rates',
                    'forecast': '/api/forecast',
                    'news': '/api/news/<pair>',
                    'models': '/api/models/performance'
                }
            })

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

