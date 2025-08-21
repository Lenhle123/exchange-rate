import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import xgboost as xgb
from datetime import datetime, timedelta
import random
import pickle
import os

class MLForecastingService:
    """Machine Learning service for exchange rate forecasting"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.model_performance = {}
        self.feature_columns = [
            'rate_lag_1', 'rate_lag_2', 'rate_lag_3', 'rate_lag_6', 'rate_lag_12',
            'rate_ma_5', 'rate_ma_10', 'rate_ma_20',
            'volatility_5', 'volatility_10',
            'rsi', 'macd', 'bollinger_position',
            'volume_ma_5', 'volume_ma_10',
            'sentiment_score', 'news_count',
            'hour_of_day', 'day_of_week', 'day_of_month'
        ]
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models"""
        # Random Forest
        self.models['random_forest'] = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # XGBoost
        self.models['xgboost'] = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        
        # Initialize scalers
        for model_name in self.models.keys():
            self.scalers[model_name] = StandardScaler()
        
        # Simulate pre-trained models with performance metrics
        self._simulate_trained_models()
    
    def _simulate_trained_models(self):
        """Simulate pre-trained models with performance metrics"""
        self.model_performance = {
            'ensemble': {
                'accuracy': 0.847,
                'mse': 0.000123,
                'mae': 0.0089,
                'directional_accuracy': 0.723,
                'last_trained': (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                'training_samples': 50000,
                'status': 'active'
            },
            'xgboost': {
                'accuracy': 0.821,
                'mse': 0.000156,
                'mae': 0.0102,
                'directional_accuracy': 0.698,
                'last_trained': (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                'training_samples': 50000,
                'status': 'active'
            },
            'random_forest': {
                'accuracy': 0.798,
                'mse': 0.000189,
                'mae': 0.0115,
                'directional_accuracy': 0.675,
                'last_trained': (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                'training_samples': 50000,
                'status': 'active'
            },
            'lstm': {
                'accuracy': 0.785,
                'mse': 0.000201,
                'mae': 0.0128,
                'directional_accuracy': 0.662,
                'last_trained': (datetime.utcnow() - timedelta(hours=8)).isoformat(),
                'training_samples': 50000,
                'status': 'active'
            }
        }
    
    def generate_features(self, historical_data, sentiment_data=None):
        """Generate features from historical data"""
        if not historical_data or len(historical_data) < 20:
            # Return default features if insufficient data
            return self._get_default_features()
        
        df = pd.DataFrame(historical_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        features = {}
        
        # Price-based features
        rates = df['rate'].values
        features['rate_lag_1'] = rates[-1] if len(rates) > 0 else 1.0
        features['rate_lag_2'] = rates[-2] if len(rates) > 1 else 1.0
        features['rate_lag_3'] = rates[-3] if len(rates) > 2 else 1.0
        features['rate_lag_6'] = rates[-6] if len(rates) > 5 else 1.0
        features['rate_lag_12'] = rates[-12] if len(rates) > 11 else 1.0
        
        # Moving averages
        features['rate_ma_5'] = np.mean(rates[-5:]) if len(rates) >= 5 else rates[-1]
        features['rate_ma_10'] = np.mean(rates[-10:]) if len(rates) >= 10 else rates[-1]
        features['rate_ma_20'] = np.mean(rates[-20:]) if len(rates) >= 20 else rates[-1]
        
        # Volatility features
        if len(rates) >= 5:
            features['volatility_5'] = np.std(rates[-5:])
        else:
            features['volatility_5'] = 0.01
            
        if len(rates) >= 10:
            features['volatility_10'] = np.std(rates[-10:])
        else:
            features['volatility_10'] = 0.01
        
        # Technical indicators
        features['rsi'] = self._calculate_rsi(rates)
        features['macd'] = self._calculate_macd(rates)
        features['bollinger_position'] = self._calculate_bollinger_position(rates)
        
        # Volume features
        if 'volume' in df.columns:
            volumes = df['volume'].values
            features['volume_ma_5'] = np.mean(volumes[-5:]) if len(volumes) >= 5 else volumes[-1]
            features['volume_ma_10'] = np.mean(volumes[-10:]) if len(volumes) >= 10 else volumes[-1]
        else:
            features['volume_ma_5'] = 1000000
            features['volume_ma_10'] = 1000000
        
        # Sentiment features
        if sentiment_data:
            features['sentiment_score'] = sentiment_data.get('score', 0.0)
            features['news_count'] = sentiment_data.get('article_count', 10)
        else:
            features['sentiment_score'] = 0.0
            features['news_count'] = 10
        
        # Time-based features
        last_timestamp = df['timestamp'].iloc[-1]
        features['hour_of_day'] = last_timestamp.hour
        features['day_of_week'] = last_timestamp.weekday()
        features['day_of_month'] = last_timestamp.day
        
        return features
    
    def _get_default_features(self):
        """Get default features when insufficient data is available"""
        return {
            'rate_lag_1': 1.0545,
            'rate_lag_2': 1.0540,
            'rate_lag_3': 1.0535,
            'rate_lag_6': 1.0530,
            'rate_lag_12': 1.0525,
            'rate_ma_5': 1.0540,
            'rate_ma_10': 1.0535,
            'rate_ma_20': 1.0530,
            'volatility_5': 0.01,
            'volatility_10': 0.012,
            'rsi': 50.0,
            'macd': 0.0,
            'bollinger_position': 0.5,
            'volume_ma_5': 1000000,
            'volume_ma_10': 1000000,
            'sentiment_score': 0.0,
            'news_count': 10,
            'hour_of_day': datetime.utcnow().hour,
            'day_of_week': datetime.utcnow().weekday(),
            'day_of_month': datetime.utcnow().day
        }
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices, fast=12, slow=26):
        """Calculate MACD"""
        if len(prices) < slow:
            return 0.0
        
        ema_fast = self._calculate_ema(prices, fast)
        ema_slow = self._calculate_ema(prices, slow)
        
        return ema_fast - ema_slow
    
    def _calculate_ema(self, prices, period):
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return np.mean(prices)
        
        alpha = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        
        return ema
    
    def _calculate_bollinger_position(self, prices, period=20):
        """Calculate position within Bollinger Bands"""
        if len(prices) < period:
            return 0.5
        
        ma = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        
        upper_band = ma + (2 * std)
        lower_band = ma - (2 * std)
        
        current_price = prices[-1]
        
        if upper_band == lower_band:
            return 0.5
        
        position = (current_price - lower_band) / (upper_band - lower_band)
        return max(0, min(1, position))
    
    def predict(self, model_name, features, horizon=24):
        """Generate predictions using specified model"""
        if model_name not in ['ensemble', 'xgboost', 'random_forest', 'lstm']:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Convert features to array
        feature_array = np.array([features.get(col, 0.0) for col in self.feature_columns]).reshape(1, -1)
        
        predictions = []
        current_rate = features.get('rate_lag_1', 1.0545)
        
        for i in range(1, horizon + 1):
            # Simulate prediction based on model type
            if model_name == 'ensemble':
                # Ensemble combines multiple models
                trend = self._simulate_trend_prediction(current_rate, i)
                noise = random.uniform(-0.002, 0.002)
                predicted_rate = current_rate + trend + noise
                confidence = 0.85 * (1 - (i - 1) / horizon * 0.3)
                
            elif model_name == 'xgboost':
                # XGBoost prediction simulation
                trend = self._simulate_xgboost_prediction(current_rate, i, features)
                noise = random.uniform(-0.003, 0.003)
                predicted_rate = current_rate + trend + noise
                confidence = 0.80 * (1 - (i - 1) / horizon * 0.3)
                
            elif model_name == 'random_forest':
                # Random Forest prediction simulation
                trend = self._simulate_rf_prediction(current_rate, i, features)
                noise = random.uniform(-0.004, 0.004)
                predicted_rate = current_rate + trend + noise
                confidence = 0.75 * (1 - (i - 1) / horizon * 0.3)
                
            else:  # lstm
                # LSTM prediction simulation
                trend = self._simulate_lstm_prediction(current_rate, i, features)
                noise = random.uniform(-0.005, 0.005)
                predicted_rate = current_rate + trend + noise
                confidence = 0.70 * (1 - (i - 1) / horizon * 0.3)
            
            # Calculate prediction intervals
            uncertainty = 0.005 * (1 + i / horizon)
            lower_bound = predicted_rate - uncertainty
            upper_bound = predicted_rate + uncertainty
            
            prediction = {
                'timestamp': (datetime.utcnow() + timedelta(hours=i)).isoformat(),
                'predicted': round(predicted_rate, 4),
                'confidence': round(max(0.5, confidence), 3),
                'lower_bound': round(lower_bound, 4),
                'upper_bound': round(upper_bound, 4),
                'trend': 'up' if predicted_rate > current_rate else 'down',
                'volatility': round(uncertainty, 4)
            }
            
            predictions.append(prediction)
            
            # Update current rate for next iteration
            current_rate = predicted_rate
        
        return predictions
    
    def _simulate_trend_prediction(self, current_rate, step):
        """Simulate ensemble trend prediction"""
        # Combine multiple factors
        time_factor = 0.0001 * step
        seasonal_factor = 0.001 * np.sin(2 * np.pi * step / 24)
        momentum_factor = random.uniform(-0.0005, 0.0005)
        
        return time_factor + seasonal_factor + momentum_factor
    
    def _simulate_xgboost_prediction(self, current_rate, step, features):
        """Simulate XGBoost prediction"""
        # XGBoost tends to capture non-linear patterns
        sentiment_impact = features.get('sentiment_score', 0) * 0.002
        volatility_impact = features.get('volatility_5', 0.01) * random.uniform(-0.1, 0.1)
        time_decay = 0.0001 * step * random.uniform(0.8, 1.2)
        
        return sentiment_impact + volatility_impact + time_decay
    
    def _simulate_rf_prediction(self, current_rate, step, features):
        """Simulate Random Forest prediction"""
        # Random Forest provides stable predictions
        ma_trend = (features.get('rate_ma_5', current_rate) - features.get('rate_ma_20', current_rate)) * 0.1
        rsi_impact = (features.get('rsi', 50) - 50) / 1000
        time_factor = 0.0001 * step * random.uniform(0.9, 1.1)
        
        return ma_trend + rsi_impact + time_factor
    
    def _simulate_lstm_prediction(self, current_rate, step, features):
        """Simulate LSTM prediction"""
        # LSTM captures sequential patterns
        sequence_pattern = 0.001 * np.sin(2 * np.pi * step / 12)  # 12-hour cycle
        momentum = (features.get('rate_lag_1', current_rate) - features.get('rate_lag_3', current_rate)) * 0.5
        noise = random.uniform(-0.001, 0.001)
        
        return sequence_pattern + momentum + noise
    
    def get_model_performance(self):
        """Get performance metrics for all models"""
        return self.model_performance
    
    def retrain_model(self, model_name, training_data):
        """Simulate model retraining"""
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Simulate retraining process
        print(f"Retraining {model_name} model...")
        
        # Update performance metrics
        self.model_performance[model_name]['last_trained'] = datetime.utcnow().isoformat()
        self.model_performance[model_name]['training_samples'] = len(training_data) if training_data else 50000
        
        # Simulate slight improvement in metrics
        current_accuracy = self.model_performance[model_name]['accuracy']
        improvement = random.uniform(-0.02, 0.05)
        new_accuracy = max(0.7, min(0.95, current_accuracy + improvement))
        self.model_performance[model_name]['accuracy'] = round(new_accuracy, 3)
        
        return {
            'status': 'completed',
            'model': model_name,
            'new_accuracy': new_accuracy,
            'training_samples': len(training_data) if training_data else 50000,
            'training_time': random.uniform(300, 900)  # 5-15 minutes
        }
    
    def evaluate_model(self, model_name, test_data):
        """Evaluate model performance on test data"""
        if not test_data:
            return self.model_performance.get(model_name, {})
        
        # Simulate evaluation
        predictions = []
        actuals = []
        
        for data_point in test_data:
            # Generate prediction
            features = self.generate_features([data_point])
            pred = self.predict(model_name, features, horizon=1)[0]
            
            predictions.append(pred['predicted'])
            actuals.append(data_point.get('rate', 1.0))
        
        # Calculate metrics
        mse = mean_squared_error(actuals, predictions) if len(actuals) > 1 else 0.001
        mae = mean_absolute_error(actuals, predictions) if len(actuals) > 1 else 0.01
        
        # Calculate directional accuracy
        directional_correct = 0
        for i in range(1, len(predictions)):
            pred_direction = predictions[i] > predictions[i-1]
            actual_direction = actuals[i] > actuals[i-1]
            if pred_direction == actual_direction:
                directional_correct += 1
        
        directional_accuracy = directional_correct / max(1, len(predictions) - 1)
        
        return {
            'mse': round(mse, 6),
            'mae': round(mae, 4),
            'directional_accuracy': round(directional_accuracy, 3),
            'test_samples': len(test_data)
        }

# Global instance
ml_service = MLForecastingService()

