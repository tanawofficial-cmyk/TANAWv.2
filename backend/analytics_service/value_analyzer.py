"""
Phase 3: Value Sampling & Local Inference
Implements comprehensive value analysis to improve column mapping accuracy.
Analyzes actual column values to infer semantics (numeric/date/currency/ID/category).

Features:
- Intelligent value sampling strategy
- Multiple value detectors (numeric, date, currency, ID, category)
- Signal combination with weighted scoring
- Local inference and confidence calculation
- Failure modes and fallbacks
- Comprehensive observability
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import warnings
from collections import Counter
import math

# Try to import optional dependencies
try:
    from dateutil import parser as date_parser
    DATEUTIL_AVAILABLE = True
except ImportError:
    DATEUTIL_AVAILABLE = False
    warnings.warn("dateutil not available. Install with: pip install python-dateutil")

# Import existing configuration
from config_manager import get_config

@dataclass
class ValueSignal:
    """Represents a value analysis signal for a column."""
    numeric_pct: float
    date_pct: float
    currency_pct: float
    unique_pct: float
    avg_len: float
    entropy: float
    id_pattern_pct: float
    region_geo_pct: float
    sku_pattern_pct: float
    null_pct: float
    sample_size: int

@dataclass
class ColumnInference:
    """Represents local inference result for a column."""
    column_name: str
    best_candidate: str
    local_confidence: float
    signals: ValueSignal
    weighted_score: float
    inference_method: str
    reasoning: str

@dataclass
class ValueAnalysisResult:
    """Results from value analysis and local inference."""
    column_inferences: Dict[str, ColumnInference]
    processing_time_seconds: float
    metrics: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

class ValueAnalyzer:
    """
    Phase 3: Value sampling and local inference system.
    
    Features:
    - Intelligent value sampling strategy
    - Multiple value detectors
    - Signal combination with weighted scoring
    - Local inference and confidence calculation
    - Failure modes and fallbacks
    - Comprehensive observability
    """
    
    def __init__(self, config=None):
        """Initialize value analyzer with configuration."""
        self.config = config or get_config()
        self.analyzer_version = "3.0.0"
        
        # Initialize value detectors
        self._init_value_detectors()
        
        # Initialize geographic patterns
        self._init_geographic_patterns()
        
        # Initialize SKU patterns
        self._init_sku_patterns()
        
        # Metrics tracking
        self.metrics = {
            'columns_analyzed': 0,
            'samples_processed': 0,
            'numeric_detections': 0,
            'date_detections': 0,
            'currency_detections': 0,
            'id_detections': 0,
            'region_detections': 0,
            'sku_detections': 0,
            'processing_time_ms': 0.0,
            'local_confidence_avg': 0.0
        }
    
    def analyze_values(self, df: pd.DataFrame, header_candidates: Dict[str, List[Any]]) -> ValueAnalysisResult:
        """
        Analyze column values and perform local inference.
        
        Args:
            df: DataFrame with columns to analyze
            header_candidates: Header candidates from Phase 2
            
        Returns:
            ValueAnalysisResult with local inference results
        """
        start_time = datetime.now()
        
        try:
            column_inferences = {}
            
            for col in df.columns:
                try:
                    # Ensure col is a string to avoid Series ambiguity
                    col_str = str(col)
                    
                    # Get header candidates for this column
                    candidates = header_candidates.get(col_str, [])
                    if not candidates:
                        continue
                    
                    # Analyze column values
                    signals = self._compute_value_signals(df[col_str])
                    
                    # Perform local inference
                    inference = self._perform_local_inference(col_str, signals, candidates)
                    column_inferences[col_str] = inference
                    
                    self.metrics['columns_analyzed'] += 1
                    
                except Exception as e:
                    print(f"⚠️ Error analyzing column '{col_str}': {e}")
                    continue
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics['processing_time_ms'] = processing_time * 1000
            
            # Calculate average local confidence
            if column_inferences:
                avg_confidence = sum(inf.local_confidence for inf in column_inferences.values()) / len(column_inferences)
                self.metrics['local_confidence_avg'] = avg_confidence
            
            return ValueAnalysisResult(
                column_inferences=column_inferences,
                processing_time_seconds=processing_time,
                metrics=self.metrics.copy(),
                success=True
            )
            
        except Exception as e:
            return ValueAnalysisResult(
                column_inferences={},
                processing_time_seconds=0.0,
                metrics=self.metrics.copy(),
                success=False,
                error_message=str(e)
            )
    
    def _compute_value_signals(self, series: pd.Series) -> ValueSignal:
        """
        Compute value analysis signals for a column.
        
        Args:
            series: Pandas Series to analyze
            
        Returns:
            ValueSignal with computed signals
        """
        # Create intelligent sample
        sample = self._create_intelligent_sample(series)
        sample_size = len(sample)
        
        if sample_size == 0:
            return ValueSignal(
                numeric_pct=0.0, date_pct=0.0, currency_pct=0.0, unique_pct=0.0,
                avg_len=0.0, entropy=0.0, id_pattern_pct=0.0, region_geo_pct=0.0,
                sku_pattern_pct=0.0, null_pct=100.0, sample_size=0
            )
        
        # Compute signals
        numeric_pct = self._detect_numeric_percentage(sample)
        date_pct = self._detect_date_percentage(sample)
        currency_pct = self._detect_currency_percentage(sample)
        unique_pct = (len(sample.unique()) / sample_size) * 100
        avg_len = sample.astype(str).str.len().mean()
        entropy = self._calculate_entropy(sample)
        id_pattern_pct = self._detect_id_pattern_percentage(sample)
        region_geo_pct = self._detect_region_geo_percentage(sample)
        sku_pattern_pct = self._detect_sku_pattern_percentage(sample)
        null_pct = (sample.isna().sum() / sample_size) * 100
        
        return ValueSignal(
            numeric_pct=numeric_pct,
            date_pct=date_pct,
            currency_pct=currency_pct,
            unique_pct=unique_pct,
            avg_len=avg_len,
            entropy=entropy,
            id_pattern_pct=id_pattern_pct,
            region_geo_pct=region_geo_pct,
            sku_pattern_pct=sku_pattern_pct,
            null_pct=null_pct,
            sample_size=sample_size
        )
    
    def _create_intelligent_sample(self, series: pd.Series) -> pd.Series:
        """
        Create intelligent sample using head + tail + random strategy.
        
        Args:
            series: Pandas Series to sample
            
        Returns:
            Sampled Series
        """
        total_rows = len(series)
        
        # Calculate sample size
        sample_size = min(
            self.config.file_processing.sample_rows_limit,
            max(
                self.config.file_processing.sample_min,
                int(0.05 * total_rows)
            )
        )
        
        if total_rows <= sample_size:
            return series
        
        # Create sample: head(20) + tail(20) + random(sample_size-40)
        head_size = min(20, sample_size // 3)
        tail_size = min(20, sample_size // 3)
        random_size = sample_size - head_size - tail_size
        
        samples = []
        
        # Add head
        if head_size > 0:
            samples.append(series.head(head_size))
        
        # Add tail
        if tail_size > 0:
            samples.append(series.tail(tail_size))
        
        # Add random sample
        if random_size > 0:
            random_indices = np.random.choice(
                series.index[head_size:-tail_size] if tail_size > 0 else series.index[head_size:],
                size=min(random_size, total_rows - head_size - tail_size),
                replace=False
            )
            samples.append(series.loc[random_indices])
        
        # Combine samples
        if samples:
            return pd.concat(samples, ignore_index=True)
        else:
            return series.head(sample_size)
    
    def _detect_numeric_percentage(self, sample: pd.Series) -> float:
        """Detect percentage of numeric values in sample."""
        try:
            # Strip currency symbols and commas
            cleaned = sample.astype(str).str.replace(r'[$€₱£¥]', '', regex=True)
            cleaned = cleaned.str.replace(',', '')
            
            # Try to convert to numeric
            numeric_count = 0
            for value in cleaned:
                try:
                    pd.to_numeric(value)
                    numeric_count += 1
                except (ValueError, TypeError):
                    continue
            
            return (numeric_count / len(sample)) * 100
            
        except Exception:
            return 0.0
    
    def _detect_date_percentage(self, sample: pd.Series) -> float:
        """Detect percentage of date values in sample."""
        if not DATEUTIL_AVAILABLE:
            return 0.0
        
        try:
            date_count = 0
            for value in sample.dropna():
                try:
                    # Try multiple date formats
                    if isinstance(value, str):
                        date_parser.parse(value, fuzzy=False)
                        date_count += 1
                    elif pd.api.types.is_datetime64_any_dtype(type(value)):
                        date_count += 1
                except (ValueError, TypeError):
                    continue
            
            return (date_count / len(sample)) * 100
            
        except Exception:
            return 0.0
    
    def _detect_currency_percentage(self, sample: pd.Series) -> float:
        """Detect percentage of currency values in sample."""
        try:
            currency_patterns = [
                r'\$[\d,]+\.?\d*',  # $123.45
                r'€[\d,]+\.?\d*',   # €123.45
                r'₱[\d,]+\.?\d*',   # ₱123.45
                r'£[\d,]+\.?\d*',   # £123.45
                r'¥[\d,]+\.?\d*',   # ¥123.45
                r'USD[\d,]+\.?\d*', # USD123.45
                r'EUR[\d,]+\.?\d*', # EUR123.45
            ]
            
            currency_count = 0
            for value in sample.dropna().astype(str):
                for pattern in currency_patterns:
                    if re.search(pattern, value):
                        currency_count += 1
                        break
            
            return (currency_count / len(sample)) * 100
            
        except Exception:
            return 0.0
    
    def _detect_id_pattern_percentage(self, sample: pd.Series) -> float:
        """Detect percentage of ID pattern values in sample."""
        try:
            id_patterns = [
                r'^\d{6,}$',  # Long digits
                r'^INV-\d+$',  # Invoice ID
                r'^ORD-\d+$',  # Order ID
                r'^CUST-\d+$', # Customer ID
                r'^[A-Z]{2,}\d{4,}$',  # Prefixed IDs
            ]
            
            id_count = 0
            for value in sample.dropna().astype(str):
                for pattern in id_patterns:
                    if re.search(pattern, value):
                        id_count += 1
                        break
            
            return (id_count / len(sample)) * 100
            
        except Exception:
            return 0.0
    
    def _detect_region_geo_percentage(self, sample: pd.Series) -> float:
        """Detect percentage of geographic/region values in sample."""
        try:
            geo_count = 0
            for value in sample.dropna().astype(str):
                if value.lower() in self.geographic_patterns:
                    geo_count += 1
            
            return (geo_count / len(sample)) * 100
            
        except Exception:
            return 0.0
    
    def _detect_sku_pattern_percentage(self, sample: pd.Series) -> float:
        """Detect percentage of SKU pattern values in sample."""
        try:
            sku_count = 0
            for value in sample.dropna().astype(str):
                if self._matches_sku_pattern(value):
                    sku_count += 1
            
            return (sku_count / len(sample)) * 100
            
        except Exception:
            return 0.0
    
    def _calculate_entropy(self, sample: pd.Series) -> float:
        """Calculate entropy of the sample."""
        try:
            value_counts = sample.value_counts()
            total = len(sample)
            
            entropy = 0.0
            for count in value_counts:
                p = count / total
                if p > 0:
                    entropy -= p * math.log2(p)
            
            return entropy
            
        except Exception:
            return 0.0
    
    def _perform_local_inference(self, column_name: str, signals: ValueSignal, candidates: List[Any]) -> ColumnInference:
        """
        Perform local inference using header + value signals.
        
        Args:
            column_name: Name of the column
            signals: Value analysis signals
            candidates: Header candidates from Phase 2
            
        Returns:
            ColumnInference result
        """
        best_candidate = None
        best_score = 0.0
        best_confidence = 0.0
        reasoning = ""
        
        for candidate in candidates:
            if hasattr(candidate, 'canonical_type'):
                canonical_type = candidate.canonical_type
                header_score = candidate.score
            else:
                canonical_type = candidate.get('canonical_type', 'Unknown')
                header_score = candidate.get('score', 0.0)
            
            # Calculate value signal score for this candidate
            value_score = self._calculate_value_score_for_candidate(canonical_type, signals)
            
            # Weighted combination: header_score*0.45 + value_score*0.55
            combined_score = header_score * 0.45 + value_score * 0.55
            
            if combined_score > best_score:
                best_score = combined_score
                best_candidate = canonical_type
                best_confidence = self._calculate_local_confidence(combined_score, signals)
                reasoning = f"Header: {header_score:.2f}, Value: {value_score:.2f}, Combined: {combined_score:.2f}"
        
        return ColumnInference(
            column_name=column_name,
            best_candidate=best_candidate or 'Unknown',
            local_confidence=best_confidence,
            signals=signals,
            weighted_score=best_score,
            inference_method='local_inference',
            reasoning=reasoning
        )
    
    def _calculate_value_score_for_candidate(self, canonical_type: str, signals: ValueSignal) -> float:
        """Calculate value signal score for a specific candidate type."""
        score = 0.0
        
        if canonical_type == 'Date':
            score = signals.date_pct / 100.0
        elif canonical_type in ['Sales', 'Amount']:
            # Prefer currency or numeric signals
            score = max(signals.currency_pct, signals.numeric_pct) / 100.0
        elif canonical_type == 'Product':
            # Prefer SKU patterns or unique values
            score = max(signals.sku_pattern_pct, signals.unique_pct) / 100.0
        elif canonical_type == 'Region':
            # Prefer geographic patterns
            score = signals.region_geo_pct / 100.0
        elif canonical_type == 'Quantity':
            # Prefer numeric but not currency
            score = (signals.numeric_pct - signals.currency_pct) / 100.0
        else:
            # Default to numeric signal
            score = signals.numeric_pct / 100.0
        
        return max(0.0, min(1.0, score))
    
    def _calculate_local_confidence(self, combined_score: float, signals: ValueSignal) -> float:
        """Calculate local confidence based on combined score and signal quality."""
        # Base confidence from combined score
        base_confidence = combined_score * 100
        
        # Adjust based on signal quality
        signal_quality = 1.0
        
        # High null percentage reduces confidence
        if signals.null_pct > 50:
            signal_quality *= 0.5
        elif signals.null_pct > 25:
            signal_quality *= 0.8
        
        # Low sample size reduces confidence
        if signals.sample_size < 10:
            signal_quality *= 0.7
        elif signals.sample_size < 20:
            signal_quality *= 0.9
        
        # Conflicting signals reduce confidence
        if signals.numeric_pct > 80 and signals.unique_pct > 80:
            signal_quality *= 0.8  # Likely ID, not numeric
        
        return base_confidence * signal_quality
    
    def _init_value_detectors(self):
        """Initialize value detection patterns."""
        self.numeric_patterns = [
            r'^\d+\.?\d*$',  # Basic numeric
            r'^\d{1,3}(,\d{3})*(\.\d{2})?$',  # Currency format
        ]
        
        self.date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
            r'^\d{2}-\d{2}-\d{4}$',  # MM-DD-YYYY
        ]
    
    def _init_geographic_patterns(self):
        """Initialize geographic patterns."""
        self.geographic_patterns = {
            # Countries
            'usa', 'united states', 'america', 'canada', 'mexico', 'brazil',
            'uk', 'united kingdom', 'england', 'scotland', 'wales',
            'france', 'germany', 'spain', 'italy', 'netherlands',
            'china', 'japan', 'india', 'australia', 'south korea',
            # States/Provinces
            'california', 'texas', 'florida', 'new york', 'illinois',
            'ontario', 'quebec', 'british columbia', 'alberta',
            # Cities
            'new york', 'los angeles', 'chicago', 'houston', 'phoenix',
            'london', 'paris', 'berlin', 'madrid', 'rome',
            'tokyo', 'beijing', 'mumbai', 'sydney', 'seoul',
            # Regions
            'north', 'south', 'east', 'west', 'northeast', 'northwest',
            'southeast', 'southwest', 'midwest', 'central'
        }
    
    def _init_sku_patterns(self):
        """Initialize SKU patterns."""
        self.sku_patterns = [
            r'^[A-Z]{2,4}\d{3,6}$',  # ABC123456
            r'^[A-Z]\d{4,8}$',       # A1234567
            r'^[A-Z]{2}\d{2,4}[A-Z]?$',  # AB1234C
        ]
    
    def _matches_sku_pattern(self, value: str) -> bool:
        """Check if value matches SKU pattern."""
        for pattern in self.sku_patterns:
            if re.match(pattern, value):
                return True
        return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            'columns_analyzed': 0,
            'samples_processed': 0,
            'numeric_detections': 0,
            'date_detections': 0,
            'currency_detections': 0,
            'id_detections': 0,
            'region_detections': 0,
            'sku_detections': 0,
            'processing_time_ms': 0.0,
            'local_confidence_avg': 0.0
        }
    
    def emit_metrics(self):
        """Emit metrics for observability."""
        try:
            metrics = {
                "value.columns_analyzed": self.metrics['columns_analyzed'],
                "value.samples_processed": self.metrics['samples_processed'],
                "value.numeric_detections": self.metrics['numeric_detections'],
                "value.date_detections": self.metrics['date_detections'],
                "value.currency_detections": self.metrics['currency_detections'],
                "value.id_detections": self.metrics['id_detections'],
                "value.region_detections": self.metrics['region_detections'],
                "value.sku_detections": self.metrics['sku_detections'],
                "value.processing_time_ms": self.metrics['processing_time_ms'],
                "value.local_confidence_avg": self.metrics['local_confidence_avg']
            }
            
            # In a real implementation, you would send these to your metrics system
            print(f"📊 Value analyzer metrics: {metrics}")
            return metrics
            
        except Exception as e:
            print(f"⚠️ Error emitting value analyzer metrics: {e}")
            return {"value.metrics_error": str(e)}

# Global analyzer instance
value_analyzer = ValueAnalyzer()

def analyze_values(df: pd.DataFrame, header_candidates: Dict[str, List[Any]]) -> ValueAnalysisResult:
    """
    Convenience function to analyze column values and perform local inference.
    
    Args:
        df: DataFrame with columns to analyze
        header_candidates: Header candidates from Phase 2
        
    Returns:
        ValueAnalysisResult with local inference results
    """
    return value_analyzer.analyze_values(df, header_candidates)

if __name__ == "__main__":
    # Test the value analyzer
    print("🧪 Testing Value Analyzer")
    print("=" * 50)
    
    # Create test DataFrame
    test_data = {
        'Transaction_Date': pd.date_range('2023-01-01', periods=100),
        'Sales_Amount': [f"${np.random.uniform(100, 1000):.2f}" for _ in range(100)],
        'Product_ID': [f"SKU-{i:04d}" for i in range(100)],
        'Customer_Region': np.random.choice(['North', 'South', 'East', 'West'], 100),
        'Quantity_Sold': np.random.randint(1, 50, 100)
    }
    
    test_df = pd.DataFrame(test_data)
    
    # Mock header candidates
    header_candidates = {
        'Transaction_Date': [{'canonical_type': 'Date', 'score': 0.9}],
        'Sales_Amount': [{'canonical_type': 'Sales', 'score': 0.8}],
        'Product_ID': [{'canonical_type': 'Product', 'score': 0.7}],
        'Customer_Region': [{'canonical_type': 'Region', 'score': 0.8}],
        'Quantity_Sold': [{'canonical_type': 'Quantity', 'score': 0.9}]
    }
    
    result = analyze_values(test_df, header_candidates)
    
    if result.success:
        print(f"✅ Successfully analyzed {len(result.column_inferences)} columns")
        print(f"⏱️ Processing time: {result.processing_time_seconds:.3f}s")
        
        for col, inference in result.column_inferences.items():
            print(f"\n📊 {col}:")
            print(f"   Best candidate: {inference.best_candidate}")
            print(f"   Local confidence: {inference.local_confidence:.1f}%")
            print(f"   Weighted score: {inference.weighted_score:.3f}")
            print(f"   Signals: numeric={inference.signals.numeric_pct:.1f}%, "
                  f"date={inference.signals.date_pct:.1f}%, "
                  f"unique={inference.signals.unique_pct:.1f}%")
    else:
        print(f"❌ Error: {result.error_message}")
