"""
Deploy ML Model to Production
Copies trained model to production location and updates configuration
"""

import shutil
import logging
from pathlib import Path
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def deploy_model(source_model='models/ml_signal_model.pkl',
                backup_existing=True):
    """
    Deploy trained ML model to production
    
    Args:
        source_model: Path to trained model file
        backup_existing: Whether to backup existing model
    
    Returns:
        bool: Success status
    """
    logger.info("=" * 80)
    logger.info("DEPLOYING ML MODEL")
    logger.info("=" * 80)
    
    # Check if source model exists
    source_path = Path(source_model)
    if not source_path.exists():
        logger.error(f"Source model not found: {source_model}")
        logger.error("Run 3_train_ml_model.py first!")
        return False
    
    # Production model location (same as source in this case)
    prod_model = source_model
    prod_path = Path(prod_model)
    
    # Backup existing model if requested
    if backup_existing and prod_path.exists():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"models/ml_signal_model_backup_{timestamp}.pkl"
        
        try:
            shutil.copy2(prod_model, backup_file)
            logger.info(f"✅ Existing model backed up to {backup_file}")
        except Exception as e:
            logger.warning(f"⚠️  Could not backup existing model: {e}")
    
    # Load and verify model metadata
    metadata_file = source_model.replace('.pkl', '_metadata.json')
    if Path(metadata_file).exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        logger.info("\nModel Information:")
        logger.info(f"  Trained: {metadata.get('trained_date', 'Unknown')}")
        logger.info(f"  Samples: {metadata.get('samples', 'Unknown')}")
        logger.info(f"  Accuracy: {metadata.get('test_accuracy', 0):.4f}")
        logger.info(f"  Precision: {metadata.get('test_precision', 0):.4f}")
        logger.info(f"  Recall: {metadata.get('test_recall', 0):.4f}")
        logger.info(f"  F1 Score: {metadata.get('test_f1', 0):.4f}")
        
        # Check if model is good enough
        accuracy = metadata.get('test_accuracy', 0)
        if accuracy < 0.55:
            logger.warning("\n⚠️  WARNING: Model accuracy is low!")
            logger.warning("   Consider training with more data before deploying")
            response = input("\nDeploy anyway? (yes/no): ")
            if response.lower() != 'yes':
                logger.info("Deployment cancelled")
                return False
    
    # Model is already in production location, just verify it
    logger.info(f"\n✅ Model is ready at {prod_model}")
    
    # Update bot configuration
    config_file = 'bot_config.json'
    config_path = Path(config_file)
    
    if config_path.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Update ML settings
            config['ml_enabled'] = True
            config['ml_model_path'] = prod_model
            
            # Save updated config
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            
            logger.info(f"✅ Bot configuration updated")
            logger.info(f"   ml_enabled: true")
            logger.info(f"   ml_model_path: {prod_model}")
        except Exception as e:
            logger.warning(f"⚠️  Could not update bot config: {e}")
    
    # Create deployment record
    deployment_record = {
        'deployed_date': datetime.now().isoformat(),
        'model_file': prod_model,
        'metadata': metadata if Path(metadata_file).exists() else {}
    }
    
    deployment_file = 'ml_training/deployment_history.json'
    deployment_path = Path(deployment_file)
    
    # Load existing deployment history
    if deployment_path.exists():
        with open(deployment_file, 'r') as f:
            history = json.load(f)
    else:
        history = []
    
    # Add new deployment
    history.append(deployment_record)
    
    # Save deployment history
    with open(deployment_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    logger.info(f"✅ Deployment recorded in {deployment_file}")
    
    # Verify model can be loaded
    logger.info("\nVerifying model can be loaded...")
    try:
        import pickle
        with open(prod_model, 'rb') as f:
            model = pickle.load(f)
        logger.info("✅ Model loads successfully")
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        return False
    
    logger.info("\n" + "=" * 80)
    logger.info("DEPLOYMENT COMPLETE")
    logger.info("=" * 80)
    logger.info("\nNext steps:")
    logger.info("1. Restart the trading bot")
    logger.info("2. Check logs for 'ML INTEGRATION INITIALIZED'")
    logger.info("3. Monitor ML performance in live trading")
    logger.info("4. Watch for 'ML APPROVED' and 'ML REJECTED' messages")
    
    return True


if __name__ == '__main__':
    print("=" * 80)
    print("DEPLOY ML MODEL")
    print("=" * 80)
    print()
    
    success = deploy_model()
    
    if success:
        print()
        print("✅ ML model deployed successfully!")
        print()
        print("IMPORTANT: Restart the trading bot to use the new model")
        print()
        print("Commands:")
        print("  python web_dashboard.py")
        print()
        print("Then watch for ML logs:")
        print("  - '✅ ML INTEGRATION INITIALIZED'")
        print("  - '🤖 ML ENHANCED SIGNAL ANALYSIS'")
        print("  - '✅ ML APPROVED' or '❌ ML REJECTED'")
        print()
    else:
        print()
        print("❌ Deployment failed")
        print()
