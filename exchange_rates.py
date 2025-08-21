from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random

exchange_bp = Blueprint('exchange', __name__)

# Sample exchange rate data
SUPPORTED_PAIRS = ['USD/EUR', 'USD/GBP', 'USD/JPY', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY']

@exchange_bp.route('/exchange/pairs')
def get_supported_pairs():
    """Get list of supported currency pairs"""
    return jsonify({
        'pairs': SUPPORTED_PAIRS,
        'count': len(SUPPORTED_PAIRS)
    })

@exchange_bp.route('/exchange/<pair>/history')
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

@exchange_bp.route('/exchange/<pair>/live')
def get_live_rate(pair):
    """Get live exchange rate with real-time updates"""
    if pair not in SUPPORTED_PAIRS:
        return jsonify({'error': 'Unsupported currency pair'}), 400
    
    # Simulate live rate
    base_rates = {
        'USD/EUR': 1.0545,
        'USD/GBP': 0.7823,
        'USD/JPY': 149.85,
        'EUR/GBP': 0.8412,
        'EUR/JPY': 142.15,
        'GBP/JPY': 191.58
    }
    
    base_rate = base_rates.get(pair, 1.0000)
    current_rate = base_rate + random.uniform(-0.01, 0.01)
    change = random.uniform(-0.005, 0.005)
    
    return jsonify({
        'pair': pair,
        'rate': round(current_rate, 4),
        'change': round(change, 4),
        'change_percent': round((change / current_rate) * 100, 3),
        'timestamp': datetime.utcnow().isoformat(),
        'bid': round(current_rate - 0.0002, 4),
        'ask': round(current_rate + 0.0002, 4),
        'spread': 0.0004,
        'volume_24h': random.randint(50000000, 200000000)
    })

