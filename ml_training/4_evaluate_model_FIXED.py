"""
Evaluate Trained ML Model
Tests model performance and generates detailed reports
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
import pickle
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import xgboost as xgb
    from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                                 f1_score, confusion_matrix, classification_report)
    import matplotlib.pyplot as plt
    EVAL_AVAILABLE = True
except ImportError:
    EVAL_AVAILABLE = False
    logger.error("Evaluation libraries not available")


def evaluate_model(model_file='models/ml_signal_model.pkl',
                   data_file='data/ml_training_data.csv'):
    """
    Evaluate trained ML model
    
    Args:
        model_file: Path to trained model
        data_file: Path to test data
    
    Returns:
        bool: Success status
    """
    if not EVAL_AVAILABLE:
        logger.error("Cannot evaluate - libraries not installed")
        return False
    
    logger.info("=" * 80)
    logger.info("EVALUATING ML MODEL")
    logger.info("=" * 80)
    
    # Load model
    model_path = Path(model_file)
    if not model_path.exists():
        logger.error(f"Model file not found: {model_file}")
        logger.error("Run 3_train_ml_model.py first!")
        return False
    
    try:
        with open(model_file, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"✅ Model loaded from {model_file}")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False
    
    # Load metadata
    metadata_file = model_file.replace('.pkl', '_metadata.json')
    if Path(metadata_file).exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        logger.info(f"\nModel Metadata:")
        logger.info(f"  Trained: {metadata.get('trained_date', 'Unknown')}")
        logger.info(f"  Samples: {metadata.get('samples', 'Unknown')}")
        logger.info(f"  Test Accuracy: {metadata.get('test_accuracy', 0):.4f}")
    
    # Load test data
    data_path = Path(data_file)
    if not data_path.exists():
        logger.error(f"Data file not found: {data_file}")
        return False
    
    try:
        df = pd.read_csv(data_file)
        logger.info(f"\n✅ Loaded {len(df)} samples for evaluation")
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return False
    
    # Prepare features
    exclude_columns = ['timestamp', 'symbol', 'profitable',
                       'signal_type', 'max_move_up_atr', 'max_move_down_atr']
    feature_columns = [col for col in df.columns if col not in exclude_columns]
    
    X = df[feature_columns]
    y = df['profitable']
    
    # Make predictions
    logger.info("\nMaking predictions...")
    y_pred = model.predict(X)
    y_pred_proba = model.predict_proba(X)[:, 1]  # Probability of profitable trade
    
    # Calculate metrics
    accuracy = accuracy_score(y, y_pred)
    precision = precision_score(y, y_pred, zero_division=0)
    recall = recall_score(y, y_pred, zero_division=0)
    f1 = f1_score(y, y_pred, zero_division=0)
    
    logger.info("\n" + "=" * 80)
    logger.info("MODEL PERFORMANCE METRICS")
    logger.info("=" * 80)
    logger.info(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    logger.info(f"Precision: {precision:.4f} ({precision*100:.2f}%)")
    logger.info(f"Recall:    {recall:.4f} ({recall*100:.2f}%)")
    logger.info(f"F1 Score:  {f1:.4f} ({f1*100:.2f}%)")
    
    # Confusion matrix
    cm = confusion_matrix(y, y_pred)
    logger.info("\n" + "=" * 80)
    logger.info("CONFUSION MATRIX")
    logger.info("=" * 80)
    logger.info(f"                 Predicted Negative  Predicted Positive")
    logger.info(f"Actual Negative       {cm[0][0]:6d}              {cm[0][1]:6d}")
    logger.info(f"Actual Positive       {cm[1][0]:6d}              {cm[1][1]:6d}")
    
    # Calculate additional metrics
    tn, fp, fn, tp = cm.ravel()
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0
    
    logger.info("\n" + "=" * 80)
    logger.info("DETAILED METRICS")
    logger.info("=" * 80)
    logger.info(f"True Positives:  {tp} (Correctly predicted profitable)")
    logger.info(f"True Negatives:  {tn} (Correctly predicted losing)")
    logger.info(f"False Positives: {fp} (Predicted profitable, was losing)")
    logger.info(f"False Negatives: {fn} (Predicted losing, was profitable)")
    logger.info(f"\nSpecificity: {specificity:.4f} ({specificity*100:.2f}%)")
    logger.info(f"NPV:         {npv:.4f} ({npv*100:.2f}%)")
    
    # Classification report
    logger.info("\n" + "=" * 80)
    logger.info("CLASSIFICATION REPORT")
    logger.info("=" * 80)
    print(classification_report(y, y_pred, target_names=['Losing', 'Profitable']))
    
    # Feature importance
    if hasattr(model, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("\n" + "=" * 80)
        logger.info("FEATURE IMPORTANCE (Top 15)")
        logger.info("=" * 80)
        for idx, row in feature_importance.head(15).iterrows():
            bar = '█' * int(row['importance'] * 50)
            logger.info(f"{row['feature']:20s} {bar} {row['importance']:.4f}")
    
    # Confidence distribution
    logger.info("\n" + "=" * 80)
    logger.info("PREDICTION CONFIDENCE DISTRIBUTION")
    logger.info("=" * 80)
    
    confidence_bins = [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    confidence_labels = ['<50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
    
    df['confidence'] = y_pred_proba
    df['confidence_bin'] = pd.cut(df['confidence'], bins=confidence_bins, labels=confidence_labels)
    
    for bin_label in confidence_labels:
        bin_data = df[df['confidence_bin'] == bin_label]
        if len(bin_data) > 0:
            bin_accuracy = accuracy_score(bin_data['profitable'], 
                                         model.predict(bin_data[feature_columns]))
            logger.info(f"{bin_label:10s}: {len(bin_data):4d} samples, "
                       f"accuracy: {bin_accuracy:.2%}")
    
    # Recommendations
    logger.info("\n" + "=" * 80)
    logger.info("RECOMMENDATIONS")
    logger.info("=" * 80)
    
    if accuracy >= 0.75:
        logger.info("✅ EXCELLENT: Model performance is very good!")
        logger.info("   → Deploy this model to production")
        logger.info("   → Monitor performance in live trading")
    elif accuracy >= 0.65:
        logger.info("✅ GOOD: Model performance is acceptable")
        logger.info("   → Can deploy with monitoring")
        logger.info("   → Consider collecting more data for improvement")
    elif accuracy >= 0.55:
        logger.info("⚠️  FAIR: Model performance is marginal")
        logger.info("   → Collect more training data")
        logger.info("   → Review feature engineering")
        logger.info("   → Consider different model parameters")
    else:
        logger.info("❌ POOR: Model performance is insufficient")
        logger.info("   → Do NOT deploy this model")
        logger.info("   → Collect significantly more data")
        logger.info("   → Review data quality")
        logger.info("   → Consider different approach")
    
    # Save evaluation report
    report_file = 'ml_training/evaluation_report.txt'
    with open(report_file, 'w') as f:
        f.write("ML MODEL EVALUATION REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Model: {model_file}\n")
        f.write(f"Data: {data_file}\n")
        f.write(f"Samples: {len(df)}\n\n")
        f.write(f"Accuracy:  {accuracy:.4f}\n")
        f.write(f"Precision: {precision:.4f}\n")
        f.write(f"Recall:    {recall:.4f}\n")
        f.write(f"F1 Score:  {f1:.4f}\n\n")
        f.write("Confusion Matrix:\n")
        f.write(f"TN: {tn}, FP: {fp}\n")
        f.write(f"FN: {fn}, TP: {tp}\n")
    
    logger.info(f"\n✅ Evaluation report saved to {report_file}")
    
    logger.info("\n" + "=" * 80)
    logger.info("EVALUATION COMPLETE")
    logger.info("=" * 80)
    
    return True


if __name__ == '__main__':
    print("=" * 80)
    print("EVALUATE ML MODEL")
    print("=" * 80)
    print()
    
    success = evaluate_model()
    
    if success:
        print()
        print("✅ Model evaluation complete!")
        print()
        print("Next steps:")
        print("1. Review evaluation metrics above")
        print("2. Check ml_training/evaluation_report.txt")
        print("3. If satisfied, run: python ml_training/5_deploy_model.py")
        print()
    else:
        print()
        print("❌ Failed to evaluate model")
        print()
