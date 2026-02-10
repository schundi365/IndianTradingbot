"""
Train ML Model for Trading Bot
Trains XGBoost model on prepared trading data
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
import pickle
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import ML libraries
try:
    import xgboost as xgb
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.error("ML libraries not available. Install with: pip install xgboost scikit-learn")


def train_ml_model(data_file='data/training_data_prepared.csv',
                   model_file='models/ml_signal_model.pkl',
                   test_size=0.2,
                   random_state=42):
    """
    Train ML model on prepared data
    
    Args:
        data_file: Path to prepared training data
        model_file: Path to save trained model
        test_size: Fraction of data for testing
        random_state: Random seed for reproducibility
    
    Returns:
        bool: Success status
    """
    if not ML_AVAILABLE:
        logger.error("Cannot train model - ML libraries not installed")
        return False
    
    logger.info("=" * 80)
    logger.info("TRAINING ML MODEL")
    logger.info("=" * 80)
    
    # Load data
    data_path = Path(data_file)
    if not data_path.exists():
        logger.error(f"Data file not found: {data_file}")
        logger.error("Run 2_prepare_training_data.py first!")
        return False
    
    try:
        df = pd.read_csv(data_file)
        logger.info(f"Loaded {len(df)} samples")
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return False
    
    # Check minimum samples
    if len(df) < 50:
        logger.error(f"Insufficient data: {len(df)} samples (minimum 50 required)")
        return False
    
    # Prepare features and target
    # Remove non-feature columns
    exclude_columns = ['timestamp', 'symbol', 'profitable']
    feature_columns = [col for col in df.columns if col not in exclude_columns]
    
    X = df[feature_columns]
    y = df['profitable']
    
    logger.info(f"Features: {len(feature_columns)}")
    logger.info(f"Feature names: {feature_columns}")
    logger.info(f"Target distribution: {y.value_counts().to_dict()}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    logger.info(f"Training samples: {len(X_train)}")
    logger.info(f"Testing samples: {len(X_test)}")
    
    # Train model
    logger.info("\nTraining XGBoost model...")
    
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=random_state,
        eval_metric='logloss'
    )
    
    try:
        model.fit(X_train, y_train)
        logger.info("✅ Model training complete")
    except Exception as e:
        logger.error(f"Error training model: {e}")
        return False
    
    # Evaluate on training set
    y_train_pred = model.predict(X_train)
    train_accuracy = accuracy_score(y_train, y_train_pred)
    logger.info(f"\nTraining Set Performance:")
    logger.info(f"  Accuracy: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
    
    # Evaluate on test set
    y_test_pred = model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    test_precision = precision_score(y_test, y_test_pred, zero_division=0)
    test_recall = recall_score(y_test, y_test_pred, zero_division=0)
    test_f1 = f1_score(y_test, y_test_pred, zero_division=0)
    
    logger.info(f"\nTest Set Performance:")
    logger.info(f"  Accuracy:  {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
    logger.info(f"  Precision: {test_precision:.4f} ({test_precision*100:.2f}%)")
    logger.info(f"  Recall:    {test_recall:.4f} ({test_recall*100:.2f}%)")
    logger.info(f"  F1 Score:  {test_f1:.4f} ({test_f1*100:.2f}%)")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_test_pred)
    logger.info(f"\nConfusion Matrix:")
    logger.info(f"  True Negatives:  {cm[0][0]}")
    logger.info(f"  False Positives: {cm[0][1]}")
    logger.info(f"  False Negatives: {cm[1][0]}")
    logger.info(f"  True Positives:  {cm[1][1]}")
    
    # Cross-validation
    logger.info(f"\nPerforming 5-fold cross-validation...")
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    logger.info(f"  CV Scores: {cv_scores}")
    logger.info(f"  CV Mean:   {cv_scores.mean():.4f} ({cv_scores.mean()*100:.2f}%)")
    logger.info(f"  CV Std:    {cv_scores.std():.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    logger.info(f"\nTop 10 Most Important Features:")
    for idx, row in feature_importance.head(10).iterrows():
        logger.info(f"  {row['feature']}: {row['importance']:.4f}")
    
    # Check for overfitting
    if train_accuracy - test_accuracy > 0.1:
        logger.warning("\n⚠️  WARNING: Possible overfitting detected!")
        logger.warning(f"   Training accuracy ({train_accuracy:.2%}) is much higher than test accuracy ({test_accuracy:.2%})")
        logger.warning("   Consider:")
        logger.warning("   - Collecting more diverse data")
        logger.warning("   - Reducing model complexity")
        logger.warning("   - Using regularization")
    
    # Check if model is good enough
    if test_accuracy < 0.55:
        logger.warning("\n⚠️  WARNING: Model accuracy is low!")
        logger.warning("   Consider:")
        logger.warning("   - Collecting more training data")
        logger.warning("   - Improving data quality")
        logger.warning("   - Feature engineering")
    elif test_accuracy >= 0.70:
        logger.info("\n✅ Model performance is GOOD!")
    elif test_accuracy >= 0.60:
        logger.info("\n✅ Model performance is ACCEPTABLE")
    
    # Save model
    model_path = Path(model_file)
    model_path.parent.mkdir(exist_ok=True)
    
    try:
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"\n✅ Model saved to {model_file}")
    except Exception as e:
        logger.error(f"Error saving model: {e}")
        return False
    
    # Save metadata
    metadata = {
        'trained_date': datetime.now().isoformat(),
        'samples': len(df),
        'features': feature_columns,
        'test_accuracy': float(test_accuracy),
        'test_precision': float(test_precision),
        'test_recall': float(test_recall),
        'test_f1': float(test_f1),
        'cv_mean': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std())
    }
    
    metadata_file = model_file.replace('.pkl', '_metadata.json')
    import json
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"✅ Metadata saved to {metadata_file}")
    
    logger.info("\n" + "=" * 80)
    logger.info("TRAINING COMPLETE")
    logger.info("=" * 80)
    
    return True


if __name__ == '__main__':
    print("=" * 80)
    print("TRAIN ML MODEL")
    print("=" * 80)
    print()
    
    success = train_ml_model()
    
    if success:
        print()
        print("✅ ML model trained successfully!")
        print()
        print("Next steps:")
        print("1. Review model performance metrics above")
        print("2. Run: python ml_training/4_evaluate_model.py")
        print("3. If satisfied, run: python ml_training/5_deploy_model.py")
        print()
    else:
        print()
        print("❌ Failed to train ML model")
        print()
        print("Troubleshooting:")
        print("1. Make sure data/training_data_prepared.csv exists")
        print("2. Run: python ml_training/2_prepare_training_data.py")
        print("3. Install ML libraries: pip install xgboost scikit-learn")
        print()
