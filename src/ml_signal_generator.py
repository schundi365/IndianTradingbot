"""
ML-Based Signal Generator
Uses XGBoost for trend classification and signal generation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
import pickle
import os

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost not available. Install with: pip install xgboost")


class MLSignalGenerator:
    """
    Machine Learning based signal generator using XGBoost
    Predicts trend direction and generates trading signals
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.model = None
        self.is_trained = False
        self.feature_names = []
        self.model_path = "models/ml_signal_model.pkl"
        
        # Model parameters
        self.params = {
            'objective': 'binary:logistic',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42
        }
        
        # Load existing model if available
        self._load_model()
    
    def extract_features(self, data: Dict) -> np.ndarray:
        """
        Extract ML features from market data
        
        Args:
            data: Dictionary containing OHLCV and indicators
            
        Returns:
            Feature array for ML model
        """
        features = []
        feature_names_debug = []
        
        try:
            self.logger.info("📊 ML FEATURE EXTRACTION - Starting feature extraction")
            
            # Price-based features
            if 'close' in data and len(data['close']) > 0:
                close = data['close']
                current_close = close[-1] if len(close) > 0 else 0
                price_return = (close[-1] - close[-2]) / close[-2] if len(close) > 1 else 0
                volatility = np.std(close[-20:]) if len(close) >= 20 else 0
                
                features.extend([current_close, price_return, volatility])
                feature_names_debug.extend(['close', 'return', 'volatility'])
                
                self.logger.info(f"   💰 Price Features:")
                self.logger.info(f"      Current Close: {current_close:.5f}")
                self.logger.info(f"      Price Return: {price_return:.5f} ({price_return*100:.2f}%)")
                self.logger.info(f"      Volatility (20-period): {volatility:.5f}")
            
            # Technical indicators
            if 'rsi' in data:
                rsi_val = data['rsi']
                features.append(rsi_val)
                feature_names_debug.append('rsi')
                self.logger.info(f"   📈 RSI: {rsi_val:.2f}")
            
            if 'macd' in data and 'macd_signal' in data:
                macd_val = data['macd']
                macd_signal_val = data['macd_signal']
                macd_hist = macd_val - macd_signal_val
                
                features.extend([macd_val, macd_signal_val, macd_hist])
                feature_names_debug.extend(['macd', 'macd_signal', 'macd_histogram'])
                
                self.logger.info(f"   📊 MACD Features:")
                self.logger.info(f"      MACD: {macd_val:.5f}")
                self.logger.info(f"      Signal: {macd_signal_val:.5f}")
                self.logger.info(f"      Histogram: {macd_hist:.5f}")
            
            if 'adx' in data:
                adx_val = data['adx']
                features.append(adx_val)
                feature_names_debug.append('adx')
                self.logger.info(f"   💪 ADX (Trend Strength): {adx_val:.2f}")
            
            if 'atr' in data:
                atr_val = data['atr']
                features.append(atr_val)
                feature_names_debug.append('atr')
                self.logger.info(f"   📏 ATR (Volatility): {atr_val:.5f}")
            
            # Moving averages
            if 'ema_fast' in data and 'ema_slow' in data:
                ema_fast = data['ema_fast']
                ema_slow = data['ema_slow']
                ema_divergence = (ema_fast - ema_slow) / ema_slow
                
                features.extend([ema_fast, ema_slow, ema_divergence])
                feature_names_debug.extend(['ema_fast', 'ema_slow', 'ema_divergence'])
                
                self.logger.info(f"   📉 EMA Features:")
                self.logger.info(f"      Fast EMA: {ema_fast:.5f}")
                self.logger.info(f"      Slow EMA: {ema_slow:.5f}")
                self.logger.info(f"      Divergence: {ema_divergence:.5f} ({ema_divergence*100:.2f}%)")
            
            # Volume features
            if 'volume' in data and len(data['volume']) > 0:
                volume = data['volume']
                current_volume = volume[-1] if len(volume) > 0 else 0
                avg_volume = np.mean(volume[-20:]) if len(volume) >= 20 else 0
                
                features.extend([current_volume, avg_volume])
                feature_names_debug.extend(['volume', 'avg_volume'])
                
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                self.logger.info(f"   📊 Volume Features:")
                self.logger.info(f"      Current Volume: {current_volume:.0f}")
                self.logger.info(f"      Average Volume (20): {avg_volume:.0f}")
                self.logger.info(f"      Volume Ratio: {volume_ratio:.2f}x")
            
            # Bollinger Bands
            if 'bb_upper' in data and 'bb_lower' in data and 'close' in data:
                close_val = data['close'][-1] if len(data['close']) > 0 else 0
                bb_upper = data['bb_upper']
                bb_lower = data['bb_lower']
                bb_position = (close_val - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
                
                features.append(bb_position)
                feature_names_debug.append('bb_position')
                
                self.logger.info(f"   📊 Bollinger Bands:")
                self.logger.info(f"      Upper: {bb_upper:.5f}")
                self.logger.info(f"      Lower: {bb_lower:.5f}")
                self.logger.info(f"      Position: {bb_position:.2f} (0=lower, 0.5=middle, 1=upper)")
            
            feature_array = np.array(features).reshape(1, -1)
            self.logger.info(f"✅ ML FEATURE EXTRACTION - Extracted {len(features)} features successfully")
            
            return feature_array
            
        except Exception as e:
            self.logger.error(f"❌ ML FEATURE EXTRACTION - Error extracting features: {e}")
            return np.zeros((1, 15))  # Return default feature array
    
    def train_model(self, historical_data: pd.DataFrame, labels: np.ndarray):
        """
        Train the XGBoost model on historical data
        
        Args:
            historical_data: DataFrame with features
            labels: Binary labels (1 for buy, 0 for sell)
        """
        if not XGBOOST_AVAILABLE:
            self.logger.error("❌ ML TRAINING - XGBoost not available. Cannot train model.")
            return False
        
        try:
            self.logger.info("=" * 80)
            self.logger.info("🎓 ML MODEL TRAINING - Starting training process")
            self.logger.info("=" * 80)
            
            self.logger.info(f"   📊 Training Data:")
            self.logger.info(f"      Samples: {len(historical_data)}")
            self.logger.info(f"      Features: {len(historical_data.columns)}")
            self.logger.info(f"      Feature Names: {list(historical_data.columns)}")
            
            # Analyze label distribution
            buy_count = np.sum(labels == 1)
            sell_count = np.sum(labels == 0)
            self.logger.info(f"   📈 Label Distribution:")
            self.logger.info(f"      BUY signals: {buy_count} ({buy_count/len(labels)*100:.1f}%)")
            self.logger.info(f"      SELL signals: {sell_count} ({sell_count/len(labels)*100:.1f}%)")
            
            self.logger.info(f"   ⚙️ Model Parameters:")
            for param, value in self.params.items():
                self.logger.info(f"      {param}: {value}")
            
            # Create and train model
            self.logger.info("   🔄 Training XGBoost classifier...")
            self.model = xgb.XGBClassifier(**self.params)
            self.model.fit(historical_data, labels)
            
            self.is_trained = True
            self.feature_names = list(historical_data.columns)
            
            # Log feature importance
            if hasattr(self.model, 'feature_importances_'):
                importance = self.model.feature_importances_
                feature_importance = sorted(zip(self.feature_names, importance), key=lambda x: x[1], reverse=True)
                self.logger.info(f"   🔝 Feature Importance (Top 10):")
                for i, (feat_name, feat_importance) in enumerate(feature_importance[:10], 1):
                    self.logger.info(f"      {i}. {feat_name}: {feat_importance:.4f}")
            
            # Save model
            self._save_model()
            
            self.logger.info("=" * 80)
            self.logger.info("✅ ML MODEL TRAINING - Training complete successfully")
            self.logger.info("=" * 80)
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ML MODEL TRAINING - Error training model: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def predict_signal(self, features: np.ndarray) -> Tuple[str, float]:
        """
        Predict trading signal using trained model
        
        Args:
            features: Feature array
            
        Returns:
            Tuple of (signal, confidence)
            signal: 'BUY', 'SELL', or 'NEUTRAL'
            confidence: Probability score (0-1)
        """
        if not self.is_trained or self.model is None:
            self.logger.warning("⚠️ ML PREDICTION - Model not trained, returning NEUTRAL")
            return 'NEUTRAL', 0.0
        
        try:
            self.logger.info("🤖 ML PREDICTION - Starting signal prediction")
            
            # Get prediction probability
            proba = self.model.predict_proba(features)[0]
            
            # proba[0] is probability of class 0 (SELL), proba[1] is probability of class 1 (BUY)
            sell_prob = proba[0]
            buy_prob = proba[1]
            
            self.logger.info(f"   📊 Model Probabilities:")
            self.logger.info(f"      BUY Probability: {buy_prob:.4f} ({buy_prob*100:.2f}%)")
            self.logger.info(f"      SELL Probability: {sell_prob:.4f} ({sell_prob*100:.2f}%)")
            
            # Generate signal based on probability
            if buy_prob > 0.65:
                signal = 'BUY'
                confidence = buy_prob
                self.logger.info(f"   ✅ ML SIGNAL: {signal} (Confidence: {confidence:.4f})")
                self.logger.info(f"      Reason: BUY probability {buy_prob:.2%} > 65% threshold")
            elif buy_prob < 0.35:
                signal = 'SELL'
                confidence = 1 - buy_prob
                self.logger.info(f"   ✅ ML SIGNAL: {signal} (Confidence: {confidence:.4f})")
                self.logger.info(f"      Reason: BUY probability {buy_prob:.2%} < 35% threshold")
            else:
                signal = 'NEUTRAL'
                confidence = max(buy_prob, 1 - buy_prob)
                self.logger.info(f"   ⚪ ML SIGNAL: {signal} (Confidence: {confidence:.4f})")
                self.logger.info(f"      Reason: BUY probability {buy_prob:.2%} in neutral zone (35%-65%)")
            
            # Log feature importance if available
            try:
                if hasattr(self.model, 'feature_importances_') and len(self.feature_names) > 0:
                    importance = self.model.feature_importances_
                    top_features = sorted(zip(self.feature_names, importance), key=lambda x: x[1], reverse=True)[:5]
                    self.logger.info(f"   🔝 Top 5 Important Features:")
                    for feat_name, feat_importance in top_features:
                        self.logger.info(f"      {feat_name}: {feat_importance:.4f}")
            except Exception as feat_err:
                pass  # Feature importance logging is optional
            
            return signal, confidence
                
        except Exception as e:
            self.logger.error(f"❌ ML PREDICTION - Error predicting signal: {e}")
            return 'NEUTRAL', 0.0
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        if not self.is_trained or self.model is None:
            return {}
        
        try:
            importance = self.model.feature_importances_
            return dict(zip(self.feature_names, importance))
        except Exception as e:
            self.logger.error(f"Error getting feature importance: {e}")
            return {}
    
    def _save_model(self):
        """Save trained model to disk"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'feature_names': self.feature_names,
                'params': self.params,
                'trained_date': datetime.now().isoformat()
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            self.logger.info(f"Model saved to {self.model_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
    
    def _load_model(self):
        """Load trained model from disk"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.model = model_data['model']
                self.feature_names = model_data['feature_names']
                self.params = model_data.get('params', self.params)
                self.is_trained = True
                
                self.logger.info(f"Model loaded from {self.model_path}")
                return True
                
        except Exception as e:
            self.logger.warning(f"Could not load model: {e}")
        
        return False
    
    def update_model(self, new_data: pd.DataFrame, new_labels: np.ndarray):
        """
        Incrementally update model with new data
        
        Args:
            new_data: New feature data
            new_labels: New labels
        """
        if not self.is_trained:
            return self.train_model(new_data, new_labels)
        
        try:
            # Retrain with new data
            self.model.fit(new_data, new_labels)
            self._save_model()
            
            self.logger.info("Model updated with new data")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating model: {e}")
            return False
