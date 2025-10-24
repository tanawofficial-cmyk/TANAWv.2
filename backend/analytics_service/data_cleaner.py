"""
Phase 6: Data Cleaning (Post-Rename)
Implements comprehensive data cleaning for canonical columns after rename.

Features:
- Type coercion for Date and numeric columns
- Null handling policy with quality assessment
- Duplicate detection and resolution
- Outlier detection with IQR and z-score
- Data normalization and standardization
- Comprehensive failure handling
- Advanced observability
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import warnings
import re
from scipy import stats

# Import existing configuration
from config_manager import get_config

@dataclass
class CleaningResult:
    """Represents the result of data cleaning for a column."""
    column_name: str
    original_type: str
    cleaned_type: str
    null_count: int
    null_percentage: float
    duplicates_count: int
    outliers_count: int
    quality_score: float
    cleaning_applied: List[str]
    warnings: List[str]

@dataclass
class DataCleaningResult:
    """Results from data cleaning process."""
    cleaned_df: pd.DataFrame
    cleaning_results: Dict[str, CleaningResult]
    processing_time_seconds: float
    metrics: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

class DataCleaner:
    """
    Phase 6: Data cleaning system for canonical columns.
    
    Features:
    - Type coercion for Date and numeric columns
    - Null handling policy with quality assessment
    - Duplicate detection and resolution
    - Outlier detection with IQR and z-score
    - Data normalization and standardization
    - Comprehensive failure handling
    - Advanced observability
    """
    
    def __init__(self, config=None):
        """Initialize data cleaner with configuration."""
        self.config = config or get_config()
        self.cleaner_version = "6.0.0"
        
        # Currency symbols and patterns
        self.currency_symbols = ['$', '€', '₱', '£', '¥', 'USD', 'EUR', 'PHP', 'GBP', 'JPY']
        self.currency_patterns = [
            r'[$€₱£¥]\s*[\d,]+\.?\d*',  # Symbol + number
            r'[\d,]+\.?\d*\s*[$€₱£¥]',  # Number + symbol
            r'USD\s*[\d,]+\.?\d*',      # USD + number
            r'EUR\s*[\d,]+\.?\d*',      # EUR + number
        ]
        
        # Region normalization mapping
        self.region_mapping = {
            'north': 'North', 'south': 'South', 'east': 'East', 'west': 'West',
            'northeast': 'Northeast', 'northwest': 'Northwest',
            'southeast': 'Southeast', 'southwest': 'Southwest',
            'central': 'Central', 'midwest': 'Midwest'
        }
        
        # Metrics tracking
        self.metrics = {
            'columns_cleaned': 0,
            'type_conversions': 0,
            'null_fills': 0,
            'duplicates_removed': 0,
            'outliers_detected': 0,
            'normalizations_applied': 0,
            'processing_time_ms': 0.0,
            'quality_issues': 0,
            'cleaning_failures': 0
        }
    
    def clean_data(self, df: pd.DataFrame, canonical_columns: List[str]) -> DataCleaningResult:
        """
        Clean data for canonical columns after rename.
        
        Args:
            df: DataFrame with canonical columns
            canonical_columns: List of canonical column names
            
        Returns:
            DataCleaningResult with cleaned DataFrame and results
        """
        start_time = datetime.now()
        
        try:
            # Create a copy to avoid modifying original
            cleaned_df = df.copy()
            cleaning_results = {}
            
            # Step 1: Type coercion
            print("🔧 Phase 6: Applying type coercion...")
            cleaned_df, type_results = self._apply_type_coercion(cleaned_df, canonical_columns)
            
            # Step 2: Null handling
            print("🔧 Phase 6: Handling null values...")
            cleaned_df, null_results = self._handle_nulls(cleaned_df, canonical_columns)
            
            # Step 3: Duplicate detection and resolution
            print("🔧 Phase 6: Detecting and resolving duplicates...")
            cleaned_df, duplicate_results = self._handle_duplicates(cleaned_df, canonical_columns)
            
            # Step 4: Outlier detection
            print("🔧 Phase 6: Detecting outliers...")
            cleaned_df, outlier_results = self._detect_outliers(cleaned_df, canonical_columns)
            
            # Step 5: Data normalization
            print("🔧 Phase 6: Normalizing data...")
            cleaned_df, normalization_results = self._normalize_data(cleaned_df, canonical_columns)
            
            # Combine all cleaning results
            for col in canonical_columns:
                if col in cleaned_df.columns:
                    cleaning_results[col] = CleaningResult(
                        column_name=col,
                        original_type=str(df[col].dtype),
                        cleaned_type=str(cleaned_df[col].dtype),
                        null_count=cleaned_df[col].isna().sum(),
                        null_percentage=(cleaned_df[col].isna().sum() / len(cleaned_df)) * 100,
                        duplicates_count=duplicate_results.get(col, {}).get('duplicates_removed', 0),
                        outliers_count=outlier_results.get(col, {}).get('outliers_detected', 0),
                        quality_score=self._calculate_quality_score(cleaned_df[col]),
                        cleaning_applied=self._get_cleaning_applied(col, type_results, null_results, duplicate_results, outlier_results, normalization_results),
                        warnings=self._get_cleaning_warnings(col, type_results, null_results, duplicate_results, outlier_results, normalization_results)
                    )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics['processing_time_ms'] = processing_time * 1000
            self.metrics['columns_cleaned'] = len(cleaning_results)
            
            return DataCleaningResult(
                cleaned_df=cleaned_df,
                cleaning_results=cleaning_results,
                processing_time_seconds=processing_time,
                metrics=self.metrics.copy(),
                success=True
            )
            
        except Exception as e:
            return DataCleaningResult(
                cleaned_df=df,
                cleaning_results={},
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                metrics=self.metrics.copy(),
                success=False,
                error_message=str(e)
            )
    
    def _apply_type_coercion(self, df: pd.DataFrame, canonical_columns: List[str]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Apply type coercion for canonical columns."""
        type_results = {}
        
        for col in canonical_columns:
            if col not in df.columns:
                continue
            
            try:
                original_dtype = df[col].dtype
                cleaning_applied = []
                
                if col == 'Date':
                    # Date coercion
                    df[col] = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                    cleaning_applied.append('date_coercion')
                    
                elif col in ['Sales', 'Amount']:
                    # Numeric coercion with currency handling
                    df[col] = self._clean_numeric_column(df[col])
                    cleaning_applied.append('numeric_coercion')
                    
                elif col == 'Quantity':
                    # Quantity coercion
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    cleaning_applied.append('quantity_coercion')
                    
                elif col in ['Product', 'Region', 'Customer']:
                    # String normalization
                    df[col] = df[col].astype(str).str.strip()
                    cleaning_applied.append('string_normalization')
                
                type_results[col] = {
                    'original_dtype': str(original_dtype),
                    'new_dtype': str(df[col].dtype),
                    'cleaning_applied': cleaning_applied,
                    'conversion_success': True
                }
                
                self.metrics['type_conversions'] += 1
                
            except Exception as e:
                type_results[col] = {
                    'original_dtype': str(df[col].dtype),
                    'new_dtype': str(df[col].dtype),
                    'cleaning_applied': [],
                    'conversion_success': False,
                    'error': str(e)
                }
                self.metrics['cleaning_failures'] += 1
        
        return df, type_results
    
    def _clean_numeric_column(self, series: pd.Series) -> pd.Series:
        """Clean numeric column by removing currency symbols and separators."""
        try:
            # Convert to string and clean
            cleaned = series.astype(str)
            
            # Remove currency symbols
            for symbol in self.currency_symbols:
                cleaned = cleaned.str.replace(symbol, '', regex=False)
            
            # Remove thousands separators (commas)
            cleaned = cleaned.str.replace(',', '')
            
            # Remove extra spaces
            cleaned = cleaned.str.strip()
            
            # Convert to numeric
            return pd.to_numeric(cleaned, errors='coerce')
            
        except Exception as e:
            print(f"⚠️ Error cleaning numeric column: {e}")
            return series
    
    def _handle_nulls(self, df: pd.DataFrame, canonical_columns: List[str]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Handle null values according to policy."""
        null_results = {}
        
        for col in canonical_columns:
            if col not in df.columns:
                continue
            
            try:
                null_count = df[col].isna().sum()
                null_percentage = (null_count / len(df)) * 100
                cleaning_applied = []
                quality_issues = []
                
                if null_count > 0:
                    if col in ['Sales', 'Amount', 'Quantity']:
                        # Numeric columns
                        if null_percentage < 5:
                            # Fill with median
                            median_value = df[col].median()
                            df[col].fillna(median_value, inplace=True)
                            cleaning_applied.append('median_fill')
                        elif null_percentage <= 30:
                            # Fill with median and mark low quality
                            median_value = df[col].median()
                            df[col].fillna(median_value, inplace=True)
                            cleaning_applied.append('median_fill')
                            quality_issues.append('low_data_quality')
                        else:
                            # Too many nulls - mark for analytics disable
                            quality_issues.append('disable_analytics')
                            
                    elif col in ['Product', 'Region', 'Customer']:
                        # Categorical columns
                        df[col].fillna('Unknown', inplace=True)
                        cleaning_applied.append('unknown_fill')
                        
                    elif col == 'Date':
                        # Date columns - keep as null for now
                        quality_issues.append('date_nulls_present')
                
                null_results[col] = {
                    'null_count': null_count,
                    'null_percentage': null_percentage,
                    'cleaning_applied': cleaning_applied,
                    'quality_issues': quality_issues
                }
                
                if cleaning_applied:
                    self.metrics['null_fills'] += 1
                if quality_issues:
                    self.metrics['quality_issues'] += 1
                
            except Exception as e:
                null_results[col] = {
                    'null_count': null_count,
                    'null_percentage': null_percentage,
                    'cleaning_applied': [],
                    'quality_issues': ['cleaning_error'],
                    'error': str(e)
                }
                self.metrics['cleaning_failures'] += 1
        
        return df, null_results
    
    def _handle_duplicates(self, df: pd.DataFrame, canonical_columns: List[str]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Handle duplicate rows."""
        duplicate_results = {}
        
        try:
            # Check if Transaction_ID exists
            if 'Transaction_ID' in df.columns:
                # Keep last by Date
                df = df.sort_values('Date').drop_duplicates(subset=['Transaction_ID'], keep='last')
                duplicate_results['Transaction_ID'] = {
                    'duplicates_removed': len(df) - len(df.drop_duplicates(subset=['Transaction_ID'])),
                    'method': 'keep_last_by_date'
                }
            else:
                # Use composite key
                composite_key = ['Date', 'Product', 'Region', 'Sales']
                available_keys = [key for key in composite_key if key in df.columns]
                
                if available_keys:
                    df = df.drop_duplicates(subset=available_keys, keep='last')
                    duplicate_results['composite_key'] = {
                        'duplicates_removed': len(df) - len(df.drop_duplicates(subset=available_keys)),
                        'method': 'composite_key',
                        'keys_used': available_keys
                    }
            
            self.metrics['duplicates_removed'] += sum(result.get('duplicates_removed', 0) for result in duplicate_results.values())
            
        except Exception as e:
            print(f"⚠️ Error handling duplicates: {e}")
            self.metrics['cleaning_failures'] += 1
        
        return df, duplicate_results
    
    def _detect_outliers(self, df: pd.DataFrame, canonical_columns: List[str]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Detect outliers using IQR and z-score methods."""
        outlier_results = {}
        
        for col in canonical_columns:
            if col not in df.columns or col not in ['Sales', 'Amount', 'Quantity']:
                continue
            
            try:
                # Convert to numeric if not already
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                
                if numeric_series.isna().all():
                    continue
                
                # IQR method
                Q1 = numeric_series.quantile(0.25)
                Q3 = numeric_series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                iqr_outliers = (numeric_series < lower_bound) | (numeric_series > upper_bound)
                
                # Z-score method
                z_scores = np.abs(stats.zscore(numeric_series.dropna()))
                z_outliers = z_scores > 3
                
                # Combine methods
                outliers = iqr_outliers | z_outliers
                outlier_count = outliers.sum()
                
                # Add anomaly flag column
                df[f'{col}_anomaly_flag'] = outliers.astype(int)
                
                outlier_results[col] = {
                    'outliers_detected': int(outlier_count),
                    'outlier_percentage': (outlier_count / len(df)) * 100,
                    'iqr_outliers': int(iqr_outliers.sum()),
                    'z_score_outliers': int(z_outliers.sum()),
                    'anomaly_flag_added': True
                }
                
                self.metrics['outliers_detected'] += outlier_count
                
            except Exception as e:
                outlier_results[col] = {
                    'outliers_detected': 0,
                    'outlier_percentage': 0,
                    'error': str(e)
                }
                self.metrics['cleaning_failures'] += 1
        
        return df, outlier_results
    
    def _normalize_data(self, df: pd.DataFrame, canonical_columns: List[str]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Normalize and standardize data."""
        normalization_results = {}
        
        for col in canonical_columns:
            if col not in df.columns:
                continue
            
            try:
                cleaning_applied = []
                
                if col in ['Product', 'Region', 'Customer']:
                    # String normalization
                    df[col] = df[col].astype(str).str.strip().str.title()
                    cleaning_applied.append('string_trim')
                    cleaning_applied.append('case_standardization')
                    
                    if col == 'Region':
                        # Region normalization
                        df[col] = df[col].str.lower().map(self.region_mapping).fillna(df[col])
                        cleaning_applied.append('region_normalization')
                        
                elif col in ['Sales', 'Amount']:
                    # Currency normalization
                    df[col] = df[col].round(2)  # Round to 2 decimal places
                    cleaning_applied.append('currency_rounding')
                
                normalization_results[col] = {
                    'cleaning_applied': cleaning_applied,
                    'normalization_success': True
                }
                
                if cleaning_applied:
                    self.metrics['normalizations_applied'] += 1
                
            except Exception as e:
                normalization_results[col] = {
                    'cleaning_applied': [],
                    'normalization_success': False,
                    'error': str(e)
                }
                self.metrics['cleaning_failures'] += 1
        
        return df, normalization_results
    
    def _calculate_quality_score(self, series: pd.Series) -> float:
        """Calculate data quality score for a column."""
        try:
            total_rows = len(series)
            if total_rows == 0:
                return 0.0
            
            # Null percentage (lower is better)
            null_pct = (series.isna().sum() / total_rows) * 100
            null_score = max(0, 100 - null_pct)
            
            # Duplicate percentage (lower is better)
            duplicate_pct = (series.duplicated().sum() / total_rows) * 100
            duplicate_score = max(0, 100 - duplicate_pct)
            
            # Overall quality score
            quality_score = (null_score + duplicate_score) / 2
            
            return round(quality_score, 2)
            
        except Exception:
            return 0.0
    
    def _get_cleaning_applied(self, col: str, type_results: Dict, null_results: Dict, 
                            duplicate_results: Dict, outlier_results: Dict, normalization_results: Dict) -> List[str]:
        """Get list of cleaning operations applied to a column."""
        applied = []
        
        if col in type_results:
            applied.extend(type_results[col].get('cleaning_applied', []))
        if col in null_results:
            applied.extend(null_results[col].get('cleaning_applied', []))
        if col in normalization_results:
            applied.extend(normalization_results[col].get('cleaning_applied', []))
        
        return list(set(applied))  # Remove duplicates
    
    def _get_cleaning_warnings(self, col: str, type_results: Dict, null_results: Dict,
                             duplicate_results: Dict, outlier_results: Dict, normalization_results: Dict) -> List[str]:
        """Get list of warnings for a column."""
        warnings = []
        
        if col in null_results:
            warnings.extend(null_results[col].get('quality_issues', []))
        if col in outlier_results:
            if outlier_results[col].get('outlier_percentage', 0) > 10:
                warnings.append('high_outlier_percentage')
        
        return warnings
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            'columns_cleaned': 0,
            'type_conversions': 0,
            'null_fills': 0,
            'duplicates_removed': 0,
            'outliers_detected': 0,
            'normalizations_applied': 0,
            'processing_time_ms': 0.0,
            'quality_issues': 0,
            'cleaning_failures': 0
        }
    
    def emit_metrics(self):
        """Emit metrics for observability."""
        try:
            metrics = {
                "cleaning.columns_cleaned": self.metrics['columns_cleaned'],
                "cleaning.type_conversions": self.metrics['type_conversions'],
                "cleaning.null_fills": self.metrics['null_fills'],
                "cleaning.duplicates_removed": self.metrics['duplicates_removed'],
                "cleaning.outliers_detected": self.metrics['outliers_detected'],
                "cleaning.normalizations_applied": self.metrics['normalizations_applied'],
                "cleaning.processing_time_ms": self.metrics['processing_time_ms'],
                "cleaning.quality_issues": self.metrics['quality_issues'],
                "cleaning.cleaning_failures": self.metrics['cleaning_failures']
            }
            
            # In a real implementation, you would send these to your metrics system
            print(f"📊 Data cleaning metrics: {metrics}")
            return metrics
            
        except Exception as e:
            print(f"⚠️ Error emitting data cleaning metrics: {e}")
            return {"cleaning.metrics_error": str(e)}

# Global cleaner instance
data_cleaner = DataCleaner()

def clean_data(df: pd.DataFrame, canonical_columns: List[str]) -> DataCleaningResult:
    """
    Convenience function to clean data for canonical columns.
    
    Args:
        df: DataFrame with canonical columns
        canonical_columns: List of canonical column names
        
    Returns:
        DataCleaningResult with cleaned DataFrame and results
    """
    return data_cleaner.clean_data(df, canonical_columns)

if __name__ == "__main__":
    # Test the data cleaner
    print("🧪 Testing Data Cleaner")
    print("=" * 50)
    
    # Create test DataFrame
    test_df = pd.DataFrame({
        'Date': ['2023-01-01', '2023-01-02', '2023-01-03', 'invalid', '2023-01-05'],
        'Sales': ['$100.50', '€200.75', '₱300.00', 'invalid', '$500.25'],
        'Product': ['Product A', 'Product B', 'Product C', None, 'Product E'],
        'Region': ['north', 'SOUTH', 'east', 'west', 'central'],
        'Quantity': [1, 2, 3, 'invalid', 5]
    })
    
    canonical_columns = ['Date', 'Sales', 'Product', 'Region', 'Quantity']
    
    result = clean_data(test_df, canonical_columns)
    
    if result.success:
        print(f"✅ Successfully cleaned {len(result.cleaning_results)} columns")
        print(f"⏱️ Processing time: {result.processing_time_seconds:.3f}s")
        
        print("\n📊 Cleaning Results:")
        for col, cleaning_result in result.cleaning_results.items():
            print(f"   {col}: {cleaning_result.cleaning_applied} (quality: {cleaning_result.quality_score})")
    else:
        print(f"❌ Error: {result.error_message}")
