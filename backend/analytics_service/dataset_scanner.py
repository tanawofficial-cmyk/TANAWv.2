# dataset_scanner.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import re
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os

class DatasetScanner:
    """
    Enhanced dataset scanning and classification logic for TANAW.
    Implements advanced column detection, temporal analysis, and analytics type classification.
    """
    
    def __init__(self):
        self.temporal_keywords = {
            'date': ['date', 'time', 'timestamp', 'created', 'updated', 'order', 'transaction'],
            'month': ['month', 'period', 'billing'],
            'day': ['day', 'daily'],
            'week': ['week', 'weekly'],
            'year': ['year', 'annual', 'fiscal']
        }
        
        self.numeric_indicators = ['price', 'amount', 'cost', 'revenue', 'sales', 'quantity', 'qty', 'volume', 'count', 'total', 'sum', 'value', 'rate', 'percent']
        
        self.categorical_indicators = ['product', 'category', 'brand', 'customer', 'region', 'type', 'status', 'id', 'code', 'name']
        
        self.load_or_train_classifier()
    
    def load_or_train_classifier(self):
        """Load existing classifier or train a new one for analytics type prediction."""
        model_path = "analytics_type_classifier.pkl"
        vectorizer_path = "analytics_vectorizer.pkl"
        
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            try:
                self.classifier = joblib.load(model_path)
                self.vectorizer = joblib.load(vectorizer_path)
                return
            except Exception as e:
                print(f"Failed to load existing classifier: {e}")
        
        # Train fallback classifier
        self._train_fallback_classifier()
    
    def _train_fallback_classifier(self):
        """Train a simple classifier based on column patterns."""
        # Training data based on common column patterns
        training_samples = [
            # Predictive patterns (time + numeric)
            ("date price quantity", "predictive"),
            ("timestamp revenue sales", "predictive"),
            ("order_date amount units", "predictive"),
            ("created_at cost volume", "predictive"),
            
            # Descriptive patterns (no time or limited time)
            ("product category price", "descriptive"),
            ("customer region sales", "descriptive"),
            ("brand type quantity", "descriptive"),
            ("status code amount", "descriptive"),
            
            # Mixed patterns
            ("date product price", "predictive"),
            ("month category revenue", "predictive"),
            ("product customer rating", "descriptive"),
            ("region type count", "descriptive")
        ]
        
        X, y = zip(*training_samples)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=100)
        X_vec = self.vectorizer.fit_transform(X)
        
        self.classifier = LogisticRegression(max_iter=500)
        self.classifier.fit(X_vec, y)
        
        # Save the trained model
        joblib.dump(self.classifier, "analytics_type_classifier.pkl")
        joblib.dump(self.vectorizer, "analytics_vectorizer.pkl")
    
    def detect_temporal_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect temporal columns and analyze their frequency patterns.
        
        Returns:
            Dict containing temporal column information and frequency analysis
        """
        temporal_info = {
            'columns': [],
            'frequency_analysis': {},
            'temporal_strength': 0.0
        }
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Check if column name suggests temporal data
            is_temporal_name = any(
                keyword in col_lower for keyword_set in self.temporal_keywords.values() 
                for keyword in keyword_set
            )
            
            # Check if values look like dates/times
            is_temporal_values = self._analyze_temporal_values(df[col])
            
            if is_temporal_name or is_temporal_values['is_temporal']:
                temporal_info['columns'].append({
                    'column': col,
                    'confidence': is_temporal_values['confidence'],
                    'frequency': is_temporal_values.get('frequency'),
                    'pattern': is_temporal_values.get('pattern'),
                    'detection_method': 'name' if is_temporal_name else 'values'
                })
                
                # Calculate temporal strength
                temporal_info['temporal_strength'] += is_temporal_values['confidence']
                
                # Store frequency analysis
                if is_temporal_values.get('frequency'):
                    temporal_info['frequency_analysis'][col] = is_temporal_values['frequency']
        
        # Normalize temporal strength
        if temporal_info['columns']:
            temporal_info['temporal_strength'] /= len(temporal_info['columns'])
        
        return temporal_info
    
    def _analyze_temporal_values(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze if a series contains temporal data and detect frequency patterns."""
        result = {
            'is_temporal': False,
            'confidence': 0.0,
            'frequency': None,
            'pattern': None
        }
        
        try:
            # Try to convert to datetime
            parsed_dates = pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
            valid_dates = parsed_dates.dropna()
            
            if len(valid_dates) == 0:
                return result
            
            # Calculate confidence based on conversion success rate
            confidence = len(valid_dates) / len(series)
            
            if confidence < 0.6:  # Need at least 60% valid dates
                return result
            
            result['is_temporal'] = True
            result['confidence'] = confidence * 100
            
            # Analyze frequency if we have enough data points
            if len(valid_dates) >= 3:
                try:
                    # Sort dates and calculate frequency
                    sorted_dates = valid_dates.sort_values()
                    
                    # Use pandas infer_freq for frequency detection
                    freq = pd.infer_freq(sorted_dates)
                    result['frequency'] = freq
                    
                    # Determine pattern
                    if freq:
                        result['pattern'] = self._classify_temporal_pattern(freq)
                    else:
                        # Manual frequency analysis
                        result['pattern'] = self._manual_frequency_analysis(sorted_dates)
                        
                except Exception as e:
                    print(f"Frequency analysis failed: {e}")
            
        except Exception as e:
            print(f"Temporal analysis failed for series: {e}")
        
        return result
    
    def _classify_temporal_pattern(self, frequency: str) -> str:
        """Classify temporal frequency into pattern categories."""
        if not frequency:
            return 'irregular'
        
        if 'D' in frequency or 'day' in frequency.lower():
            return 'daily'
        elif 'W' in frequency or 'week' in frequency.lower():
            return 'weekly'
        elif 'M' in frequency or 'month' in frequency.lower():
            return 'monthly'
        elif 'Q' in frequency or 'quarter' in frequency.lower():
            return 'quarterly'
        elif 'Y' in frequency or 'year' in frequency.lower():
            return 'yearly'
        else:
            return 'custom'
    
    def _manual_frequency_analysis(self, dates: pd.Series) -> str:
        """Manual frequency analysis when pandas infer_freq fails."""
        if len(dates) < 2:
            return 'insufficient_data'
        
        # Calculate time differences
        diffs = dates.diff().dropna()
        
        if len(diffs) == 0:
            return 'insufficient_data'
        
        # Get median difference
        median_diff = diffs.median()
        
        if median_diff.days == 1:
            return 'daily'
        elif median_diff.days == 7:
            return 'weekly'
        elif median_diff.days <= 31:
            return 'monthly'
        elif median_diff.days <= 93:
            return 'quarterly'
        elif median_diff.days <= 365:
            return 'yearly'
        else:
            return 'irregular'
    
    def classify_numeric_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Identify and classify numeric columns with enhanced detection.
        
        Returns:
            Dict containing numeric column information and metrics
        """
        numeric_info = {
            'columns': [],
            'metrics_count': 0,
            'dimensions_count': 0,
            'total_numeric_strength': 0.0
        }
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Check if column name suggests numeric data
            is_numeric_name = any(keyword in col_lower for keyword in self.numeric_indicators)
            
            # Analyze values for numeric patterns
            numeric_analysis = self._analyze_numeric_values(df[col])
            
            if is_numeric_name or numeric_analysis['is_numeric']:
                column_info = {
                    'column': col,
                    'confidence': numeric_analysis['confidence'],
                    'data_type': numeric_analysis.get('data_type', 'unknown'),
                    'is_metric': self._is_likely_metric(col, numeric_analysis),
                    'detection_method': 'name' if is_numeric_name else 'values'
                }
                
                numeric_info['columns'].append(column_info)
                numeric_info['total_numeric_strength'] += numeric_analysis['confidence']
                
                if column_info['is_metric']:
                    numeric_info['metrics_count'] += 1
                else:
                    numeric_info['dimensions_count'] += 1
        
        return numeric_info
    
    def _analyze_numeric_values(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze if a series contains numeric data with enhanced detection."""
        result = {
            'is_numeric': False,
            'confidence': 0.0,
            'data_type': 'unknown'
        }
        
        try:
            # Try direct numeric conversion
            numeric_values = pd.to_numeric(series, errors='coerce')
            valid_numeric = numeric_values.dropna()
            
            if len(valid_numeric) == 0:
                return result
            
            # Calculate confidence
            confidence = len(valid_numeric) / len(series)
            
            if confidence < 0.6:  # Need at least 60% valid numeric values
                return result
            
            result['is_numeric'] = True
            result['confidence'] = confidence * 100
            
            # Determine data type
            if all(isinstance(x, (int, np.integer)) for x in valid_numeric.dropna().head(10)):
                result['data_type'] = 'integer'
            elif all(isinstance(x, (float, np.floating)) for x in valid_numeric.dropna().head(10)):
                result['data_type'] = 'float'
            else:
                result['data_type'] = 'mixed_numeric'
                
        except Exception as e:
            print(f"Numeric analysis failed for series: {e}")
        
        return result
    
    def _is_likely_metric(self, column_name: str, numeric_analysis: Dict) -> bool:
        """Determine if a numeric column is likely a metric (measurable value) vs dimension (identifier)."""
        col_lower = column_name.lower()
        
        # Metrics are typically continuous values that can be aggregated
        metric_indicators = ['price', 'amount', 'cost', 'revenue', 'sales', 'quantity', 'volume', 'rate', 'percent', 'score', 'rating']
        
        # Dimensions are typically identifiers or categories
        dimension_indicators = ['id', 'code', 'number', 'count', 'total_count']
        
        if any(indicator in col_lower for indicator in metric_indicators):
            return True
        elif any(indicator in col_lower for indicator in dimension_indicators):
            return False
        
        # Fallback: if it's a float, more likely to be a metric
        if numeric_analysis.get('data_type') == 'float':
            return True
        
        return False
    
    def classify_categorical_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify and classify categorical columns."""
        categorical_info = {
            'columns': [],
            'total_categorical_strength': 0.0
        }
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Check if column name suggests categorical data
            is_categorical_name = any(keyword in col_lower for keyword in self.categorical_indicators)
            
            # Analyze values for categorical patterns
            categorical_analysis = self._analyze_categorical_values(df[col])
            
            if is_categorical_name or categorical_analysis['is_categorical']:
                column_info = {
                    'column': col,
                    'confidence': categorical_analysis['confidence'],
                    'unique_values': categorical_analysis.get('unique_count', 0),
                    'cardinality': categorical_analysis.get('cardinality', 'unknown'),
                    'detection_method': 'name' if is_categorical_name else 'values'
                }
                
                categorical_info['columns'].append(column_info)
                categorical_info['total_categorical_strength'] += categorical_analysis['confidence']
        
        return categorical_info
    
    def _analyze_categorical_values(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze if a series contains categorical data."""
        result = {
            'is_categorical': False,
            'confidence': 0.0,
            'unique_count': 0,
            'cardinality': 'unknown'
        }
        
        try:
            # Convert to string and analyze
            str_series = series.astype(str)
            unique_values = str_series.nunique()
            total_values = len(str_series)
            
            # Calculate cardinality ratio
            cardinality_ratio = unique_values / total_values
            
            # Determine if it's categorical based on cardinality
            if cardinality_ratio < 0.5:  # Less than 50% unique values suggests categorical
                result['is_categorical'] = True
                result['confidence'] = (1 - cardinality_ratio) * 100
                result['unique_count'] = unique_values
                
                # Classify cardinality
                if cardinality_ratio < 0.1:
                    result['cardinality'] = 'low'  # < 10% unique
                elif cardinality_ratio < 0.3:
                    result['cardinality'] = 'medium'  # 10-30% unique
                else:
                    result['cardinality'] = 'high'  # 30-50% unique
                    
        except Exception as e:
            print(f"Categorical analysis failed for series: {e}")
        
        return result
    
    def classify_analytics_type(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Classify the dataset as suitable for descriptive or predictive analytics.
        
        Returns:
            Dict containing analytics type classification and confidence
        """
        # Get column analysis
        temporal_info = self.detect_temporal_columns(df)
        numeric_info = self.classify_numeric_columns(df)
        categorical_info = self.classify_categorical_columns(df)
        
        # Create feature vector for classification
        feature_vector = self._create_feature_vector(
            temporal_info, numeric_info, categorical_info, df
        )
        
        # Use ML classifier to predict analytics type
        analytics_type, confidence = self._predict_analytics_type(feature_vector)
        
        # Rule-based validation and enhancement
        rule_based_type, rule_confidence = self._rule_based_classification(
            temporal_info, numeric_info, categorical_info
        )
        
        # Combine ML and rule-based predictions
        final_type, final_confidence = self._combine_predictions(
            analytics_type, confidence, rule_based_type, rule_confidence
        )
        
        return {
            'analytics_type': final_type,
            'confidence': final_confidence,
            'temporal_info': temporal_info,
            'numeric_info': numeric_info,
            'categorical_info': categorical_info,
            'reasoning': self._generate_reasoning(
                temporal_info, numeric_info, categorical_info, final_type
            ),
            'metadata_score': self._calculate_metadata_score(
                temporal_info, numeric_info, categorical_info
            )
        }
    
    def _create_feature_vector(self, temporal_info: Dict, numeric_info: Dict, 
                             categorical_info: Dict, df: pd.DataFrame) -> str:
        """Create a feature vector string for ML classification."""
        features = []
        
        # Temporal features
        features.append(f"temporal_cols_{len(temporal_info['columns'])}")
        features.append(f"temporal_strength_{temporal_info['temporal_strength']:.1f}")
        
        # Numeric features
        features.append(f"numeric_cols_{len(numeric_info['columns'])}")
        features.append(f"metrics_{numeric_info['metrics_count']}")
        features.append(f"dimensions_{numeric_info['dimensions_count']}")
        
        # Categorical features
        features.append(f"categorical_cols_{len(categorical_info['columns'])}")
        
        # Dataset size features
        features.append(f"rows_{len(df)}")
        features.append(f"total_cols_{len(df.columns)}")
        
        return " ".join(features)
    
    def _predict_analytics_type(self, feature_vector: str) -> Tuple[str, float]:
        """Use ML classifier to predict analytics type."""
        try:
            X_vec = self.vectorizer.transform([feature_vector])
            prediction = self.classifier.predict(X_vec)[0]
            confidence = max(self.classifier.predict_proba(X_vec)[0]) * 100
            return prediction, confidence
        except Exception as e:
            print(f"ML prediction failed: {e}")
            return "descriptive", 50.0
    
    def _rule_based_classification(self, temporal_info: Dict, numeric_info: Dict, 
                                 categorical_info: Dict) -> Tuple[str, float]:
        """Rule-based classification logic."""
        # Check for predictive analytics requirements
        has_temporal = len(temporal_info['columns']) > 0
        has_numeric_metrics = numeric_info['metrics_count'] > 0
        has_strong_temporal = temporal_info['temporal_strength'] > 50
        
        if has_temporal and has_numeric_metrics and has_strong_temporal:
            confidence = min(90, temporal_info['temporal_strength'] + numeric_info['total_numeric_strength'] / 2)
            return "predictive", confidence
        
        # Check for descriptive analytics
        has_numeric = len(numeric_info['columns']) > 0
        has_categorical = len(categorical_info['columns']) > 0
        
        if has_numeric or has_categorical:
            confidence = max(60, (numeric_info['total_numeric_strength'] + categorical_info['total_categorical_strength']) / 2)
            return "descriptive", confidence
        
        return "unknown", 30.0
    
    def _combine_predictions(self, ml_type: str, ml_conf: float, 
                           rule_type: str, rule_conf: float) -> Tuple[str, float]:
        """Combine ML and rule-based predictions."""
        # If both agree, use higher confidence
        if ml_type == rule_type:
            return ml_type, max(ml_conf, rule_conf)
        
        # If they disagree, use rule-based if it has high confidence
        if rule_conf > 80:
            return rule_type, rule_conf
        elif ml_conf > 70:
            return ml_type, ml_conf
        else:
            # Default to descriptive if uncertain
            return "descriptive", 50.0
    
    def _generate_reasoning(self, temporal_info: Dict, numeric_info: Dict, 
                          categorical_info: Dict, analytics_type: str) -> str:
        """Generate human-readable reasoning for the classification."""
        reasons = []
        
        if analytics_type == "predictive":
            reasons.append(f"Found {len(temporal_info['columns'])} temporal column(s) with {temporal_info['temporal_strength']:.1f}% strength")
            reasons.append(f"Detected {numeric_info['metrics_count']} numeric metrics suitable for forecasting")
            if temporal_info['frequency_analysis']:
                reasons.append(f"Temporal patterns detected: {', '.join(temporal_info['frequency_analysis'].keys())}")
        else:
            reasons.append(f"Found {len(numeric_info['columns'])} numeric column(s) suitable for descriptive analysis")
            reasons.append(f"Detected {len(categorical_info['columns'])} categorical dimension(s)")
            if len(temporal_info['columns']) == 0:
                reasons.append("No strong temporal patterns detected")
        
        return "; ".join(reasons)
    
    def _calculate_metadata_score(self, temporal_info: Dict, numeric_info: Dict, 
                                categorical_info: Dict) -> float:
        """Calculate a 0-1 metadata quality score."""
        score = 0.0
        
        # Temporal score (0.4 weight)
        if temporal_info['temporal_strength'] > 0:
            score += 0.4 * (temporal_info['temporal_strength'] / 100)
        
        # Numeric score (0.4 weight)
        if numeric_info['total_numeric_strength'] > 0:
            score += 0.4 * min(1.0, numeric_info['total_numeric_strength'] / 100)
        
        # Categorical score (0.2 weight)
        if categorical_info['total_categorical_strength'] > 0:
            score += 0.2 * min(1.0, categorical_info['total_categorical_strength'] / 100)
        
        return round(score, 3)
