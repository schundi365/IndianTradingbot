"""
Advanced Trend Detection Engine for GEM Trading Bot
Implements sophisticated market structure analysis, divergence detection, and multi-timeframe confirmation

Performance Optimizations:
- Efficient data structures and caching
- Vectorized operations using NumPy
- Memory-efficient storage for historical data
- Sub-100ms analysis per symbol per timeframe

Enhanced Logging Integration:
- Detailed analysis logging with configurable levels
- Performance monitoring and timing logs
- Component-specific error tracking
- Integration with existing bot logging system
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import logging
from enum import Enum
import time
from functools import lru_cache
import weakref
import traceback
import sys
import gc
from contextlib import contextmanager

# Configure logging with enhanced detail levels
logger = logging.getLogger(__name__)

class TrendDetectionLogger:
    """
    Enhanced logging system for trend detection with configurable detail levels
    Integrates with existing bot logging system while providing trend-specific logging
    """
    
    def __init__(self, base_logger: logging.Logger = None, logging_level: str = 'standard'):
        """
        Initialize trend detection logger
        
        Args:
            base_logger: Base logger instance (uses module logger if None)
            logging_level: Logging detail level ('minimal', 'standard', 'detailed', 'debug')
        """
        self.base_logger = base_logger or logger
        self.logging_level = logging_level
        self.component_loggers = {}
        
        # Performance tracking
        self.analysis_times = {}
        self.component_performance = {}
        
        # Configure logging levels
        self._configure_logging_levels()
        
        self.base_logger.info(f"🔍 TrendDetectionLogger initialized with level: {logging_level}")
    
    def _configure_logging_levels(self):
        """Configure logging behavior based on detail level"""
        self.log_analysis_start = self.logging_level in ['detailed', 'debug']
        self.log_component_details = self.logging_level in ['detailed', 'debug']
        self.log_performance_metrics = self.logging_level in ['standard', 'detailed', 'debug']
        self.log_signal_generation = self.logging_level in ['standard', 'detailed', 'debug']
        self.log_cache_operations = self.logging_level == 'debug'
        self.enable_data_validation_logging = self.logging_level == 'debug'
        self.log_error_recovery = self.logging_level in ['detailed', 'debug']
    
    def set_logging_level(self, level: str):
        """Update logging level dynamically"""
        if level in ['minimal', 'standard', 'detailed', 'debug']:
            self.logging_level = level
            self._configure_logging_levels()
            self.base_logger.info(f"🔧 Trend detection logging level changed to: {level}")
        else:
            self.base_logger.warning(f"Invalid logging level: {level}")
    
    def log_analysis_start_event(self, symbol: str, timeframe: str = None):
        """Log start of trend analysis"""
        if self.log_analysis_start:
            tf_info = f" ({timeframe})" if timeframe else ""
            self.base_logger.info(f"🔍 Starting trend analysis for {symbol}{tf_info}")
    
    def log_analysis_complete(self, symbol: str, signals_count: int, confidence: float, elapsed_ms: float):
        """Log completion of trend analysis with results"""
        if self.log_performance_metrics:
            self.base_logger.info(f"✅ Trend analysis complete for {symbol}: "
                                f"{signals_count} signals, confidence={confidence:.2f}, "
                                f"time={elapsed_ms:.1f}ms")
    
    def log_component_analysis(self, component: str, symbol: str, result_summary: str):
        """Log component-specific analysis results"""
        if self.log_component_details:
            self.base_logger.info(f"🔧 {component.upper()}: {symbol} - {result_summary}")
    
    def log_signal_generated(self, signal_type: str, source: str, confidence: float, strength: float):
        """Log signal generation with details"""
        if self.log_signal_generation:
            self.base_logger.info(f"📊 SIGNAL: {signal_type} from {source} "
                                f"(confidence={confidence:.2f}, strength={strength:.2f})")
    
    def log_signal_filtered(self, signal_type: str, reason: str, confidence: float):
        """Log signal filtering decisions"""
        if self.log_signal_generation:
            self.base_logger.debug(f"🚫 FILTERED: {signal_type} - {reason} (confidence={confidence:.2f})")
    
    def log_performance_warning(self, operation: str, elapsed_ms: float, threshold_ms: float):
        """Log performance warnings for slow operations"""
        if self.log_performance_metrics:
            self.base_logger.warning(f"⚠️ PERFORMANCE: {operation} took {elapsed_ms:.1f}ms "
                                   f"(threshold: {threshold_ms:.1f}ms)")
    
    def log_cache_operation(self, operation: str, key: str, hit: bool = None):
        """Log cache operations"""
        if self.log_cache_operations:
            if hit is not None:
                status = "HIT" if hit else "MISS"
                self.base_logger.debug(f"💾 CACHE {status}: {key}")
            else:
                self.base_logger.debug(f"💾 CACHE {operation}: {key}")
    
    def log_data_validation(self, symbol: str, status: str, details: str = None):
        """Log data validation results"""
        if self.enable_data_validation_logging:
            detail_info = f" - {details}" if details else ""
            self.base_logger.debug(f"📋 DATA VALIDATION: {symbol} - {status}{detail_info}")
    
    def log_error_recovery(self, component: str, error_type: str, recovery_action: str):
        """Log error recovery actions"""
        if self.log_error_recovery:
            self.base_logger.warning(f"🔄 ERROR RECOVERY: {component} - {error_type} -> {recovery_action}")
    
    def log_component_failure(self, component: str, error: str, symbol: str = None):
        """Log component failures"""
        symbol_info = f" for {symbol}" if symbol else ""
        self.base_logger.error(f"❌ COMPONENT FAILURE: {component}{symbol_info} - {error}")
    
    def log_configuration_change(self, parameter: str, old_value: Any, new_value: Any):
        """Log configuration changes"""
        self.base_logger.info(f"🔧 CONFIG CHANGE: {parameter} changed from {old_value} to {new_value}")
    
    def log_memory_usage(self, operation: str, usage_mb: float, limit_mb: float):
        """Log memory usage information"""
        if self.log_performance_metrics:
            percentage = (usage_mb / limit_mb) * 100 if limit_mb > 0 else 0
            if percentage > 80:
                self.base_logger.warning(f"🧠 MEMORY: {operation} using {usage_mb:.1f}MB "
                                       f"({percentage:.1f}% of {limit_mb:.1f}MB limit)")
            elif self.logging_level == 'debug':
                self.base_logger.debug(f"🧠 MEMORY: {operation} using {usage_mb:.1f}MB "
                                     f"({percentage:.1f}% of limit)")
    
    def log_circuit_breaker_action(self, component: str, action: str, failure_count: int):
        """Log circuit breaker actions"""
        if self.log_error_recovery:
            self.base_logger.warning(f"⚡ CIRCUIT BREAKER: {component} - {action} "
                                   f"(failures: {failure_count})")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance logging summary"""
        return {
            'analysis_count': len(self.analysis_times),
            'avg_analysis_time': np.mean(list(self.analysis_times.values())) if self.analysis_times else 0,
            'component_performance': self.component_performance.copy(),
            'logging_level': self.logging_level
        }

# Global trend detection logger instance
trend_logger = TrendDetectionLogger()

class ConfigurationValidator:
    """Validates trend detection configuration parameters"""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.validation_errors = []
        
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate configuration parameters and return corrected config
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_messages, corrected_config)
        """
        self.validation_errors = []
        corrected_config = config.copy()
        
        # Validate basic trend detection settings
        corrected_config = self._validate_basic_settings(corrected_config)
        
        # Validate performance settings
        corrected_config = self._validate_performance_settings(corrected_config)
        
        # Validate component-specific settings
        corrected_config = self._validate_component_settings(corrected_config)
        
        # Validate multi-timeframe settings
        corrected_config = self._validate_multi_timeframe_settings(corrected_config)
        
        # Validate error handling settings
        corrected_config = self._validate_error_handling_settings(corrected_config)
        
        is_valid = len(self.validation_errors) == 0
        
        if not is_valid:
            self.logger.warning(f"Configuration validation found {len(self.validation_errors)} issues")
            for error in self.validation_errors:
                self.logger.warning(f"  - {error}")
        else:
            self.logger.info("Configuration validation passed")
        
        return is_valid, self.validation_errors.copy(), corrected_config
    
    def _validate_basic_settings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate basic trend detection settings"""
        
        # Validate use_trend_detection
        if 'use_trend_detection' in config:
            if not isinstance(config['use_trend_detection'], bool):
                self.validation_errors.append("use_trend_detection must be a boolean")
                config['use_trend_detection'] = True
        else:
            config['use_trend_detection'] = True
        
        # Validate trend_detection_sensitivity (1-10)
        if 'trend_detection_sensitivity' in config:
            sensitivity = config['trend_detection_sensitivity']
            if not isinstance(sensitivity, (int, float)):
                self.validation_errors.append("trend_detection_sensitivity must be a number")
                config['trend_detection_sensitivity'] = 5
            elif sensitivity < 1 or sensitivity > 10:
                self.validation_errors.append("trend_detection_sensitivity must be between 1 and 10")
                config['trend_detection_sensitivity'] = max(1, min(10, sensitivity))
        else:
            config['trend_detection_sensitivity'] = 5
        
        # Validate min_trend_confidence (0.0-1.0)
        if 'min_trend_confidence' in config:
            confidence = config['min_trend_confidence']
            if not isinstance(confidence, (int, float)):
                self.validation_errors.append("min_trend_confidence must be a number")
                config['min_trend_confidence'] = 0.6
            elif confidence < 0.0 or confidence > 1.0:
                self.validation_errors.append("min_trend_confidence must be between 0.0 and 1.0")
                config['min_trend_confidence'] = max(0.0, min(1.0, confidence))
        else:
            config['min_trend_confidence'] = 0.6
        
        # Validate enable_early_signals
        if 'enable_early_signals' in config:
            if not isinstance(config['enable_early_signals'], bool):
                self.validation_errors.append("enable_early_signals must be a boolean")
                config['enable_early_signals'] = True
        else:
            config['enable_early_signals'] = True
        
        return config
    
    def _validate_performance_settings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate performance-related settings"""
        
        # Validate max_analysis_time_ms (10-1000ms)
        if 'max_analysis_time_ms' in config:
            time_ms = config['max_analysis_time_ms']
            if not isinstance(time_ms, (int, float)):
                self.validation_errors.append("max_analysis_time_ms must be a number")
                config['max_analysis_time_ms'] = 100
            elif time_ms < 10 or time_ms > 1000:
                self.validation_errors.append("max_analysis_time_ms must be between 10 and 1000")
                config['max_analysis_time_ms'] = max(10, min(1000, time_ms))
        else:
            config['max_analysis_time_ms'] = 100
        
        # Validate trend_cache_size (10-10000)
        if 'trend_cache_size' in config:
            cache_size = config['trend_cache_size']
            if not isinstance(cache_size, int):
                self.validation_errors.append("trend_cache_size must be an integer")
                config['trend_cache_size'] = 1000
            elif cache_size < 10 or cache_size > 10000:
                self.validation_errors.append("trend_cache_size must be between 10 and 10000")
                config['trend_cache_size'] = max(10, min(10000, cache_size))
        else:
            config['trend_cache_size'] = 1000
        
        # Validate max_memory_mb (50-2000MB)
        if 'max_memory_mb' in config:
            memory_mb = config['max_memory_mb']
            if not isinstance(memory_mb, (int, float)):
                self.validation_errors.append("max_memory_mb must be a number")
                config['max_memory_mb'] = 500
            elif memory_mb < 50 or memory_mb > 2000:
                self.validation_errors.append("max_memory_mb must be between 50 and 2000")
                config['max_memory_mb'] = max(50, min(2000, memory_mb))
        else:
            config['max_memory_mb'] = 500
        
        # Validate boolean performance settings
        bool_settings = [
            'enable_performance_monitoring',
            'cache_analysis_results'
        ]
        
        for setting in bool_settings:
            if setting in config:
                if not isinstance(config[setting], bool):
                    self.validation_errors.append(f"{setting} must be a boolean")
                    config[setting] = True
            else:
                config[setting] = True
        
        return config
    
    def _validate_component_settings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component-specific settings"""
        
        # Validate EMA periods (5-200)
        ema_settings = [
            ('ema_fast_period', 20, 5, 200),
            ('ema_slow_period', 50, 5, 200)
        ]
        
        for setting, default, min_val, max_val in ema_settings:
            if setting in config:
                period = config[setting]
                if not isinstance(period, int):
                    self.validation_errors.append(f"{setting} must be an integer")
                    config[setting] = default
                elif period < min_val or period > max_val:
                    self.validation_errors.append(f"{setting} must be between {min_val} and {max_val}")
                    config[setting] = max(min_val, min(max_val, period))
            else:
                config[setting] = default
        
        # Validate Aroon period (5-100)
        if 'aroon_period' in config:
            period = config['aroon_period']
            if not isinstance(period, int):
                self.validation_errors.append("aroon_period must be an integer")
                config['aroon_period'] = 25
            elif period < 5 or period > 100:
                self.validation_errors.append("aroon_period must be between 5 and 100")
                config['aroon_period'] = max(5, min(100, period))
        else:
            config['aroon_period'] = 25
        
        # Validate Aroon threshold (50-100)
        if 'aroon_threshold' in config:
            threshold = config['aroon_threshold']
            if not isinstance(threshold, (int, float)):
                self.validation_errors.append("aroon_threshold must be a number")
                config['aroon_threshold'] = 70
            elif threshold < 50 or threshold > 100:
                self.validation_errors.append("aroon_threshold must be between 50 and 100")
                config['aroon_threshold'] = max(50, min(100, threshold))
        else:
            config['aroon_threshold'] = 70
        
        # Validate market structure settings
        if 'min_swing_strength' in config:
            strength = config['min_swing_strength']
            if not isinstance(strength, int):
                self.validation_errors.append("min_swing_strength must be an integer")
                config['min_swing_strength'] = 3
            elif strength < 1 or strength > 10:
                self.validation_errors.append("min_swing_strength must be between 1 and 10")
                config['min_swing_strength'] = max(1, min(10, strength))
        else:
            config['min_swing_strength'] = 3
        
        # Validate structure break threshold (0.0001-0.01)
        if 'structure_break_threshold' in config:
            threshold = config['structure_break_threshold']
            if not isinstance(threshold, (int, float)):
                self.validation_errors.append("structure_break_threshold must be a number")
                config['structure_break_threshold'] = 0.001
            elif threshold < 0.0001 or threshold > 0.01:
                self.validation_errors.append("structure_break_threshold must be between 0.0001 and 0.01")
                config['structure_break_threshold'] = max(0.0001, min(0.01, threshold))
        else:
            config['structure_break_threshold'] = 0.001
        
        # Validate divergence settings
        if 'divergence_lookback' in config:
            lookback = config['divergence_lookback']
            if not isinstance(lookback, int):
                self.validation_errors.append("divergence_lookback must be an integer")
                config['divergence_lookback'] = 50
            elif lookback < 20 or lookback > 200:
                self.validation_errors.append("divergence_lookback must be between 20 and 200")
                config['divergence_lookback'] = max(20, min(200, lookback))
        else:
            config['divergence_lookback'] = 50
        
        # Validate min divergence strength (0.1-1.0)
        if 'min_divergence_strength' in config:
            strength = config['min_divergence_strength']
            if not isinstance(strength, (int, float)):
                self.validation_errors.append("min_divergence_strength must be a number")
                config['min_divergence_strength'] = 0.3
            elif strength < 0.1 or strength > 1.0:
                self.validation_errors.append("min_divergence_strength must be between 0.1 and 1.0")
                config['min_divergence_strength'] = max(0.1, min(1.0, strength))
        else:
            config['min_divergence_strength'] = 0.3
        
        # Validate trendline settings
        if 'max_trendlines' in config:
            max_lines = config['max_trendlines']
            if not isinstance(max_lines, int):
                self.validation_errors.append("max_trendlines must be an integer")
                config['max_trendlines'] = 5
            elif max_lines < 1 or max_lines > 20:
                self.validation_errors.append("max_trendlines must be between 1 and 20")
                config['max_trendlines'] = max(1, min(20, max_lines))
        else:
            config['max_trendlines'] = 5
        
        # Validate min trendline touches (2-10)
        if 'min_trendline_touches' in config:
            touches = config['min_trendline_touches']
            if not isinstance(touches, int):
                self.validation_errors.append("min_trendline_touches must be an integer")
                config['min_trendline_touches'] = 2
            elif touches < 2 or touches > 10:
                self.validation_errors.append("min_trendline_touches must be between 2 and 10")
                config['min_trendline_touches'] = max(2, min(10, touches))
        else:
            config['min_trendline_touches'] = 2
        
        # Validate trendline angles (5-85 degrees)
        angle_settings = [
            ('trendline_angle_min', 10, 5, 85),
            ('trendline_angle_max', 80, 5, 85)
        ]
        
        for setting, default, min_val, max_val in angle_settings:
            if setting in config:
                angle = config[setting]
                if not isinstance(angle, (int, float)):
                    self.validation_errors.append(f"{setting} must be a number")
                    config[setting] = default
                elif angle < min_val or angle > max_val:
                    self.validation_errors.append(f"{setting} must be between {min_val} and {max_val}")
                    config[setting] = max(min_val, min(max_val, angle))
            else:
                config[setting] = default
        
        # Ensure min angle < max angle
        if config['trendline_angle_min'] >= config['trendline_angle_max']:
            self.validation_errors.append("trendline_angle_min must be less than trendline_angle_max")
            config['trendline_angle_min'] = 10
            config['trendline_angle_max'] = 80
        
        # Validate volume spike threshold (1.0-5.0)
        if 'volume_spike_threshold' in config:
            threshold = config['volume_spike_threshold']
            if not isinstance(threshold, (int, float)):
                self.validation_errors.append("volume_spike_threshold must be a number")
                config['volume_spike_threshold'] = 1.5
            elif threshold < 1.0 or threshold > 5.0:
                self.validation_errors.append("volume_spike_threshold must be between 1.0 and 5.0")
                config['volume_spike_threshold'] = max(1.0, min(5.0, threshold))
        else:
            config['volume_spike_threshold'] = 1.5
        
        return config
    
    def _validate_multi_timeframe_settings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate multi-timeframe settings"""
        
        # Validate enable_mtf_confirmation
        if 'enable_mtf_confirmation' in config:
            if not isinstance(config['enable_mtf_confirmation'], bool):
                self.validation_errors.append("enable_mtf_confirmation must be a boolean")
                config['enable_mtf_confirmation'] = True
        else:
            config['enable_mtf_confirmation'] = True
        
        # Validate MTF weight (0.0-1.0)
        if 'mtf_weight' in config:
            weight = config['mtf_weight']
            if not isinstance(weight, (int, float)):
                self.validation_errors.append("mtf_weight must be a number")
                config['mtf_weight'] = 0.3
            elif weight < 0.0 or weight > 1.0:
                self.validation_errors.append("mtf_weight must be between 0.0 and 1.0")
                config['mtf_weight'] = max(0.0, min(1.0, weight))
        else:
            config['mtf_weight'] = 0.3
        
        # Validate MTF confirmation bars (50-500)
        if 'mtf_confirmation_bars' in config:
            bars = config['mtf_confirmation_bars']
            if not isinstance(bars, int):
                self.validation_errors.append("mtf_confirmation_bars must be an integer")
                config['mtf_confirmation_bars'] = 100
            elif bars < 50 or bars > 500:
                self.validation_errors.append("mtf_confirmation_bars must be between 50 and 500")
                config['mtf_confirmation_bars'] = max(50, min(500, bars))
        else:
            config['mtf_confirmation_bars'] = 100
        
        # Validate MTF alignment threshold (0.3-1.0)
        if 'mtf_alignment_threshold' in config:
            threshold = config['mtf_alignment_threshold']
            if not isinstance(threshold, (int, float)):
                self.validation_errors.append("mtf_alignment_threshold must be a number")
                config['mtf_alignment_threshold'] = 0.6
            elif threshold < 0.3 or threshold > 1.0:
                self.validation_errors.append("mtf_alignment_threshold must be between 0.3 and 1.0")
                config['mtf_alignment_threshold'] = max(0.3, min(1.0, threshold))
        else:
            config['mtf_alignment_threshold'] = 0.6
        
        # Validate MTF contradiction penalty (0.1-0.8)
        if 'mtf_contradiction_penalty' in config:
            penalty = config['mtf_contradiction_penalty']
            if not isinstance(penalty, (int, float)):
                self.validation_errors.append("mtf_contradiction_penalty must be a number")
                config['mtf_contradiction_penalty'] = 0.4
            elif penalty < 0.1 or penalty > 0.8:
                self.validation_errors.append("mtf_contradiction_penalty must be between 0.1 and 0.8")
                config['mtf_contradiction_penalty'] = max(0.1, min(0.8, penalty))
        else:
            config['mtf_contradiction_penalty'] = 0.4
        
        # Validate MTF primary to higher mapping
        if 'mtf_primary_to_higher' in config:
            mapping = config['mtf_primary_to_higher']
            if not isinstance(mapping, dict):
                self.validation_errors.append("mtf_primary_to_higher must be a dictionary")
                config['mtf_primary_to_higher'] = {}
            else:
                # Validate that all keys and values are valid timeframe constants
                valid_timeframes = [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60, 120, 240, 360, 480, 720, 1440, 10080, 43200]
                
                for primary_tf, higher_tf in mapping.items():
                    if not isinstance(primary_tf, int) or primary_tf not in valid_timeframes:
                        self.validation_errors.append(f"Invalid primary timeframe in mtf_primary_to_higher: {primary_tf}")
                    if not isinstance(higher_tf, int) or higher_tf not in valid_timeframes:
                        self.validation_errors.append(f"Invalid higher timeframe in mtf_primary_to_higher: {higher_tf}")
                    if isinstance(primary_tf, int) and isinstance(higher_tf, int) and primary_tf >= higher_tf:
                        self.validation_errors.append(f"Primary timeframe ({primary_tf}) must be smaller than higher timeframe ({higher_tf})")
        
        return config
    
    def _validate_error_handling_settings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate error handling settings"""
        
        # Validate max_error_retries (1-10)
        if 'max_error_retries' in config:
            retries = config['max_error_retries']
            if not isinstance(retries, int):
                self.validation_errors.append("max_error_retries must be an integer")
                config['max_error_retries'] = 3
            elif retries < 1 or retries > 10:
                self.validation_errors.append("max_error_retries must be between 1 and 10")
                config['max_error_retries'] = max(1, min(10, retries))
        else:
            config['max_error_retries'] = 3
        
        # Validate boolean error handling settings
        bool_settings = [
            'enable_circuit_breaker',
            'graceful_degradation'
        ]
        
        for setting in bool_settings:
            if setting in config:
                if not isinstance(config[setting], bool):
                    self.validation_errors.append(f"{setting} must be a boolean")
                    config[setting] = True
            else:
                config[setting] = True
        
        return config
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation results"""
        return {
            'total_errors': len(self.validation_errors),
            'errors': self.validation_errors.copy(),
            'is_valid': len(self.validation_errors) == 0
        }

class TrendDetectionError(Exception):
    """Base exception for trend detection errors"""
    pass

class DataValidationError(TrendDetectionError):
    """Raised when input data validation fails"""
    pass

class AnalysisTimeoutError(TrendDetectionError):
    """Raised when analysis exceeds time limits"""
    pass

class ComponentInitializationError(TrendDetectionError):
    """Raised when component initialization fails"""
    pass

class MemoryError(TrendDetectionError):
    """Raised when memory usage exceeds limits"""
    pass

class ErrorRecoveryManager:
    """Manages error recovery and diagnostic information"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.error_counts = {}
        self.recovery_strategies = {}
        self.diagnostic_info = {}
        
    def record_error(self, error_type: str, error: Exception, context: Dict[str, Any] = None):
        """Record error occurrence for tracking"""
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        # Store diagnostic information
        self.diagnostic_info[f"{error_type}_{self.error_counts[error_type]}"] = {
            'timestamp': datetime.now(),
            'error': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        self.logger.error(f"Error recorded: {error_type} (count: {self.error_counts[error_type]})")
        
    def get_recovery_strategy(self, error_type: str) -> Optional[str]:
        """Get recovery strategy for error type"""
        strategies = {
            'data_validation': 'use_fallback_data',
            'component_failure': 'skip_component',
            'timeout': 'reduce_analysis_scope',
            'memory_limit': 'clear_cache_and_retry',
            'calculation_error': 'use_simplified_calculation'
        }
        return strategies.get(error_type)
        
    def should_retry(self, error_type: str, max_retries: int = 3) -> bool:
        """Determine if operation should be retried"""
        count = self.error_counts.get(error_type, 0)
        return count < max_retries
        
    def get_diagnostic_report(self) -> Dict[str, Any]:
        """Get comprehensive diagnostic report"""
        return {
            'error_counts': self.error_counts.copy(),
            'recent_errors': list(self.diagnostic_info.values())[-10:],  # Last 10 errors
            'total_errors': sum(self.error_counts.values()),
            'error_types': list(self.error_counts.keys())
        }

class MemoryManager:
    """Manages memory usage and cleanup for trend detection"""
    
    def __init__(self, max_memory_mb: int = 500):
        self.max_memory_mb = max_memory_mb
        self.logger = logging.getLogger(__name__)
        
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # Fallback if psutil not available
            return 0.0
            
    def check_memory_limit(self) -> bool:
        """Check if memory usage is within limits"""
        current_usage = self.get_memory_usage_mb()
        if current_usage > self.max_memory_mb:
            self.logger.warning(f"Memory usage ({current_usage:.1f}MB) exceeds limit ({self.max_memory_mb}MB)")
            return False
        return True
        
    def force_cleanup(self):
        """Force garbage collection and cleanup"""
        gc.collect()
        self.logger.debug("Forced memory cleanup completed")
        
    @contextmanager
    def memory_monitor(self, operation_name: str):
        """Context manager to monitor memory usage during operations"""
        start_memory = self.get_memory_usage_mb()
        try:
            yield
        finally:
            end_memory = self.get_memory_usage_mb()
            memory_delta = end_memory - start_memory
            if memory_delta > 50:  # Log if operation used >50MB
                self.logger.warning(f"High memory usage in {operation_name}: {memory_delta:.1f}MB")

class CircuitBreaker:
    """Circuit breaker pattern for component failure handling"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half_open
        
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'open':
            if self._should_attempt_reset():
                self.state = 'half_open'
            else:
                raise TrendDetectionError("Circuit breaker is open")
                
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
            
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return (datetime.now() - self.last_failure_time).seconds > self.recovery_timeout
        
    def _on_success(self):
        """Handle successful operation"""
        self.failure_count = 0
        self.state = 'closed'
        
    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'

class PerformanceTimer:
    """Context manager for timing operations"""
    def __init__(self, operation_name: str, logger: logging.Logger = None, warning_threshold_ms: float = 100):
        self.operation_name = operation_name
        self.logger = logger or logging.getLogger(__name__)
        self.warning_threshold_ms = warning_threshold_ms
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (time.perf_counter() - self.start_time) * 1000  # Convert to milliseconds
        if elapsed > self.warning_threshold_ms:  # Log if over threshold
            self.logger.warning(f"⚠️ Performance: {self.operation_name} took {elapsed:.1f}ms (>{self.warning_threshold_ms:.0f}ms threshold)")
        else:
            self.logger.debug(f"⏱️ Performance: {self.operation_name} took {elapsed:.1f}ms")

class DataCache:
    """Efficient caching system for analysis data with error handling"""
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache = {}
        self._access_times = {}
        self._current_time = 0
        self.logger = logging.getLogger(__name__)
        
    def get(self, key: str) -> Optional[Any]:
        """Get cached data with error handling"""
        try:
            if key in self._cache:
                self._access_times[key] = self._current_time
                self._current_time += 1
                return self._cache[key]
        except Exception as e:
            self.logger.error(f"Error accessing cache key {key}: {e}")
        return None
        
    def set(self, key: str, value: Any) -> None:
        """Set cached data with LRU eviction and error handling"""
        try:
            # Clean up if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                # Find least recently used item
                if self._access_times:
                    lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
                    del self._cache[lru_key]
                    del self._access_times[lru_key]
                
            self._cache[key] = value
            self._access_times[key] = self._current_time
            self._current_time += 1
        except Exception as e:
            self.logger.error(f"Error setting cache key {key}: {e}")
        
    def clear(self) -> None:
        """Clear all cached data with error handling"""
        try:
            self._cache.clear()
            self._access_times.clear()
            self._current_time = 0
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
        
    def size(self) -> int:
        """Get current cache size"""
        try:
            return len(self._cache)
        except Exception:
            return 0
            
    def cleanup_expired(self, max_age_seconds: int = 3600):
        """Clean up expired cache entries"""
        try:
            current_time = time.time()
            expired_keys = []
            
            for key in list(self._cache.keys()):
                # Simple time-based expiration (would need timestamps in real implementation)
                if self._current_time - self._access_times.get(key, 0) > max_age_seconds:
                    expired_keys.append(key)
            
            for key in expired_keys:
                if key in self._cache:
                    del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                    
            if expired_keys:
                self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                
        except Exception as e:
            self.logger.error(f"Error during cache cleanup: {e}")

class SignalType(Enum):
    """Enumeration for different signal types"""
    BULLISH_TREND_CHANGE = "bullish_trend_change"
    BEARISH_TREND_CHANGE = "bearish_trend_change"
    EARLY_WARNING_BULLISH = "early_warning_bullish"
    EARLY_WARNING_BEARISH = "early_warning_bearish"

class BreakType(Enum):
    """Enumeration for market structure break types"""
    HIGHER_HIGH = "higher_high"
    LOWER_LOW = "lower_low"
    SUPPORT_BREAK = "support_break"
    RESISTANCE_BREAK = "resistance_break"

class DivergenceType(Enum):
    """Enumeration for divergence types"""
    BULLISH_RSI = "bullish_rsi"
    BEARISH_RSI = "bearish_rsi"
    BULLISH_MACD = "bullish_macd"
    BEARISH_MACD = "bearish_macd"

@dataclass
class TrendSignal:
    """Represents a trend detection signal"""
    signal_type: str
    strength: float  # 0.0 to 1.0
    source: str  # 'market_structure', 'divergence', 'aroon', etc.
    confidence: float
    timestamp: datetime
    price_level: float
    supporting_factors: List[str]

@dataclass
class StructureBreakResult:
    """Represents a market structure break analysis result"""
    break_type: str  # 'higher_high', 'lower_low', 'support_break', 'resistance_break'
    break_level: float
    previous_level: float
    volume_confirmation: bool
    strength: float
    confirmed: bool

@dataclass
class DivergenceResult:
    """Represents a divergence analysis result"""
    divergence_type: str  # 'bullish_rsi', 'bearish_rsi', 'bullish_macd', 'bearish_macd'
    indicator: str  # 'RSI', 'MACD'
    price_points: List[Tuple[datetime, float]]
    indicator_points: List[Tuple[datetime, float]]
    strength: float
    validated: bool

@dataclass
class AroonSignal:
    """Represents an Aroon indicator signal"""
    aroon_up: float
    aroon_down: float
    oscillator: float
    signal_type: str  # 'bullish_cross', 'bearish_cross', 'consolidation'
    trend_strength: float

@dataclass
class Trendline:
    """Represents a trendline"""
    start_point: Tuple[datetime, float]
    end_point: Tuple[datetime, float]
    slope: float
    touch_points: int
    strength: float
    line_type: str  # 'support', 'resistance'

@dataclass
class TrendlineBreak:
    """Represents a trendline break"""
    trendline: Trendline
    break_point: Tuple[datetime, float]
    volume_confirmation: bool
    retest_confirmed: bool
    break_strength: float

@dataclass
class TimeframeAlignment:
    """Represents multi-timeframe alignment analysis"""
    primary_timeframe: str
    higher_timeframe: str
    alignment_score: float
    confirmation_level: str

@dataclass
class VolumeConfirmation:
    """Represents volume confirmation analysis"""
    volume_spike: bool
    volume_ratio: float
    strength: float

@dataclass
class EarlyWarningSignal:
    """Represents an early warning signal"""
    warning_type: str  # 'trend_weakness', 'key_level_approach', 'reversal_pattern'
    confidence: float  # 0.0 to 1.0
    probability_score: float  # Historical accuracy-based probability
    price_level: float
    current_price: float
    factors: List[str]
    strength: float  # Signal strength 0.0 to 1.0
    timestamp: datetime
    description: str

@dataclass
class TrendAnalysisResult:
    """Comprehensive trend analysis result"""
    signals: List[TrendSignal]
    confidence: float
    market_structure: Optional[StructureBreakResult]
    divergences: List[DivergenceResult]
    aroon_signal: Optional[AroonSignal]
    ema_signal: Optional['EMASignal']
    trendline_breaks: List[TrendlineBreak]
    timeframe_alignment: Optional[TimeframeAlignment]
    volume_confirmation: Optional[VolumeConfirmation]
    early_warnings: List[EarlyWarningSignal]

class TrendDetectionEngine:
    """
    Main orchestrator for all trend detection functionality
    Integrates market structure analysis, divergence detection, and multi-timeframe confirmation
    
    Performance Features:
    - Efficient data caching and reuse
    - Vectorized operations for speed
    - Memory-efficient storage
    - Sub-100ms analysis guarantee
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the trend detection engine with comprehensive error handling and configuration validation
        
        Args:
            config: Configuration dictionary with trend detection parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize enhanced logging system
        logging_level = config.get('logging_level', 'standard')
        self.trend_logger = TrendDetectionLogger(self.logger, logging_level)
        
        # Validate and correct configuration
        self.config_validator = ConfigurationValidator(self.logger)
        is_valid, validation_errors, corrected_config = self.config_validator.validate_config(config)
        
        if not is_valid:
            self.logger.warning(f"Configuration validation found {len(validation_errors)} issues. Using corrected values.")
            for error in validation_errors:
                self.logger.warning(f"  Config Error: {error}")
        
        # Use corrected configuration
        self.config = corrected_config
        
        # Initialize error handling and recovery systems
        self.error_recovery = ErrorRecoveryManager(self.logger)
        self.memory_manager = MemoryManager(max_memory_mb=self.config.get('max_memory_mb', 500))
        self.circuit_breakers = {}
        
        # Performance monitoring
        self.performance_stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'avg_analysis_time': 0.0,
            'max_analysis_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'memory_cleanups': 0,
            'component_failures': 0,
            'config_validation_errors': len(validation_errors)
        }
        
        # Initialize caching system with error handling
        try:
            cache_size = self.config.get('trend_cache_size', 1000)
            self.data_cache = DataCache(max_size=cache_size)
        except Exception as e:
            self.logger.error(f"Failed to initialize cache: {e}")
            self.data_cache = None
        
        # Configuration parameters (already validated)
        self.use_trend_detection = self.config.get('use_trend_detection', True)
        self.sensitivity = self.config.get('trend_detection_sensitivity', 5)
        self.min_confidence = self.config.get('min_trend_confidence', 0.6)
        self.enable_early_signals = self.config.get('enable_early_signals', True)
        
        # Performance optimization settings
        self.max_analysis_time_ms = self.config.get('max_analysis_time_ms', 100)
        self.enable_performance_monitoring = self.config.get('enable_performance_monitoring', True)
        self.cache_analysis_results = self.config.get('cache_analysis_results', True)
        
        # Error handling settings
        self.max_retries = self.config.get('max_error_retries', 3)
        self.enable_circuit_breaker = self.config.get('enable_circuit_breaker', True)
        self.graceful_degradation = self.config.get('graceful_degradation', True)
        
        # Initialize sub-components with comprehensive error handling
        self._initialize_components_with_recovery()
        
        # Log initialization summary with enhanced logging
        self.trend_logger.log_configuration_change('initialization', 'none', 
                                                  f"sensitivity={self.sensitivity}, cache_size={cache_size if 'cache_size' in locals() else 'unknown'}, "
                                                  f"max_time={self.max_analysis_time_ms}ms, validation_errors={len(validation_errors)}")
        
        self.logger.info(f"TrendDetectionEngine initialized with validated config - "
                        f"sensitivity={self.sensitivity}, cache_size={cache_size if 'cache_size' in locals() else 'unknown'}, "
                        f"max_time={self.max_analysis_time_ms}ms, validation_errors={len(validation_errors)}")
    
    def set_logging_level(self, level: str):
        """
        Update logging level for trend detection system
        
        Args:
            level: Logging level ('minimal', 'standard', 'detailed', 'debug')
        """
        self.trend_logger.set_logging_level(level)
        self.config['logging_level'] = level
        self.trend_logger.log_configuration_change('logging_level', 
                                                  self.trend_logger.logging_level, level)
    
    def validate_runtime_config(self, new_config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate configuration at runtime for dynamic updates with comprehensive trend detection parameter validation
        
        Args:
            new_config: New configuration to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            is_valid, validation_errors, _ = self.config_validator.validate_config(new_config)
            
            # Additional runtime-specific validations
            runtime_errors = []
            
            # Validate that critical components are available for enabled features
            if new_config.get('use_trend_detection', True):
                required_components = ['market_structure', 'aroon', 'ema', 'divergence']
                unavailable_components = [comp for comp in required_components 
                                        if not self.is_component_available(comp)]
                
                if unavailable_components:
                    runtime_errors.append(f"Trend detection enabled but components unavailable: {unavailable_components}")
            
            # Validate memory settings against current usage
            new_memory_limit = new_config.get('max_memory_mb', 500)
            current_usage = self.memory_manager.get_memory_usage_mb()
            if current_usage > new_memory_limit:
                runtime_errors.append(f"New memory limit ({new_memory_limit}MB) is below current usage ({current_usage:.1f}MB)")
            
            # Validate cache size changes
            new_cache_size = new_config.get('trend_cache_size', 1000)
            if new_cache_size < 10:
                runtime_errors.append("Cache size too small, minimum 10 entries required")
            
            # Validate performance settings
            new_max_time = new_config.get('max_analysis_time_ms', 100)
            if new_max_time < 10:
                runtime_errors.append("Analysis time limit too low, minimum 10ms required")
            
            # Log validation results
            all_errors = validation_errors + runtime_errors
            if all_errors:
                self.trend_logger.log_configuration_change('validation_failed', 
                    f'{len(all_errors)} errors', ', '.join(all_errors[:3]))
            else:
                self.trend_logger.log_configuration_change('validation_passed', 
                    'no errors', f'{len(new_config)} parameters validated')
            
            return len(all_errors) == 0, all_errors
            
        except Exception as e:
            self.logger.error(f"Error during runtime config validation: {e}")
            self.trend_logger.log_component_failure('config_validator', str(e))
            return False, [f"Validation error: {e}"]
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Update configuration with validation and enhanced logging
        
        Args:
            new_config: New configuration parameters
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Log configuration update attempt
            self.trend_logger.log_configuration_change('update_attempt', 
                'current_config', f'updating {len(new_config)} parameters')
            
            # Validate new configuration
            is_valid, validation_errors, corrected_config = self.config_validator.validate_config(new_config)
            
            if not is_valid:
                self.logger.warning(f"Config update validation found {len(validation_errors)} issues")
                for error in validation_errors:
                    self.logger.warning(f"  Config Error: {error}")
                
                # Decide whether to proceed with corrected config
                if len(validation_errors) > 10:  # Too many errors
                    self.logger.error("Too many validation errors, rejecting config update")
                    self.trend_logger.log_configuration_change('update_rejected', 
                        f'{len(validation_errors)} errors', 'too many validation errors')
                    return False
            
            # Track configuration changes for logging
            old_config = self.config.copy()
            changed_params = []
            
            # Update configuration
            self.config.update(corrected_config)
            
            # Track what actually changed
            for key, new_value in corrected_config.items():
                old_value = old_config.get(key, 'not_set')
                if old_value != new_value:
                    changed_params.append(f"{key}: {old_value} -> {new_value}")
                    self.trend_logger.log_configuration_change(key, old_value, new_value)
            
            # Update internal parameters
            self.use_trend_detection = self.config.get('use_trend_detection', True)
            self.sensitivity = self.config.get('trend_detection_sensitivity', 5)
            self.min_confidence = self.config.get('min_trend_confidence', 0.6)
            self.enable_early_signals = self.config.get('enable_early_signals', True)
            self.max_analysis_time_ms = self.config.get('max_analysis_time_ms', 100)
            self.enable_performance_monitoring = self.config.get('enable_performance_monitoring', True)
            self.cache_analysis_results = self.config.get('cache_analysis_results', True)
            self.max_retries = self.config.get('max_error_retries', 3)
            self.enable_circuit_breaker = self.config.get('enable_circuit_breaker', True)
            self.graceful_degradation = self.config.get('graceful_degradation', True)
            
            # Update logging level if changed
            new_logging_level = self.config.get('logging_level', 'standard')
            if new_logging_level != self.trend_logger.logging_level:
                self.trend_logger.set_logging_level(new_logging_level)
            
            # Update memory manager if limit changed
            new_memory_limit = self.config.get('max_memory_mb', 500)
            if new_memory_limit != old_config.get('max_memory_mb', 500):
                old_limit = self.memory_manager.max_memory_mb
                self.memory_manager.max_memory_mb = new_memory_limit
                self.trend_logger.log_configuration_change('memory_limit', old_limit, new_memory_limit)
            
            # Clear cache if cache size changed significantly
            new_cache_size = self.config.get('trend_cache_size', 1000)
            old_cache_size = old_config.get('trend_cache_size', 1000)
            if abs(new_cache_size - old_cache_size) > 100:
                self.clear_cache()
                if self.data_cache is not None:
                    self.data_cache.max_size = new_cache_size
                self.trend_logger.log_configuration_change('cache_size', old_cache_size, new_cache_size)
            
            # Log successful update
            self.logger.info(f"Configuration updated successfully (validation_errors: {len(validation_errors)})")
            if changed_params:
                self.logger.info(f"Changed parameters: {len(changed_params)}")
                for change in changed_params[:5]:  # Log first 5 changes
                    self.logger.debug(f"  {change}")
                if len(changed_params) > 5:
                    self.logger.debug(f"  ... and {len(changed_params) - 5} more changes")
            
            self.trend_logger.log_configuration_change('update_completed', 
                f'{len(changed_params)} changes', f'validation_errors: {len(validation_errors)}')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
            self.error_recovery.record_error('config_update', e)
            self.trend_logger.log_component_failure('config_manager', str(e))
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get current configuration information with validation status"""
        try:
            # Re-validate current config to check for any issues
            is_valid, validation_errors, _ = self.config_validator.validate_config(self.config)
            
            return {
                'current_config': self.config.copy(),
                'is_valid': is_valid,
                'validation_errors': validation_errors,
                'validation_summary': self.config_validator.get_validation_summary(),
                'config_keys_count': len(self.config),
                'last_validation_time': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting config info: {e}")
            return {
                'error': str(e),
                'current_config': self.config.copy() if hasattr(self, 'config') else {}
            }
    
    def _initialize_components_with_recovery(self):
        """Initialize trend detection components with comprehensive error handling and recovery"""
        self.components_status = {}
        
        # Component initialization with individual error handling
        components_to_init = [
            ('market_structure', 'src.market_structure_analyzer', 'MarketStructureAnalyzer'),
            ('aroon', 'src.aroon_indicator', 'AroonIndicator'),
            ('ema', 'src.ema_momentum_analyzer', 'EMAMomentumAnalyzer'),
            ('divergence', 'src.divergence_detector', 'DivergenceDetector'),
            ('multi_timeframe', 'src.multi_timeframe_analyzer', 'MultiTimeframeAnalyzer'),
            ('trendline', 'src.trendline_analyzer', 'TrendlineAnalyzer')
        ]
        
        for component_name, module_name, class_name in components_to_init:
            try:
                # Import module
                module = __import__(module_name, fromlist=[class_name])
                component_class = getattr(module, class_name)
                
                # Initialize with performance-optimized configuration
                perf_config = self.config.copy()
                perf_config.update({
                    'enable_caching': True,
                    'vectorized_operations': True,
                    'memory_efficient': True,
                    'error_recovery': True
                })
                
                # Special handling for AroonIndicator (different constructor)
                if component_name == 'aroon':
                    component = component_class(period=perf_config.get('aroon_period', 25))
                else:
                    component = component_class(perf_config)
                
                # Store component and mark as available
                setattr(self, f"{component_name}_analyzer" if component_name != 'aroon' else f"{component_name}_indicator", component)
                self.components_status[component_name] = 'available'
                
                # Initialize circuit breaker for this component
                if self.enable_circuit_breaker:
                    self.circuit_breakers[component_name] = CircuitBreaker(
                        failure_threshold=3,
                        recovery_timeout=60
                    )
                
                self.logger.debug(f"Component {component_name} initialized successfully")
                
            except ImportError as e:
                self.logger.error(f"Failed to import {component_name} component: {e}")
                self.components_status[component_name] = 'import_failed'
                setattr(self, f"{component_name}_analyzer" if component_name != 'aroon' else f"{component_name}_indicator", None)
                self.error_recovery.record_error('component_import', e, {'component': component_name})
                
            except Exception as e:
                self.logger.error(f"Failed to initialize {component_name} component: {e}")
                self.components_status[component_name] = 'init_failed'
                setattr(self, f"{component_name}_analyzer" if component_name != 'aroon' else f"{component_name}_indicator", None)
                self.error_recovery.record_error('component_init', e, {'component': component_name})
        
        # Set up weak references to avoid circular dependencies (only for successfully initialized components)
        self._components = {}
        for component_name in self.components_status:
            if self.components_status[component_name] == 'available':
                component = getattr(self, f"{component_name}_analyzer" if component_name != 'aroon' else f"{component_name}_indicator", None)
                if component is not None:
                    self._components[component_name] = weakref.ref(component)
        
        # Log initialization summary
        available_components = [name for name, status in self.components_status.items() if status == 'available']
        failed_components = [name for name, status in self.components_status.items() if status != 'available']
        
        self.logger.info(f"Component initialization complete: {len(available_components)} available, {len(failed_components)} failed")
        
        if available_components:
            self.logger.info(f"Available components: {', '.join(available_components)}")
        
        if failed_components:
            self.logger.warning(f"Failed components: {', '.join(failed_components)}")
            if not self.graceful_degradation:
                raise ComponentInitializationError(f"Critical components failed to initialize: {failed_components}")
    
    def get_component_status(self) -> Dict[str, str]:
        """Get status of all components"""
        return self.components_status.copy()
    
    def is_component_available(self, component_name: str) -> bool:
        """Check if a component is available for use"""
        return self.components_status.get(component_name) == 'available'
    
    def get_error_diagnostics(self) -> Dict[str, Any]:
        """Get comprehensive error diagnostics"""
        return {
            'error_recovery': self.error_recovery.get_diagnostic_report(),
            'component_status': self.get_component_status(),
            'performance_stats': self.get_performance_stats(),
            'memory_usage_mb': self.memory_manager.get_memory_usage_mb(),
            'circuit_breaker_states': {name: cb.state for name, cb in self.circuit_breakers.items()}
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        cache_total = self.performance_stats['cache_hits'] + self.performance_stats['cache_misses']
        cache_hit_rate = (self.performance_stats['cache_hits'] / cache_total * 100) if cache_total > 0 else 0
        
        return {
            **self.performance_stats,
            'cache_hit_rate_percent': cache_hit_rate,
            'cache_size': self.data_cache.size(),
            'cache_max_size': self.data_cache.max_size
        }
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self.data_cache.clear()
        self.logger.info("Trend detection cache cleared")
    
    @lru_cache(maxsize=128)
    def _get_cache_key(self, symbol: str, timeframe: int, data_hash: str) -> str:
        """Generate cache key for analysis results"""
        return f"{symbol}_{timeframe}_{data_hash}"
    
    def _get_data_hash(self, df: pd.DataFrame) -> str:
        """Generate hash for dataframe to detect changes"""
        if len(df) == 0:
            return "empty"
        
        # Use last few rows and key columns for hash
        key_data = df.tail(10)[['open', 'high', 'low', 'close']].values
        return str(hash(key_data.tobytes()))
    
    def _validate_input_data(self, df: pd.DataFrame, symbol: str) -> bool:
        """Validate input data for analysis with comprehensive error handling"""
        try:
            if df is None:
                self.logger.debug(f"No data provided for {symbol}")
                self.error_recovery.record_error('data_validation', DataValidationError("No data provided"), {'symbol': symbol})
                return False
                
            if len(df) < 50:
                self.logger.debug(f"Insufficient data for {symbol}: {len(df)} bars (minimum 50 required)")
                self.error_recovery.record_error('data_validation', DataValidationError("Insufficient data"), {'symbol': symbol, 'bars': len(df)})
                return False
                
            required_columns = ['open', 'high', 'low', 'close']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.logger.error(f"Missing required columns for {symbol}: {missing_columns}")
                self.error_recovery.record_error('data_validation', DataValidationError(f"Missing columns: {missing_columns}"), {'symbol': symbol})
                return False
                
            # Check for NaN values in recent data
            recent_data = df.tail(20)
            nan_columns = []
            for col in required_columns:
                if recent_data[col].isnull().any():
                    nan_columns.append(col)
            
            if nan_columns:
                self.logger.warning(f"NaN values detected in recent data for {symbol} in columns: {nan_columns}")
                
                # Try to handle NaN values
                if self.graceful_degradation:
                    try:
                        # Forward fill NaN values
                        df[nan_columns] = df[nan_columns].fillna(method='ffill')
                        self.logger.info(f"NaN values filled for {symbol}")
                    except Exception as e:
                        self.logger.error(f"Failed to fill NaN values for {symbol}: {e}")
                        self.error_recovery.record_error('data_validation', DataValidationError(f"NaN values in: {nan_columns}"), {'symbol': symbol})
                        return False
                else:
                    self.error_recovery.record_error('data_validation', DataValidationError(f"NaN values in: {nan_columns}"), {'symbol': symbol})
                    return False
            
            # Check for data integrity
            try:
                # Verify high >= low, high >= open, high >= close, low <= open, low <= close
                integrity_issues = []
                
                if (df['high'] < df['low']).any():
                    integrity_issues.append("high < low")
                if (df['high'] < df['open']).any():
                    integrity_issues.append("high < open")
                if (df['high'] < df['close']).any():
                    integrity_issues.append("high < close")
                if (df['low'] > df['open']).any():
                    integrity_issues.append("low > open")
                if (df['low'] > df['close']).any():
                    integrity_issues.append("low > close")
                
                if integrity_issues:
                    self.logger.warning(f"Data integrity issues for {symbol}: {integrity_issues}")
                    if not self.graceful_degradation:
                        self.error_recovery.record_error('data_validation', DataValidationError(f"Data integrity issues: {integrity_issues}"), {'symbol': symbol})
                        return False
                        
            except Exception as e:
                self.logger.error(f"Error checking data integrity for {symbol}: {e}")
                if not self.graceful_degradation:
                    return False
            
            # Check for reasonable price ranges
            try:
                price_columns = ['open', 'high', 'low', 'close']
                for col in price_columns:
                    if col in df.columns:
                        if (df[col] <= 0).any():
                            self.logger.error(f"Non-positive prices found in {col} for {symbol}")
                            if not self.graceful_degradation:
                                self.error_recovery.record_error('data_validation', DataValidationError(f"Non-positive prices in {col}"), {'symbol': symbol})
                                return False
                        
                        # Check for extreme values (more than 1000x difference)
                        price_range = df[col].max() / df[col].min()
                        if price_range > 1000:
                            self.logger.warning(f"Extreme price range in {col} for {symbol}: {price_range:.1f}x")
                            
            except Exception as e:
                self.logger.error(f"Error checking price ranges for {symbol}: {e}")
                if not self.graceful_degradation:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Unexpected error in data validation for {symbol}: {e}")
            self.error_recovery.record_error('data_validation', e, {'symbol': symbol})
            return False
    
    def detect_trend_weakness(self, df: pd.DataFrame, current_trend: str = 'auto') -> List[EarlyWarningSignal]:
        """
        Detect trend weakness patterns for early warning signals
        
        Detects:
        - Failure to create new highs in uptrends
        - Failure to create new lows in downtrends
        - Momentum divergence patterns
        - Volume exhaustion at extremes
        
        Args:
            df: Price data with indicators
            current_trend: 'up', 'down', or 'auto' to detect automatically
            
        Returns:
            List of early warning signals for trend weakness
        """
        if len(df) < 50:
            return []
        
        warnings = []
        current_price = df['close'].iloc[-1]
        current_time = datetime.now()
        
        # Auto-detect trend if not specified
        if current_trend == 'auto':
            # Use EMA relationship to determine trend
            if 'ema_20' in df.columns and 'ema_50' in df.columns:
                if df['ema_20'].iloc[-1] > df['ema_50'].iloc[-1]:
                    current_trend = 'up'
                elif df['ema_20'].iloc[-1] < df['ema_50'].iloc[-1]:
                    current_trend = 'down'
                else:
                    current_trend = 'sideways'
            else:
                # Fallback: use price action
                recent_highs = df['high'].rolling(10).max()
                recent_lows = df['low'].rolling(10).min()
                
                if current_price > recent_highs.iloc[-10]:
                    current_trend = 'up'
                elif current_price < recent_lows.iloc[-10]:
                    current_trend = 'down'
                else:
                    current_trend = 'sideways'
        
        # 1. Detect failure to create new highs in uptrend
        if current_trend == 'up':
            # Look for failure to make new highs over last 20 periods
            lookback_period = 20
            recent_df = df.iloc[-lookback_period:]
            
            # Find the highest high in the period
            highest_high = recent_df['high'].max()
            highest_high_idx = recent_df['high'].idxmax()
            
            # Check if we've failed to break above this high recently
            bars_since_high = len(recent_df) - recent_df.index.get_loc(highest_high_idx) - 1
            
            if bars_since_high >= 10:  # 10 bars without new high
                # Check for lower highs pattern
                recent_highs = []
                for i in range(5, len(recent_df) - 2):
                    if (recent_df['high'].iloc[i] > recent_df['high'].iloc[i-2:i].max() and
                        recent_df['high'].iloc[i] > recent_df['high'].iloc[i+1:i+3].max()):
                        recent_highs.append(recent_df['high'].iloc[i])
                
                if len(recent_highs) >= 2 and recent_highs[-1] < recent_highs[-2]:
                    # Lower highs detected in uptrend
                    strength = min(1.0, bars_since_high / 20.0)  # Stronger signal with more bars
                    confidence = 0.7 if len(recent_highs) >= 3 else 0.6
                    
                    # Check for volume confirmation
                    volume_confirmation = False
                    if hasattr(self, 'volume_analyzer'):
                        try:
                            from src.analyzers.volume_analyzer import VolumeAnalyzer
                            volume_analyzer = VolumeAnalyzer(self.config)
                            exhaustion = volume_analyzer.detect_exhaustion_volume(df, highest_high)
                            if exhaustion['detected'] and exhaustion['type'] == 'bullish_exhaustion':
                                volume_confirmation = True
                                confidence += 0.1
                        except:
                            pass
                    
                    factors = ['lower_highs_in_uptrend', f'no_new_high_{bars_since_high}_bars']
                    if volume_confirmation:
                        factors.append('volume_exhaustion')
                    
                    warnings.append(EarlyWarningSignal(
                        warning_type='trend_weakness',
                        confidence=confidence,
                        probability_score=self._calculate_probability_score('uptrend_weakness', factors),
                        price_level=highest_high,
                        current_price=current_price,
                        factors=factors,
                        strength=strength,
                        timestamp=current_time,
                        description=f"Uptrend weakness: Lower highs pattern, {bars_since_high} bars since high"
                    ))
        
        # 2. Detect failure to create new lows in downtrend
        elif current_trend == 'down':
            # Look for failure to make new lows over last 20 periods
            lookback_period = 20
            recent_df = df.iloc[-lookback_period:]
            
            # Find the lowest low in the period
            lowest_low = recent_df['low'].min()
            lowest_low_idx = recent_df['low'].idxmin()
            
            # Check if we've failed to break below this low recently
            bars_since_low = len(recent_df) - recent_df.index.get_loc(lowest_low_idx) - 1
            
            if bars_since_low >= 10:  # 10 bars without new low
                # Check for higher lows pattern
                recent_lows = []
                for i in range(5, len(recent_df) - 2):
                    if (recent_df['low'].iloc[i] < recent_df['low'].iloc[i-2:i].min() and
                        recent_df['low'].iloc[i] < recent_df['low'].iloc[i+1:i+3].min()):
                        recent_lows.append(recent_df['low'].iloc[i])
                
                if len(recent_lows) >= 2 and recent_lows[-1] > recent_lows[-2]:
                    # Higher lows detected in downtrend
                    strength = min(1.0, bars_since_low / 20.0)
                    confidence = 0.7 if len(recent_lows) >= 3 else 0.6
                    
                    # Check for volume confirmation
                    volume_confirmation = False
                    if hasattr(self, 'volume_analyzer'):
                        try:
                            from src.analyzers.volume_analyzer import VolumeAnalyzer
                            volume_analyzer = VolumeAnalyzer(self.config)
                            exhaustion = volume_analyzer.detect_exhaustion_volume(df, lowest_low)
                            if exhaustion['detected'] and exhaustion['type'] == 'bearish_exhaustion':
                                volume_confirmation = True
                                confidence += 0.1
                        except:
                            pass
                    
                    factors = ['higher_lows_in_downtrend', f'no_new_low_{bars_since_low}_bars']
                    if volume_confirmation:
                        factors.append('volume_exhaustion')
                    
                    warnings.append(EarlyWarningSignal(
                        warning_type='trend_weakness',
                        confidence=confidence,
                        probability_score=self._calculate_probability_score('downtrend_weakness', factors),
                        price_level=lowest_low,
                        current_price=current_price,
                        factors=factors,
                        strength=strength,
                        timestamp=current_time,
                        description=f"Downtrend weakness: Higher lows pattern, {bars_since_low} bars since low"
                    ))
        
        # 3. Detect momentum divergence as early warning
        try:
            if hasattr(self, 'divergence_analyzer'):
                # Check for early divergence patterns (less strict criteria)
                rsi_divergence = self.divergence_analyzer.detect_rsi_divergence(df, min_strength=0.4)
                if rsi_divergence and rsi_divergence.strength >= 0.4:
                    warning_type = 'trend_weakness'
                    confidence = 0.6 + (rsi_divergence.strength - 0.4) * 0.5  # Scale from 0.6 to 0.9
                    
                    factors = ['rsi_divergence_early', f'strength_{rsi_divergence.strength:.2f}']
                    
                    warnings.append(EarlyWarningSignal(
                        warning_type=warning_type,
                        confidence=confidence,
                        probability_score=self._calculate_probability_score('rsi_divergence_early', factors),
                        price_level=current_price,
                        current_price=current_price,
                        factors=factors,
                        strength=rsi_divergence.strength,
                        timestamp=current_time,
                        description=f"Early RSI divergence detected: {rsi_divergence.divergence_type}"
                    ))
        except:
            pass
        
        return warnings
    
    def monitor_key_levels(self, df: pd.DataFrame, sensitivity_multiplier: float = 1.5) -> List[EarlyWarningSignal]:
        """
        Monitor price approaches to significant support/resistance levels with increased sensitivity
        
        Args:
            df: Price data with indicators
            sensitivity_multiplier: Multiplier for detection sensitivity (higher = more sensitive)
            
        Returns:
            List of early warning signals for key level approaches
        """
        if len(df) < 100:
            return []
        
        warnings = []
        current_price = df['close'].iloc[-1]
        current_time = datetime.now()
        
        # 1. Identify key support and resistance levels
        key_levels = self._identify_key_levels(df)
        
        # 2. Check proximity to key levels with increased sensitivity
        proximity_threshold = 0.002 * sensitivity_multiplier  # 0.2% * sensitivity
        
        for level_info in key_levels:
            level_price = level_info['price']
            level_type = level_info['type']  # 'support' or 'resistance'
            level_strength = level_info['strength']
            level_touches = level_info['touches']
            
            # Calculate distance to level
            distance_pct = abs(current_price - level_price) / level_price
            
            if distance_pct <= proximity_threshold:
                # We're approaching a key level
                approach_strength = 1.0 - (distance_pct / proximity_threshold)
                
                # Determine expected reaction based on level type and trend
                if level_type == 'resistance' and current_price < level_price:
                    warning_type = 'key_level_approach'
                    expected_reaction = 'rejection'
                elif level_type == 'support' and current_price > level_price:
                    warning_type = 'key_level_approach'
                    expected_reaction = 'bounce'
                else:
                    # Price is above resistance or below support - potential breakout
                    warning_type = 'key_level_approach'
                    expected_reaction = 'breakout'
                
                # Calculate confidence based on level strength and historical touches
                base_confidence = 0.5 + (level_strength * 0.3)  # 0.5 to 0.8
                touch_bonus = min(0.15, level_touches * 0.03)   # Up to 0.15 bonus
                proximity_bonus = approach_strength * 0.1       # Up to 0.1 bonus
                
                confidence = min(0.95, base_confidence + touch_bonus + proximity_bonus)
                
                # Check for volume confirmation
                volume_confirmation = False
                volume_analysis = {}
                
                try:
                    from src.analyzers.volume_analyzer import VolumeAnalyzer
                    volume_analyzer = VolumeAnalyzer(self.config)
                    
                    # Check if volume is increasing as we approach the level
                    volume_trend = volume_analyzer.get_volume_trend(df.iloc[-10:])
                    if volume_trend == 'increasing':
                        volume_confirmation = True
                        confidence += 0.05
                    
                    # Check for potential breakout volume
                    if expected_reaction == 'breakout':
                        breakout_direction = 'up' if level_type == 'resistance' else 'down'
                        breakout_confirmation = volume_analyzer.confirm_breakout_volume(
                            df, level_price, breakout_direction
                        )
                        if breakout_confirmation['confirmed']:
                            volume_confirmation = True
                            confidence += 0.1
                            volume_analysis = breakout_confirmation
                    
                except:
                    pass
                
                factors = [
                    f'{level_type}_level',
                    f'strength_{level_strength:.2f}',
                    f'touches_{level_touches}',
                    f'distance_{distance_pct:.3%}',
                    f'expected_{expected_reaction}'
                ]
                
                if volume_confirmation:
                    factors.append('volume_confirmation')
                
                description = (f"Approaching {level_type} at {level_price:.5f} "
                             f"({distance_pct:.2%} away), expecting {expected_reaction}")
                
                warnings.append(EarlyWarningSignal(
                    warning_type=warning_type,
                    confidence=confidence,
                    probability_score=self._calculate_probability_score(f'{level_type}_approach', factors),
                    price_level=level_price,
                    current_price=current_price,
                    factors=factors,
                    strength=approach_strength,
                    timestamp=current_time,
                    description=description
                ))
        
        # 3. Detect reversal patterns at key levels
        reversal_warnings = self._detect_reversal_patterns_at_levels(df, key_levels)
        warnings.extend(reversal_warnings)
        
        return warnings
    
    def _identify_key_levels(self, df: pd.DataFrame, min_touches: int = 2) -> List[Dict]:
        """
        Identify significant support and resistance levels
        
        Args:
            df: Price data
            min_touches: Minimum number of touches to consider a level significant
            
        Returns:
            List of key level information dictionaries
        """
        key_levels = []
        
        # Use last 200 bars for level identification
        analysis_df = df.iloc[-200:] if len(df) > 200 else df
        
        # Find swing highs and lows
        swing_highs = []
        swing_lows = []
        
        for i in range(5, len(analysis_df) - 5):
            current_high = analysis_df['high'].iloc[i]
            current_low = analysis_df['low'].iloc[i]
            
            # Check for swing high
            if (current_high >= analysis_df['high'].iloc[i-5:i].max() and
                current_high >= analysis_df['high'].iloc[i+1:i+6].max()):
                swing_highs.append((analysis_df.index[i], current_high))
            
            # Check for swing low
            if (current_low <= analysis_df['low'].iloc[i-5:i].min() and
                current_low <= analysis_df['low'].iloc[i+1:i+6].min()):
                swing_lows.append((analysis_df.index[i], current_low))
        
        # Group similar price levels (within 0.1% of each other)
        def group_levels(levels, level_type):
            if not levels:
                return []
            
            grouped = []
            tolerance = 0.001  # 0.1%
            
            for timestamp, price in levels:
                # Find existing group for this price
                found_group = False
                for group in grouped:
                    group_price = group['price']
                    if abs(price - group_price) / group_price <= tolerance:
                        # Add to existing group
                        group['touches'] += 1
                        group['timestamps'].append(timestamp)
                        # Update price to average
                        group['price'] = (group['price'] * (group['touches'] - 1) + price) / group['touches']
                        found_group = True
                        break
                
                if not found_group:
                    # Create new group
                    grouped.append({
                        'price': price,
                        'type': level_type,
                        'touches': 1,
                        'timestamps': [timestamp],
                        'strength': 0.5  # Will be calculated later
                    })
            
            return grouped
        
        # Group swing highs and lows
        resistance_groups = group_levels(swing_highs, 'resistance')
        support_groups = group_levels(swing_lows, 'support')
        
        # Calculate strength and filter by minimum touches
        all_groups = resistance_groups + support_groups
        
        for group in all_groups:
            if group['touches'] >= min_touches:
                # Calculate strength based on touches, recency, and volume
                touch_strength = min(1.0, group['touches'] / 5.0)  # Max strength at 5 touches
                
                # Recency bonus (more recent touches are stronger)
                recent_touches = sum(1 for ts in group['timestamps'] 
                                   if len(df) - df.index.get_loc(ts) <= 50)
                recency_strength = min(0.3, recent_touches * 0.1)
                
                group['strength'] = min(1.0, touch_strength + recency_strength)
                key_levels.append(group)
        
        # Sort by strength (strongest first)
        key_levels.sort(key=lambda x: x['strength'], reverse=True)
        
        # Return top 10 levels to avoid noise
        return key_levels[:10]
    
    def _detect_reversal_patterns_at_levels(self, df: pd.DataFrame, key_levels: List[Dict]) -> List[EarlyWarningSignal]:
        """
        Detect reversal patterns at key support/resistance levels
        
        Args:
            df: Price data
            key_levels: List of key level information
            
        Returns:
            List of reversal pattern early warning signals
        """
        warnings = []
        current_price = df['close'].iloc[-1]
        current_time = datetime.now()
        
        # Look for reversal patterns in the last 10 bars
        recent_df = df.iloc[-10:]
        
        for level_info in key_levels:
            level_price = level_info['price']
            level_type = level_info['type']
            level_strength = level_info['strength']
            
            # Check if price has interacted with this level recently
            level_tolerance = level_price * 0.002  # 0.2% tolerance
            
            level_interactions = []
            for i, row in recent_df.iterrows():
                if (row['low'] <= level_price + level_tolerance and 
                    row['high'] >= level_price - level_tolerance):
                    level_interactions.append((i, row))
            
            if not level_interactions:
                continue
            
            # Analyze the most recent interaction
            last_interaction_idx, last_interaction = level_interactions[-1]
            
            # Check for reversal patterns
            if level_type == 'support' and current_price > level_price:
                # Look for bounce from support
                if (last_interaction['low'] <= level_price + level_tolerance and
                    current_price > last_interaction['low'] * 1.005):  # 0.5% bounce
                    
                    # Calculate bounce strength
                    bounce_pct = (current_price - last_interaction['low']) / last_interaction['low']
                    bounce_strength = min(1.0, bounce_pct / 0.02)  # Max strength at 2% bounce
                    
                    # Check for volume confirmation
                    volume_confirmed = False
                    try:
                        from src.analyzers.volume_analyzer import VolumeAnalyzer
                        volume_analyzer = VolumeAnalyzer(self.config)
                        
                        # Check if bounce came with volume
                        bounce_bars = df.loc[last_interaction_idx:]
                        if len(bounce_bars) >= 2:
                            avg_volume = df['tick_volume'].rolling(20).mean().iloc[-1]
                            bounce_volume = bounce_bars['tick_volume'].mean()
                            if bounce_volume > avg_volume * 1.2:
                                volume_confirmed = True
                    except:
                        pass
                    
                    confidence = 0.6 + (level_strength * 0.2) + (bounce_strength * 0.15)
                    if volume_confirmed:
                        confidence += 0.1
                    
                    factors = [
                        'support_bounce',
                        f'level_strength_{level_strength:.2f}',
                        f'bounce_{bounce_pct:.2%}',
                        f'touches_{level_info["touches"]}'
                    ]
                    
                    if volume_confirmed:
                        factors.append('volume_confirmation')
                    
                    warnings.append(EarlyWarningSignal(
                        warning_type='reversal_pattern',
                        confidence=confidence,
                        probability_score=self._calculate_probability_score('support_bounce', factors),
                        price_level=level_price,
                        current_price=current_price,
                        factors=factors,
                        strength=bounce_strength,
                        timestamp=current_time,
                        description=f"Support bounce at {level_price:.5f} ({bounce_pct:.2%} recovery)"
                    ))
            
            elif level_type == 'resistance' and current_price < level_price:
                # Look for rejection from resistance
                if (last_interaction['high'] >= level_price - level_tolerance and
                    current_price < last_interaction['high'] * 0.995):  # 0.5% rejection
                    
                    # Calculate rejection strength
                    rejection_pct = (last_interaction['high'] - current_price) / last_interaction['high']
                    rejection_strength = min(1.0, rejection_pct / 0.02)  # Max strength at 2% rejection
                    
                    # Check for volume confirmation
                    volume_confirmed = False
                    try:
                        from src.analyzers.volume_analyzer import VolumeAnalyzer
                        volume_analyzer = VolumeAnalyzer(self.config)
                        
                        # Check if rejection came with volume
                        rejection_bars = df.loc[last_interaction_idx:]
                        if len(rejection_bars) >= 2:
                            avg_volume = df['tick_volume'].rolling(20).mean().iloc[-1]
                            rejection_volume = rejection_bars['tick_volume'].mean()
                            if rejection_volume > avg_volume * 1.2:
                                volume_confirmed = True
                    except:
                        pass
                    
                    confidence = 0.6 + (level_strength * 0.2) + (rejection_strength * 0.15)
                    if volume_confirmed:
                        confidence += 0.1
                    
                    factors = [
                        'resistance_rejection',
                        f'level_strength_{level_strength:.2f}',
                        f'rejection_{rejection_pct:.2%}',
                        f'touches_{level_info["touches"]}'
                    ]
                    
                    if volume_confirmed:
                        factors.append('volume_confirmation')
                    
                    warnings.append(EarlyWarningSignal(
                        warning_type='reversal_pattern',
                        confidence=confidence,
                        probability_score=self._calculate_probability_score('resistance_rejection', factors),
                        price_level=level_price,
                        current_price=current_price,
                        factors=factors,
                        strength=rejection_strength,
                        timestamp=current_time,
                        description=f"Resistance rejection at {level_price:.5f} ({rejection_pct:.2%} decline)"
                    ))
        
        return warnings
    
    def _calculate_probability_score(self, pattern_type: str, factors: List[str]) -> float:
        """
        Calculate probability score based on historical accuracy of pattern types
        
        This is a simplified implementation. In production, this would use
        historical backtesting data to calculate actual success rates.
        
        Args:
            pattern_type: Type of pattern detected
            factors: List of supporting factors
            
        Returns:
            Probability score (0.0 to 1.0)
        """
        # Base probability scores for different pattern types
        base_probabilities = {
            'uptrend_weakness': 0.65,
            'downtrend_weakness': 0.65,
            'rsi_divergence_early': 0.60,
            'support_approach': 0.70,
            'resistance_approach': 0.70,
            'support_bounce': 0.75,
            'resistance_rejection': 0.75,
            'breakout_pattern': 0.55
        }
        
        base_prob = base_probabilities.get(pattern_type, 0.50)
        
        # Adjust based on supporting factors
        factor_adjustments = {
            'volume_confirmation': +0.10,
            'volume_exhaustion': +0.08,
            'multiple_touches': +0.05,
            'recent_interaction': +0.03,
            'strong_level': +0.05,
            'momentum_divergence': +0.07
        }
        
        total_adjustment = 0.0
        for factor in factors:
            for key, adjustment in factor_adjustments.items():
                if key in factor:
                    total_adjustment += adjustment
                    break
        
        # Cap adjustments to prevent unrealistic probabilities
        total_adjustment = min(0.25, max(-0.25, total_adjustment))
        
        final_probability = max(0.1, min(0.95, base_prob + total_adjustment))
        
        return final_probability

    def analyze_trend_change(self, df: pd.DataFrame, symbol: str) -> TrendAnalysisResult:
        """
        Perform comprehensive trend change analysis with robust error handling and recovery
        
        Args:
            df: Price data with indicators
            symbol: Trading symbol
            
        Returns:
            TrendAnalysisResult with all analysis components
        """
        # Enhanced logging: Start analysis
        timeframe_name = self.config.get('timeframe_name', str(self.config.get('timeframe', 'unknown')))
        self.trend_logger.log_analysis_start_event(symbol, timeframe_name)
        
        # Start performance timer and memory monitoring
        analysis_start_time = time.perf_counter()
        
        # Use config threshold for performance warnings
        warning_threshold = self.config.get('max_analysis_time_ms', 250)
        with PerformanceTimer(f"Trend Analysis - {symbol}", self.logger, warning_threshold) as timer:
            with self.memory_manager.memory_monitor(f"trend_analysis_{symbol}"):
                
                # Update performance stats
                self.performance_stats['total_analyses'] += 1
                
                # Log memory usage
                memory_usage = self.memory_manager.get_memory_usage_mb()
                self.trend_logger.log_memory_usage(f"analysis_start_{symbol}", 
                                                 memory_usage, self.memory_manager.max_memory_mb)
                
                try:
                    # Check memory limits before starting
                    if not self.memory_manager.check_memory_limit():
                        self.memory_manager.force_cleanup()
                        self.performance_stats['memory_cleanups'] += 1
                        self.trend_logger.log_error_recovery('memory_manager', 'memory_limit_exceeded', 'force_cleanup')
                        
                        # Recheck after cleanup
                        if not self.memory_manager.check_memory_limit():
                            raise MemoryError("Memory usage exceeds limits even after cleanup")
                    
                    # Validate input data with comprehensive error handling
                    if not self.use_trend_detection:
                        self.trend_logger.log_data_validation(symbol, 'disabled', 'trend detection disabled in config')
                        return self._create_empty_result()
                        
                    if not self._validate_input_data(df, symbol):
                        self.trend_logger.log_data_validation(symbol, 'failed', f'insufficient or invalid data (bars: {len(df)})')
                        return self._create_empty_result()
                    
                    self.trend_logger.log_data_validation(symbol, 'passed', f'validated {len(df)} bars')
                    
                    # Check cache first (with error handling)
                    cached_result = None
                    if self.cache_analysis_results and self.data_cache is not None:
                        try:
                            data_hash = self._get_data_hash(df)
                            timeframe = self.config.get('timeframe', 30)
                            cache_key = self._get_cache_key(symbol, timeframe, data_hash)
                            
                            cached_result = self.data_cache.get(cache_key)
                            if cached_result is not None:
                                self.performance_stats['cache_hits'] += 1
                                self.performance_stats['successful_analyses'] += 1
                                self.trend_logger.log_cache_operation('get', cache_key, hit=True)
                                
                                # Log cached result summary
                                elapsed_ms = (time.perf_counter() - analysis_start_time) * 1000
                                self.trend_logger.log_analysis_complete(symbol, len(cached_result.signals), 
                                                                     cached_result.confidence, elapsed_ms)
                                return cached_result
                            else:
                                self.performance_stats['cache_misses'] += 1
                                self.trend_logger.log_cache_operation('get', cache_key, hit=False)
                        except Exception as e:
                            self.logger.error(f"Cache access error for {symbol}: {e}")
                            self.error_recovery.record_error('cache_error', e, {'symbol': symbol})
                            self.trend_logger.log_error_recovery('cache', 'access_error', 'continue_without_cache')
                    
                    # Perform analysis with timeout protection and error recovery
                    result = self._perform_analysis_with_error_handling(df, symbol)
                    
                    # Cache the result (with error handling)
                    if self.cache_analysis_results and self.data_cache is not None and result is not None:
                        try:
                            self.data_cache.set(cache_key, result)
                            self.trend_logger.log_cache_operation('set', cache_key)
                        except Exception as e:
                            self.logger.error(f"Cache storage error for {symbol}: {e}")
                            self.error_recovery.record_error('cache_error', e, {'symbol': symbol})
                            self.trend_logger.log_error_recovery('cache', 'storage_error', 'continue_without_caching')
                    
                    # Update performance statistics
                    elapsed_ms = (time.perf_counter() - analysis_start_time) * 1000
                    self._update_performance_stats(elapsed_ms, success=True)
                    
                    # Enhanced logging: Analysis complete
                    self.trend_logger.log_analysis_complete(symbol, len(result.signals), 
                                                          result.confidence, elapsed_ms)
                    
                    # Log performance warning if needed
                    if elapsed_ms > self.max_analysis_time_ms:
                        self.trend_logger.log_performance_warning(f"trend_analysis_{symbol}", 
                                                                elapsed_ms, self.max_analysis_time_ms)
                    
                    self.performance_stats['successful_analyses'] += 1
                    return result
                    
                except AnalysisTimeoutError as e:
                    self.logger.warning(f"Analysis timeout for {symbol}: {e}")
                    self.error_recovery.record_error('analysis_timeout', e, {'symbol': symbol})
                    self.trend_logger.log_component_failure('analysis_engine', f'timeout: {e}', symbol)
                    self.performance_stats['failed_analyses'] += 1
                    return self._create_empty_result()
                    
                except MemoryError as e:
                    self.logger.error(f"Memory error during analysis for {symbol}: {e}")
                    self.error_recovery.record_error('memory_error', e, {'symbol': symbol})
                    self.trend_logger.log_component_failure('memory_manager', f'memory_error: {e}', symbol)
                    self.memory_manager.force_cleanup()
                    self.performance_stats['failed_analyses'] += 1
                    return self._create_empty_result()
                    
                except Exception as e:
                    self.logger.error(f"❌ Unexpected error in trend analysis for {symbol}: {e}")
                    self.error_recovery.record_error('analysis_error', e, {'symbol': symbol})
                    self.trend_logger.log_component_failure('analysis_engine', f'unexpected_error: {e}', symbol)
                    
                    if self.logger.isEnabledFor(logging.DEBUG):
                        self.logger.debug(f"Traceback: {traceback.format_exc()}")
                    
                    # Update performance stats
                    elapsed_ms = (time.perf_counter() - analysis_start_time) * 1000
                    self._update_performance_stats(elapsed_ms, success=False)
                    
                    self.performance_stats['failed_analyses'] += 1
                    return self._create_empty_result()
                    if self.cache_analysis_results and self.data_cache is not None and result is not None:
                        try:
                            self.data_cache.set(cache_key, result)
                        except Exception as e:
                            self.logger.error(f"Cache storage error for {symbol}: {e}")
                            self.error_recovery.record_error('cache_error', e, {'symbol': symbol})
                    
                    # Update performance statistics
                    elapsed_ms = (time.perf_counter() - timer.start_time) * 1000
                    self._update_performance_stats(elapsed_ms, success=True)
                    
                    self.performance_stats['successful_analyses'] += 1
                    return result
                    
                except AnalysisTimeoutError as e:
                    self.logger.warning(f"Analysis timeout for {symbol}: {e}")
                    self.error_recovery.record_error('analysis_timeout', e, {'symbol': symbol})
                    self.performance_stats['failed_analyses'] += 1
                    return self._create_empty_result()
                    
                except MemoryError as e:
                    self.logger.error(f"Memory error during analysis for {symbol}: {e}")
                    self.error_recovery.record_error('memory_error', e, {'symbol': symbol})
                    self.memory_manager.force_cleanup()
                    self.performance_stats['failed_analyses'] += 1
                    return self._create_empty_result()
                    
                except Exception as e:
                    self.logger.error(f"❌ Unexpected error in trend analysis for {symbol}: {e}")
                    self.error_recovery.record_error('analysis_error', e, {'symbol': symbol})
                    
                    if self.logger.isEnabledFor(logging.DEBUG):
                        self.logger.debug(f"Traceback: {traceback.format_exc()}")
                    
                    # Update performance stats
                    elapsed_ms = (time.perf_counter() - timer.start_time) * 1000
                    self._update_performance_stats(elapsed_ms, success=False)
                    
                    self.performance_stats['failed_analyses'] += 1
                    return self._create_empty_result()
    
    def _perform_analysis_with_error_handling(self, df: pd.DataFrame, symbol: str) -> TrendAnalysisResult:
        """
        Perform analysis with comprehensive error handling and recovery strategies
        """
        start_time = time.perf_counter()
        max_time_seconds = self.max_analysis_time_ms / 1000.0
        
        # Initialize result components
        signals = []
        current_price = df.iloc[-1]['close']
        
        # Track analysis progress for timeout handling
        analysis_steps = [
            ('market_structure', self._analyze_market_structure_safe),
            ('aroon', self._analyze_aroon_safe),
            ('ema', self._analyze_ema_safe),
            ('divergence', self._analyze_divergence_safe),
            ('trendline', self._analyze_trendline_safe),
            ('multi_timeframe', self._analyze_multi_timeframe_safe),
            ('volume', self._analyze_volume_safe),
            ('early_warnings', self._analyze_early_warnings_safe)
        ]
        
        # Results storage
        analysis_results = {}
        
        # Map step names to component names
        step_to_component = {
            'market_structure': 'market_structure',
            'aroon': 'aroon',
            'ema': 'ema',
            'divergence': 'divergence',
            'trendline': 'trendline',
            'multi_timeframe': 'multi_timeframe',
            'volume': 'volume',  # Special case - no component check needed
            'early_warnings': None  # Special case - no component check needed
        }
        
        # Execute analysis steps with timeout checking and error recovery
        for step_name, analysis_func in analysis_steps:
            # Check timeout before each step
            elapsed = time.perf_counter() - start_time
            if elapsed > max_time_seconds * 0.8:  # Use 80% of max time as safety margin
                self.logger.warning(f"⚠️ Analysis timeout approaching for {symbol}, skipping {step_name}")
                break
            
            # Check if component is available (skip check for special cases)
            component_name = step_to_component.get(step_name)
            if component_name is not None and not self.is_component_available(component_name):
                self.logger.debug(f"Component {component_name} not available, skipping {step_name}")
                analysis_results[step_name] = None
                continue
            
            # Execute with circuit breaker protection
            try:
                step_start = time.perf_counter()
                
                if self.enable_circuit_breaker and step_name in self.circuit_breakers:
                    result = self.circuit_breakers[step_name].call(analysis_func, df, symbol)
                else:
                    result = analysis_func(df, symbol)
                
                step_time = (time.perf_counter() - step_start) * 1000
                analysis_results[step_name] = result
                
                if step_time > 20:  # Log slow steps
                    self.logger.debug(f"Slow analysis step {step_name}: {step_time:.1f}ms")
                    
            except TrendDetectionError as e:
                self.logger.warning(f"Component error in {step_name} for {symbol}: {e}")
                self.error_recovery.record_error(f'{step_name}_error', e, {'symbol': symbol})
                self.performance_stats['component_failures'] += 1
                analysis_results[step_name] = None
                
                # Apply recovery strategy if available
                recovery_strategy = self.error_recovery.get_recovery_strategy(step_name)
                if recovery_strategy == 'skip_component':
                    self.logger.info(f"Skipping {step_name} component due to repeated failures")
                    continue
                    
            except Exception as e:
                self.logger.error(f"Unexpected error in {step_name} analysis for {symbol}: {e}")
                self.error_recovery.record_error(f'{step_name}_error', e, {'symbol': symbol})
                self.performance_stats['component_failures'] += 1
                analysis_results[step_name] = None
        
        # Compile results efficiently with error handling
        try:
            return self._compile_analysis_results(analysis_results, signals, current_price)
        except Exception as e:
            self.logger.error(f"Error compiling analysis results for {symbol}: {e}")
            self.error_recovery.record_error('compilation_error', e, {'symbol': symbol})
            return self._create_empty_result()
    
    def _analyze_market_structure_safe(self, df: pd.DataFrame, symbol: str) -> Optional[StructureBreakResult]:
        """Safe market structure analysis with error handling"""
        try:
            if not self.is_component_available('market_structure'):
                self.trend_logger.log_component_analysis('market_structure', symbol, 'component not available')
                return None
            
            result = self.market_structure_analyzer.detect_structure_break(df)
            
            if result:
                self.trend_logger.log_component_analysis('market_structure', symbol, 
                    f'{result.break_type} at {result.break_level:.5f} (strength={result.strength:.2f}, '
                    f'volume_confirmed={result.volume_confirmation})')
            else:
                self.trend_logger.log_component_analysis('market_structure', symbol, 'no structure breaks detected')
            
            return result
        except Exception as e:
            self.trend_logger.log_component_failure('market_structure', str(e), symbol)
            raise TrendDetectionError(f"Market structure analysis failed: {e}")
    
    def _analyze_aroon_safe(self, df: pd.DataFrame, symbol: str) -> Optional[AroonSignal]:
        """Safe Aroon analysis with error handling"""
        try:
            if not self.is_component_available('aroon'):
                self.trend_logger.log_component_analysis('aroon', symbol, 'component not available')
                return None
            
            result = self.aroon_indicator.get_aroon_signal(df)
            
            if result:
                self.trend_logger.log_component_analysis('aroon', symbol, 
                    f'{result.signal_type} (up={result.aroon_up:.1f}, down={result.aroon_down:.1f}, '
                    f'strength={result.trend_strength:.2f})')
            else:
                self.trend_logger.log_component_analysis('aroon', symbol, 'no aroon signals generated')
            
            return result
        except Exception as e:
            self.trend_logger.log_component_failure('aroon', str(e), symbol)
            raise TrendDetectionError(f"Aroon analysis failed: {e}")
    
    def _analyze_ema_safe(self, df: pd.DataFrame, symbol: str) -> Optional['EMASignal']:
        """Safe EMA analysis with error handling"""
        try:
            if not self.is_component_available('ema'):
                self.trend_logger.log_component_analysis('ema', symbol, 'component not available')
                return None
            
            result = self.ema_analyzer.get_ema_signal(df)
            
            if result:
                self.trend_logger.log_component_analysis('ema', symbol, 
                    f'{result.signal_type} (separation={result.separation:.2f}%, '
                    f'momentum={result.momentum_strength:.2f}, confirmed={result.crossover_confirmed})')
            else:
                self.trend_logger.log_component_analysis('ema', symbol, 'no ema signals generated')
            
            return result
        except Exception as e:
            self.trend_logger.log_component_failure('ema', str(e), symbol)
            raise TrendDetectionError(f"EMA analysis failed: {e}")
    
    def _analyze_divergence_safe(self, df: pd.DataFrame, symbol: str) -> List[DivergenceResult]:
        """Safe divergence analysis with error handling"""
        try:
            if not self.is_component_available('divergence'):
                self.trend_logger.log_component_analysis('divergence', symbol, 'component not available')
                return []
            
            divergences = []
            
            # Try RSI divergence first (less computationally expensive)
            try:
                rsi_div = self.divergence_analyzer.detect_rsi_divergence(df)
                if rsi_div and rsi_div.validated:
                    divergences.append(rsi_div)
                    self.trend_logger.log_component_analysis('divergence', symbol, 
                        f'RSI {rsi_div.divergence_type} (strength={rsi_div.strength:.2f})')
            except Exception as e:
                self.trend_logger.log_component_failure('divergence_rsi', str(e), symbol)
            
            # Only check MACD if we have time and no RSI divergence found
            if not divergences:
                try:
                    macd_div = self.divergence_analyzer.detect_macd_divergence(df)
                    if macd_div and macd_div.validated:
                        divergences.append(macd_div)
                        self.trend_logger.log_component_analysis('divergence', symbol, 
                            f'MACD {macd_div.divergence_type} (strength={macd_div.strength:.2f})')
                except Exception as e:
                    self.trend_logger.log_component_failure('divergence_macd', str(e), symbol)
            
            if not divergences:
                self.trend_logger.log_component_analysis('divergence', symbol, 'no validated divergences detected')
            
            return divergences
            
        except Exception as e:
            self.trend_logger.log_component_failure('divergence', str(e), symbol)
            raise TrendDetectionError(f"Divergence analysis failed: {e}")
    
    def _analyze_trendline_safe(self, df: pd.DataFrame, symbol: str) -> List[TrendlineBreak]:
        """Safe trendline analysis with error handling"""
        try:
            if not self.is_component_available('trendline'):
                return []
            
            # Use cached trendlines if available
            cache_key = f"trendlines_{symbol}_{len(df)}"
            cached_trendlines = None
            
            if self.data_cache is not None:
                try:
                    cached_trendlines = self.data_cache.get(cache_key)
                except Exception as e:
                    self.logger.debug(f"Trendline cache access failed: {e}")
            
            if cached_trendlines is None:
                # Limit trendline identification for speed and reliability
                try:
                    trendlines = self.trendline_analyzer.identify_trendlines(df)
                    active_trendlines = self.trendline_analyzer.get_active_trendlines(df, trendlines)
                    
                    # Cache for reuse
                    if self.data_cache is not None:
                        try:
                            self.data_cache.set(cache_key, active_trendlines)
                        except Exception as e:
                            self.logger.debug(f"Trendline cache storage failed: {e}")
                            
                except Exception as e:
                    self.logger.debug(f"Trendline identification failed for {symbol}: {e}")
                    return []
            else:
                active_trendlines = cached_trendlines
            
            # Detect breaks in active trendlines
            try:
                return self.trendline_analyzer.detect_trendline_breaks(df, active_trendlines)
            except Exception as e:
                self.logger.debug(f"Trendline break detection failed for {symbol}: {e}")
                return []
                
        except Exception as e:
            self.logger.debug(f"Trendline analysis failed for {symbol}: {e}")
            raise TrendDetectionError(f"Trendline analysis failed: {e}")
    
    def _analyze_multi_timeframe_safe(self, df: pd.DataFrame, symbol: str) -> Optional[TimeframeAlignment]:
        """Safe multi-timeframe analysis with error handling"""
        try:
            if not self.is_component_available('multi_timeframe'):
                return None
            
            primary_timeframe = self.config.get('timeframe', 30)
            
            # Use cached higher timeframe data if available
            cache_key = f"mtf_data_{symbol}_{primary_timeframe}"
            higher_df = None
            
            if self.data_cache is not None:
                try:
                    higher_df = self.data_cache.get(cache_key)
                except Exception as e:
                    self.logger.debug(f"MTF cache access failed: {e}")
            
            if higher_df is None:
                try:
                    higher_df = self.multi_timeframe_analyzer.get_higher_timeframe_data(symbol, primary_timeframe)
                    if higher_df is not None and self.data_cache is not None:
                        # Cache for 5 minutes (higher timeframe data changes less frequently)
                        try:
                            self.data_cache.set(cache_key, higher_df)
                        except Exception as e:
                            self.logger.debug(f"MTF cache storage failed: {e}")
                except Exception as e:
                    self.logger.debug(f"Higher timeframe data retrieval failed for {symbol}: {e}")
                    return None
            
            if higher_df is not None and len(higher_df) > 20:
                try:
                    alignment_result = self.multi_timeframe_analyzer.analyze_timeframe_alignment(df, higher_df)
                    
                    primary_tf_name = self.multi_timeframe_analyzer.get_timeframe_name(primary_timeframe)
                    higher_tf_mapping = self.multi_timeframe_analyzer.primary_to_higher.get(primary_timeframe)
                    higher_tf_name = self.multi_timeframe_analyzer.get_timeframe_name(higher_tf_mapping) if higher_tf_mapping else "Unknown"
                    
                    return TimeframeAlignment(
                        primary_timeframe=primary_tf_name,
                        higher_timeframe=higher_tf_name,
                        alignment_score=alignment_result.alignment_score,
                        confirmation_level=alignment_result.confirmation_level
                    )
                except Exception as e:
                    self.logger.debug(f"Timeframe alignment analysis failed for {symbol}: {e}")
                    return None
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Multi-timeframe analysis failed for {symbol}: {e}")
            raise TrendDetectionError(f"Multi-timeframe analysis failed: {e}")
    
    def _analyze_volume_safe(self, df: pd.DataFrame, symbol: str) -> Optional[VolumeConfirmation]:
        """Safe volume analysis with error handling"""
        try:
            from src.analyzers.volume_analyzer import VolumeAnalyzer
            
            # Use simplified volume analysis for speed and reliability
            volume_analyzer = VolumeAnalyzer(self.config)
            
            try:
                volume_ratio = volume_analyzer.get_volume_ratio(df)
            except Exception as e:
                self.logger.debug(f"Volume ratio calculation failed for {symbol}: {e}")
                volume_ratio = 1.0
            
            # Quick volume spike detection with error handling
            try:
                recent_volume = df['tick_volume'].iloc[-5:].mean() if 'tick_volume' in df.columns else 1.0
                avg_volume = df['tick_volume'].rolling(20).mean().iloc[-1] if 'tick_volume' in df.columns else 1.0
                volume_spike = recent_volume > avg_volume * 1.5
            except Exception as e:
                self.logger.debug(f"Volume spike detection failed for {symbol}: {e}")
                volume_spike = False
            
            return VolumeConfirmation(
                volume_spike=volume_spike,
                volume_ratio=volume_ratio,
                strength=min(1.0, volume_ratio / 2.0)
            )
            
        except Exception as e:
            self.logger.debug(f"Volume analysis failed for {symbol}: {e}")
            return VolumeConfirmation(volume_spike=False, volume_ratio=1.0, strength=0.5)
    
    def _analyze_early_warnings_safe(self, df: pd.DataFrame, symbol: str) -> List[EarlyWarningSignal]:
        """Safe early warning analysis with error handling"""
        if not self.enable_early_signals:
            return []
        
        try:
            # Simplified early warning detection for speed and reliability
            warnings = []
            
            # Quick trend weakness check with error handling
            if len(df) >= 20:
                try:
                    current_price = df['close'].iloc[-1]
                    
                    # Simple momentum check
                    price_change = (current_price - df['close'].iloc[-10]) / df['close'].iloc[-10]
                    
                    if abs(price_change) > 0.02:  # 2% move
                        warning_type = 'trend_momentum'
                        confidence = min(0.8, abs(price_change) * 10)
                        
                        warnings.append(EarlyWarningSignal(
                            warning_type=warning_type,
                            confidence=confidence,
                            probability_score=0.6,
                            price_level=current_price,
                            current_price=current_price,
                            factors=['momentum_shift'],
                            strength=abs(price_change) * 5,
                            timestamp=datetime.now(),
                            description=f"Momentum shift detected: {price_change:.2%}"
                        ))
                except Exception as e:
                    self.logger.debug(f"Momentum analysis failed for {symbol}: {e}")
            
            return warnings
            
        except Exception as e:
            self.logger.debug(f"Early warning analysis failed for {symbol}: {e}")
            return []
    
    def _compile_analysis_results(self, analysis_results: Dict[str, Any], signals: List[TrendSignal], current_price: float) -> TrendAnalysisResult:
        """Efficiently compile analysis results into final result"""
        
        # Extract results with defaults
        structure_break = analysis_results.get('market_structure')
        aroon_signal = analysis_results.get('aroon')
        ema_signal = analysis_results.get('ema')
        divergences = analysis_results.get('divergence', [])
        trendline_breaks = analysis_results.get('trendline', [])
        timeframe_alignment = analysis_results.get('multi_timeframe')
        volume_confirmation = analysis_results.get('volume')
        early_warnings = analysis_results.get('early_warnings', [])
        
        # Generate signals from analysis results
        signals = self._generate_signals_from_results(
            structure_break, aroon_signal, ema_signal, divergences, 
            trendline_breaks, current_price
        )
        
        # Apply fast signal filtering
        filtered_signals = self._apply_fast_signal_filtering(signals)
        
        # Calculate confidence efficiently
        overall_confidence = self._calculate_trend_confidence(filtered_signals)
        
        return TrendAnalysisResult(
            signals=filtered_signals,
            confidence=overall_confidence,
            market_structure=structure_break,
            divergences=divergences,
            aroon_signal=aroon_signal,
            ema_signal=ema_signal,
            trendline_breaks=trendline_breaks,
            timeframe_alignment=timeframe_alignment,
            volume_confirmation=volume_confirmation,
            early_warnings=early_warnings
        )
    
    def _generate_signals_from_results(self, structure_break, aroon_signal, ema_signal, 
                                     divergences, trendline_breaks, current_price) -> List[TrendSignal]:
        """Generate trend signals from analysis results with enhanced logging"""
        signals = []
        current_time = datetime.now()
        
        # Market structure signals
        if structure_break and structure_break.confirmed:
            signal_type = SignalType.BULLISH_TREND_CHANGE if 'bullish' in structure_break.break_type else SignalType.BEARISH_TREND_CHANGE
            confidence = 0.8 if structure_break.volume_confirmation else 0.6
            
            signal = TrendSignal(
                signal_type=signal_type.value,
                strength=structure_break.strength,
                source='market_structure',
                confidence=confidence,
                timestamp=current_time,
                price_level=structure_break.break_level,
                supporting_factors=['structure_break'] + (['volume_confirmation'] if structure_break.volume_confirmation else [])
            )
            signals.append(signal)
            
            # Enhanced logging for signal generation
            self.trend_logger.log_signal_generated(signal_type.value, 'market_structure', confidence, structure_break.strength)
        
        # Aroon signals
        if aroon_signal and aroon_signal.signal_type != 'consolidation' and 'cross' in aroon_signal.signal_type:
            signal_type = SignalType.BULLISH_TREND_CHANGE if 'bullish' in aroon_signal.signal_type else SignalType.BEARISH_TREND_CHANGE
            confidence = 0.8 if 'strong' in aroon_signal.signal_type else 0.7
            
            signal = TrendSignal(
                signal_type=signal_type.value,
                strength=aroon_signal.trend_strength,
                source='aroon',
                confidence=confidence,
                timestamp=current_time,
                price_level=current_price,
                supporting_factors=['aroon_crossover']
            )
            signals.append(signal)
            
            # Enhanced logging for signal generation
            self.trend_logger.log_signal_generated(signal_type.value, 'aroon', confidence, aroon_signal.trend_strength)
        
        # EMA signals
        if ema_signal and 'cross' in ema_signal.signal_type:
            signal_type = SignalType.BULLISH_TREND_CHANGE if 'bullish' in ema_signal.signal_type else SignalType.BEARISH_TREND_CHANGE
            confidence = 0.8 if ema_signal.crossover_confirmed else 0.6
            
            signal = TrendSignal(
                signal_type=signal_type.value,
                strength=ema_signal.momentum_strength,
                source='ema',
                confidence=confidence,
                timestamp=current_time,
                price_level=current_price,
                supporting_factors=['ema_crossover'] + (['momentum_confirmation'] if ema_signal.crossover_confirmed else [])
            )
            signals.append(signal)
            
            # Enhanced logging for signal generation
            self.trend_logger.log_signal_generated(signal_type.value, 'ema', confidence, ema_signal.momentum_strength)
        
        # Divergence signals
        for divergence in divergences:
            if divergence.validated:
                signal_type = SignalType.BULLISH_TREND_CHANGE if 'bullish' in divergence.divergence_type else SignalType.BEARISH_TREND_CHANGE
                confidence = 0.8 if divergence.strength > 0.7 else 0.6
                
                signal = TrendSignal(
                    signal_type=signal_type.value,
                    strength=divergence.strength,
                    source='divergence',
                    confidence=confidence,
                    timestamp=current_time,
                    price_level=current_price,
                    supporting_factors=[f'{divergence.indicator.lower()}_divergence', 'validated_pattern']
                )
                signals.append(signal)
                
                # Enhanced logging for signal generation
                self.trend_logger.log_signal_generated(signal_type.value, 'divergence', confidence, divergence.strength)
        
        # Trendline break signals
        for break_info in trendline_breaks:
            if break_info.volume_confirmation or break_info.break_strength > 0.7:
                signal_type = SignalType.BULLISH_TREND_CHANGE if break_info.trendline.line_type == 'resistance' else SignalType.BEARISH_TREND_CHANGE
                
                base_confidence = 0.7
                if break_info.volume_confirmation:
                    base_confidence += 0.1
                if break_info.retest_confirmed:
                    base_confidence += 0.1
                
                confidence = min(0.95, base_confidence)
                
                supporting_factors = ['trendline_break']
                if break_info.volume_confirmation:
                    supporting_factors.append('volume_confirmation')
                if break_info.retest_confirmed:
                    supporting_factors.append('retest_confirmation')
                
                signal = TrendSignal(
                    signal_type=signal_type.value,
                    strength=break_info.break_strength,
                    source='trendline',
                    confidence=confidence,
                    timestamp=current_time,
                    price_level=break_info.break_point[1],
                    supporting_factors=supporting_factors
                )
                signals.append(signal)
                
                # Enhanced logging for signal generation
                self.trend_logger.log_signal_generated(signal_type.value, 'trendline', confidence, break_info.break_strength)
        
        return signals
    
    def _apply_fast_signal_filtering(self, signals: List[TrendSignal]) -> List[TrendSignal]:
        """Apply fast signal filtering for performance"""
        if not signals:
            return signals
        
        # Quick confidence filter
        filtered_signals = [s for s in signals if s.confidence >= self.min_confidence]
        
        # Quick conflict resolution - keep strongest signal per direction
        bullish_signals = [s for s in filtered_signals if 'bullish' in s.signal_type]
        bearish_signals = [s for s in filtered_signals if 'bearish' in s.signal_type]
        
        result_signals = []
        
        if bullish_signals:
            # Keep strongest bullish signal
            strongest_bullish = max(bullish_signals, key=lambda s: s.confidence * s.strength)
            result_signals.append(strongest_bullish)
        
        if bearish_signals:
            # Keep strongest bearish signal
            strongest_bearish = max(bearish_signals, key=lambda s: s.confidence * s.strength)
            result_signals.append(strongest_bearish)
        
        return result_signals
    
    def _create_empty_result(self) -> TrendAnalysisResult:
        """Create empty analysis result for error cases"""
        return TrendAnalysisResult(
            signals=[],
            confidence=0.0,
            market_structure=None,
            divergences=[],
            aroon_signal=None,
            ema_signal=None,
            trendline_breaks=[],
            timeframe_alignment=None,
            volume_confirmation=None,
            early_warnings=[]
        )
    
    def _update_performance_stats(self, elapsed_ms: float, success: bool = True) -> None:
        """Update performance statistics with error tracking"""
        if not self.enable_performance_monitoring:
            return
        
        try:
            # Update average analysis time
            total_analyses = self.performance_stats['total_analyses']
            current_avg = self.performance_stats['avg_analysis_time']
            
            new_avg = ((current_avg * (total_analyses - 1)) + elapsed_ms) / total_analyses
            self.performance_stats['avg_analysis_time'] = new_avg
            
            # Update max analysis time
            if elapsed_ms > self.performance_stats['max_analysis_time']:
                self.performance_stats['max_analysis_time'] = elapsed_ms
            
            # Log performance warnings
            if elapsed_ms > self.max_analysis_time_ms:
                self.logger.warning(f"⚠️ Analysis exceeded target time: {elapsed_ms:.1f}ms > {self.max_analysis_time_ms}ms")
                
            # Update success/failure counts
            if success:
                self.performance_stats['successful_analyses'] += 1
            else:
                self.performance_stats['failed_analyses'] += 1
                
        except Exception as e:
            self.logger.error(f"Error updating performance stats: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics including error information"""
        try:
            cache_total = self.performance_stats['cache_hits'] + self.performance_stats['cache_misses']
            cache_hit_rate = (self.performance_stats['cache_hits'] / cache_total * 100) if cache_total > 0 else 0
            
            success_rate = 0
            if self.performance_stats['total_analyses'] > 0:
                success_rate = (self.performance_stats['successful_analyses'] / self.performance_stats['total_analyses'] * 100)
            
            return {
                **self.performance_stats,
                'cache_hit_rate_percent': cache_hit_rate,
                'success_rate_percent': success_rate,
                'cache_size': self.data_cache.size() if self.data_cache else 0,
                'cache_max_size': self.data_cache.max_size if self.data_cache else 0,
                'memory_usage_mb': self.memory_manager.get_memory_usage_mb(),
                'error_counts': self.error_recovery.error_counts.copy(),
                'component_status': self.get_component_status()
            }
        except Exception as e:
            self.logger.error(f"Error getting performance stats: {e}")
            return {'error': str(e)}
    
    def clear_cache(self) -> None:
        """Clear all cached data with error handling"""
        try:
            if self.data_cache is not None:
                self.data_cache.clear()
                self.logger.info("Trend detection cache cleared")
            else:
                self.logger.warning("Cache not available for clearing")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
    
    def cleanup_resources(self) -> None:
        """Clean up resources and perform maintenance"""
        try:
            # Clear cache
            self.clear_cache()
            
            # Force memory cleanup
            self.memory_manager.force_cleanup()
            
            # Reset circuit breakers
            for cb in self.circuit_breakers.values():
                cb.failure_count = 0
                cb.state = 'closed'
            
            # Clean up expired cache entries
            if self.data_cache is not None:
                self.data_cache.cleanup_expired()
            
            self.logger.info("Resource cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during resource cleanup: {e}")
    
    def reset_error_counts(self) -> None:
        """Reset error counts for fresh start"""
        try:
            self.error_recovery.error_counts.clear()
            self.error_recovery.diagnostic_info.clear()
            
            # Reset performance stats
            self.performance_stats.update({
                'failed_analyses': 0,
                'component_failures': 0,
                'memory_cleanups': 0
            })
            
            self.logger.info("Error counts reset")
            
        except Exception as e:
            self.logger.error(f"Error resetting error counts: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            stats = self.get_performance_stats()
            
            # Determine health status
            health_score = 100
            issues = []
            
            # Check success rate
            if stats.get('success_rate_percent', 0) < 80:
                health_score -= 30
                issues.append(f"Low success rate: {stats.get('success_rate_percent', 0):.1f}%")
            
            # Check performance
            if stats.get('avg_analysis_time', 0) > self.max_analysis_time_ms:
                health_score -= 20
                issues.append(f"Slow analysis: {stats.get('avg_analysis_time', 0):.1f}ms avg")
            
            # Check memory usage
            memory_usage = stats.get('memory_usage_mb', 0)
            if memory_usage > self.memory_manager.max_memory_mb * 0.8:
                health_score -= 15
                issues.append(f"High memory usage: {memory_usage:.1f}MB")
            
            # Check component failures
            component_failures = stats.get('component_failures', 0)
            if component_failures > 10:
                health_score -= 25
                issues.append(f"High component failure rate: {component_failures}")
            
            # Check error counts
            total_errors = sum(self.error_recovery.error_counts.values())
            if total_errors > 50:
                health_score -= 10
                issues.append(f"High error count: {total_errors}")
            
            health_status = 'excellent' if health_score >= 90 else \
                           'good' if health_score >= 70 else \
                           'fair' if health_score >= 50 else 'poor'
            
            return {
                'health_score': max(0, health_score),
                'health_status': health_status,
                'issues': issues,
                'component_availability': sum(1 for status in self.components_status.values() if status == 'available'),
                'total_components': len(self.components_status),
                'uptime_analyses': stats.get('total_analyses', 0),
                'memory_usage_mb': memory_usage,
                'cache_efficiency': stats.get('cache_hit_rate_percent', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting health status: {e}")
            return {
                'health_score': 0,
                'health_status': 'error',
                'issues': [f"Health check failed: {e}"],
                'error': str(e)
            }
    
    def get_trend_signals(self, df: pd.DataFrame, signal_type: str, symbol: str = "unknown") -> List[TrendSignal]:
        """
        Get trend signals for a specific signal type
        
        Args:
            df: Price data with indicators
            signal_type: 'buy' or 'sell'
            symbol: Trading symbol (default: "unknown" for backward compatibility)
            
        Returns:
            List of relevant trend signals
        """
        analysis_result = self.analyze_trend_change(df, symbol)
        
        if signal_type.lower() == 'buy':
            return [s for s in analysis_result.signals if 'bullish' in s.signal_type]
        elif signal_type.lower() == 'sell':
            return [s for s in analysis_result.signals if 'bearish' in s.signal_type]
        else:
            return analysis_result.signals
    
    def filter_signals_by_confidence(self, signals: List[TrendSignal], min_confidence: float = None) -> List[TrendSignal]:
        """
        Filter signals by minimum confidence threshold with enhanced logging
        
        Args:
            signals: List of trend signals to filter
            min_confidence: Minimum confidence threshold (uses config default if None)
            
        Returns:
            Filtered list of signals meeting confidence requirements
        """
        if min_confidence is None:
            min_confidence = self.min_confidence
        
        filtered_signals = []
        
        for signal in signals:
            if signal.confidence >= min_confidence:
                filtered_signals.append(signal)
                self.logger.debug(f"Signal passed confidence filter: {signal.signal_type} "
                                f"(confidence: {signal.confidence:.3f} >= {min_confidence:.3f})")
            else:
                # Enhanced logging for filtered signals
                self.trend_logger.log_signal_filtered(signal.signal_type, 
                    f'confidence_too_low ({signal.confidence:.3f} < {min_confidence:.3f})', 
                    signal.confidence)
                self.logger.debug(f"Signal filtered out by confidence: {signal.signal_type} "
                                f"(confidence: {signal.confidence:.3f} < {min_confidence:.3f})")
        
        if len(filtered_signals) < len(signals):
            self.logger.info(f"Confidence filter applied: {len(filtered_signals)}/{len(signals)} signals passed "
                           f"(threshold: {min_confidence:.3f})")
        
        return filtered_signals
    
    def filter_conflicting_signals(self, signals: List[TrendSignal]) -> List[TrendSignal]:
        """
        Filter out conflicting signals, keeping only the strongest in each direction
        
        Args:
            signals: List of trend signals
            
        Returns:
            Filtered list with conflicts resolved
        """
        if len(signals) <= 1:
            return signals
        
        # Group signals by direction
        bullish_signals = [s for s in signals if 'bullish' in s.signal_type]
        bearish_signals = [s for s in signals if 'bearish' in s.signal_type]
        
        # If no conflicts, return all signals
        if not bullish_signals or not bearish_signals:
            return signals
        
        # Calculate strength scores for each direction
        bullish_score = sum(s.confidence * s.strength for s in bullish_signals) / len(bullish_signals)
        bearish_score = sum(s.confidence * s.strength for s in bearish_signals) / len(bearish_signals)
        
        # Determine winning direction
        if bullish_score > bearish_score * 1.2:  # 20% advantage needed
            filtered_signals = bullish_signals
            self.logger.info(f"Conflict resolution: Keeping {len(bullish_signals)} bullish signals "
                           f"(score: {bullish_score:.3f} vs {bearish_score:.3f})")
        elif bearish_score > bullish_score * 1.2:
            filtered_signals = bearish_signals
            self.logger.info(f"Conflict resolution: Keeping {len(bearish_signals)} bearish signals "
                           f"(score: {bearish_score:.3f} vs {bullish_score:.3f})")
        else:
            # Too close to call - keep all but reduce confidence
            filtered_signals = signals.copy()
            conflict_penalty = 0.2  # 20% confidence penalty
            
            for signal in filtered_signals:
                signal.confidence *= (1.0 - conflict_penalty)
                if 'conflict_penalty' not in signal.supporting_factors:
                    signal.supporting_factors.append('conflict_penalty')
            
            self.logger.info(f"Conflict resolution: Signals too close, applying {conflict_penalty:.1%} penalty "
                           f"(bullish: {bullish_score:.3f}, bearish: {bearish_score:.3f})")
        
        return filtered_signals
    
    def filter_signals_by_source_quality(self, signals: List[TrendSignal]) -> List[TrendSignal]:
        """
        Filter signals based on source quality and reliability
        
        Args:
            signals: List of trend signals
            
        Returns:
            Filtered list of high-quality signals
        """
        # Source reliability scores (higher = more reliable)
        source_reliability = {
            'market_structure': 0.9,
            'divergence': 0.85,
            'trendline': 0.8,
            'ema': 0.75,
            'aroon': 0.7,
            'volume': 0.6
        }
        
        # Minimum quality thresholds by source
        min_quality_by_source = {
            'market_structure': 0.5,  # Lower threshold for high-reliability sources
            'divergence': 0.55,
            'trendline': 0.6,
            'ema': 0.65,
            'aroon': 0.7,
            'volume': 0.75  # Higher threshold for lower-reliability sources
        }
        
        filtered_signals = []
        
        for signal in signals:
            source = signal.source
            reliability = source_reliability.get(source, 0.5)
            min_quality = min_quality_by_source.get(source, 0.7)
            
            # Calculate signal quality score
            quality_score = signal.confidence * signal.strength * reliability
            
            if quality_score >= min_quality:
                filtered_signals.append(signal)
                self.logger.debug(f"Signal passed quality filter: {signal.signal_type} from {source} "
                                f"(quality: {quality_score:.3f} >= {min_quality:.3f})")
            else:
                self.logger.debug(f"Signal filtered out by quality: {signal.signal_type} from {source} "
                                f"(quality: {quality_score:.3f} < {min_quality:.3f})")
        
        if len(filtered_signals) < len(signals):
            self.logger.info(f"Quality filter applied: {len(filtered_signals)}/{len(signals)} signals passed")
        
        return filtered_signals
    
    def apply_comprehensive_signal_filtering(self, signals: List[TrendSignal]) -> List[TrendSignal]:
        """
        Apply comprehensive signal filtering including confidence, quality, and conflict resolution
        
        Args:
            signals: Raw list of trend signals
            
        Returns:
            Filtered and validated list of signals
        """
        if not signals:
            return signals
        
        self.logger.info(f"🔍 APPLYING SIGNAL FILTERS:")
        self.logger.info(f"  Input signals: {len(signals)}")
        
        # Step 1: Filter by minimum confidence
        filtered_signals = self.filter_signals_by_confidence(signals)
        self.logger.info(f"  After confidence filter: {len(filtered_signals)}")
        
        if not filtered_signals:
            self.logger.info("  ❌ No signals passed confidence filter")
            return []
        
        # Step 2: Filter by source quality
        filtered_signals = self.filter_signals_by_source_quality(filtered_signals)
        self.logger.info(f"  After quality filter: {len(filtered_signals)}")
        
        if not filtered_signals:
            self.logger.info("  ❌ No signals passed quality filter")
            return []
        
        # Step 3: Resolve conflicts
        filtered_signals = self.filter_conflicting_signals(filtered_signals)
        self.logger.info(f"  After conflict resolution: {len(filtered_signals)}")
        
        # Step 4: Apply additional validation
        validated_signals = []
        
        for signal in filtered_signals:
            # Check for minimum supporting factors
            min_factors = 1 if signal.source in ['market_structure', 'divergence'] else 2
            
            if len(signal.supporting_factors) >= min_factors:
                validated_signals.append(signal)
                self.logger.debug(f"Signal validated: {signal.signal_type} "
                                f"({len(signal.supporting_factors)} factors: {', '.join(signal.supporting_factors)})")
            else:
                self.logger.debug(f"Signal lacks supporting factors: {signal.signal_type} "
                                f"({len(signal.supporting_factors)} < {min_factors})")
        
        self.logger.info(f"  After validation: {len(validated_signals)}")
        
        if validated_signals:
            # Log final signal summary
            self.logger.info(f"  ✅ FINAL FILTERED SIGNALS:")
            for i, signal in enumerate(validated_signals, 1):
                self.logger.info(f"    {i}. {signal.signal_type} from {signal.source}")
                self.logger.info(f"       Confidence: {signal.confidence:.3f}, Strength: {signal.strength:.3f}")
                self.logger.info(f"       Factors: {', '.join(signal.supporting_factors)}")
        else:
            self.logger.info("  ❌ No signals passed all filters")
        
        return validated_signals

    def calculate_trend_confidence(self, signals: List[TrendSignal]) -> float:
        """
        Calculate overall trend confidence from multiple signals
        
        Args:
            signals: List of trend signals
            
        Returns:
            Overall confidence score (0.0 to 1.0)
        """
        return self._calculate_trend_confidence(signals)
    
    def should_trade_trend(self, df: pd.DataFrame, signal_type: str, symbol: str = "unknown") -> Tuple[bool, float]:
        """
        Determine if trend conditions support trading
        
        Args:
            df: Price data with indicators
            signal_type: 'buy' or 'sell'
            symbol: Trading symbol (default: "unknown" for backward compatibility)
            
        Returns:
            Tuple of (should_trade, confidence_score)
        """
        analysis_result = self.analyze_trend_change(df, symbol)
        
        # Check if we have relevant signals
        relevant_signals = self.get_trend_signals(df, signal_type, symbol)
        
        if not relevant_signals:
            # ---------------------------------------------------------------
            # No active crossover / structure-break events.
            # Fall back to computing directional confidence from continuous
            # EMA and Aroon state so we don't always block trading when the
            # trend is intact but no recent crossover has occurred.
            # ---------------------------------------------------------------
            fallback_confidence = self._compute_directional_confidence(
                df, signal_type, symbol
            )
            self.logger.debug(
                f"No trend signals for {symbol} ({signal_type}); "
                f"fallback directional confidence = {fallback_confidence:.3f}"
            )
            if fallback_confidence >= self.min_confidence:
                return True, fallback_confidence
            return False, fallback_confidence
        
        # Check if confidence meets minimum threshold
        if analysis_result.confidence < self.min_confidence:
            return False, analysis_result.confidence
        
        # Check multi-timeframe confirmation if available
        if (analysis_result.timeframe_alignment is not None and 
            hasattr(self, 'multi_timeframe_analyzer') and 
            self.multi_timeframe_analyzer.enable_mtf):
            
            # Convert timeframe alignment to AlignmentResult for confirmation check
            from src.analyzers.multi_timeframe_analyzer import AlignmentResult
            
            # Determine expected signals based on signal type
            expected_signal = 'bullish' if signal_type.lower() == 'buy' else 'bearish'
            
            # Create a mock alignment result for confirmation check
            # In practice, this would use the actual alignment result from analysis
            alignment_result = AlignmentResult(
                primary_signal=expected_signal,
                higher_signal=analysis_result.timeframe_alignment.confirmation_level,
                alignment_score=analysis_result.timeframe_alignment.alignment_score,
                confirmation_level=analysis_result.timeframe_alignment.confirmation_level,
                factors=['mtf_analysis']
            )
            
            # Check if higher timeframe confirms the signal
            mtf_confirmed = self.multi_timeframe_analyzer.should_confirm_signal(alignment_result, signal_type)
            
            if not mtf_confirmed:
                self.logger.info(f"❌ Multi-timeframe confirmation failed for {signal_type} signal")
                return False, analysis_result.confidence * 0.5  # Reduced confidence for failed MTF
            else:
                self.logger.info(f"✅ Multi-timeframe confirmation passed for {signal_type} signal")
        
        return True, analysis_result.confidence

    def _compute_directional_confidence(
        self, df: pd.DataFrame, signal_type: str, symbol: str = "unknown"
    ) -> float:
        """
        Compute a directional confidence score from continuous EMA and Aroon
        state (not crossover events). Used as fallback when no crossover-based
        TrendSignals are detected.

        Returns a value in [0.0, 1.0].
        """
        try:
            is_buy = signal_type.lower() == "buy"
            score = 0.0
            components = 0

            # --- EMA alignment ---
            try:
                ema_signal = self._analyze_ema_safe(df, symbol)
                if ema_signal is not None:
                    ema_type = ema_signal.signal_type.lower()
                    # "bullish_*" or "bearish_*" (may not contain "cross")
                    aligned = (is_buy and "bullish" in ema_type) or (
                        not is_buy and "bearish" in ema_type
                    )
                    # separation gives strength: clamp 0-3 % → 0-1
                    ema_strength = min(1.0, abs(ema_signal.separation) / 3.0)
                    if aligned:
                        score += 0.5 * (0.5 + 0.5 * ema_strength)
                    components += 1
            except Exception as e:
                self.logger.debug(f"EMA directional confidence failed: {e}")

            # --- Aroon direction ---
            try:
                aroon_signal = self._analyze_aroon_safe(df, symbol)
                if aroon_signal is not None:
                    aroon_type = aroon_signal.signal_type.lower()
                    # Aroon Up > Aroon Down → bullish tendency (and vice-versa)
                    up_dominant = aroon_signal.aroon_up > aroon_signal.aroon_down
                    aligned = (is_buy and up_dominant) or (
                        not is_buy and not up_dominant
                    )
                    if aligned:
                        # aroon oscillator: use trend_strength as proxy
                        score += 0.3 * (0.5 + 0.5 * min(1.0, aroon_signal.trend_strength))
                    components += 1
            except Exception as e:
                self.logger.debug(f"Aroon directional confidence failed: {e}")

            # --- Simple price-EMA relationship (robust fallback) ---
            try:
                if "close" in df.columns and len(df) >= 20:
                    close = df["close"].iloc[-1]
                    ema20 = df["close"].ewm(span=20, adjust=False).mean().iloc[-1]
                    above_ema = close > ema20
                    aligned = (is_buy and above_ema) or (not is_buy and not above_ema)
                    if aligned:
                        score += 0.2
                    components += 1
            except Exception as e:
                self.logger.debug(f"Price-EMA directional confidence failed: {e}")

            # Normalise: if no components ran, return 0
            if components == 0:
                return 0.0

            return min(1.0, score)

        except Exception as e:
            self.logger.debug(f"_compute_directional_confidence error: {e}")
            return 0.0
    
    def _calculate_trend_confidence(self, signals: List[TrendSignal]) -> float:
        """
        Internal method to calculate confidence from signals with enhanced weighting
        
        Args:
            signals: List of trend signals
            
        Returns:
            Weighted confidence score
        """
        if not signals:
            return 0.0
        
        # Enhanced weight system based on signal reliability and source
        source_weights = {
            'market_structure': 0.35,  # Highest weight - structure breaks are very reliable
            'divergence': 0.30,        # High weight - divergences are strong reversal signals
            'trendline': 0.28,         # High weight - trendline breaks are reliable trend signals
            'ema': 0.25,              # Good weight - EMA crossovers are reliable trend signals
            'aroon': 0.20,            # Moderate weight - Aroon is good for trend strength
            'volume': 0.15            # Supporting weight - volume confirms other signals
        }
        
        # Group signals by type to handle multiple signals of same type
        signal_groups = {}
        for signal in signals:
            signal_direction = 'bullish' if 'bullish' in signal.signal_type else 'bearish'
            if signal_direction not in signal_groups:
                signal_groups[signal_direction] = []
            signal_groups[signal_direction].append(signal)
        
        # Calculate confidence for each direction
        direction_confidences = {}
        
        for direction, direction_signals in signal_groups.items():
            total_weight = 0.0
            weighted_confidence = 0.0
            
            # Track which sources we've seen to avoid double-counting
            sources_used = set()
            
            for signal in direction_signals:
                source = signal.source
                weight = source_weights.get(source, 0.1)
                
                # If we already have a signal from this source, use the stronger one
                if source in sources_used:
                    # Find existing signal from this source and compare
                    existing_signals = [s for s in direction_signals if s.source == source and s != signal]
                    if existing_signals:
                        existing_signal = existing_signals[0]
                        if signal.strength * signal.confidence > existing_signal.strength * existing_signal.confidence:
                            # Replace with stronger signal
                            weighted_confidence -= existing_signal.confidence * existing_signal.strength * weight
                            weighted_confidence += signal.confidence * signal.strength * weight
                    continue
                
                sources_used.add(source)
                
                # Calculate signal quality score
                signal_quality = signal.confidence * signal.strength
                
                # Apply supporting factors bonus
                supporting_bonus = 1.0
                if 'volume_confirmation' in signal.supporting_factors:
                    supporting_bonus += 0.1
                if 'validated_pattern' in signal.supporting_factors:
                    supporting_bonus += 0.1
                if 'momentum_confirmation' in signal.supporting_factors:
                    supporting_bonus += 0.05
                
                signal_quality *= min(1.3, supporting_bonus)  # Cap bonus at 30%
                
                weighted_confidence += signal_quality * weight
                total_weight += weight
            
            if total_weight > 0:
                direction_confidences[direction] = weighted_confidence / total_weight
        
        # If we have conflicting signals, reduce overall confidence
        if len(direction_confidences) > 1:
            # Conflicting signals - return the stronger direction but penalized
            max_confidence = max(direction_confidences.values())
            min_confidence = min(direction_confidences.values())
            
            # Penalty based on how close the conflicting signals are
            conflict_penalty = 0.8 - (min_confidence / max_confidence * 0.3)
            return min(1.0, max_confidence * conflict_penalty)
        
        elif len(direction_confidences) == 1:
            # Single direction - apply consensus bonus
            confidence = list(direction_confidences.values())[0]
            
            # Bonus for multiple confirming signals
            signal_count = len(signals)
            if signal_count >= 3:
                consensus_bonus = 1.15  # 15% bonus for 3+ signals
            elif signal_count >= 2:
                consensus_bonus = 1.10  # 10% bonus for 2+ signals
            else:
                consensus_bonus = 1.0
            
            return min(1.0, confidence * consensus_bonus)
        
        else:
            return 0.0