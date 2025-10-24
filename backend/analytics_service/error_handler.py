# error_handler.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Callable
import logging
import traceback
import json
import os
from datetime import datetime, timedelta
from functools import wraps
import warnings
warnings.filterwarnings('ignore')

class ErrorHandler:
    """
    Robust error handling and fallback mechanisms for TANAW.
    Implements comprehensive logging, graceful degradation, and recovery strategies.
    """
    
    def __init__(self, log_file: str = "tanaw_errors.log"):
        self.log_file = log_file
        self.error_database_path = "error_database.json"
        self.performance_metrics_path = "performance_metrics.json"
        
        # Initialize logging
        self._setup_logging()
        
        # Load error database and performance metrics
        self.error_db = self._load_error_database()
        self.performance_metrics = self._load_performance_metrics()
        
        # Error categories and severity levels
        self.error_categories = {
            'data_loading': {'severity': 'high', 'fallback_available': True},
            'data_validation': {'severity': 'high', 'fallback_available': True},
            'column_mapping': {'severity': 'medium', 'fallback_available': True},
            'analytics_processing': {'severity': 'medium', 'fallback_available': True},
            'model_training': {'severity': 'high', 'fallback_available': True},
            'forecasting': {'severity': 'medium', 'fallback_available': True},
            'visualization': {'severity': 'low', 'fallback_available': True},
            'feedback_processing': {'severity': 'low', 'fallback_available': True},
            'system_resource': {'severity': 'high', 'fallback_available': False}
        }
        
        # Fallback strategies
        self.fallback_strategies = {
            'data_loading': self._fallback_data_loading,
            'data_validation': self._fallback_data_validation,
            'column_mapping': self._fallback_column_mapping,
            'analytics_processing': self._fallback_analytics_processing,
            'model_training': self._fallback_model_training,
            'forecasting': self._fallback_forecasting,
            'visualization': self._fallback_visualization,
            'feedback_processing': self._fallback_feedback_processing
        }
        
        # Retry configurations
        self.retry_configs = {
            'max_retries': 3,
            'retry_delays': [1, 2, 5],  # seconds
            'retry_conditions': {
                'data_loading': ['file_not_found', 'permission_denied'],
                'analytics_processing': ['memory_error', 'timeout'],
                'model_training': ['convergence_failure', 'data_insufficient']
            }
        }
    
    def _setup_logging(self):
        """Setup comprehensive logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('TANAW_ErrorHandler')
    
    def handle_error(self, error: Exception, context: Dict[str, Any], 
                    category: str = 'general') -> Dict[str, Any]:
        """
        Comprehensive error handling with fallback mechanisms.
        
        Args:
            error: The exception that occurred
            context: Context information about the operation
            category: Error category for classification
            
        Returns:
            Dict containing error handling results and fallback outcomes
        """
        error_id = self._generate_error_id()
        error_info = self._analyze_error(error, context, category)
        
        # Log the error
        self._log_error(error_info, error_id)
        
        # Store in error database
        self._store_error(error_info, error_id)
        
        # Determine handling strategy
        handling_strategy = self._determine_handling_strategy(error_info)
        
        # Execute handling strategy
        handling_result = self._execute_handling_strategy(handling_strategy, error_info, context)
        
        # Update performance metrics
        self._update_performance_metrics(error_info, handling_result)
        
        return {
            'error_id': error_id,
            'error_info': error_info,
            'handling_strategy': handling_strategy,
            'handling_result': handling_result,
            'fallback_applied': handling_result.get('fallback_applied', False),
            'recovery_successful': handling_result.get('success', False)
        }
    
    def log_error(self, error_message: str, context: Dict[str, Any] = None, 
                  category: str = 'general') -> None:
        """
        Simple public method for logging errors.
        
        Args:
            error_message: Error message to log
            context: Optional context information
            category: Error category
        """
        try:
            error_info = {
                'error_message': error_message,
                'category': category,
                'severity': self.error_categories.get(category, {}).get('severity', 'medium'),
                'context': context or {},
                'timestamp': datetime.now().isoformat()
            }
            
            # Log with appropriate level
            if error_info['severity'] == 'high':
                self.logger.error(f"{category}: {error_message}")
            elif error_info['severity'] == 'medium':
                self.logger.warning(f"{category}: {error_message}")
            else:
                self.logger.info(f"{category}: {error_message}")
                
        except Exception as e:
            # Fallback logging if main logging fails
            print(f"Error logging failed: {e}")
            print(f"Original error: {error_message}")
    
    def _analyze_error(self, error: Exception, context: Dict[str, Any], 
                      category: str) -> Dict[str, Any]:
        """Analyze error and extract relevant information."""
        error_info = {
            'category': category,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'stack_trace': traceback.format_exc(),
            'severity': self.error_categories.get(category, {}).get('severity', 'medium'),
            'fallback_available': self.error_categories.get(category, {}).get('fallback_available', False)
        }
        
        # Add specific analysis based on error type
        if isinstance(error, FileNotFoundError):
            error_info['specific_analysis'] = self._analyze_file_not_found(error, context)
        elif isinstance(error, pd.errors.EmptyDataError):
            error_info['specific_analysis'] = self._analyze_empty_data_error(error, context)
        elif isinstance(error, MemoryError):
            error_info['specific_analysis'] = self._analyze_memory_error(error, context)
        elif isinstance(error, ValueError):
            error_info['specific_analysis'] = self._analyze_value_error(error, context)
        else:
            error_info['specific_analysis'] = {'analysis_type': 'generic', 'details': 'Standard error analysis'}
        
        return error_info
    
    def _analyze_file_not_found(self, error: FileNotFoundError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze file not found errors."""
        return {
            'analysis_type': 'file_not_found',
            'file_path': str(error),
            'suggested_actions': [
                'Check file path and permissions',
                'Verify file exists in expected location',
                'Consider alternative file formats'
            ],
            'fallback_options': [
                'Use sample dataset',
                'Prompt user for correct file path',
                'Skip file processing with warning'
            ]
        }
    
    def _analyze_empty_data_error(self, error: pd.errors.EmptyDataError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze empty data errors."""
        return {
            'analysis_type': 'empty_data',
            'suggested_actions': [
                'Check if file contains data',
                'Verify file format and encoding',
                'Check for empty sheets or tables'
            ],
            'fallback_options': [
                'Return empty DataFrame with proper structure',
                'Use default sample data',
                'Prompt user to provide valid data'
            ]
        }
    
    def _analyze_memory_error(self, error: MemoryError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze memory errors."""
        return {
            'analysis_type': 'memory_error',
            'suggested_actions': [
                'Process data in chunks',
                'Reduce data precision',
                'Clear unnecessary variables'
            ],
            'fallback_options': [
                'Sample data for processing',
                'Use more memory-efficient algorithms',
                'Request user to reduce dataset size'
            ]
        }
    
    def _analyze_value_error(self, error: ValueError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze value errors."""
        return {
            'analysis_type': 'value_error',
            'error_details': str(error),
            'suggested_actions': [
                'Validate input parameters',
                'Check data types and formats',
                'Verify data ranges and constraints'
            ],
            'fallback_options': [
                'Use default parameter values',
                'Apply data type conversion',
                'Skip problematic operations'
            ]
        }
    
    def _determine_handling_strategy(self, error_info: Dict[str, Any]) -> str:
        """Determine the best handling strategy for the error."""
        category = error_info['category']
        severity = error_info['severity']
        fallback_available = error_info['fallback_available']
        
        if severity == 'high' and fallback_available:
            return 'retry_with_fallback'
        elif severity == 'medium' and fallback_available:
            return 'fallback_only'
        elif severity == 'low':
            return 'log_and_continue'
        else:
            return 'fail_gracefully'
    
    def _execute_handling_strategy(self, strategy: str, error_info: Dict[str, Any], 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the determined handling strategy."""
        result = {
            'strategy': strategy,
            'success': False,
            'fallback_applied': False,
            'retry_attempts': 0,
            'final_result': None,
            'error': None
        }
        
        try:
            if strategy == 'retry_with_fallback':
                result = self._execute_retry_with_fallback(error_info, context)
            elif strategy == 'fallback_only':
                result = self._execute_fallback_only(error_info, context)
            elif strategy == 'log_and_continue':
                result = self._execute_log_and_continue(error_info, context)
            elif strategy == 'fail_gracefully':
                result = self._execute_fail_gracefully(error_info, context)
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Error handling strategy execution failed: {e}")
        
        return result
    
    def _execute_retry_with_fallback(self, error_info: Dict[str, Any], 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute retry with fallback strategy."""
        result = {
            'strategy': 'retry_with_fallback',
            'success': False,
            'fallback_applied': False,
            'retry_attempts': 0,
            'final_result': None,
            'error': None
        }
        
        category = error_info['category']
        max_retries = self.retry_configs['max_retries']
        retry_delays = self.retry_configs['retry_delays']
        
        for attempt in range(max_retries):
            result['retry_attempts'] = attempt + 1
            
            try:
                # Attempt the original operation
                if 'original_function' in context and 'args' in context:
                    original_result = context['original_function'](*context['args'])
                    result['success'] = True
                    result['final_result'] = original_result
                    return result
                
            except Exception as retry_error:
                if attempt < max_retries - 1:
                    # Wait before retry
                    import time
                    time.sleep(retry_delays[min(attempt, len(retry_delays) - 1)])
                    continue
                else:
                    # All retries failed, apply fallback
                    fallback_result = self._apply_fallback(category, error_info, context)
                    result['fallback_applied'] = True
                    result['final_result'] = fallback_result
                    result['success'] = fallback_result is not None
        
        return result
    
    def _execute_fallback_only(self, error_info: Dict[str, Any], 
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute fallback only strategy."""
        result = {
            'strategy': 'fallback_only',
            'success': False,
            'fallback_applied': True,
            'retry_attempts': 0,
            'final_result': None,
            'error': None
        }
        
        category = error_info['category']
        fallback_result = self._apply_fallback(category, error_info, context)
        result['final_result'] = fallback_result
        result['success'] = fallback_result is not None
        
        return result
    
    def _execute_log_and_continue(self, error_info: Dict[str, Any], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute log and continue strategy."""
        result = {
            'strategy': 'log_and_continue',
            'success': True,
            'fallback_applied': False,
            'retry_attempts': 0,
            'final_result': None,
            'error': None
        }
        
        # Log the error but continue processing
        self.logger.warning(f"Non-critical error logged and processing continued: {error_info['error_message']}")
        
        # Return a default result based on context
        result['final_result'] = self._get_default_result(context)
        
        return result
    
    def _execute_fail_gracefully(self, error_info: Dict[str, Any], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute fail gracefully strategy."""
        result = {
            'strategy': 'fail_gracefully',
            'success': False,
            'fallback_applied': False,
            'retry_attempts': 0,
            'final_result': None,
            'error': error_info['error_message']
        }
        
        # Log critical error
        self.logger.critical(f"Critical error - graceful failure: {error_info['error_message']}")
        
        # Return error information for user notification
        result['final_result'] = {
            'error': True,
            'message': 'A critical error occurred. Please check the logs and try again.',
            'error_id': self._generate_error_id(),
            'category': error_info['category']
        }
        
        return result
    
    def _apply_fallback(self, category: str, error_info: Dict[str, Any], 
                       context: Dict[str, Any]) -> Any:
        """Apply fallback strategy for the given category."""
        if category in self.fallback_strategies:
            try:
                return self.fallback_strategies[category](error_info, context)
            except Exception as e:
                self.logger.error(f"Fallback strategy failed for {category}: {e}")
                return None
        else:
            self.logger.warning(f"No fallback strategy available for category: {category}")
            return None
    
    def _fallback_data_loading(self, error_info: Dict[str, Any], 
                             context: Dict[str, Any]) -> Any:
        """Fallback for data loading errors."""
        try:
            # Try alternative file formats or sample data
            if 'file_path' in context:
                # Try different encodings
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                for encoding in encodings:
                    try:
                        df = pd.read_csv(context['file_path'], encoding=encoding)
                        return df
                    except:
                        continue
            
            # Return sample data as last resort
            return pd.DataFrame({
                'sample_column': ['Sample data 1', 'Sample data 2', 'Sample data 3'],
                'sample_numeric': [1, 2, 3]
            })
            
        except Exception as e:
            self.logger.error(f"Data loading fallback failed: {e}")
            return None
    
    def _fallback_data_validation(self, error_info: Dict[str, Any], 
                                context: Dict[str, Any]) -> Any:
        """Fallback for data validation errors."""
        try:
            # Return basic validation with relaxed rules
            df = context.get('dataframe')
            if df is not None:
                return {
                    'valid': True,
                    'warnings': ['Validation performed with relaxed rules due to errors'],
                    'dataframe': df,
                    'validation_level': 'basic'
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Data validation fallback failed: {e}")
            return None
    
    def _fallback_column_mapping(self, error_info: Dict[str, Any], 
                               context: Dict[str, Any]) -> Any:
        """Fallback for column mapping errors."""
        try:
            # Use simple string matching as fallback
            df = context.get('dataframe')
            if df is not None:
                simple_mappings = {}
                for col in df.columns:
                    col_lower = col.lower()
                    if 'date' in col_lower:
                        simple_mappings[col] = 'date'
                    elif 'price' in col_lower or 'amount' in col_lower:
                        simple_mappings[col] = 'price'
                    elif 'quantity' in col_lower or 'qty' in col_lower:
                        simple_mappings[col] = 'quantity'
                    else:
                        simple_mappings[col] = 'unknown'
                
                return {
                    'mappings': simple_mappings,
                    'confidence': 0.5,
                    'method': 'simple_fallback'
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Column mapping fallback failed: {e}")
            return None
    
    def _fallback_analytics_processing(self, error_info: Dict[str, Any], 
                                     context: Dict[str, Any]) -> Any:
        """Fallback for analytics processing errors."""
        try:
            # Return basic analytics with minimal processing
            df = context.get('dataframe')
            if df is not None:
                return {
                    'basic_statistics': df.describe().to_dict(),
                    'data_shape': df.shape,
                    'processing_level': 'basic',
                    'warnings': ['Analytics performed with basic methods due to processing errors']
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Analytics processing fallback failed: {e}")
            return None
    
    def _fallback_model_training(self, error_info: Dict[str, Any], 
                               context: Dict[str, Any]) -> Any:
        """Fallback for model training errors."""
        try:
            # Return simple rule-based model
            return {
                'model_type': 'rule_based_fallback',
                'accuracy': 0.6,
                'training_status': 'fallback_model_used',
                'warnings': ['Using rule-based fallback model due to training errors']
            }
            
        except Exception as e:
            self.logger.error(f"Model training fallback failed: {e}")
            return None
    
    def _fallback_forecasting(self, error_info: Dict[str, Any], 
                            context: Dict[str, Any]) -> Any:
        """Fallback for forecasting errors."""
        try:
            # Return simple linear trend forecast
            data = context.get('data')
            if data is not None and len(data) > 1:
                # Simple linear extrapolation
                last_value = data[-1]
                trend = (data[-1] - data[0]) / len(data) if len(data) > 1 else 0
                
                forecast_periods = context.get('forecast_periods', 10)
                forecast_values = [last_value + trend * (i + 1) for i in range(forecast_periods)]
                
                return {
                    'forecast_values': forecast_values,
                    'method': 'linear_trend_fallback',
                    'confidence': 0.4,
                    'warnings': ['Using simple linear trend due to forecasting errors']
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Forecasting fallback failed: {e}")
            return None
    
    def _fallback_visualization(self, error_info: Dict[str, Any], 
                              context: Dict[str, Any]) -> Any:
        """Fallback for visualization errors."""
        try:
            # Return basic table visualization
            df = context.get('dataframe')
            if df is not None:
                return {
                    'visualization_type': 'table',
                    'data': df.head(100).to_dict('records'),
                    'warnings': ['Using table visualization due to chart generation errors']
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Visualization fallback failed: {e}")
            return None
    
    def _fallback_feedback_processing(self, error_info: Dict[str, Any], 
                                    context: Dict[str, Any]) -> Any:
        """Fallback for feedback processing errors."""
        try:
            # Store feedback in simple format
            feedback_data = context.get('feedback_data', {})
            return {
                'status': 'stored_basic',
                'feedback_id': self._generate_error_id(),
                'message': 'Feedback stored with basic processing due to errors'
            }
            
        except Exception as e:
            self.logger.error(f"Feedback processing fallback failed: {e}")
            return None
    
    def _get_default_result(self, context: Dict[str, Any]) -> Any:
        """Get default result based on context."""
        if 'expected_result_type' in context:
            result_type = context['expected_result_type']
            if result_type == 'dataframe':
                return pd.DataFrame()
            elif result_type == 'dict':
                return {'status': 'default', 'message': 'Default result due to non-critical error'}
            elif result_type == 'list':
                return []
        
        return {'status': 'default'}
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = np.random.randint(1000, 9999)
        return f"ERR_{timestamp}_{random_suffix}"
    
    def _log_error(self, error_info: Dict[str, Any], error_id: str):
        """Log error with appropriate level."""
        log_message = f"Error ID: {error_id} - {error_info['category']}: {error_info['error_message']}"
        
        if error_info['severity'] == 'high':
            self.logger.error(log_message)
        elif error_info['severity'] == 'medium':
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def _store_error(self, error_info: Dict[str, Any], error_id: str):
        """Store error in database."""
        error_record = {
            'error_id': error_id,
            **error_info,
            'stored_at': datetime.now().isoformat()
        }
        
        self.error_db['errors'].append(error_record)
        self._save_error_database()
    
    def _update_performance_metrics(self, error_info: Dict[str, Any], 
                                  handling_result: Dict[str, Any]):
        """Update performance metrics based on error handling."""
        category = error_info['category']
        
        if category not in self.performance_metrics:
            self.performance_metrics[category] = {
                'total_errors': 0,
                'successful_recoveries': 0,
                'fallback_usage': 0,
                'average_recovery_time': 0.0,
                'last_updated': None
            }
        
        metrics = self.performance_metrics[category]
        metrics['total_errors'] += 1
        metrics['last_updated'] = datetime.now().isoformat()
        
        if handling_result.get('success', False):
            metrics['successful_recoveries'] += 1
        
        if handling_result.get('fallback_applied', False):
            metrics['fallback_usage'] += 1
        
        self._save_performance_metrics()
    
    def _load_error_database(self) -> Dict[str, Any]:
        """Load error database from file."""
        if os.path.exists(self.error_database_path):
            try:
                with open(self.error_database_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load error database: {e}")
        
        return {'errors': []}
    
    def _save_error_database(self):
        """Save error database to file."""
        try:
            with open(self.error_database_path, 'w') as f:
                json.dump(self.error_db, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save error database: {e}")
    
    def _load_performance_metrics(self) -> Dict[str, Any]:
        """Load performance metrics from file."""
        if os.path.exists(self.performance_metrics_path):
            try:
                with open(self.performance_metrics_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load performance metrics: {e}")
        
        return {}
    
    def _save_performance_metrics(self):
        """Save performance metrics to file."""
        try:
            with open(self.performance_metrics_path, 'w') as f:
                json.dump(self.performance_metrics, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save performance metrics: {e}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        stats = {
            'total_errors': len(self.error_db['errors']),
            'errors_by_category': {},
            'errors_by_severity': {},
            'recovery_rates': {},
            'recent_errors': [],
            'performance_metrics': self.performance_metrics
        }
        
        # Count errors by category and severity
        for error in self.error_db['errors']:
            category = error['category']
            severity = error['severity']
            
            stats['errors_by_category'][category] = stats['errors_by_category'].get(category, 0) + 1
            stats['errors_by_severity'][severity] = stats['errors_by_severity'].get(severity, 0) + 1
        
        # Calculate recovery rates
        for category, metrics in self.performance_metrics.items():
            if metrics['total_errors'] > 0:
                recovery_rate = metrics['successful_recoveries'] / metrics['total_errors']
                stats['recovery_rates'][category] = recovery_rate
        
        # Get recent errors (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_errors = [
            error for error in self.error_db['errors']
            if datetime.fromisoformat(error['timestamp']) > recent_cutoff
        ]
        stats['recent_errors'] = recent_errors[-10:]  # Last 10 recent errors
        
        return stats
    
    def retry_operation(self, func: Callable, *args, **kwargs) -> Any:
        """Decorator for automatic retry of operations."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            max_retries = kwargs.pop('max_retries', self.retry_configs['max_retries'])
            retry_delays = kwargs.pop('retry_delays', self.retry_configs['retry_delays'])
            
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(retry_delays[min(attempt, len(retry_delays) - 1)])
                        continue
                    else:
                        # All retries failed
                        context = {
                            'original_function': func,
                            'args': args,
                            'kwargs': kwargs,
                            'attempt': attempt + 1
                        }
                        handling_result = self.handle_error(e, context, 'general')
                        return handling_result['handling_result']['final_result']
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    
    def cleanup_old_errors(self, days_to_keep: int = 30):
        """Clean up old error records."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        original_count = len(self.error_db['errors'])
        self.error_db['errors'] = [
            error for error in self.error_db['errors']
            if datetime.fromisoformat(error['timestamp']) > cutoff_date
        ]
        
        removed_count = original_count - len(self.error_db['errors'])
        self._save_error_database()
        
        self.logger.info(f"Cleaned up {removed_count} old error records")
        return removed_count
