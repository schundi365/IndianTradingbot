"""
Validate Training Data Quality
Checks CSV format and data quality for ML training
"""

import csv
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_training_data(data_file='data/training_data.csv'):
    """
    Validate training data CSV file
    
    Args:
        data_file: Path to training data CSV
        
    Returns:
        Tuple of (is_valid, issues_list)
    """
    logger.info(f"Validating training data: {data_file}")
    
    data_path = Path(data_file)
    if not data_path.exists():
        return False, [f"File not found: {data_file}"]
    
    issues = []
    warnings = []
    
    # Required columns
    required_columns = ['timestamp', 'symbol', 'close', 'rsi', 'macd', 'macd_signal', 
                       'adx', 'atr', 'ema_fast', 'ema_slow', 'volume', 'profitable']
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Check columns
            if not reader.fieldnames:
                return False, ["CSV file has no headers"]
            
            missing_columns = set(required_columns) - set(reader.fieldnames)
            if missing_columns:
                issues.append(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Read and validate rows
            rows = list(reader)
            
            if len(rows) == 0:
                return False, ["CSV file is empty"]
            
            logger.info(f"Found {len(rows)} samples")
            
            # Check minimum samples
            if len(rows) < 50:
                warnings.append(f"Only {len(rows)} samples (minimum 100 recommended)")
            elif len(rows) < 100:
                warnings.append(f"Only {len(rows)} samples (200+ recommended for best results)")
            
            # Validate data quality
            profitable_count = 0
            symbols_found = set()
            invalid_rows = []
            
            for i, row in enumerate(rows, start=2):  # Start at 2 (1 is header)
                # Check profitable label
                try:
                    profitable = int(row.get('profitable', -1))
                    if profitable not in [0, 1]:
                        invalid_rows.append(f"Row {i}: Invalid profitable value '{row.get('profitable')}'")
                    elif profitable == 1:
                        profitable_count += 1
                except ValueError:
                    invalid_rows.append(f"Row {i}: Profitable must be 0 or 1")
                
                # Check symbol
                symbol = row.get('symbol', '').strip()
                if symbol:
                    symbols_found.add(symbol)
                else:
                    invalid_rows.append(f"Row {i}: Missing symbol")
                
                # Check numeric fields
                numeric_fields = ['close', 'rsi', 'macd', 'macd_signal', 'adx', 'atr', 
                                'ema_fast', 'ema_slow', 'volume']
                
                for field in numeric_fields:
                    try:
                        value = float(row.get(field, 0))
                        
                        # Sanity checks
                        if field == 'rsi' and (value < 0 or value > 100):
                            warnings.append(f"Row {i}: RSI value {value} out of range (0-100)")
                        elif field == 'adx' and (value < 0 or value > 100):
                            warnings.append(f"Row {i}: ADX value {value} out of range (0-100)")
                        elif value < 0 and field not in ['macd', 'macd_signal']:
                            warnings.append(f"Row {i}: Negative {field} value: {value}")
                    except (ValueError, TypeError):
                        invalid_rows.append(f"Row {i}: Invalid {field} value '{row.get(field)}'")
            
            # Report invalid rows (limit to first 10)
            if invalid_rows:
                issues.extend(invalid_rows[:10])
                if len(invalid_rows) > 10:
                    issues.append(f"... and {len(invalid_rows) - 10} more invalid rows")
            
            # Check class balance
            loss_count = len(rows) - profitable_count
            if profitable_count == 0:
                issues.append("No profitable trades in dataset")
            elif loss_count == 0:
                issues.append("No losing trades in dataset")
            else:
                win_rate = profitable_count / len(rows) * 100
                logger.info(f"Win rate: {win_rate:.1f}% ({profitable_count} wins, {loss_count} losses)")
                
                if win_rate < 20 or win_rate > 80:
                    warnings.append(f"Imbalanced dataset: {win_rate:.1f}% wins (40-60% is ideal)")
            
            # Check symbols
            logger.info(f"Symbols found: {', '.join(sorted(symbols_found))}")
            if len(symbols_found) == 1:
                warnings.append("Only one symbol in dataset (multiple symbols recommended)")
            
            # Check timestamps
            timestamps_valid = True
            for i, row in enumerate(rows[:10], start=2):  # Check first 10
                timestamp = row.get('timestamp', '').strip()
                if timestamp:
                    try:
                        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except ValueError:
                        timestamps_valid = False
                        warnings.append(f"Row {i}: Invalid timestamp format '{timestamp}'")
                        break
            
            if not timestamps_valid:
                warnings.append("Some timestamps have invalid format (should be YYYY-MM-DD HH:MM:SS)")
            
    except Exception as e:
        return False, [f"Error reading CSV: {str(e)}"]
    
    # Summary
    is_valid = len(issues) == 0
    
    if is_valid:
        logger.info("✅ Validation passed!")
        if warnings:
            logger.warning(f"⚠️  {len(warnings)} warnings found")
            for warning in warnings:
                logger.warning(f"  - {warning}")
    else:
        logger.error(f"❌ Validation failed with {len(issues)} issues")
        for issue in issues:
            logger.error(f"  - {issue}")
    
    return is_valid, issues + warnings


if __name__ == '__main__':
    print("=" * 80)
    print("VALIDATE TRAINING DATA")
    print("=" * 80)
    print()
    
    data_file = input("Enter path to training data CSV (or press Enter for default): ").strip()
    if not data_file:
        data_file = 'data/training_data.csv'
    
    print()
    is_valid, messages = validate_training_data(data_file)
    
    print()
    print("=" * 80)
    if is_valid:
        print("✅ VALIDATION PASSED")
        print()
        print("Your training data is ready to use!")
        print()
        print("Next steps:")
        print("1. Open dashboard → ML Features")
        print("2. Set 'Training Data Path' to:", data_file)
        print("3. Click 'Train ML Model'")
    else:
        print("❌ VALIDATION FAILED")
        print()
        print("Please fix the issues above before training")
        print()
        print("Common fixes:")
        print("- Ensure CSV has all required columns")
        print("- Check profitable column has only 0 or 1 values")
        print("- Verify numeric fields contain valid numbers")
        print("- Add more samples (minimum 100 recommended)")
    print("=" * 80)
    print()
