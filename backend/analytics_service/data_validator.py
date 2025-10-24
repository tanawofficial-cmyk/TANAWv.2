# data_validator.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
import re
from datetime import datetime, timedelta
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class DataValidator:
    """
    Comprehensive data validation and cleaning logic for TANAW.
    Implements missing value handling, outlier detection, duplicate removal, and data type validation.
    """
    
    def __init__(self):
        self.validation_schema = {}
        self.cleaning_log = []
        self.outlier_methods = ['iqr', 'zscore', 'isolation_forest', 'local_outlier_factor']
        
    def validate_and_clean_dataset(self, df: pd.DataFrame, 
                                 column_mapping: Dict[str, Any] = None,
                                 validation_config: Dict[str, Any] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Comprehensive dataset validation and cleaning.
        
        Args:
            df: DataFrame to validate and clean
            column_mapping: Optional column mapping information
            validation_config: Configuration for validation rules
            
        Returns:
            Tuple of (cleaned_dataframe, validation_report)
        """
        self.cleaning_log = []
        original_df = df.copy()
        
        # Initialize validation report
        validation_report = {
            'original_shape': df.shape,
            'cleaning_steps': [],
            'data_quality_score': 0.0,
            'issues_found': [],
            'issues_resolved': [],
            'warnings': [],
            'summary': {}
        }
        
        try:
            # Step 1: Basic data type validation
            df = self._validate_data_types(df, validation_report, column_mapping)
            
            # Step 2: Handle missing values
            df = self._handle_missing_values(df, validation_report)
            
            # Step 3: Detect and handle outliers
            df = self._handle_outliers(df, validation_report)
            
            # Step 4: Remove duplicates
            df = self._remove_duplicates(df, validation_report)
            
            # Step 5: Validate business rules
            df = self._validate_business_rules(df, column_mapping, validation_report)
            
            # Step 6: Final data quality assessment
            validation_report['data_quality_score'] = self._calculate_quality_score(original_df, df)
            validation_report['final_shape'] = df.shape
            validation_report['summary'] = self._generate_summary(validation_report)
            
        except Exception as e:
            validation_report['errors'] = [f"Validation failed: {str(e)}"]
            self.cleaning_log.append(f"ERROR: {str(e)}")
        
        return df, validation_report
    
    def _validate_data_types(self, df: pd.DataFrame, report: Dict[str, Any], column_mapping: Dict[str, Any] = None) -> pd.DataFrame:
        """Validate and correct data types based on column content."""
        self.cleaning_log.append("Starting data type validation...")
        
        type_corrections = []
        
        for col in df.columns:
            original_dtype = df[col].dtype
            
            # Try to infer better data type with column mapping hints
            inferred_type = self._infer_optimal_type(df[col], column_name=col, column_mapping=column_mapping)
            
            if inferred_type != original_dtype:
                try:
                    df[col] = self._convert_to_type(df[col], inferred_type)
                    type_corrections.append({
                        'column': col,
                        'original_type': str(original_dtype),
                        'corrected_type': str(inferred_type),
                        'success': True
                    })
                    self.cleaning_log.append(f"✓ Converted {col} from {original_dtype} to {inferred_type}")
                except Exception as e:
                    type_corrections.append({
                        'column': col,
                        'original_type': str(original_dtype),
                        'corrected_type': str(inferred_type),
                        'success': False,
                        'error': str(e)
                    })
                    self.cleaning_log.append(f"✗ Failed to convert {col}: {str(e)}")
        
        report['cleaning_steps'].append({
            'step': 'data_type_validation',
            'details': type_corrections,
            'timestamp': datetime.now().isoformat()
        })
        
        return df
    
    def _infer_optimal_type(self, series: pd.Series, column_name: str = None, column_mapping: Dict[str, Any] = None) -> str:
        """Infer the optimal data type for a series."""
        # Handle missing values
        non_null_series = series.dropna()
        
        if len(non_null_series) == 0:
            return 'object'
        
        # Check column mapping first for hints
        if column_name and column_mapping:
            mapped_columns = column_mapping.get('mapped_columns', [])
            for mapping in mapped_columns:
                if mapping.get('original_column') == column_name:
                    mapped_type = mapping.get('mapped_column', '').lower()
                    # Use mapping hints to influence type inference
                    if mapped_type in ['date', 'timestamp', 'time']:
                        # Only use datetime if it actually looks like datetime
                        if self._looks_like_datetime(non_null_series):
                            return 'datetime64[ns]'
                    elif mapped_type in ['quantity', 'price', 'amount', 'sales', 'revenue']:
                        # Force numeric for these business metrics
                        if self._looks_like_numeric(non_null_series):
                            return 'float64' if not self._looks_like_integer(non_null_series) else 'int64'
                    break
        
        # Try numeric first for business data (more common than datetime)
        if self._looks_like_numeric(non_null_series):
            if self._looks_like_integer(non_null_series):
                return 'int64'
            else:
                return 'float64'
        
        # Try datetime only if it doesn't look numeric
        if self._looks_like_datetime(non_null_series):
            return 'datetime64[ns]'
        
        # Try boolean
        if self._looks_like_boolean(non_null_series):
            return 'bool'
        
        # Default to string
        return 'object'
    
    def _looks_like_datetime(self, series: pd.Series) -> bool:
        """Check if series looks like datetime data."""
        try:
            # Sample first 100 values for efficiency
            sample = series.head(100)
            
            # First check if it's already numeric - if so, it's likely not a datetime
            if pd.api.types.is_numeric_dtype(sample):
                # Only consider numeric as datetime if it looks like a timestamp
                # Check if values are in reasonable timestamp range (after 1970, before 2100)
                numeric_sample = pd.to_numeric(sample, errors='coerce').dropna()
                if len(numeric_sample) > 0:
                    # Unix timestamp range: 1970-01-01 to 2100-01-01
                    min_timestamp = 0  # 1970-01-01
                    max_timestamp = 4102444800  # 2100-01-01
                    
                    # Check if values are in timestamp range and look like timestamps
                    in_range = ((numeric_sample >= min_timestamp) & (numeric_sample <= max_timestamp)).mean()
                    
                    # Also check if they look like formatted dates (not just large numbers)
                    # If they're very large numbers, they're probably not dates
                    if in_range < 0.8 or numeric_sample.mean() > 1e12:  # 1e12 = year 2001
                        return False
            
            # For non-numeric or potential timestamp data, try parsing
            parsed = pd.to_datetime(sample, errors='coerce', infer_datetime_format=True)
            return parsed.notna().mean() >= 0.8
        except:
            return False
    
    def _looks_like_numeric(self, series: pd.Series) -> bool:
        """Check if series looks like numeric data."""
        try:
            sample = series.head(100)
            numeric = pd.to_numeric(sample, errors='coerce')
            return numeric.notna().mean() >= 0.8
        except:
            return False
    
    def _looks_like_integer(self, series: pd.Series) -> bool:
        """Check if numeric series looks like integers."""
        try:
            numeric = pd.to_numeric(series, errors='coerce').dropna()
            return all(val.is_integer() for val in numeric.head(50))
        except:
            return False
    
    def _looks_like_boolean(self, series: pd.Series) -> bool:
        """Check if series looks like boolean data."""
        sample = series.head(100).astype(str).str.lower()
        boolean_values = {'true', 'false', '1', '0', 'yes', 'no', 'y', 'n', 't', 'f'}
        return sample.isin(boolean_values).mean() >= 0.8
    
    def _convert_to_type(self, series: pd.Series, target_type: str) -> pd.Series:
        """Convert series to target type with error handling."""
        if target_type == 'datetime64[ns]':
            return pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
        elif target_type == 'bool':
            return series.astype(str).str.lower().map({
                'true': True, 'false': False, '1': True, '0': False,
                'yes': True, 'no': False, 'y': True, 'n': False,
                't': True, 'f': False
            })
        elif target_type in ['int64', 'float64']:
            return pd.to_numeric(series, errors='coerce')
        else:
            return series.astype(target_type)
    
    def _handle_missing_values(self, df: pd.DataFrame, report: Dict[str, Any]) -> pd.DataFrame:
        """Handle missing values with intelligent imputation strategies."""
        self.cleaning_log.append("Handling missing values...")
        
        missing_summary = []
        
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            
            if missing_count > 0:
                missing_percentage = (missing_count / len(df)) * 100
                
                # Choose imputation strategy
                strategy = self._choose_imputation_strategy(df[col], missing_percentage)
                
                # Apply imputation
                df[col] = self._apply_imputation(df[col], strategy)
                
                missing_summary.append({
                    'column': col,
                    'missing_count': missing_count,
                    'missing_percentage': round(missing_percentage, 2),
                    'strategy': strategy,
                    'success': True
                })
                
                self.cleaning_log.append(
                    f"✓ Imputed {missing_count} missing values in {col} using {strategy}"
                )
        
        report['cleaning_steps'].append({
            'step': 'missing_value_imputation',
            'details': missing_summary,
            'timestamp': datetime.now().isoformat()
        })
        
        return df
    
    def _choose_imputation_strategy(self, series: pd.Series, missing_percentage: float) -> str:
        """Choose appropriate imputation strategy based on data characteristics."""
        # If more than 50% missing, consider dropping the column
        if missing_percentage > 50:
            return 'drop_column'
        
        # Check data type
        if pd.api.types.is_numeric_dtype(series):
            # For numeric data, use mean/median based on distribution
            non_null = series.dropna()
            if len(non_null) > 0:
                skewness = abs(stats.skew(non_null))
                if skewness > 1:  # Highly skewed
                    return 'median'
                else:
                    return 'mean'
            else:
                return 'zero'
        elif pd.api.types.is_datetime64_any_dtype(series):
            return 'forward_fill'
        else:
            # For categorical data, use mode
            return 'mode'
    
    def _apply_imputation(self, series: pd.Series, strategy: str) -> pd.Series:
        """Apply the chosen imputation strategy."""
        if strategy == 'mean':
            return series.fillna(series.mean())
        elif strategy == 'median':
            return series.fillna(series.median())
        elif strategy == 'mode':
            mode_val = series.mode()
            return series.fillna(mode_val.iloc[0] if not mode_val.empty else 'Unknown')
        elif strategy == 'forward_fill':
            return series.fillna(method='ffill').fillna(method='bfill')
        elif strategy == 'zero':
            return series.fillna(0)
        elif strategy == 'drop_column':
            # This would be handled at a higher level
            return series
        else:
            return series.fillna('Unknown')
    
    def _handle_outliers(self, df: pd.DataFrame, report: Dict[str, Any]) -> pd.DataFrame:
        """Detect and handle outliers in numeric columns."""
        self.cleaning_log.append("Detecting and handling outliers...")
        
        outlier_summary = []
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            outliers = self._detect_outliers(df[col], method='iqr')
            
            if outliers.sum() > 0:
                outlier_count = int(outliers.sum())
                outlier_percentage = (outlier_count / len(df)) * 100
                
                # Choose handling strategy
                strategy = self._choose_outlier_strategy(outlier_percentage)
                
                # Apply strategy
                df[col] = self._apply_outlier_strategy(df[col], outliers, strategy)
                
                outlier_summary.append({
                    'column': col,
                    'outlier_count': outlier_count,
                    'outlier_percentage': round(outlier_percentage, 2),
                    'strategy': strategy,
                    'success': True
                })
                
                self.cleaning_log.append(
                    f"✓ Handled {outlier_count} outliers in {col} using {strategy}"
                )
        
        report['cleaning_steps'].append({
            'step': 'outlier_handling',
            'details': outlier_summary,
            'timestamp': datetime.now().isoformat()
        })
        
        return df
    
    def _detect_outliers(self, series: pd.Series, method: str = 'iqr') -> pd.Series:
        """Detect outliers using specified method."""
        if method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return (series < lower_bound) | (series > upper_bound)
        
        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(series.dropna()))
            threshold = 3
            outlier_mask = pd.Series(False, index=series.index)
            outlier_mask.loc[series.dropna().index[z_scores > threshold]] = True
            return outlier_mask
        
        else:
            return pd.Series(False, index=series.index)
    
    def _choose_outlier_strategy(self, outlier_percentage: float) -> str:
        """Choose appropriate outlier handling strategy."""
        if outlier_percentage > 20:
            return 'remove'  # Too many outliers, remove them
        elif outlier_percentage > 5:
            return 'cap'     # Cap outliers to reasonable bounds
        else:
            return 'keep'    # Keep outliers, they might be legitimate
    
    def _apply_outlier_strategy(self, series: pd.Series, outliers: pd.Series, 
                              strategy: str) -> pd.Series:
        """Apply the chosen outlier handling strategy."""
        if strategy == 'remove':
            return series[~outliers]
        elif strategy == 'cap':
            # Cap outliers to 95th and 5th percentiles
            lower_bound = series.quantile(0.05)
            upper_bound = series.quantile(0.95)
            return series.clip(lower_bound, upper_bound)
        else:
            return series  # Keep outliers
    
    def _remove_duplicates(self, df: pd.DataFrame, report: Dict[str, Any]) -> pd.DataFrame:
        """Remove duplicate rows with intelligent detection."""
        self.cleaning_log.append("Removing duplicate rows...")
        
        # Count duplicates
        duplicate_count = df.duplicated().sum()
        
        if duplicate_count > 0:
            duplicate_percentage = (duplicate_count / len(df)) * 100
            
            # Remove duplicates, keeping first occurrence
            df_cleaned = df.drop_duplicates(keep='first')
            
            duplicate_summary = {
                'duplicate_count': duplicate_count,
                'duplicate_percentage': round(duplicate_percentage, 2),
                'rows_before': len(df),
                'rows_after': len(df_cleaned),
                'success': True
            }
            
            self.cleaning_log.append(
                f"✓ Removed {duplicate_count} duplicate rows ({duplicate_percentage:.2f}%)"
            )
            
            report['cleaning_steps'].append({
                'step': 'duplicate_removal',
                'details': duplicate_summary,
                'timestamp': datetime.now().isoformat()
            })
            
            return df_cleaned
        else:
            self.cleaning_log.append("✓ No duplicate rows found")
            return df
    
    def _validate_business_rules(self, df: pd.DataFrame, column_mapping: Dict[str, Any], 
                               report: Dict[str, Any]) -> pd.DataFrame:
        """Validate business rules based on column types."""
        self.cleaning_log.append("Validating business rules...")
        
        business_rule_violations = []
        
        # Validate price columns
        price_columns = self._get_columns_by_type(df, column_mapping, ['price', 'amount', 'cost', 'revenue'])
        for col in price_columns:
            violations = self._validate_price_column(df[col])
            if violations:
                business_rule_violations.extend([{
                    'column': col,
                    'rule': 'price_validation',
                    'violations': violations
                }])
        
        # Validate quantity columns
        quantity_columns = self._get_columns_by_type(df, column_mapping, ['quantity', 'qty', 'units'])
        for col in quantity_columns:
            violations = self._validate_quantity_column(df[col])
            if violations:
                business_rule_violations.extend([{
                    'column': col,
                    'rule': 'quantity_validation',
                    'violations': violations
                }])
        
        # Validate date columns
        date_columns = self._get_columns_by_type(df, column_mapping, ['date', 'timestamp'])
        for col in date_columns:
            violations = self._validate_date_column(df[col])
            if violations:
                business_rule_violations.extend([{
                    'column': col,
                    'rule': 'date_validation',
                    'violations': violations
                }])
        
        report['cleaning_steps'].append({
            'step': 'business_rule_validation',
            'details': business_rule_violations,
            'timestamp': datetime.now().isoformat()
        })
        
        return df
    
    def _get_columns_by_type(self, df: pd.DataFrame, column_mapping: Dict[str, Any], 
                           types: List[str]) -> List[str]:
        """Get columns that match specified types."""
        if not column_mapping:
            return []
        
        matching_columns = []
        for col in df.columns:
            if column_mapping.get(col, {}).get('mapped_column', '').lower() in types:
                matching_columns.append(col)
        
        return matching_columns
    
    def _validate_price_column(self, series: pd.Series) -> List[str]:
        """Validate price column business rules."""
        violations = []
        
        # Check for negative prices
        if pd.api.types.is_numeric_dtype(series):
            negative_count = (series < 0).sum()
            if negative_count > 0:
                violations.append(f"{negative_count} negative prices found")
            
            # Check for unreasonably high prices
            if series.max() > 1000000:  # 1 million
                violations.append("Unreasonably high prices detected")
        
        return violations
    
    def _validate_quantity_column(self, series: pd.Series) -> List[str]:
        """Validate quantity column business rules."""
        violations = []
        
        # Check for negative quantities
        if pd.api.types.is_numeric_dtype(series):
            negative_count = (series < 0).sum()
            if negative_count > 0:
                violations.append(f"{negative_count} negative quantities found")
            
            # Check for non-integer quantities (if expected)
            non_integer_count = (series % 1 != 0).sum()
            if non_integer_count > 0:
                violations.append(f"{non_integer_count} non-integer quantities found")
        
        return violations
    
    def _validate_date_column(self, series: pd.Series) -> List[str]:
        """Validate date column business rules."""
        violations = []
        
        if pd.api.types.is_datetime64_any_dtype(series):
            # Check for future dates (if not expected)
            future_dates = (series > datetime.now()).sum()
            if future_dates > 0:
                violations.append(f"{future_dates} future dates found")
            
            # Check for very old dates
            old_dates = (series < datetime(1900, 1, 1)).sum()
            if old_dates > 0:
                violations.append(f"{old_dates} very old dates found")
        
        return violations
    
    def _calculate_quality_score(self, original_df: pd.DataFrame, 
                               cleaned_df: pd.DataFrame) -> float:
        """Calculate overall data quality score (0-100)."""
        score = 100.0
        
        # Deduct for data loss
        data_loss = (len(original_df) - len(cleaned_df)) / len(original_df)
        score -= data_loss * 30
        
        # Deduct for remaining missing values
        missing_percentage = cleaned_df.isnull().sum().sum() / (len(cleaned_df) * len(cleaned_df.columns))
        score -= missing_percentage * 20
        
        # Deduct for data type inconsistencies
        type_issues = self._count_type_issues(cleaned_df)
        score -= type_issues * 5
        
        return max(0.0, min(100.0, score))
    
    def _count_type_issues(self, df: pd.DataFrame) -> int:
        """Count potential data type issues."""
        issues = 0
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Check for non-numeric values in numeric columns
                if df[col].dtype == 'object':
                    issues += 1
        
        return issues
    
    def _generate_summary(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics for the validation report."""
        steps = report.get('cleaning_steps', [])
        
        summary = {
            'total_cleaning_steps': len(steps),
            'data_loss_percentage': 0.0,
            'quality_improvement': 0.0,
            'issues_resolved': 0,
            'warnings_generated': 0
        }
        
        if steps:
            # Calculate data loss
            original_rows = report.get('original_shape', (0, 0))[0]
            final_rows = report.get('final_shape', (0, 0))[0]
            if original_rows > 0:
                summary['data_loss_percentage'] = round(
                    ((original_rows - final_rows) / original_rows) * 100, 2
                )
            
            # Count resolved issues
            for step in steps:
                if step.get('step') == 'missing_value_imputation':
                    summary['issues_resolved'] += len(step.get('details', []))
                elif step.get('step') == 'outlier_handling':
                    summary['issues_resolved'] += len(step.get('details', []))
                elif step.get('step') == 'duplicate_removal':
                    summary['issues_resolved'] += 1
        
        return summary
    
    def get_validation_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate a validation schema for the dataset."""
        schema = {
            'columns': {},
            'rules': [],
            'constraints': []
        }
        
        for col in df.columns:
            col_schema = {
                'name': col,
                'dtype': str(df[col].dtype),
                'nullable': df[col].isnull().any(),
                'unique': df[col].nunique() == len(df[col]),
                'constraints': []
            }
            
            # Add type-specific constraints
            if pd.api.types.is_numeric_dtype(df[col]):
                col_schema['constraints'].extend([
                    {'type': 'min_value', 'value': float(df[col].min())},
                    {'type': 'max_value', 'value': float(df[col].max())},
                    {'type': 'mean', 'value': float(df[col].mean())}
                ])
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                col_schema['constraints'].extend([
                    {'type': 'min_date', 'value': df[col].min().isoformat()},
                    {'type': 'max_date', 'value': df[col].max().isoformat()}
                ])
            
            schema['columns'][col] = col_schema
        
        return schema
