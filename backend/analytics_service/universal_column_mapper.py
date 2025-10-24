#!/usr/bin/env python3
"""
Universal Column Mapper for TANAW Analytics
==========================================

A robust, comprehensive column mapping system that can handle ANY dataset
without heavy dependency on external ML libraries like SBERT.

Features:
- Advanced value pattern recognition
- Multi-layered mapping strategy
- Intelligent fallback systems
- Context-aware business logic
- Language-agnostic detection
- Statistical pattern analysis
"""

import pandas as pd
import numpy as np
import re
import json
from typing import Dict, List, Tuple, Any, Optional, Set, Union
from datetime import datetime, date
from collections import Counter, defaultdict
import sqlite3
from dataclasses import dataclass
from enum import Enum

# Import conflict resolver
try:
    from column_conflict_resolver import ColumnConflictResolver
    CONFLICT_RESOLVER_AVAILABLE = True
except ImportError:
    CONFLICT_RESOLVER_AVAILABLE = False
    print("⚠️ Conflict Resolver not available. Conflicts will not be auto-resolved.")

# Optional imports with graceful fallbacks
try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    print("⚠️ RapidFuzz not available. Using basic string matching.")

try:
    from sentence_transformers import SentenceTransformer, util
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False
    print("⚠️ SBERT not available. Using pattern-based mapping.")

# Optional Pandera for data validation
try:
    import pandera as pa
    from pandera import Column, DataFrameSchema
    PANDERA_AVAILABLE = True
except ImportError:
    PANDERA_AVAILABLE = False
    print("⚠️ Pandera not available. Using basic validation.")


class ColumnType(Enum):
    """Standard column types for TANAW analytics."""
    DATE = "Date"
    SALES = "Sales"
    AMOUNT = "Amount"
    PRODUCT = "Product"
    QUANTITY = "Quantity"
    REGION = "Region"
    IGNORE = "Ignore"


@dataclass
class PatternMatch:
    """Represents a pattern match result."""
    pattern_type: str
    confidence: float
    evidence: List[str]
    method: str


@dataclass
class ColumnAnalysis:
    """Comprehensive analysis of a column."""
    column_name: str
    data_type: str
    sample_values: List[Any]
    unique_count: int
    null_count: int
    patterns: List[PatternMatch]
    statistical_features: Dict[str, Any]
    business_context: Dict[str, Any]


class UniversalColumnMapper:
    """
    Universal Column Mapper that can handle any dataset.
    
    Uses a multi-layered approach:
    1. Direct pattern matching (fastest, most reliable)
    2. Value analysis and statistical patterns
    3. Business context understanding
    4. Fuzzy string matching (if available)
    5. Semantic similarity (if SBERT available)
    6. Intelligent fallback systems
    """
    
    def __init__(self, db_path: str = "universal_column_mapping.db", 
                 use_weighted_voting: bool = True,
                 enable_explainability: bool = True):
        self.db_path = db_path
        self.confidence_threshold = 60.0  # Lower threshold for better coverage
        self.use_weighted_voting = use_weighted_voting
        self.enable_explainability = enable_explainability
        
        # Weighted voting configuration (Pattern > Context > Fuzzy > SBERT > Statistical)
        self.layer_weights = {
            'pattern': 0.35,      # Highest weight - most reliable
            'context': 0.25,      # Business logic understanding
            'fuzzy': 0.20,        # String matching
            'semantic': 0.15,     # SBERT - only when needed
            'statistical': 0.05   # Data distribution analysis
        }
        
        # Performance tracking
        self.performance_stats = {
            'sbert_calls': 0,
            'pattern_hits': 0,
            'fuzzy_hits': 0,
            'total_mappings': 0
        }
        
        # Initialize optional components
        self._init_fuzzy_matcher()
        self._init_semantic_matcher()
        self._init_database()
        
        # Pattern recognition engines
        self._init_pattern_recognizers()
        
        # Business context rules
        self._init_business_rules()
        
        # Pandera validation schemas
        if PANDERA_AVAILABLE:
            self._init_validation_schemas()
        
        # Conflict resolver
        if CONFLICT_RESOLVER_AVAILABLE:
            self.conflict_resolver = ColumnConflictResolver(db_path=db_path)
        else:
            self.conflict_resolver = None
        
        print("🚀 Universal Column Mapper initialized")
        print(f"   - Fuzzy matching: {'✅' if RAPIDFUZZ_AVAILABLE else '❌'}")
        print(f"   - Semantic matching: {'✅' if SBERT_AVAILABLE else '❌'}")
        print(f"   - Pandera validation: {'✅' if PANDERA_AVAILABLE else '❌'}")
        print(f"   - Pattern recognition: ✅")
        print(f"   - Business logic: ✅")
        print(f"   - Weighted voting: {'✅' if use_weighted_voting else '❌'}")
        print(f"   - Explainability: {'✅' if enable_explainability else '❌'}")
        print(f"   - Conflict resolution: {'✅' if CONFLICT_RESOLVER_AVAILABLE else '❌'}")
    
    def _init_fuzzy_matcher(self):
        """Initialize fuzzy string matching."""
        if RAPIDFUZZ_AVAILABLE:
            # Comprehensive synonym sets
            self.synonym_sets = {
                ColumnType.DATE: [
                    'date', 'time', 'timestamp', 'datetime', 'created', 'updated',
                    'order_date', 'transaction_date', 'purchase_date', 'sale_date',
                    'invoice_date', 'period', 'day', 'month', 'year', 'dt',
                    'fecha', 'data', 'datum', 'fecha', 'tarih', 'tanggal'
                ],
                ColumnType.SALES: [
                    'sales', 'revenue', 'income', 'earnings', 'turnover',
                    'gross_sales', 'net_sales', 'total_sales', 'sale_amount',
                    'ventas', 'ingresos', 'chiffre', 'umsatz', 'satış'
                ],
                ColumnType.AMOUNT: [
                    'amount', 'total', 'total_amount', 'price', 'value',
                    'cost', 'total_price', 'sum', 'grand_total', 'amt',
                    'monto', 'importe', 'betrag', 'tutar', 'jumlah'
                ],
                ColumnType.PRODUCT: [
                    'product', 'item', 'sku', 'product_name', 'item_name',
                    'product_id', 'item_id', 'goods', 'merchandise',
                    'article', 'product_code', 'prod', 'artículo', 'artikel'
                ],
                ColumnType.QUANTITY: [
                    'quantity', 'qty', 'units', 'volume', 'count', 'pieces',
                    'items', 'number', 'amount_sold', 'units_sold', 'sold',
                    'stock', 'cantidad', 'menge', 'miktar', 'jumlah'
                ],
                ColumnType.REGION: [
                    'region', 'area', 'territory', 'zone', 'district', 'location',
                    'city', 'state', 'country', 'province', 'market', 'geo',
                    'brand', 'company', 'manufacturer', 'supplier',  # Business entities as regions
                    'región', 'gebiet', 'bölge', 'wilayah'
                ]
            }
        else:
            self.synonym_sets = {}
    
    def _init_semantic_matcher(self):
        """Initialize semantic matching."""
        if SBERT_AVAILABLE:
            try:
                self.sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.semantic_descriptions = {
                    ColumnType.DATE: "date time timestamp when temporal period day month year",
                    ColumnType.SALES: "sales revenue income earnings money sold",
                    ColumnType.AMOUNT: "amount total value price cost sum",
                    ColumnType.PRODUCT: "product item sku name goods merchandise what",
                    ColumnType.QUANTITY: "quantity units count volume how many number",
                    ColumnType.REGION: "region area location territory where geographic place"
                }
                self._precompute_embeddings()
                print("✅ Semantic matcher initialized")
            except Exception as e:
                print(f"⚠️ Semantic matcher failed: {e}")
                self.sbert_model = None
        else:
            self.sbert_model = None
    
    def _precompute_embeddings(self):
        """Precompute embeddings for semantic matching."""
        if self.sbert_model:
            self.canonical_embeddings = {}
            for col_type, description in self.semantic_descriptions.items():
                self.canonical_embeddings[col_type] = self.sbert_model.encode(
                    description, convert_to_tensor=True
                )
    
    def _init_database(self):
        """Initialize SQLite database for knowledge base."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create mappings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS universal_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_column TEXT NOT NULL,
                    mapped_column TEXT NOT NULL,
                    confidence REAL,
                    method TEXT,
                    pattern_evidence TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    UNIQUE(original_column, mapped_column)
                )
            ''')
            
            # Create pattern patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS column_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    column_name TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT,
                    confidence REAL,
                    frequency INTEGER DEFAULT 1,
                    created_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Database initialization failed: {e}")
    
    def _init_pattern_recognizers(self):
        """Initialize advanced pattern recognition systems."""
        
        # Date pattern recognizers
        self.date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
            r'\d{2}/\d{2}/\d{2}',  # MM/DD/YY
            r'\d{1,2}/\d{1,2}/\d{4}',  # M/D/YYYY
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO datetime
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # Space datetime
        ]
        
        # Numeric pattern recognizers
        self.numeric_patterns = [
            r'^\d+$',  # Integer
            r'^\d+\.\d+$',  # Decimal
            r'^\d+\.\d{2}$',  # Currency (2 decimals)
            r'^\$\d+\.\d{2}$',  # Dollar amount
            r'^\d+,\d{3}(\.\d{2})?$',  # Comma-separated thousands
            r'^\d+\.\d{3}(,\d{2})?$',  # European format
        ]
        
        # ID pattern recognizers
        self.id_patterns = [
            r'^[A-Z]{2,4}\d{3,6}$',  # Product IDs like PEP642
            r'^\d{6,10}$',  # Numeric IDs
            r'^[A-Z]{2,4}-\d{3,6}$',  # Hyphenated IDs
            r'^[A-Z]{2,4}_\d{3,6}$',  # Underscore IDs
            r'^[A-Z]{2,4}\d{2,4}[A-Z]?\d{2,4}$',  # Mixed IDs
        ]
        
        # Email pattern
        self.email_pattern = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
        
        # Currency symbols
        self.currency_symbols = ['$', '€', '£', '¥', '₹', '₽', '¢', '₩']
        
        print("✅ Pattern recognizers initialized")
    
    def _init_business_rules(self):
        """Initialize business context rules."""
        
        # Business context patterns
        self.business_context = {
            'retail': {
                'amount_indicators': ['total', 'subtotal', 'tax', 'shipping', 'discount'],
                'quantity_indicators': ['qty', 'quantity', 'units', 'pieces', 'items'],
                'product_indicators': ['sku', 'product', 'item', 'name', 'description'],
                'date_indicators': ['order', 'ship', 'delivery', 'purchase', 'invoice']
            },
            'finance': {
                'amount_indicators': ['balance', 'amount', 'value', 'price', 'cost'],
                'date_indicators': ['date', 'time', 'timestamp', 'period', 'month'],
                'region_indicators': ['country', 'region', 'state', 'city', 'area']
            },
            'ecommerce': {
                'amount_indicators': ['price', 'total', 'subtotal', 'tax', 'shipping'],
                'product_indicators': ['product', 'item', 'sku', 'category', 'brand'],
                'quantity_indicators': ['quantity', 'qty', 'stock', 'inventory']
            }
        }
        
        print("✅ Business rules initialized")
    
    def _init_validation_schemas(self):
        """Initialize Pandera validation schemas for data type verification."""
        if not PANDERA_AVAILABLE:
            return
        
        try:
            # Define validation schemas for each column type
            self.validation_schemas = {
                ColumnType.DATE: {
                    'check': lambda x: self._is_date_pattern('date', x),
                    'dtype_hint': ['object', 'datetime64']
                },
                ColumnType.AMOUNT: {
                    'check': lambda x: pd.api.types.is_numeric_dtype(x) or self._is_numeric_pattern('amount', x),
                    'dtype_hint': ['float64', 'int64', 'object']
                },
                ColumnType.SALES: {
                    'check': lambda x: pd.api.types.is_numeric_dtype(x) or self._is_numeric_pattern('sales', x),
                    'dtype_hint': ['float64', 'int64', 'object']
                },
                ColumnType.QUANTITY: {
                    'check': lambda x: pd.api.types.is_numeric_dtype(x) or self._is_numeric_pattern('quantity', x),
                    'dtype_hint': ['int64', 'float64', 'object']
                },
                ColumnType.PRODUCT: {
                    'check': lambda x: True,  # Any type can be a product
                    'dtype_hint': ['object', 'string']
                },
                ColumnType.REGION: {
                    'check': lambda x: True,  # Any type can be a region
                    'dtype_hint': ['object', 'string']
                }
            }
            print("✅ Pandera validation schemas initialized")
        except Exception as e:
            print(f"⚠️ Failed to initialize validation schemas: {e}")
    
    def map_columns(self, df: pd.DataFrame, user_confirmed: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Map dataset columns using universal approach.
        
        Args:
            df: DataFrame with columns to map
            user_confirmed: Optional user-confirmed mappings
            
        Returns:
            Dict containing comprehensive mapping results
        """
        print(f"🗺️ Starting universal column mapping for {len(df.columns)} columns...")
        
        mapping_results = {
            'mapped_columns': [],
            'uncertain_columns': [],
            'unmapped_columns': [],
            'confidence_scores': {},
            'suggestions': {},
            'requires_confirmation': False,
            'mapping_method_distribution': {},
            'pattern_analysis': {},
            'business_context': {}
        }
        
        method_counts = {}
        
        # Analyze each column comprehensively
        for col in df.columns:
            print(f"   Analyzing column: {col}")
            
            # Track total mappings
            self.performance_stats['total_mappings'] += 1
            
            # Comprehensive column analysis
            analysis = self._analyze_column_comprehensive(col, df[col])
            mapping_results['pattern_analysis'][col] = analysis
            
            # Apply user confirmation if available
            if user_confirmed and col in user_confirmed:
                result = self._create_user_confirmed_result(col, user_confirmed[col], analysis)
            else:
                # Multi-layered mapping approach
                result = self._map_column_universal(col, analysis)
            
            # Track methods
            method = result.get('method', 'unknown')
            method_counts[method] = method_counts.get(method, 0) + 1
            
            # Categorize result
            if result['status'] == 'mapped':
                mapping_results['mapped_columns'].append(result)
                mapping_results['confidence_scores'][col] = result['confidence']
            elif result['status'] == 'uncertain':
                mapping_results['uncertain_columns'].append(result)
                mapping_results['suggestions'][col] = result['suggestions']
                # 🔥 CRITICAL FIX: Only require confirmation if no user mappings provided
                if not user_confirmed:
                    mapping_results['requires_confirmation'] = True
            else:
                mapping_results['unmapped_columns'].append(result)
        
        mapping_results['mapping_method_distribution'] = method_counts
        
        # ═══════════════════════════════════════════════════════════
        # CONFLICT DETECTION & RESOLUTION
        # ═══════════════════════════════════════════════════════════
        if self.conflict_resolver:
            conflicts = self.conflict_resolver.detect_conflicts(mapping_results, df)
            
            if conflicts:
                mapping_results['conflicts_detected'] = True
                mapping_results['conflicts'] = []
                mapping_results['conflict_resolutions'] = []
                
                for conflict in conflicts:
                    # Resolve each conflict
                    resolution = self.conflict_resolver.resolve_conflict(conflict, df, auto_resolve=True)
                    
                    # Save resolution (for learning)
                    self.conflict_resolver.save_resolution(resolution, user_confirmed=False)
                    
                    # Update mapping results with resolution
                    self._apply_conflict_resolution(mapping_results, conflict, resolution)
                    
                    # Get merge recommendations
                    merge_recommendations = self.conflict_resolver.get_merge_recommendations(conflict, df)
                    
                    # Format for UI
                    from column_conflict_resolver import format_conflict_for_ui
                    ui_formatted = format_conflict_for_ui(conflict, resolution, merge_recommendations)
                    mapping_results['conflict_resolutions'].append(ui_formatted)
                
                print(f"   ✅ Resolved {len(conflicts)} conflict(s) automatically")
            else:
                mapping_results['conflicts_detected'] = False
        else:
            mapping_results['conflicts_detected'] = False
        
        # Update knowledge base
        self._update_knowledge_base(mapping_results['mapped_columns'])
        
        print(f"✅ Mapping completed: {len(mapping_results['mapped_columns'])} mapped, "
              f"{len(mapping_results['uncertain_columns'])} uncertain, "
              f"{len(mapping_results['unmapped_columns'])} unmapped")
        
        return mapping_results
    
    def _analyze_column_comprehensive(self, column_name: str, series: pd.Series) -> ColumnAnalysis:
        """Perform comprehensive analysis of a column."""
        
        # Basic statistics
        sample_values = series.dropna().head(10).tolist()
        unique_count = series.nunique()
        null_count = series.isnull().sum()
        data_type = str(series.dtype)
        
        # Pattern recognition
        patterns = self._recognize_patterns(column_name, series)
        
        # Statistical features
        statistical_features = self._extract_statistical_features(series)
        
        # Business context
        business_context = self._analyze_business_context(column_name, series)
        
        return ColumnAnalysis(
            column_name=column_name,
            data_type=data_type,
            sample_values=sample_values,
            unique_count=unique_count,
            null_count=null_count,
            patterns=patterns,
            statistical_features=statistical_features,
            business_context=business_context
        )
    
    def _recognize_patterns(self, column_name: str, series: pd.Series) -> List[PatternMatch]:
        """Recognize various patterns in column data."""
        patterns = []
        
        # Date patterns
        if self._is_date_pattern(column_name, series):
            patterns.append(PatternMatch(
                pattern_type='date',
                confidence=95.0,
                evidence=['date_pattern_detected'],
                method='pattern_recognition'
            ))
        
        # Numeric patterns
        if self._is_numeric_pattern(column_name, series):
            patterns.append(PatternMatch(
                pattern_type='numeric',
                confidence=90.0,
                evidence=['numeric_values_detected'],
                method='pattern_recognition'
            ))
        
        # ID patterns
        if self._is_id_pattern(column_name, series):
            patterns.append(PatternMatch(
                pattern_type='id',
                confidence=85.0,
                evidence=['id_pattern_detected'],
                method='pattern_recognition'
            ))
        
        # Currency patterns
        if self._is_currency_pattern(column_name, series):
            patterns.append(PatternMatch(
                pattern_type='currency',
                confidence=90.0,
                evidence=['currency_symbols_or_format'],
                method='pattern_recognition'
            ))
        
        # Email patterns
        if self._is_email_pattern(column_name, series):
            patterns.append(PatternMatch(
                pattern_type='email',
                confidence=95.0,
                evidence=['email_format_detected'],
                method='pattern_recognition'
            ))
        
        # Categorical patterns
        if self._is_categorical_pattern(column_name, series):
            patterns.append(PatternMatch(
                pattern_type='categorical',
                confidence=80.0,
                evidence=['limited_unique_values'],
                method='statistical_analysis'
            ))
        
        return patterns
    
    def _is_date_pattern(self, column_name: str, series: pd.Series) -> bool:
        """Check if column contains date patterns."""
        # Check column name first
        col_lower = column_name.lower()
        if any(date_word in col_lower for date_word in ['date', 'time', 'timestamp', 'created', 'updated']):
            return True
        
        # Check data patterns
        sample_values = series.dropna().head(20).astype(str)
        if len(sample_values) == 0:
            return False
        
        # Try parsing as dates
        try:
            parsed = pd.to_datetime(sample_values, errors='coerce')
            success_rate = parsed.notna().mean()
            return success_rate >= 0.7
        except:
            return False
    
    def _is_numeric_pattern(self, column_name: str, series: pd.Series) -> bool:
        """Check if column contains numeric patterns."""
        sample_values = series.dropna().head(20)
        if len(sample_values) == 0:
            return False
        
        # Check if already numeric
        if pd.api.types.is_numeric_dtype(series):
            return True
        
        # Check string representations
        try:
            numeric_values = pd.to_numeric(sample_values, errors='coerce')
            success_rate = numeric_values.notna().mean()
            return success_rate >= 0.7
        except:
            return False
    
    def _is_id_pattern(self, column_name: str, series: pd.Series) -> bool:
        """Check if column contains ID patterns."""
        sample_values = series.dropna().head(20).astype(str)
        if len(sample_values) == 0:
            return False
        
        # Check against ID patterns
        matches = 0
        for value in sample_values:
            for pattern in self.id_patterns:
                if re.match(pattern, value):
                    matches += 1
                    break
        
        return matches / len(sample_values) >= 0.6
    
    def _is_currency_pattern(self, column_name: str, series: pd.Series) -> bool:
        """Check if column contains currency patterns."""
        sample_values = series.dropna().head(20).astype(str)
        if len(sample_values) == 0:
            return False
        
        # Check for currency symbols
        has_currency = any(
            any(symbol in str(val) for symbol in self.currency_symbols)
            for val in sample_values
        )
        
        # Check for decimal patterns (likely currency)
        decimal_pattern = re.compile(r'^\d+\.\d{2}$')
        has_decimal = sum(1 for val in sample_values if decimal_pattern.match(val))
        
        return has_currency or (has_decimal / len(sample_values) >= 0.7)
    
    def _is_email_pattern(self, column_name: str, series: pd.Series) -> bool:
        """Check if column contains email patterns."""
        sample_values = series.dropna().head(20).astype(str)
        if len(sample_values) == 0:
            return False
        
        matches = sum(1 for val in sample_values if self.email_pattern.match(val))
        return matches / len(sample_values) >= 0.7
    
    def _is_categorical_pattern(self, column_name: str, series: pd.Series) -> bool:
        """Check if column contains categorical patterns."""
        unique_ratio = series.nunique() / len(series)
        return unique_ratio <= 0.1  # Less than 10% unique values
    
    def _extract_statistical_features(self, series: pd.Series) -> Dict[str, Any]:
        """Extract statistical features from the series."""
        features = {
            'mean': None,
            'std': None,
            'min': None,
            'max': None,
            'median': None,
            'unique_ratio': series.nunique() / len(series),
            'null_ratio': series.isnull().sum() / len(series)
        }
        
        if pd.api.types.is_numeric_dtype(series):
            features.update({
                'mean': series.mean(),
                'std': series.std(),
                'min': series.min(),
                'max': series.max(),
                'median': series.median()
            })
        
        return features
    
    def _analyze_business_context(self, column_name: str, series: pd.Series) -> Dict[str, Any]:
        """Analyze business context of the column."""
        col_lower = column_name.lower()
        context = {
            'likely_business_domain': 'unknown',
            'confidence': 0.0,
            'indicators': []
        }
        
        # Check against business context patterns
        for domain, patterns in self.business_context.items():
            score = 0
            indicators = []
            
            for pattern_type, indicators_list in patterns.items():
                for indicator in indicators_list:
                    if indicator in col_lower:
                        score += 1
                        indicators.append(f"{pattern_type}:{indicator}")
            
            if score > context['confidence']:
                context['likely_business_domain'] = domain
                context['confidence'] = score
                context['indicators'] = indicators
        
        return context
    
    def _map_column_universal(self, column_name: str, analysis: ColumnAnalysis) -> Dict[str, Any]:
        """Apply universal mapping strategy with optional weighted voting."""
        
        if self.use_weighted_voting:
            return self._map_column_weighted_voting(column_name, analysis)
        else:
            # Original sequential approach (legacy mode)
            return self._map_column_sequential(column_name, analysis)
    
    def _map_column_sequential(self, column_name: str, analysis: ColumnAnalysis) -> Dict[str, Any]:
        """Apply sequential mapping strategy (original approach)."""
        
        # Layer 1: Direct pattern-based mapping (highest priority)
        pattern_result = self._map_by_patterns(column_name, analysis)
        if pattern_result['confidence'] >= 80.0:
            self.performance_stats['pattern_hits'] += 1
            return pattern_result
        
        # Layer 2: Business context mapping
        context_result = self._map_by_business_context(column_name, analysis)
        if context_result['confidence'] >= 70.0:
            return context_result
        
        # Layer 3: Fuzzy string matching (if available)
        if RAPIDFUZZ_AVAILABLE:
            fuzzy_result = self._map_by_fuzzy_matching(column_name, analysis)
            if fuzzy_result['confidence'] >= 60.0:
                self.performance_stats['fuzzy_hits'] += 1
                return fuzzy_result
        
        # Layer 4: Semantic matching (if available)
        if self.sbert_model:
            self.performance_stats['sbert_calls'] += 1
            semantic_result = self._map_by_semantic_similarity(column_name, analysis)
            if semantic_result['confidence'] >= 60.0:
                return semantic_result
        
        # Layer 5: Statistical inference
        statistical_result = self._map_by_statistics(column_name, analysis)
        if statistical_result['confidence'] >= 50.0:
            return statistical_result
        
        # Layer 6: Intelligent fallback
        return self._intelligent_fallback(column_name, analysis)
    
    def _map_column_weighted_voting(self, column_name: str, analysis: ColumnAnalysis) -> Dict[str, Any]:
        """
        Apply weighted voting strategy for robust mapping.
        This aggregates results from multiple layers intelligently.
        """
        
        layer_results = []
        
        # Layer 1: Pattern Recognition (Weight: 0.35)
        pattern_result = self._map_by_patterns(column_name, analysis)
        if pattern_result['confidence'] > 0:
            layer_results.append({
                'result': pattern_result,
                'weight': self.layer_weights['pattern'],
                'layer': 'pattern'
            })
            # If pattern is highly confident, we can skip expensive SBERT
            if pattern_result['confidence'] >= 85.0:
                self.performance_stats['pattern_hits'] += 1
        
        # Layer 2: Business Context (Weight: 0.25)
        context_result = self._map_by_business_context(column_name, analysis)
        if context_result['confidence'] > 0:
            layer_results.append({
                'result': context_result,
                'weight': self.layer_weights['context'],
                'layer': 'context'
            })
        
        # Layer 3: Fuzzy Matching (Weight: 0.20)
        if RAPIDFUZZ_AVAILABLE:
            fuzzy_result = self._map_by_fuzzy_matching(column_name, analysis)
            if fuzzy_result['confidence'] > 0:
                layer_results.append({
                    'result': fuzzy_result,
                    'weight': self.layer_weights['fuzzy'],
                    'layer': 'fuzzy'
                })
                if fuzzy_result['confidence'] >= 80.0:
                    self.performance_stats['fuzzy_hits'] += 1
        
        # 🎯 CRITICAL OPTIMIZATION: Only use SBERT if previous layers are uncertain
        # This is the key performance improvement - skip SBERT when not needed
        max_confidence_so_far = max(
            [lr['result']['confidence'] for lr in layer_results], 
            default=0
        )
        
        # Layer 4: SBERT - ONLY if previous layers didn't achieve high confidence (Weight: 0.15)
        if self.sbert_model and max_confidence_so_far < 80.0:
            self.performance_stats['sbert_calls'] += 1
            semantic_result = self._map_by_semantic_similarity(column_name, analysis)
            if semantic_result['confidence'] > 0:
                layer_results.append({
                    'result': semantic_result,
                    'weight': self.layer_weights['semantic'],
                    'layer': 'semantic'
                })
        
        # Layer 5: Statistical Inference (Weight: 0.05)
        statistical_result = self._map_by_statistics(column_name, analysis)
        if statistical_result['confidence'] > 0:
            layer_results.append({
                'result': statistical_result,
                'weight': self.layer_weights['statistical'],
                'layer': 'statistical'
            })
        
        # Perform weighted voting
        if layer_results:
            return self._weighted_vote(column_name, layer_results, analysis)
        else:
            # No results from any layer - use fallback
            return self._intelligent_fallback(column_name, analysis)
    
    def _map_by_patterns(self, column_name: str, analysis: ColumnAnalysis) -> Dict[str, Any]:
        """Map column based on recognized patterns."""
        col_lower = column_name.lower()
        patterns = analysis.patterns
        
        # Date pattern mapping
        if any(p.pattern_type == 'date' for p in patterns):
            return {
                'original_column': column_name,
                'mapped_column': ColumnType.DATE.value,
                'confidence': 95.0,
                'method': 'pattern_recognition',
                'status': 'mapped',
                'suggestions': [],
                'evidence': ['date_pattern_detected']
            }
        
        # Numeric pattern mapping
        if any(p.pattern_type == 'numeric' for p in patterns):
            # Determine if it's amount/sales or quantity
            if any(word in col_lower for word in ['amount', 'total', 'price', 'cost', 'value']):
                return {
                    'original_column': column_name,
                    'mapped_column': ColumnType.AMOUNT.value,
                    'confidence': 90.0,
                    'method': 'pattern_recognition',
                    'status': 'mapped',
                    'suggestions': [],
                    'evidence': ['numeric_amount_pattern']
                }
            elif any(word in col_lower for word in ['quantity', 'qty', 'units', 'count']):
                return {
                    'original_column': column_name,
                    'mapped_column': ColumnType.QUANTITY.value,
                    'confidence': 90.0,
                    'method': 'pattern_recognition',
                    'status': 'mapped',
                    'suggestions': [],
                    'evidence': ['numeric_quantity_pattern']
                }
        
        # ID pattern mapping
        if any(p.pattern_type == 'id' for p in patterns):
            if any(word in col_lower for word in ['product', 'item', 'sku']):
                return {
                    'original_column': column_name,
                    'mapped_column': ColumnType.PRODUCT.value,
                    'confidence': 85.0,
                    'method': 'pattern_recognition',
                    'status': 'mapped',
                    'suggestions': [],
                    'evidence': ['product_id_pattern']
                }
        
        # Categorical pattern mapping
        if any(p.pattern_type == 'categorical' for p in patterns):
            if any(word in col_lower for word in ['region', 'area', 'location', 'brand', 'category']):
                return {
                    'original_column': column_name,
                    'mapped_column': ColumnType.REGION.value,
                    'confidence': 80.0,
                    'method': 'pattern_recognition',
                    'status': 'mapped',
                    'suggestions': [],
                    'evidence': ['categorical_region_pattern']
                }
        
        return {'confidence': 0.0, 'status': 'unmapped'}
    
    def _map_by_business_context(self, column_name: str, analysis: ColumnAnalysis) -> Dict[str, Any]:
        """Map column based on business context."""
        context = analysis.business_context
        
        if context['confidence'] > 0:
            # Map based on business domain indicators
            indicators = context['indicators']
            
            for indicator in indicators:
                pattern_type, indicator_name = indicator.split(':')
                
                if pattern_type == 'amount_indicators':
                    return {
                        'original_column': column_name,
                        'mapped_column': ColumnType.AMOUNT.value,
                        'confidence': 75.0,
                        'method': 'business_context',
                        'status': 'mapped',
                        'suggestions': [],
                        'evidence': [f'business_{indicator_name}']
                    }
                elif pattern_type == 'quantity_indicators':
                    return {
                        'original_column': column_name,
                        'mapped_column': ColumnType.QUANTITY.value,
                        'confidence': 75.0,
                        'method': 'business_context',
                        'status': 'mapped',
                        'suggestions': [],
                        'evidence': [f'business_{indicator_name}']
                    }
                elif pattern_type == 'product_indicators':
                    return {
                        'original_column': column_name,
                        'mapped_column': ColumnType.PRODUCT.value,
                        'confidence': 75.0,
                        'method': 'business_context',
                        'status': 'mapped',
                        'suggestions': [],
                        'evidence': [f'business_{indicator_name}']
                    }
                elif pattern_type == 'date_indicators':
                    return {
                        'original_column': column_name,
                        'mapped_column': ColumnType.DATE.value,
                        'confidence': 75.0,
                        'method': 'business_context',
                        'status': 'mapped',
                        'suggestions': [],
                        'evidence': [f'business_{indicator_name}']
                    }
                elif pattern_type == 'region_indicators':
                    return {
                        'original_column': column_name,
                        'mapped_column': ColumnType.REGION.value,
                        'confidence': 75.0,
                        'method': 'business_context',
                        'status': 'mapped',
                        'suggestions': [],
                        'evidence': [f'business_{indicator_name}']
                    }
        
        return {'confidence': 0.0, 'status': 'unmapped'}
    
    def _map_by_fuzzy_matching(self, column_name: str, analysis: ColumnAnalysis) -> Dict[str, Any]:
        """Map column using fuzzy string matching."""
        if not RAPIDFUZZ_AVAILABLE:
            return {'confidence': 0.0, 'status': 'unmapped'}
        
        col_lower = column_name.lower()
        best_match = None
        best_score = 0.0
        
        for col_type, synonyms in self.synonym_sets.items():
            for synonym in synonyms:
                score = fuzz.WRatio(col_lower, synonym)
                if score > best_score:
                    best_score = score
                    best_match = col_type
        
        if best_score >= 60.0:
            return {
                'original_column': column_name,
                'mapped_column': best_match.value,
                'confidence': best_score,
                'method': 'fuzzy_matching',
                'status': 'mapped',
                'suggestions': [],
                'evidence': ['fuzzy_string_match']
            }
        
        return {'confidence': 0.0, 'status': 'unmapped'}
    
    def _map_by_semantic_similarity(self, column_name: str, analysis: ColumnAnalysis) -> Dict[str, Any]:
        """Map column using semantic similarity."""
        if not self.sbert_model:
            return {'confidence': 0.0, 'status': 'unmapped'}
        
        try:
            # Clean column name
            cleaned_name = column_name.replace('_', ' ').replace('-', ' ').lower()
            column_embedding = self.sbert_model.encode(cleaned_name, convert_to_tensor=True)
            
            best_match = None
            best_similarity = 0.0
            
            for col_type, embedding in self.canonical_embeddings.items():
                similarity = util.pytorch_cos_sim(column_embedding, embedding)[0][0].item()
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = col_type
            
            confidence = best_similarity * 100
            
            if confidence >= 60.0:
                return {
                    'original_column': column_name,
                    'mapped_column': best_match.value,
                    'confidence': confidence,
                    'method': 'semantic_similarity',
                    'status': 'mapped',
                    'suggestions': [],
                    'evidence': ['semantic_similarity']
                }
        
        except Exception as e:
            print(f"⚠️ Semantic matching failed: {e}")
        
        return {'confidence': 0.0, 'status': 'unmapped'}
    
    def _map_by_statistics(self, column_name: str, analysis: ColumnAnalysis) -> Dict[str, Any]:
        """Map column based on statistical features."""
        features = analysis.statistical_features
        col_lower = column_name.lower()
        
        # High cardinality numeric columns are likely amounts
        if (features['unique_ratio'] > 0.8 and 
            features['mean'] is not None and 
            features['mean'] > 0):
            
            if any(word in col_lower for word in ['amount', 'total', 'price', 'cost']):
                return {
                    'original_column': column_name,
                    'mapped_column': ColumnType.AMOUNT.value,
                    'confidence': 65.0,
                    'method': 'statistical_inference',
                    'status': 'mapped',
                    'suggestions': [],
                    'evidence': ['high_cardinality_numeric']
                }
        
        # Low cardinality categorical columns
        if features['unique_ratio'] < 0.1:
            if any(word in col_lower for word in ['region', 'area', 'category', 'brand']):
                return {
                    'original_column': column_name,
                    'mapped_column': ColumnType.REGION.value,
                    'confidence': 60.0,
                    'method': 'statistical_inference',
                    'status': 'mapped',
                    'suggestions': [],
                    'evidence': ['low_cardinality_categorical']
                }
        
        return {'confidence': 0.0, 'status': 'unmapped'}
    
    def _intelligent_fallback(self, column_name: str, analysis: ColumnAnalysis) -> Dict[str, Any]:
        """Intelligent fallback mapping strategy."""
        col_lower = column_name.lower()
        
        # Generate suggestions based on all available evidence
        suggestions = []
        
        # Pattern-based suggestions
        for pattern in analysis.patterns:
            if pattern.pattern_type == 'date':
                suggestions.append({
                    'type': ColumnType.DATE.value,
                    'confidence': pattern.confidence,
                    'reason': 'Date pattern detected',
                    'methods': ['pattern_recognition']
                })
            elif pattern.pattern_type == 'numeric':
                suggestions.extend([
                    {
                        'type': ColumnType.AMOUNT.value,
                        'confidence': 70.0,
                        'reason': 'Numeric values detected',
                        'methods': ['pattern_recognition']
                    },
                    {
                        'type': ColumnType.QUANTITY.value,
                        'confidence': 60.0,
                        'reason': 'Numeric values detected',
                        'methods': ['pattern_recognition']
                    }
                ])
            elif pattern.pattern_type == 'categorical':
                suggestions.append({
                    'type': ColumnType.REGION.value,
                    'confidence': 65.0,
                    'reason': 'Categorical values detected',
                    'methods': ['pattern_recognition']
                })
        
        # Context-based suggestions
        if analysis.business_context['confidence'] > 0:
            for indicator in analysis.business_context['indicators']:
                pattern_type, indicator_name = indicator.split(':')
                if pattern_type == 'amount_indicators':
                    suggestions.append({
                        'type': ColumnType.AMOUNT.value,
                        'confidence': 70.0,
                        'reason': f'Business context: {indicator_name}',
                        'methods': ['business_context']
                    })
        
        # Return uncertain status with suggestions
        return {
            'original_column': column_name,
            'mapped_column': None,
            'confidence': 0.0,
            'method': 'intelligent_fallback',
            'status': 'uncertain',
            'suggestions': suggestions[:5],  # Top 5 suggestions
            'evidence': ['fallback_analysis']
        }
    
    def _weighted_vote(self, column_name: str, layer_results: List[Dict], 
                      analysis: ColumnAnalysis) -> Dict[str, Any]:
        """
        Aggregate results using weighted voting with explainability.
        This combines evidence from multiple layers intelligently.
        """
        
        vote_scores = defaultdict(lambda: {'score': 0.0, 'votes': [], 'evidence': []})
        
        # Aggregate votes from all layers
        for layer in layer_results:
            result = layer['result']
            weight = layer['weight']
            layer_name = layer['layer']
            
            if result.get('mapped_column'):
                mapped_col = result['mapped_column']
                confidence = result['confidence']
                weighted_score = (confidence / 100.0) * weight * 100
                
                vote_scores[mapped_col]['score'] += weighted_score
                vote_scores[mapped_col]['votes'].append({
                    'layer': layer_name,
                    'confidence': confidence,
                    'weight': weight,
                    'contribution': weighted_score
                })
                vote_scores[mapped_col]['evidence'].extend(result.get('evidence', []))
        
        if not vote_scores:
            return self._intelligent_fallback(column_name, analysis)
        
        # Get winner
        winner = max(vote_scores.items(), key=lambda x: x[1]['score'])
        mapped_column = winner[0]
        final_score = winner[1]['score']
        
        # Apply Pandera validation if available
        if PANDERA_AVAILABLE and hasattr(self, 'validation_schemas'):
            validation_boost = self._validate_mapping(column_name, mapped_column, analysis)
            final_score = min(100.0, final_score + validation_boost)
        
        # Build explainability
        explanation = None
        if self.enable_explainability:
            explanation = self._build_explanation(mapped_column, winner[1]['votes'])
        
        # Determine status based on confidence
        if final_score >= self.confidence_threshold:
            status = 'mapped'
        elif final_score >= 40.0:
            status = 'uncertain'
        else:
            status = 'unmapped'
        
        result = {
            'original_column': column_name,
            'mapped_column': mapped_column,
            'confidence': min(100.0, final_score),
            'method': 'weighted_voting',
            'status': status,
            'suggestions': [],
            'evidence': list(set(winner[1]['evidence']))  # Deduplicate evidence
        }
        
        # Add explainability if enabled
        if explanation:
            result['explanation'] = explanation
            result['voting_breakdown'] = winner[1]['votes']
        
        return result
    
    def _build_explanation(self, mapped_column: str, votes: List[Dict]) -> str:
        """Build human-readable explanation for mapping decision."""
        
        # Sort votes by contribution (highest first)
        sorted_votes = sorted(votes, key=lambda x: x['contribution'], reverse=True)
        
        reasons = []
        for vote in sorted_votes[:3]:  # Top 3 contributing factors
            layer = vote['layer']
            conf = vote['confidence']
            contrib = vote['contribution']
            
            if layer == 'pattern':
                reasons.append(f"pattern recognition ({conf:.0f}% confidence, {contrib:.0f}% weight)")
            elif layer == 'context':
                reasons.append(f"business context analysis ({conf:.0f}% confidence, {contrib:.0f}% weight)")
            elif layer == 'fuzzy':
                reasons.append(f"string similarity matching ({conf:.0f}% confidence, {contrib:.0f}% weight)")
            elif layer == 'semantic':
                reasons.append(f"semantic understanding ({conf:.0f}% confidence, {contrib:.0f}% weight)")
            elif layer == 'statistical':
                reasons.append(f"data distribution analysis ({conf:.0f}% confidence, {contrib:.0f}% weight)")
        
        if reasons:
            return f"Mapped to '{mapped_column}' based on: {'; '.join(reasons)}"
        else:
            return f"Mapped to '{mapped_column}'"
    
    def _validate_mapping(self, column_name: str, mapped_column: str, 
                         analysis: ColumnAnalysis) -> float:
        """
        Validate mapping using Pandera schemas.
        Returns confidence boost (positive) or penalty (negative).
        """
        try:
            # Find matching column type
            col_type = None
            for ct in ColumnType:
                if ct.value == mapped_column:
                    col_type = ct
                    break
            
            if not col_type or col_type not in self.validation_schemas:
                return 0.0
            
            schema = self.validation_schemas[col_type]
            
            # Get sample data for validation
            sample_values = pd.Series(analysis.sample_values)
            
            # Run validation check
            if schema['check'](sample_values):
                # Data matches expected type - boost confidence
                return 10.0
            else:
                # Data doesn't match expected type - slight penalty
                return -5.0
                
        except Exception as e:
            # Validation failed - no change
            return 0.0
    
    def _create_user_confirmed_result(self, column_name: str, mapped_type: str, analysis: ColumnAnalysis) -> Dict[str, Any]:
        """Create result for user-confirmed mapping."""
        result = {
            'original_column': column_name,
            'mapped_column': mapped_type,
            'confidence': 100.0,
            'method': 'user_confirmed',
            'status': 'mapped',
            'suggestions': [],
            'evidence': ['user_confirmation']
        }
        
        if self.enable_explainability:
            result['explanation'] = f"User manually confirmed mapping to '{mapped_type}'"
        
        return result
    
    def _apply_conflict_resolution(self, mapping_results: Dict[str, Any], 
                                   conflict: Dict[str, Any], 
                                   resolution) -> None:
        """
        Apply conflict resolution to mapping results.
        
        Updates the mapping_results to reflect the conflict resolution:
        - Winner column gets boosted confidence
        - Loser columns get marked as 'Ignore' or moved to uncertain
        """
        winner_column = resolution.winner_column
        loser_columns = resolution.loser_columns
        target_type = resolution.target_type
        
        # Update mapped_columns to reflect resolution
        mapped_columns_updated = []
        uncertain_columns_updated = []
        
        for mapping in mapping_results['mapped_columns']:
            if mapping['original_column'] == winner_column and mapping['mapped_column'] == target_type:
                # Boost winner confidence
                mapping['confidence'] = resolution.confidence
                mapping['method'] = 'conflict_resolution'
                mapping['evidence'] = mapping.get('evidence', []) + ['conflict_resolved']
                if self.enable_explainability:
                    mapping['explanation'] = resolution.reasoning
                mapped_columns_updated.append(mapping)
            elif mapping['original_column'] in loser_columns and mapping['mapped_column'] == target_type:
                # Move loser to 'Ignore' or uncertain
                mapping['mapped_column'] = 'Ignore'
                mapping['status'] = 'ignored'
                mapping['confidence'] = 0.0
                mapping['evidence'] = ['conflict_loser']
                if self.enable_explainability:
                    mapping['explanation'] = f"Marked as 'Ignore' due to conflict with '{winner_column}'"
                # Keep in mapped but as 'Ignore'
                mapped_columns_updated.append(mapping)
            else:
                mapped_columns_updated.append(mapping)
        
        # Update uncertain columns
        for mapping in mapping_results['uncertain_columns']:
            if mapping['original_column'] == winner_column:
                # Promote to mapped
                mapping['mapped_column'] = target_type
                mapping['confidence'] = resolution.confidence
                mapping['status'] = 'mapped'
                mapping['method'] = 'conflict_resolution'
                mapping['evidence'] = ['conflict_resolved']
                if self.enable_explainability:
                    mapping['explanation'] = resolution.reasoning
                mapped_columns_updated.append(mapping)
            elif mapping['original_column'] in loser_columns:
                # Mark as ignore
                mapping['mapped_column'] = 'Ignore'
                mapping['status'] = 'ignored'
                mapping['confidence'] = 0.0
                mapping['evidence'] = ['conflict_loser']
                uncertain_columns_updated.append(mapping)
            else:
                uncertain_columns_updated.append(mapping)
        
        # Update the mapping results
        mapping_results['mapped_columns'] = mapped_columns_updated
        mapping_results['uncertain_columns'] = uncertain_columns_updated
    
    def _update_knowledge_base(self, mapped_columns: List[Dict]):
        """Update knowledge base with successful mappings."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for mapping in mapped_columns:
                if mapping['confidence'] >= self.confidence_threshold:
                    timestamp = datetime.now().isoformat()
                    evidence_json = json.dumps(mapping.get('evidence', []))
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO universal_mappings 
                        (original_column, mapped_column, confidence, method, pattern_evidence, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        mapping['original_column'].lower(),
                        mapping['mapped_column'],
                        mapping['confidence'],
                        mapping['method'],
                        evidence_json,
                        timestamp,
                        timestamp
                    ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Failed to update knowledge base: {e}")
    
    def get_mapping_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the mapping system."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total mappings
            cursor.execute('SELECT COUNT(*) FROM universal_mappings')
            total_mappings = cursor.fetchone()[0]
            
            # Get method distribution
            cursor.execute('SELECT method, COUNT(*) FROM universal_mappings GROUP BY method')
            method_distribution = dict(cursor.fetchall())
            
            # Get most common mappings
            cursor.execute('''
                SELECT mapped_column, COUNT(*) as count 
                FROM universal_mappings 
                GROUP BY mapped_column 
                ORDER BY count DESC 
                LIMIT 10
            ''')
            most_common_types = cursor.fetchall()
            
            conn.close()
            
            # Calculate performance metrics
            total_cols = self.performance_stats['total_mappings']
            sbert_usage_rate = 0.0
            if total_cols > 0:
                sbert_usage_rate = (self.performance_stats['sbert_calls'] / total_cols) * 100
            
            return {
                'total_mappings': total_mappings,
                'method_distribution': method_distribution,
                'most_common_types': most_common_types,
                'semantic_enabled': self.sbert_model is not None,
                'fuzzy_enabled': RAPIDFUZZ_AVAILABLE,
                'pandera_enabled': PANDERA_AVAILABLE,
                'weighted_voting_enabled': self.use_weighted_voting,
                'explainability_enabled': self.enable_explainability,
                'database_path': self.db_path,
                'performance_stats': {
                    'total_columns_mapped': total_cols,
                    'sbert_calls': self.performance_stats['sbert_calls'],
                    'sbert_usage_rate': f"{sbert_usage_rate:.1f}%",
                    'pattern_hits': self.performance_stats['pattern_hits'],
                    'fuzzy_hits': self.performance_stats['fuzzy_hits']
                }
            }
            
        except Exception as e:
            print(f"⚠️ Failed to get statistics: {e}")
            return {}
    
    def get_dropdown_options(self) -> List[str]:
        """Get dropdown options for column mapping."""
        return [col_type.value for col_type in ColumnType]
    
    def reset_performance_stats(self):
        """Reset performance tracking statistics."""
        self.performance_stats = {
            'sbert_calls': 0,
            'pattern_hits': 0,
            'fuzzy_hits': 0,
            'total_mappings': 0
        }
        print("✅ Performance statistics reset")
    
    def configure_weights(self, pattern: float = None, context: float = None, 
                         fuzzy: float = None, semantic: float = None, 
                         statistical: float = None):
        """
        Configure layer weights for weighted voting.
        
        Args:
            pattern: Weight for pattern recognition (0-1)
            context: Weight for business context (0-1)
            fuzzy: Weight for fuzzy matching (0-1)
            semantic: Weight for semantic similarity (0-1)
            statistical: Weight for statistical inference (0-1)
            
        Note: Weights will be normalized to sum to 1.0
        """
        if pattern is not None:
            self.layer_weights['pattern'] = pattern
        if context is not None:
            self.layer_weights['context'] = context
        if fuzzy is not None:
            self.layer_weights['fuzzy'] = fuzzy
        if semantic is not None:
            self.layer_weights['semantic'] = semantic
        if statistical is not None:
            self.layer_weights['statistical'] = statistical
        
        # Normalize weights to sum to 1.0
        total_weight = sum(self.layer_weights.values())
        if total_weight > 0:
            for key in self.layer_weights:
                self.layer_weights[key] /= total_weight
        
        print(f"✅ Layer weights configured: {self.layer_weights}")
    
    def get_performance_report(self) -> str:
        """Generate a human-readable performance report."""
        stats = self.performance_stats
        total = stats['total_mappings']
        
        if total == 0:
            return "No mappings performed yet."
        
        sbert_rate = (stats['sbert_calls'] / total) * 100
        pattern_rate = (stats['pattern_hits'] / total) * 100
        fuzzy_rate = (stats['fuzzy_hits'] / total) * 100
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║           UNIVERSAL COLUMN MAPPER PERFORMANCE            ║
╠══════════════════════════════════════════════════════════╣
║ Total Columns Mapped:      {total:6d}                       ║
║ Pattern Recognition Hits:  {stats['pattern_hits']:6d} ({pattern_rate:5.1f}%)            ║
║ Fuzzy Matching Hits:       {stats['fuzzy_hits']:6d} ({fuzzy_rate:5.1f}%)            ║
║ SBERT Calls:               {stats['sbert_calls']:6d} ({sbert_rate:5.1f}%)            ║
╠══════════════════════════════════════════════════════════╣
║ Configuration:                                           ║
║   • Weighted Voting:       {'ENABLED ' if self.use_weighted_voting else 'DISABLED'}                      ║
║   • Explainability:        {'ENABLED ' if self.enable_explainability else 'DISABLED'}                      ║
║   • SBERT Available:       {'YES     ' if self.sbert_model else 'NO      '}                      ║
║   • RapidFuzz Available:   {'YES     ' if RAPIDFUZZ_AVAILABLE else 'NO      '}                      ║
║   • Pandera Available:     {'YES     ' if PANDERA_AVAILABLE else 'NO      '}                      ║
╠══════════════════════════════════════════════════════════╣
║ Efficiency Gain:                                         ║
║   SBERT Usage Reduction:   {100 - sbert_rate:5.1f}% fewer calls         ║
║   (Target: 80% reduction for optimal performance)        ║
╚══════════════════════════════════════════════════════════╝
        """
        return report


if __name__ == "__main__":
    # Test the universal column mapper
    print("🧪 Testing Universal Column Mapper")
    print("=" * 50)
    
    # Create test data
    test_data = {
        'Transaction ID': [100001, 100002, 100003],
        'Date': ['5/3/2025', '5/3/2025', '5/3/2025'],
        'Product ID': ['PEP642', 'PEP186', 'PEP394'],
        'Customer ID': [842, 5, 464],
        'Quantity': [2, 3, 1],
        'Unit Price': [73, 107, 66],
        'Amount': [146, 321, 66],
        'Brand': ['Pepsi', 'Pepsi', 'Pepsi']
    }
    
    df = pd.DataFrame(test_data)
    
    # Initialize mapper
    mapper = UniversalColumnMapper()
    
    # Test mapping
    results = mapper.map_columns(df)
    
    print("\n✅ MAPPING RESULTS:")
    print("=" * 50)
    
    for mapping in results['mapped_columns']:
        conf = mapping['confidence']
        method = mapping['method']
        orig = mapping['original_column']
        mapped = mapping['mapped_column']
        
        print(f"✅ {orig} → {mapped} ({conf:.1f}%, {method})")
        
        # Show explanation if available
        if 'explanation' in mapping:
            print(f"   💡 {mapping['explanation']}")
        
        # Show voting breakdown if available
        if 'voting_breakdown' in mapping:
            print(f"   📊 Voting breakdown:")
            for vote in mapping['voting_breakdown']:
                print(f"      - {vote['layer']}: {vote['confidence']:.0f}% confidence "
                      f"(weight: {vote['weight']:.2f}, contribution: {vote['contribution']:.1f})")
    
    for mapping in results['uncertain_columns']:
        print(f"❓ {mapping['original_column']} (uncertain)")
    
    for mapping in results['unmapped_columns']:
        print(f"❌ {mapping['original_column']} (unmapped)")
    
    print(f"\n📊 Method Distribution: {results['mapping_method_distribution']}")
    
    # Show performance report
    print("\n" + "=" * 60)
    print(mapper.get_performance_report())
    
    # Show mapping statistics
    print("\n📈 MAPPING STATISTICS:")
    print("=" * 50)
    stats = mapper.get_mapping_statistics()
    if 'performance_stats' in stats:
        perf = stats['performance_stats']
        print(f"Total columns mapped: {perf['total_columns_mapped']}")
        print(f"SBERT usage rate: {perf['sbert_usage_rate']}")
        print(f"Pattern hits: {perf['pattern_hits']}")
        print(f"Fuzzy hits: {perf['fuzzy_hits']}")
    
    print("\n✨ Features enabled:")
    print(f"   • Weighted Voting: {stats.get('weighted_voting_enabled', False)}")
    print(f"   • Explainability: {stats.get('explainability_enabled', False)}")
    print(f"   • SBERT: {stats.get('semantic_enabled', False)}")
    print(f"   • RapidFuzz: {stats.get('fuzzy_enabled', False)}")
    print(f"   • Pandera: {stats.get('pandera_enabled', False)}")
