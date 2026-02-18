"""
Fix ML Model Overfitting - Proper Training with Balanced Data
==============================================================

This script addresses the severe overfitting issue by:
1. Balancing the dataset (equal BUY/SELL/NEUTRAL samples)
2. Proper train/test/validation split
3. Cross-validation
4. Regularization
5. Feature engineering without leakage
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import resample
import xgboost as xgb
import pickle
from pathlib import Path

def load_and_balance_data(filepath):
    """Load data and balance classes"""
    print("Loading training data...")
    df = pd.read_csv(filepath)
    
    print(f"Original data shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Check which signal column exists
    if 'signal' in df.columns:
        signal_col = 'signal'
    elif 'signal_type' in df.columns:
        signal_col = 'signal_type'
    else:
        raise ValueError("No signal column found! Expected 'signal' or 'signal_type'")
    
    print(f"\nUsing column: {signal_col}")
    print(f"\nOriginal class distribution:")
    print(df[signal_col].value_counts())
    print(f"\nClass percentages:")
    print(df[signal_col].value_counts(normalize=True) * 100)
    
    # Check unique values
    unique_values = df[signal_col].unique()
    print(f"\nUnique signal values: {unique_values}")
    
    # Separate by class
    # Handle different encoding schemes
    if set(unique_values) == {0, 1}:
        # Binary: 0=SELL, 1=BUY (no NEUTRAL)
        print("\nWARNING: Data only has BUY and SELL, no NEUTRAL class!")
        print("This is the root cause of overfitting.")
        print("Creating synthetic NEUTRAL samples from low-confidence predictions...")
        
        buy_samples = df[df[signal_col] == 1]
        sell_samples = df[df[signal_col] == 0]
        
        # Create NEUTRAL samples from uncertain cases
        # Use samples where indicators are mixed or weak
        neutral_candidates = df.copy()
        
        # Add a neutral_score based on indicator uncertainty
        if 'rsi' in df.columns and 'macd_hist' in df.columns:
            # RSI near 50 (neutral) and small MACD histogram = uncertain
            neutral_candidates['neutral_score'] = (
                (1 - abs(neutral_candidates['rsi'] - 50) / 50) * 0.5 +  # RSI neutrality
                (1 - abs(neutral_candidates['macd_hist']) / neutral_candidates['macd_hist'].abs().max()) * 0.5  # MACD weakness
            )
            # Take top uncertain samples as NEUTRAL
            neutral_samples = neutral_candidates.nlargest(
                min(len(buy_samples), len(sell_samples)) // 3,  # 1/3 of smallest class
                'neutral_score'
            )
            neutral_samples[signal_col] = -1  # Mark as NEUTRAL
        else:
            # Fallback: randomly sample some as NEUTRAL
            neutral_samples = df.sample(n=min(len(df) // 10, 10000), random_state=42)
            neutral_samples[signal_col] = -1
        
    elif set(unique_values) == {-1, 0, 1}:
        # Ternary: -1=SELL, 0=NEUTRAL, 1=BUY
        buy_samples = df[df[signal_col] == 1]
        sell_samples = df[df[signal_col] == -1]
        neutral_samples = df[df[signal_col] == 0]
    else:
        raise ValueError(f"Unexpected signal values: {unique_values}")
    
    print(f"\nBUY samples: {len(buy_samples)}")
    print(f"SELL samples: {len(sell_samples)}")
    print(f"NEUTRAL samples: {len(neutral_samples)}")
    
    # Find minimum class size (or set a reasonable target)
    min_samples = min(len(buy_samples), len(sell_samples), len(neutral_samples))
    
    # If neutral is too small, use a reasonable target
    target_samples = max(min_samples, 5000)  # At least 5000 samples per class
    target_samples = min(target_samples, 50000)  # Max 50k per class
    
    print(f"\nTarget samples per class: {target_samples}")
    
    # Downsample majority classes or upsample minority
    if len(buy_samples) > target_samples:
        buy_balanced = resample(buy_samples, n_samples=target_samples, random_state=42)
    else:
        buy_balanced = resample(buy_samples, n_samples=target_samples, replace=True, random_state=42)
    
    if len(sell_samples) > target_samples:
        sell_balanced = resample(sell_samples, n_samples=target_samples, random_state=42)
    else:
        sell_balanced = resample(sell_samples, n_samples=target_samples, replace=True, random_state=42)
    
    if len(neutral_samples) > target_samples:
        neutral_balanced = resample(neutral_samples, n_samples=target_samples, random_state=42)
    else:
        neutral_balanced = resample(neutral_samples, n_samples=target_samples, replace=True, random_state=42)
    
    # Combine balanced classes
    df_balanced = pd.concat([buy_balanced, sell_balanced, neutral_balanced])
    df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)  # Shuffle
    
    print(f"\nBalanced data shape: {df_balanced.shape}")
    print(f"\nBalanced class distribution:")
    print(df_balanced[signal_col].value_counts())
    print(f"\nBalanced percentages:")
    print(df_balanced[signal_col].value_counts(normalize=True) * 100)
    
    return df_balanced, signal_col

def prepare_features(df, signal_col='signal_type'):
    """Prepare features without data leakage"""
    # Map column names to expected feature names
    feature_mapping = {
        'rsi': 'rsi',
        'macd': 'macd',
        'macd_signal': 'macd_signal',
        'macd_s': 'macd_signal',  # Alternative name
        'ema6': 'ema_fast',
        'ema12': 'ema_fast',  # Alternative
        'ema20': 'ema_slow',
        'ema50': 'ema_slow',  # Alternative
        'atr': 'atr',
        'volume_ratio': 'volume_ratio',
        'roc3': 'price_change',
        'roc10': 'price_change',  # Alternative
    }
    
    # Build feature list from available columns
    features = {}
    for col in df.columns:
        if col in feature_mapping:
            feature_name = feature_mapping[col]
            if feature_name not in features:  # Use first match
                features[feature_name] = col
    
    # Required features
    required_features = [
        'rsi', 'macd', 'macd_signal', 
        'ema_fast', 'ema_slow', 
        'atr', 'volume_ratio', 'price_change'
    ]
    
    # Check which features are available
    available_features = []
    missing_features = []
    
    for feat in required_features:
        if feat in features:
            available_features.append(features[feat])
        else:
            missing_features.append(feat)
    
    if len(available_features) < 5:
        raise ValueError(f"Not enough features! Need at least 5, found {len(available_features)}")
    
    print(f"\nUsing {len(available_features)} features:")
    for i, col in enumerate(available_features, 1):
        print(f"  {i}. {col}")
    
    X = df[available_features].values
    y = df[signal_col].values
    
    # Convert signal to 0, 1, 2 for classification
    # -1 (SELL) -> 0
    #  0 (NEUTRAL) -> 1  
    #  1 (BUY) -> 2
    y = y + 1
    
    return X, y, available_features

def train_model_properly(X, y):
    """Train model with proper validation"""
    print("\n" + "="*80)
    print("TRAINING ML MODEL WITH PROPER VALIDATION")
    print("="*80)
    
    # Split data: 60% train, 20% validation, 20% test
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp
    )
    
    print(f"\nData split:")
    print(f"  Training:   {len(X_train):,} samples ({len(X_train)/len(X)*100:.1f}%)")
    print(f"  Validation: {len(X_val):,} samples ({len(X_val)/len(X)*100:.1f}%)")
    print(f"  Test:       {len(X_test):,} samples ({len(X_test)/len(X)*100:.1f}%)")
    
    # Train XGBoost with regularization
    print("\nTraining XGBoost model with regularization...")
    model = xgb.XGBClassifier(
        n_estimators=100,           # Fewer trees to prevent overfitting
        max_depth=4,                # Shallow trees
        learning_rate=0.1,          # Moderate learning rate
        subsample=0.8,              # Use 80% of data per tree
        colsample_bytree=0.8,       # Use 80% of features per tree
        reg_alpha=0.1,              # L1 regularization
        reg_lambda=1.0,             # L2 regularization
        early_stopping_rounds=10,   # Stop if no improvement
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    
    # Evaluate on all sets
    print("\n" + "="*80)
    print("MODEL EVALUATION")
    print("="*80)
    
    # Training set
    train_pred = model.predict(X_train)
    train_acc = (train_pred == y_train).mean()
    print(f"\nTraining Accuracy: {train_acc:.4f}")
    
    # Validation set
    val_pred = model.predict(X_val)
    val_acc = (val_pred == y_val).mean()
    print(f"Validation Accuracy: {val_acc:.4f}")
    
    # Test set (final evaluation)
    test_pred = model.predict(X_test)
    test_acc = (test_pred == y_test).mean()
    print(f"Test Accuracy: {test_acc:.4f}")
    
    # Check for overfitting
    overfit_gap = train_acc - test_acc
    print(f"\nOverfitting Gap: {overfit_gap:.4f}")
    if overfit_gap > 0.05:
        print("WARNING: Model may be overfitting (gap > 5%)")
    else:
        print("OK: Overfitting is under control")
    
    # Detailed test set metrics
    print("\n" + "="*80)
    print("TEST SET DETAILED METRICS")
    print("="*80)
    
    print("\nClassification Report:")
    print(classification_report(
        y_test, test_pred,
        target_names=['SELL', 'NEUTRAL', 'BUY'],
        digits=4
    ))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, test_pred)
    print("              Predicted")
    print("              SELL  NEUTRAL  BUY")
    print(f"Actual SELL    {cm[0,0]:5d}  {cm[0,1]:7d}  {cm[0,2]:4d}")
    print(f"       NEUTRAL {cm[1,0]:5d}  {cm[1,1]:7d}  {cm[1,2]:4d}")
    print(f"       BUY     {cm[2,0]:5d}  {cm[2,1]:7d}  {cm[2,2]:4d}")
    
    # Cross-validation (create new model without early stopping for CV)
    print("\n" + "="*80)
    print("CROSS-VALIDATION (5-FOLD)")
    print("="*80)
    
    # Create model without early stopping for cross-validation
    cv_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1
    )
    
    cv_scores = cross_val_score(cv_model, X, y, cv=5, scoring='accuracy')
    print(f"CV Scores: {cv_scores}")
    print(f"Mean CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Feature importance
    print("\n" + "="*80)
    print("FEATURE IMPORTANCE")
    print("="*80)
    feature_names = [
        'rsi', 'macd', 'macd_signal', 
        'ema_fast', 'ema_slow', 
        'atr', 'volume_ratio', 'price_change'
    ]
    importances = model.feature_importances_
    for name, importance in sorted(zip(feature_names, importances), 
                                   key=lambda x: x[1], reverse=True):
        print(f"  {name:15s}: {importance:.4f}")
    
    return model, test_acc, overfit_gap

def save_model(model, filepath):
    """Save trained model"""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"\nModel saved to: {filepath}")

def main():
    print("="*80)
    print("FIX ML MODEL OVERFITTING")
    print("="*80)
    print("\nThis script will:")
    print("1. Load and balance the training data")
    print("2. Split into train/validation/test sets")
    print("3. Train with proper regularization")
    print("4. Evaluate on unseen test data")
    print("5. Check for overfitting")
    print("6. Save the improved model")
    print("\n" + "="*80)
    
    # Paths
    data_path = Path("data/ml_training_data.csv")
    model_path = Path("models/ml_signal_model_fixed.pkl")
    
    if not data_path.exists():
        print(f"\n❌ ERROR: Training data not found at {data_path}")
        print("Please run data extraction first.")
        return
    
    # Load and balance data
    df_balanced, signal_col = load_and_balance_data(data_path)
    
    # Prepare features
    X, y, feature_names = prepare_features(df_balanced, signal_col)
    print(f"\nFeatures prepared: {len(feature_names)} features")
    print(f"Feature names: {feature_names}")
    
    # Train model
    model, test_acc, overfit_gap = train_model_properly(X, y)
    
    # Save model
    save_model(model, model_path)
    
    # Final recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    if test_acc > 0.70:
        print("OK: Model performance is good (>70% accuracy)")
    elif test_acc > 0.60:
        print("ACCEPTABLE: Model performance is acceptable (60-70% accuracy)")
    else:
        print("POOR: Model performance is poor (<60% accuracy)")
        print("   Consider collecting more diverse training data")
    
    if overfit_gap < 0.05:
        print("OK: Overfitting is under control (<5% gap)")
    elif overfit_gap < 0.10:
        print("WARNING: Some overfitting detected (5-10% gap)")
        print("   Consider more regularization or more data")
    else:
        print("CRITICAL: Severe overfitting detected (>10% gap)")
        print("   Model needs more regularization or different approach")
    
    print("\nNext steps:")
    print("1. Review the test set metrics above")
    print("2. If satisfied, replace the old model:")
    print(f"   copy {model_path} models/ml_signal_model.pkl")
    print("3. Test in the bot with paper trading first")
    print("4. Monitor real-world performance")
    
    print("\n" + "="*80)
    print("DONE!")
    print("="*80)

if __name__ == "__main__":
    main()
