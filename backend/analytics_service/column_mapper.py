# column_mapper.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from rapidfuzz import fuzz, process
import json
import os
from datetime import datetime

class ColumnMapper:
    """
    Enhanced column mapping and standardization logic for TANAW.
    Implements fuzzy matching, confidence scoring, and user confirmation workflows.
    """
    
    def __init__(self):
        self.knowledge_base_path = "column_mapping_kb.json"
        self.confidence_threshold = 80.0
        self.load_knowledge_base()
        self.initialize_synonym_maps()
    
    def load_knowledge_base(self):
        """Load or create the column mapping knowledge base."""
        if os.path.exists(self.knowledge_base_path):
            try:
                with open(self.knowledge_base_path, 'r') as f:
                    self.knowledge_base = json.load(f)
                
                # Ensure ignored_patterns key exists
                if "ignored_patterns" not in self.knowledge_base:
                    self.knowledge_base["ignored_patterns"] = {}
                    
            except Exception as e:
                print(f"Failed to load knowledge base: {e}")
                self.knowledge_base = {"mappings": {}, "confirmations": {}, "ignored_patterns": {}}
        else:
            self.knowledge_base = {"mappings": {}, "confirmations": {}, "ignored_patterns": {}}
    
    def save_knowledge_base(self):
        """Save the knowledge base to disk."""
        try:
            with open(self.knowledge_base_path, 'w') as f:
                json.dump(self.knowledge_base, f, indent=2)
        except Exception as e:
            print(f"Failed to save knowledge base: {e}")
    
    def initialize_synonym_maps(self):
        """Initialize comprehensive synonym maps for column matching."""
        self.synonym_maps = {
            # Sales & Revenue
            'sales': ['sales', 'revenue', 'income', 'earnings', 'turnover', 'gross_sales', 'net_sales'],
            'price': ['price', 'cost', 'amount', 'value', 'unit_price', 'selling_price', 'list_price'],
            'quantity': ['quantity', 'qty', 'units', 'volume', 'count', 'pieces', 'items', 'number'],
            
            # Temporal
            'date': ['date', 'time', 'timestamp', 'created_at', 'updated_at', 'order_date', 'transaction_date'],
            'month': ['month', 'period', 'billing_month', 'reporting_month'],
            'year': ['year', 'fiscal_year', 'calendar_year'],
            
            # Products & Categories
            'product': ['product', 'item', 'sku', 'product_name', 'item_name', 'goods', 'merchandise'],
            'category': ['category', 'type', 'class', 'group', 'segment', 'department', 'division'],
            'brand': ['brand', 'manufacturer', 'maker', 'producer', 'vendor'],
            
            # Identifiers
            'id': ['id', 'identifier', 'key', 'code', 'number', 'reference'],
            'order_id': ['order_id', 'order_number', 'invoice_id', 'transaction_id', 'purchase_id'],
            'customer_id': ['customer_id', 'client_id', 'user_id', 'account_id', 'member_id'],
            
            # Customer & Location
            'customer': ['customer', 'client', 'buyer', 'user', 'account', 'member'],
            'region': ['region', 'area', 'territory', 'zone', 'district'],
            'country': ['country', 'nation', 'state'],
            'city': ['city', 'town', 'municipality', 'metro'],
            
            # Financial
            'profit': ['profit', 'margin', 'net_income', 'earnings', 'gain'],
            'loss': ['loss', 'deficit', 'expense', 'cost'],
            'discount': ['discount', 'rebate', 'reduction', 'deduction'],
            'tax': ['tax', 'duty', 'levy', 'tariff'],
            
            # Inventory
            'stock': ['stock', 'inventory', 'stock_level', 'available', 'on_hand'],
            'supplier': ['supplier', 'vendor', 'distributor', 'source'],
            
            # Analytics & Metrics
            'rating': ['rating', 'score', 'stars', 'grade', 'evaluation'],
            'review': ['review', 'feedback', 'comment', 'opinion', 'testimonial'],
            'satisfaction': ['satisfaction', 'happiness', 'contentment', 'approval']
        }
        
        # Create reverse mapping for faster lookups
        self.reverse_synonyms = {}
        for canonical, synonyms in self.synonym_maps.items():
            for synonym in synonyms:
                self.reverse_synonyms[synonym.lower()] = canonical
    
    def map_columns(self, df: pd.DataFrame, user_confirmed: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Map dataset columns to TANAW standard columns with confidence scoring.
        
        Args:
            df: DataFrame with columns to map
            user_confirmed: Optional user-confirmed mappings
            
        Returns:
            Dict containing mapping results and confidence scores
        """
        mapping_results = {
            'mapped_columns': [],
            'uncertain_columns': [],
            'unmapped_columns': [],
            'confidence_scores': {},
            'suggestions': {},
            'requires_confirmation': False
        }
        
        # Process each column
        for col in df.columns:
            col_result = self._map_single_column(col, df[col], user_confirmed)
            
            if col_result['status'] == 'mapped':
                mapping_results['mapped_columns'].append(col_result)
                mapping_results['confidence_scores'][col] = col_result['confidence']
            elif col_result['status'] == 'uncertain':
                mapping_results['uncertain_columns'].append(col_result)
                mapping_results['suggestions'][col] = col_result['suggestions']
                mapping_results['requires_confirmation'] = True
            else:
                mapping_results['unmapped_columns'].append(col_result)
        
        # Update knowledge base with successful mappings
        self._update_knowledge_base(mapping_results['mapped_columns'])
        
        return mapping_results
    
    def _map_single_column(self, column_name: str, series: pd.Series, 
                          user_confirmed: Optional[Dict] = None) -> Dict[str, Any]:
        """Map a single column to a TANAW standard column."""
        
        # Check for user-confirmed mapping first
        if user_confirmed and column_name in user_confirmed:
            confirmed_type = user_confirmed[column_name]
            return {
                'original_column': column_name,
                'mapped_column': confirmed_type,
                'confidence': 100.0,
                'method': 'user_confirmed',
                'status': 'mapped',
                'suggestions': []
            }
        
        # Check knowledge base for previous mappings
        kb_result = self._check_knowledge_base(column_name)
        if kb_result:
            return kb_result
        
        # Perform fuzzy matching
        fuzzy_result = self._fuzzy_match_column(column_name)
        
        # Analyze values for additional context
        value_analysis = self._analyze_column_values(series)
        
        # Combine results
        final_result = self._combine_mapping_results(
            column_name, fuzzy_result, value_analysis
        )
        
        return final_result
    
    def _check_knowledge_base(self, column_name: str) -> Optional[Dict[str, Any]]:
        """Check if column has been previously mapped in knowledge base."""
        col_lower = column_name.lower()
        
        # Check direct mappings
        if col_lower in self.knowledge_base.get('mappings', {}):
            mapping = self.knowledge_base['mappings'][col_lower]
            
            # Check confirmation history
            confirmations = self.knowledge_base.get('confirmations', {}).get(col_lower, [])
            confidence = self._calculate_kb_confidence(confirmations)
            
            # If no confirmation history, use fuzzy matching confidence as fallback
            if confidence == 0.0:
                fuzzy_result = self._fuzzy_match_column(column_name)
                if fuzzy_result['matched_type'] == mapping:
                    confidence = fuzzy_result['confidence']
                    method = 'knowledge_base_fuzzy_fallback'
                else:
                    confidence = 85.0  # High confidence for exact KB matches
                    method = 'knowledge_base'
            else:
                method = 'knowledge_base'
            
            return {
                'original_column': column_name,
                'mapped_column': mapping,
                'confidence': confidence,
                'method': method,
                'status': 'mapped' if confidence >= self.confidence_threshold else 'uncertain',
                'suggestions': []
            }
        
        return None
    
    def _calculate_kb_confidence(self, confirmations: List[Dict]) -> float:
        """Calculate confidence based on confirmation history."""
        if not confirmations:
            return 0.0
        
        # Weight recent confirmations more heavily
        total_weight = 0.0
        weighted_score = 0.0
        
        for confirmation in confirmations[-10:]:  # Consider last 10 confirmations
            days_ago = (datetime.now() - datetime.fromisoformat(confirmation['timestamp'])).days
            weight = max(0.1, 1.0 - (days_ago / 365))  # Decay over a year
            
            total_weight += weight
            weighted_score += weight * confirmation['confidence']
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _fuzzy_match_column(self, column_name: str) -> Dict[str, Any]:
        """Perform fuzzy matching against known column types."""
        col_lower = column_name.lower()
        
        # Try exact match in synonyms first
        if col_lower in self.reverse_synonyms:
            return {
                'matched_type': self.reverse_synonyms[col_lower],
                'confidence': 95.0,
                'method': 'exact_synonym'
            }
        
        # Fuzzy match against all synonyms
        best_match = None
        best_score = 0.0
        
        for canonical, synonyms in self.synonym_maps.items():
            for synonym in synonyms:
                score = fuzz.WRatio(col_lower, synonym.lower())
                if score > best_score:
                    best_score = score
                    best_match = canonical
        
        # Also try fuzzy match against canonical names
        canonical_names = list(self.synonym_maps.keys())
        match, score, _ = process.extractOne(col_lower, canonical_names, scorer=fuzz.WRatio)
        
        if score > best_score:
            best_score = score
            best_match = match
        
        return {
            'matched_type': best_match,
            'confidence': best_score,
            'method': 'fuzzy_match'
        }
    
    def _analyze_column_values(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze column values to provide additional context for mapping."""
        analysis = {
            'data_type': str(series.dtype),
            'unique_count': series.nunique(),
            'null_count': series.isnull().sum(),
            'sample_values': series.dropna().head(5).tolist(),
            'patterns': []
        }
        
        # Detect patterns
        if self._looks_like_date(series):
            analysis['patterns'].append('date_like')
        if self._looks_like_numeric(series):
            analysis['patterns'].append('numeric_like')
        if self._looks_like_id(series):
            analysis['patterns'].append('id_like')
        if self._looks_like_email(series):
            analysis['patterns'].append('email_like')
        
        return analysis
    
    def _looks_like_date(self, series: pd.Series) -> bool:
        """Check if series looks like date data."""
        try:
            parsed = pd.to_datetime(series.dropna().head(10), errors='coerce')
            return parsed.notna().mean() >= 0.7
        except:
            return False
    
    def _looks_like_numeric(self, series: pd.Series) -> bool:
        """Check if series looks like numeric data."""
        try:
            numeric = pd.to_numeric(series.dropna().head(10), errors='coerce')
            return numeric.notna().mean() >= 0.7
        except:
            return False
    
    def _looks_like_id(self, series: pd.Series) -> bool:
        """Check if series looks like ID data."""
        sample = series.dropna().head(10).astype(str)
        # Check if values are mostly alphanumeric and relatively short
        return all(len(val) <= 20 and val.replace('-', '').replace('_', '').isalnum() for val in sample)
    
    def _looks_like_email(self, series: pd.Series) -> bool:
        """Check if series looks like email data."""
        import re
        email_pattern = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
        sample = series.dropna().head(10).astype(str)
        return sum(1 for val in sample if email_pattern.match(val)) / len(sample) >= 0.7
    
    def _combine_mapping_results(self, column_name: str, fuzzy_result: Dict, 
                                value_analysis: Dict) -> Dict[str, Any]:
        """Combine fuzzy matching and value analysis results."""
        
        # Base result from fuzzy matching
        mapped_column = fuzzy_result.get('matched_type')
        confidence = fuzzy_result.get('confidence', 0.0)
        method = fuzzy_result.get('method', 'unknown')
        
        # Adjust confidence based on value analysis
        confidence = self._adjust_confidence_with_values(
            confidence, mapped_column, value_analysis
        )
        
        # Generate suggestions if confidence is low
        suggestions = []
        if confidence < self.confidence_threshold:
            suggestions = self._generate_suggestions(column_name, value_analysis)
        
        # Determine status
        if confidence >= self.confidence_threshold:
            status = 'mapped'
        elif confidence >= 50.0:
            status = 'uncertain'
        else:
            status = 'unmapped'
        
        return {
            'original_column': column_name,
            'mapped_column': mapped_column,
            'confidence': confidence,
            'method': method,
            'status': status,
            'suggestions': suggestions,
            'value_analysis': value_analysis
        }
    
    def _adjust_confidence_with_values(self, base_confidence: float, 
                                     mapped_column: Optional[str], 
                                     value_analysis: Dict) -> float:
        """Adjust confidence based on value analysis."""
        if not mapped_column:
            return base_confidence
        
        adjusted_confidence = base_confidence
        patterns = value_analysis.get('patterns', [])
        
        # Boost confidence if value patterns match expected column type
        if mapped_column == 'date' and 'date_like' in patterns:
            adjusted_confidence = min(95.0, adjusted_confidence + 20)
        elif mapped_column in ['price', 'quantity', 'sales'] and 'numeric_like' in patterns:
            adjusted_confidence = min(95.0, adjusted_confidence + 15)
        elif mapped_column == 'id' and 'id_like' in patterns:
            adjusted_confidence = min(95.0, adjusted_confidence + 10)
        elif mapped_column == 'email' and 'email_like' in patterns:
            adjusted_confidence = min(95.0, adjusted_confidence + 20)
        
        # Reduce confidence if patterns contradict
        elif mapped_column == 'date' and 'numeric_like' in patterns and 'date_like' not in patterns:
            adjusted_confidence = max(20.0, adjusted_confidence - 30)
        elif mapped_column in ['price', 'quantity', 'sales'] and 'date_like' in patterns:
            adjusted_confidence = max(20.0, adjusted_confidence - 25)
        
        return adjusted_confidence
    
    def _generate_suggestions(self, column_name: str, value_analysis: Dict) -> List[Dict]:
        """Generate mapping suggestions for uncertain columns."""
        suggestions = []
        patterns = value_analysis.get('patterns', [])
        
        # Suggest based on patterns
        if 'date_like' in patterns:
            suggestions.extend([
                {'type': 'date', 'confidence': 85, 'reason': 'Values look like dates'},
                {'type': 'timestamp', 'confidence': 80, 'reason': 'Values look like timestamps'}
            ])
        
        if 'numeric_like' in patterns:
            suggestions.extend([
                {'type': 'price', 'confidence': 75, 'reason': 'Values are numeric'},
                {'type': 'quantity', 'confidence': 70, 'reason': 'Values are numeric'},
                {'type': 'sales', 'confidence': 65, 'reason': 'Values are numeric'}
            ])
        
        if 'id_like' in patterns:
            suggestions.extend([
                {'type': 'id', 'confidence': 80, 'reason': 'Values look like identifiers'},
                {'type': 'order_id', 'confidence': 75, 'reason': 'Values look like IDs'},
                {'type': 'customer_id', 'confidence': 70, 'reason': 'Values look like IDs'}
            ])
        
        # Add fuzzy suggestions as fallback
        fuzzy_suggestions = self._get_fuzzy_suggestions(column_name)
        suggestions.extend(fuzzy_suggestions)
        
        # Sort by confidence and return top 5
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:5]
    
    def _get_fuzzy_suggestions(self, column_name: str) -> List[Dict]:
        """Get fuzzy matching suggestions for a column."""
        suggestions = []
        col_lower = column_name.lower()
        
        # Get top fuzzy matches
        all_synonyms = []
        for canonical, synonyms in self.synonym_maps.items():
            all_synonyms.extend(synonyms)
        
        matches = process.extract(col_lower, all_synonyms, scorer=fuzz.WRatio, limit=5)
        
        for match, score, _ in matches:
            if score >= 60:  # Only include reasonably good matches
                # Find the canonical type for this synonym
                canonical_type = None
                for canonical, synonyms in self.synonym_maps.items():
                    if match.lower() in [s.lower() for s in synonyms]:
                        canonical_type = canonical
                        break
                
                if canonical_type:
                    suggestions.append({
                        'type': canonical_type,
                        'confidence': score,
                        'reason': f'Fuzzy match with "{match}"'
                    })
        
        return suggestions
    
    def _update_knowledge_base(self, mapped_columns: List[Dict]):
        """Update knowledge base with successful mappings."""
        for mapping in mapped_columns:
            if mapping['confidence'] >= self.confidence_threshold:
                col_lower = mapping['original_column'].lower()
                self.knowledge_base['mappings'][col_lower] = mapping['mapped_column']
        
        self.save_knowledge_base()
    
    def confirm_mapping(self, column_name: str, mapped_type: str, 
                       user_confidence: float = 100.0) -> bool:
        """Record user confirmation of a column mapping."""
        try:
            col_lower = column_name.lower()
            
            # Update mappings
            self.knowledge_base['mappings'][col_lower] = mapped_type
            
            # Record confirmation
            if 'confirmations' not in self.knowledge_base:
                self.knowledge_base['confirmations'] = {}
            
            if col_lower not in self.knowledge_base['confirmations']:
                self.knowledge_base['confirmations'][col_lower] = []
            
            self.knowledge_base['confirmations'][col_lower].append({
                'timestamp': datetime.now().isoformat(),
                'confidence': user_confidence,
                'mapped_type': mapped_type
            })
            
            # Keep only recent confirmations (last 20)
            self.knowledge_base['confirmations'][col_lower] = \
                self.knowledge_base['confirmations'][col_lower][-20:]
            
            self.save_knowledge_base()
            return True
            
        except Exception as e:
            print(f"Failed to confirm mapping: {e}")
            return False
    
    def store_ignore_patterns(self, ignored_mappings: Dict[str, List[str]]) -> bool:
        """
        Store ignore patterns in the knowledge base.
        
        Args:
            ignored_mappings: Dict mapping analytics_type -> list of ignored columns
            
        Returns:
            bool indicating success
        """
        try:
            if 'ignored_patterns' not in self.knowledge_base:
                self.knowledge_base['ignored_patterns'] = {}
            
            timestamp = datetime.now().isoformat()
            
            for analytics_type, ignored_columns in ignored_mappings.items():
                for col_name in ignored_columns:
                    col_lower = col_name.lower()
                    
                    # Initialize column entry if it doesn't exist
                    if col_lower not in self.knowledge_base['ignored_patterns']:
                        self.knowledge_base['ignored_patterns'][col_lower] = []
                    
                    # Add ignore pattern with analytics type and timestamp
                    ignore_entry = {
                        'analytics_type': analytics_type,
                        'timestamp': timestamp
                    }
                    
                    # Avoid duplicates for the same analytics type
                    existing_types = [e['analytics_type'] for e in self.knowledge_base['ignored_patterns'][col_lower]]
                    if analytics_type not in existing_types:
                        self.knowledge_base['ignored_patterns'][col_lower].append(ignore_entry)
                    
                    # Keep only recent patterns (last 10)
                    self.knowledge_base['ignored_patterns'][col_lower] = \
                        self.knowledge_base['ignored_patterns'][col_lower][-10:]
            
            self.save_knowledge_base()
            print(f"💾 Stored ignore patterns for {len(ignored_mappings)} analytics type(s)")
            return True
            
        except Exception as e:
            print(f"Failed to store ignore patterns: {e}")
            return False
    
    def get_ignore_suggestions(self, column_name: str, analytics_type: str) -> bool:
        """
        Check if a column is typically ignored for a specific analytics type.
        
        Args:
            column_name: Name of the column to check
            analytics_type: Type of analytics
            
        Returns:
            bool indicating if this column is usually ignored
        """
        try:
            col_lower = column_name.lower()
            
            if 'ignored_patterns' not in self.knowledge_base:
                return False
            
            if col_lower not in self.knowledge_base['ignored_patterns']:
                return False
            
            # Check if this column was ignored for this analytics type
            for pattern in self.knowledge_base['ignored_patterns'][col_lower]:
                if pattern['analytics_type'] == analytics_type:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Failed to get ignore suggestions: {e}")
            return False
    
    def standardize_column_names(self, df: pd.DataFrame, 
                               mapping_results: Dict[str, Any]) -> pd.DataFrame:
        """Standardize column names based on mapping results."""
        standardized_df = df.copy()
        column_mapping = {}
        
        for mapping in mapping_results.get('mapped_columns', []):
            if mapping['status'] == 'mapped':
                original = mapping['original_column']
                mapped = mapping['mapped_column']
                column_mapping[original] = mapped
        
        # Apply column renaming
        standardized_df = standardized_df.rename(columns=column_mapping)
        
        return standardized_df
    
    def get_mapping_statistics(self) -> Dict[str, Any]:
        """Get statistics about the column mapping knowledge base."""
        mappings = self.knowledge_base.get('mappings', {})
        confirmations = self.knowledge_base.get('confirmations', {})
        
        total_mappings = len(mappings)
        total_confirmations = sum(len(conf_list) for conf_list in confirmations.values())
        
        # Calculate average confidence
        all_confidences = []
        for conf_list in confirmations.values():
            all_confidences.extend([conf['confidence'] for conf in conf_list])
        
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
        
        return {
            'total_mappings': total_mappings,
            'total_confirmations': total_confirmations,
            'average_confidence': round(avg_confidence, 2),
            'most_common_types': self._get_most_common_types(),
            'knowledge_base_size': os.path.getsize(self.knowledge_base_path) if os.path.exists(self.knowledge_base_path) else 0
        }
    
    def _get_most_common_types(self) -> List[Tuple[str, int]]:
        """Get the most commonly mapped column types."""
        mappings = self.knowledge_base.get('mappings', {})
        type_counts = {}
        
        for col, mapped_type in mappings.items():
            type_counts[mapped_type] = type_counts.get(mapped_type, 0) + 1
        
        return sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]
