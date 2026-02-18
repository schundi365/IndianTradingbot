@echo off
echo ================================================================
echo GEM Trading Bot - ML Model Training Pipeline
echo ================================================================
echo.
echo This will train a new ML model from your trading logs
echo.
pause

echo.
echo Step 1: Extracting training data from logs...
python ml_training/1_extract_training_data.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to extract training data
    pause
    exit /b 1
)

echo.
echo Step 2: Preparing training data...
python ml_training/2_prepare_training_data.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to prepare training data
    pause
    exit /b 1
)

echo.
echo Step 3: Training ML model...
python ml_training/3_train_ml_model.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to train ML model
    pause
    exit /b 1
)

echo.
echo Step 4: Evaluating model performance...
python ml_training/4_evaluate_model.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to evaluate model
    pause
    exit /b 1
)

echo.
echo ================================================================
echo ML Model Training Complete!
echo ================================================================
echo.
echo Review the evaluation metrics above.
echo.
echo If satisfied with the performance:
echo   Run: python ml_training/5_deploy_model.py
echo.
echo Then restart the bot to use the new model.
echo.
pause
