from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random
import numpy as np

forecast_bp = Blueprint('forecast', __name__)

# Available models
AVAILABLE_MODELS = ['ensemble', 'xgboost', 'lstm', 'random_forest']

@forecast_bp.route('/forecast/models')
def get_available_models():
    """Get list of available forecasting models"""
    return jsonify({
        'models': AVAILABLE_MODELS,
        'default': 'ensemble',
        'descriptions': {
            'ensemble': 'Combines multiple models for best accuracy',
            'xgboost': 'Gradient boosting for high performance',
            'lstm': 'Deep learning for time series patterns',
            'random_forest': 'Ensemble method for stability'
        }
    })

@forecast_bp.route('/forecast/generate', methods=['POST'])
def generate_forecast():
    """Generate exchange rate forecast"""
    data = request.get_json()
    
    pair = data.get('pair', 'USD/EUR')
    model = data.get('model', 'ensemble')
    horizon = int(data.get('horizon', 24))  # hours
    confidence_level = float(data.get('confidence_level', 0.95))
    
    if model not in AVAILABLE_MODELS:
        return jsonify({'error': 'Invalid model specified'}), 400
    
    if horizon > 168:  # Max 1 week
        return jsonify({'error': 'Horizon cannot exceed 168 hours (1 week)'}), 400
    
    # Simulate current rate
    base_rates = {
        'USD/EUR': 1.0545,
        'USD/GBP': 0.7823,
        'USD/JPY': 149.85,
        'EUR/GBP': 0.8412,
        'EUR/JPY': 142.15,
        'GBP/JPY': 191.58
    }
    
    current_rate = base_rates.get(pair, 1.0000)
    
    # Generate predictions
    predictions = []
    for i in range(1, horizon + 1):
        # Simulate realistic prediction with trend and noise
        trend_factor = 0.0001 * i  # Small trend over time
        seasonal_factor = 0.001 * np.sin(2 * np.pi * i / 24)  # Daily seasonality
        noise = random.uniform(-0.002, 0.002)
        
        predicted_rate = current_rate + trend_factor + seasonal_factor + noise
        
        # Model-specific adjustments
        if model == 'ensemble':
            accuracy_boost = 0.95
            confidence_base = 0.85
        elif model == 'xgboost':
            accuracy_boost = 0.90
            confidence_base = 0.80
        elif model == 'lstm':
            accuracy_boost = 0.88
            confidence_base = 0.78
        else:  # random_forest
            accuracy_boost = 0.85
            confidence_base = 0.75
        
        # Calculate confidence (decreases with time)
        confidence = confidence_base * (1 - (i - 1) / horizon * 0.3)
        
        # Calculate prediction intervals
        uncertainty = 0.005 * (1 + i / horizon)
        lower_bound = predicted_rate - uncertainty
        upper_bound = predicted_rate + uncertainty
        
        predictions.append({
            'timestamp': (datetime.utcnow() + timedelta(hours=i)).isoformat(),
            'predicted': round(predicted_rate, 4),
            'confidence': round(confidence, 3),
            'lower_bound': round(lower_bound, 4),
            'upper_bound': round(upper_bound, 4),
            'trend': 'up' if predicted_rate > current_rate else 'down',
            'volatility': round(uncertainty, 4)
        })
    
    # Model performance metrics
    model_info = {
        'accuracy': round(random.uniform(0.75, 0.90), 3),
        'mse': round(random.uniform(0.0001, 0.0005), 6),
        'mae': round(random.uniform(0.005, 0.015), 4),
        'directional_accuracy': round(random.uniform(0.65, 0.85), 3),
        'last_trained': (datetime.utcnow() - timedelta(hours=random.randint(1, 12))).isoformat(),
        'training_data_size': random.randint(40000, 60000),
        'features_used': [
            'price_history',
            'volume',
            'technical_indicators',
            'news_sentiment',
            'economic_indicators'
        ]
    }
    
    return jsonify({
        'pair': pair,
        'model': model,
        'horizon': horizon,
        'confidence_level': confidence_level,
        'predictions': predictions,
        'model_info': model_info,
        'generated_at': datetime.utcnow().isoformat(),
        'summary': {
            'predicted_change': round(predictions[-1]['predicted'] - current_rate, 4),
            'predicted_change_percent': round(((predictions[-1]['predicted'] - current_rate) / current_rate) * 100, 3),
            'average_confidence': round(sum(p['confidence'] for p in predictions) / len(predictions), 3),
            'trend_direction': 'bullish' if predictions[-1]['predicted'] > current_rate else 'bearish'
        }
    })

@forecast_bp.route('/forecast/<pair>/history')
def get_forecast_history(pair):
    """Get historical forecast performance"""
    model = request.args.get('model', 'ensemble')
    limit = int(request.args.get('limit', 50))
    
    # Generate historical forecast data
    forecasts = []
    for i in range(limit):
        forecast_time = datetime.utcnow() - timedelta(hours=i * 6)
        target_time = forecast_time + timedelta(hours=24)
        
        # Simulate historical prediction vs actual
        predicted = 1.0545 + random.uniform(-0.01, 0.01)
        actual = predicted + random.uniform(-0.005, 0.005)  # Close to prediction
        
        accuracy = 1 - abs(predicted - actual) / actual
        
        forecasts.append({
            'forecast_time': forecast_time.isoformat(),
            'target_time': target_time.isoformat(),
            'predicted': round(predicted, 4),
            'actual': round(actual, 4),
            'error': round(abs(predicted - actual), 4),
            'accuracy': round(accuracy, 4),
            'confidence': round(random.uniform(0.7, 0.9), 3),
            'model': model
        })
    
    # Calculate performance summary
    accuracies = [f['accuracy'] for f in forecasts]
    errors = [f['error'] for f in forecasts]
    
    performance_summary = {
        'total_forecasts': len(forecasts),
        'average_accuracy': round(sum(accuracies) / len(accuracies), 4),
        'average_error': round(sum(errors) / len(errors), 4),
        'best_accuracy': round(max(accuracies), 4),
        'worst_accuracy': round(min(accuracies), 4),
        'directional_accuracy': round(random.uniform(0.65, 0.80), 3),
        'model': model
    }
    
    return jsonify({
        'pair': pair,
        'model': model,
        'forecasts': forecasts,
        'performance_summary': performance_summary
    })

@forecast_bp.route('/forecast/backtest', methods=['POST'])
def run_backtest():
    """Run backtesting on historical data"""
    data = request.get_json()
    
    pair = data.get('pair', 'USD/EUR')
    model = data.get('model', 'ensemble')
    start_date = data.get('start_date', (datetime.utcnow() - timedelta(days=30)).isoformat())
    end_date = data.get('end_date', datetime.utcnow().isoformat())
    
    # Simulate backtest results
    test_periods = 50
    results = []
    
    for i in range(test_periods):
        test_date = datetime.fromisoformat(start_date) + timedelta(days=i * 0.6)
        
        predicted = 1.0545 + random.uniform(-0.02, 0.02)
        actual = predicted + random.uniform(-0.01, 0.01)
        
        results.append({
            'date': test_date.isoformat(),
            'predicted': round(predicted, 4),
            'actual': round(actual, 4),
            'error': round(abs(predicted - actual), 4),
            'squared_error': round((predicted - actual) ** 2, 6),
            'direction_correct': (predicted > 1.0545) == (actual > 1.0545)
        })
    
    # Calculate metrics
    errors = [r['error'] for r in results]
    squared_errors = [r['squared_error'] for r in results]
    direction_correct = sum(1 for r in results if r['direction_correct'])
    
    metrics = {
        'mae': round(sum(errors) / len(errors), 4),
        'mse': round(sum(squared_errors) / len(squared_errors), 6),
        'rmse': round(np.sqrt(sum(squared_errors) / len(squared_errors)), 4),
        'directional_accuracy': round(direction_correct / len(results), 3),
        'total_tests': len(results)
    }
    
    return jsonify({
        'pair': pair,
        'model': model,
        'period': {
            'start': start_date,
            'end': end_date
        },
        'results': results,
        'metrics': metrics,
        'backtest_completed_at': datetime.utcnow().isoformat()
    })

