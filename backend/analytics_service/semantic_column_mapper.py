# semantic_column_mapper.py
"""
Enhanced Column Mapper with Semantic Similarity (SBERT)
Combines fuzzy matching with semantic understanding for intelligent column mapping.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from rapidfuzz import fuzz, process
import json
import os
from datetime import datetime
import sqlite3

# Sentence-BERT for semantic similarity
try:
    from sentence_transformers import SentenceTransformer, util
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False
    print("⚠️ Sentence-BERT not available. Install with: pip install sentence-transformers")


class SemanticColumnMapper:
    """
    Enhanced column mapping with semantic understanding using SBERT + RapidFuzz.
    Implements smart, adaptive column understanding with SQLite knowledge base.
    """
    
    def __init__(self, db_path: str = "column_mapping_kb.db"):
        self.db_path = db_path
        self.confidence_threshold = 70.0  # Lowered to be more permissive with high-confidence mappings
        self.semantic_threshold = 0.70  # Semantic similarity threshold
        
        # Initialize SBERT model
        if SBERT_AVAILABLE:
            print("🔄 Loading SBERT model for semantic similarity...")
            try:
                self.sbert_model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast and efficient
                self.semantic_enabled = True
                print("✅ SBERT model loaded successfully")
            except Exception as e:
                print(f"⚠️ Failed to load SBERT model: {e}")
                self.sbert_model = None
                self.semantic_enabled = False
        else:
            self.sbert_model = None
            self.semantic_enabled = False
        
        # Initialize database
        self._init_database()
        
        # Load synonym maps
        self.initialize_synonym_maps()
        
        # Precompute semantic embeddings for canonical types
        if self.semantic_enabled:
            self._precompute_canonical_embeddings()
    
    def _init_database(self):
        """Initialize SQLite database for knowledge base."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create mappings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS column_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_column TEXT NOT NULL,
                    mapped_column TEXT NOT NULL,
                    confidence REAL,
                    method TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    UNIQUE(original_column, mapped_column)
                )
            ''')
            
            # Create confirmations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mapping_confirmations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_column TEXT NOT NULL,
                    mapped_column TEXT NOT NULL,
                    confidence REAL,
                    user_id TEXT,
                    timestamp TEXT,
                    feedback_score INTEGER
                )
            ''')
            
            # Create ignore patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ignore_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    column_name TEXT NOT NULL,
                    analytics_type TEXT NOT NULL,
                    timestamp TEXT,
                    reason TEXT
                )
            ''')
            
            # Create indices for faster lookups
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_original_column ON column_mappings(original_column)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_mapped_column ON column_mappings(mapped_column)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_confirmations_column ON mapping_confirmations(original_column)')
            
            conn.commit()
            conn.close()
            print("✅ SQLite knowledge base initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize database: {e}")
    
    def initialize_synonym_maps(self):
        """Initialize synonym maps focused on TANAW's 5 required columns."""
        # Import from analytics_config
        try:
            from analytics_config import COLUMN_SYNONYMS, ColumnType
            
            # Map to the 5 required column types only
            self.synonym_maps = {
                'Date': COLUMN_SYNONYMS[ColumnType.DATE],
                'Sales': COLUMN_SYNONYMS[ColumnType.SALES],
                'Amount': COLUMN_SYNONYMS[ColumnType.AMOUNT],
                'Product': COLUMN_SYNONYMS[ColumnType.PRODUCT],
                'Quantity': COLUMN_SYNONYMS[ColumnType.QUANTITY],
                'Region': COLUMN_SYNONYMS[ColumnType.REGION]
            }
            
        except ImportError:
            # Fallback to minimal hardcoded synonyms
            self.synonym_maps = {
                'Date': ['date', 'time', 'timestamp', 'datetime', 'order_date', 'transaction_date'],
                'Sales': ['sales', 'revenue', 'income', 'earnings', 'turnover'],
                'Amount': ['amount', 'amt', 'total', 'value', 'price', 'cost'],
                'Product': ['product', 'item', 'sku', 'product_name', 'item_name'],
                'Quantity': ['quantity', 'qty', 'units', 'volume', 'count'],
                'Region': ['region', 'area', 'territory', 'zone', 'location']
            }
        
        # Create reverse mapping
        self.reverse_synonyms = {}
        for canonical, synonyms in self.synonym_maps.items():
            for synonym in synonyms:
                self.reverse_synonyms[synonym.lower()] = canonical
    
    def _precompute_canonical_embeddings(self):
        """Precompute SBERT embeddings for TANAW's 5 required column types."""
        if not self.semantic_enabled:
            return
        
        try:
            # Import semantic descriptions from analytics_config
            try:
                from analytics_config import COLUMN_SEMANTIC_DESCRIPTIONS, ColumnType
                canonical_descriptions = {
                    'Date': COLUMN_SEMANTIC_DESCRIPTIONS[ColumnType.DATE],
                    'Sales': COLUMN_SEMANTIC_DESCRIPTIONS[ColumnType.SALES],
                    'Amount': COLUMN_SEMANTIC_DESCRIPTIONS[ColumnType.AMOUNT],
                    'Product': COLUMN_SEMANTIC_DESCRIPTIONS[ColumnType.PRODUCT],
                    'Quantity': COLUMN_SEMANTIC_DESCRIPTIONS[ColumnType.QUANTITY],
                    'Region': COLUMN_SEMANTIC_DESCRIPTIONS[ColumnType.REGION]
                }
            except ImportError:
                # Fallback descriptions
                canonical_descriptions = {
                    'Date': 'date time timestamp when temporal period',
                    'Sales': 'sales revenue income earnings money sold',
                    'Amount': 'amount total value price cost sum',
                    'Product': 'product item sku name goods merchandise',
                    'Quantity': 'quantity units count volume how many',
                    'Region': 'region area location territory where geographic'
                }
            
            self.canonical_embeddings = {}
            for canonical, description in canonical_descriptions.items():
                self.canonical_embeddings[canonical] = self.sbert_model.encode(
                    description, convert_to_tensor=True
                )
            
            print(f"✅ Precomputed embeddings for {len(self.canonical_embeddings)} TANAW column types")
            
        except Exception as e:
            print(f"⚠️ Failed to precompute embeddings: {e}")
            self.semantic_enabled = False
    
    def map_columns(self, df: pd.DataFrame, user_confirmed: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Map dataset columns to TANAW standard columns using semantic + fuzzy matching.
        
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
            'requires_confirmation': False,
            'mapping_method_distribution': {}
        }
        
        method_counts = {}
        
        # Process each column
        for col in df.columns:
            col_result = self._map_single_column(col, df[col], user_confirmed)
            
            # Track methods used
            method = col_result.get('method', 'unknown')
            method_counts[method] = method_counts.get(method, 0) + 1
            
            if col_result['status'] == 'mapped':
                mapping_results['mapped_columns'].append(col_result)
                mapping_results['confidence_scores'][col] = col_result['confidence']
            elif col_result['status'] == 'uncertain':
                mapping_results['uncertain_columns'].append(col_result)
                mapping_results['suggestions'][col] = col_result['suggestions']
                # 🔥 CRITICAL FIX: Only require confirmation if no user mappings provided
                if not user_confirmed:
                    mapping_results['requires_confirmation'] = True
            else:
                mapping_results['unmapped_columns'].append(col_result)
        
        mapping_results['mapping_method_distribution'] = method_counts
        
        # Update knowledge base with successful mappings
        self._update_knowledge_base(mapping_results['mapped_columns'])
        
        return mapping_results
    
    def _map_single_column(self, column_name: str, series: pd.Series, 
                          user_confirmed: Optional[Dict] = None) -> Dict[str, Any]:
        """Map a single column using hybrid approach (semantic + fuzzy + value analysis)."""
        
        # Check for user-confirmed mapping first
        if user_confirmed and column_name in user_confirmed:
            confirmed_type = user_confirmed[column_name]
            self._save_confirmation(column_name, confirmed_type, 100.0)
            return {
                'original_column': column_name,
                'mapped_column': confirmed_type,
                'confidence': 100.0,
                'method': 'user_confirmed',
                'status': 'mapped',
                'suggestions': []
            }
        
        # Check knowledge base
        kb_result = self._check_knowledge_base(column_name)
        if kb_result and kb_result['confidence'] >= self.confidence_threshold:
            return kb_result
        
        # Perform hybrid matching
        fuzzy_result = self._fuzzy_match_column(column_name)
        semantic_result = self._semantic_match_column(column_name) if self.semantic_enabled else None
        value_analysis = self._analyze_column_values(series)
        
        # Combine results intelligently
        final_result = self._combine_mapping_results(
            column_name, fuzzy_result, semantic_result, value_analysis
        )
        
        return final_result
    
    def _check_knowledge_base(self, column_name: str) -> Optional[Dict[str, Any]]:
        """Check SQLite knowledge base for previous mappings."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            col_lower = column_name.lower()
            
            # Check for direct mapping
            cursor.execute('''
                SELECT mapped_column, confidence, method, updated_at
                FROM column_mappings
                WHERE LOWER(original_column) = ?
                ORDER BY updated_at DESC
                LIMIT 1
            ''', (col_lower,))
            
            result = cursor.fetchone()
            
            if result:
                mapped_column, confidence, method, updated_at = result
                
                # Check confirmation history
                cursor.execute('''
                    SELECT AVG(confidence), COUNT(*), AVG(feedback_score)
                    FROM mapping_confirmations
                    WHERE LOWER(original_column) = ? AND LOWER(mapped_column) = ?
                ''', (col_lower, mapped_column.lower()))
                
                conf_result = cursor.fetchone()
                avg_conf, count, avg_feedback = conf_result if conf_result else (None, 0, None)
                
                # Boost confidence with confirmation history
                if count > 0 and avg_conf:
                    confidence = min(100.0, confidence + (count * 2))  # Boost by 2% per confirmation
                
                conn.close()
                
                return {
                    'original_column': column_name,
                    'mapped_column': mapped_column,
                    'confidence': confidence or 85.0,
                    'method': f'knowledge_base_{method}',
                    'status': 'mapped' if (confidence or 85.0) >= self.confidence_threshold else 'uncertain',
                    'suggestions': [],
                    'confirmations': count
                }
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Knowledge base lookup failed: {e}")
        
        return None
    
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
        
        return {
            'matched_type': best_match,
            'confidence': best_score,
            'method': 'fuzzy_match'
        }
    
    def _semantic_match_column(self, column_name: str) -> Optional[Dict[str, Any]]:
        """Perform semantic matching using SBERT."""
        if not self.semantic_enabled:
            return None
        
        try:
            # Clean column name for better semantic understanding
            cleaned_name = column_name.replace('_', ' ').replace('-', ' ').lower()
            
            # Encode column name
            column_embedding = self.sbert_model.encode(cleaned_name, convert_to_tensor=True)
            
            # Compute similarity with all canonical types
            similarities = {}
            for canonical, canonical_embedding in self.canonical_embeddings.items():
                similarity = util.pytorch_cos_sim(column_embedding, canonical_embedding)[0][0].item()
                similarities[canonical] = similarity
            
            # Get best match
            best_match = max(similarities.items(), key=lambda x: x[1])
            canonical_type, similarity_score = best_match
            
            # Convert similarity to confidence (0-1 to 0-100)
            confidence = similarity_score * 100
            
            return {
                'matched_type': canonical_type,
                'confidence': confidence,
                'method': 'semantic_match',
                'similarity_score': similarity_score
            }
            
        except Exception as e:
            print(f"⚠️ Semantic matching failed: {e}")
            return None
    
    def _analyze_column_values(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze column values to provide additional context for mapping."""
        analysis = {
            'data_type': str(series.dtype),
            'unique_count': series.nunique(),
            'null_count': series.isnull().sum(),
            'null_percentage': (series.isnull().sum() / len(series)) * 100,
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
        if self._looks_like_currency(series):
            analysis['patterns'].append('currency_like')
        
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
        if len(sample) == 0:
            return False
        # Check if values are mostly alphanumeric and relatively short
        return all(len(val) <= 20 and val.replace('-', '').replace('_', '').isalnum() for val in sample)
    
    def _looks_like_email(self, series: pd.Series) -> bool:
        """Check if series looks like email data."""
        import re
        email_pattern = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
        sample = series.dropna().head(10).astype(str)
        if len(sample) == 0:
            return False
        return sum(1 for val in sample if email_pattern.match(val)) / len(sample) >= 0.7
    
    def _looks_like_currency(self, series: pd.Series) -> bool:
        """Check if series looks like currency data."""
        sample = series.dropna().head(10).astype(str)
        if len(sample) == 0:
            return False
        # Check for currency symbols or numeric with 2 decimal places
        currency_symbols = ['$', '€', '£', '¥', '₹']
        has_currency = any(any(sym in str(val) for sym in currency_symbols) for val in sample)
        
        # Try to extract numeric values
        try:
            numeric_vals = pd.to_numeric(series.dropna().head(10), errors='coerce')
            # Check if mostly 2 decimal places
            if numeric_vals.notna().any():
                decimals = numeric_vals.apply(lambda x: len(str(x).split('.')[-1]) if '.' in str(x) else 0)
                mostly_2_decimals = (decimals == 2).mean() >= 0.7
                return has_currency or mostly_2_decimals
        except:
            pass
        
        return has_currency
    
    def _resolve_column_conflicts(self, column_name: str, candidates: Dict, value_analysis: Dict) -> Optional[str]:
        """
        Resolve specific column mapping conflicts based on column name patterns and context.
        This is critical for handling cases like Amount vs Unit Price both mapping to 'price'.
        """
        col_lower = column_name.lower()
        
        # CRITICAL FIXES for the specific dataset columns
        
        # 1. Amount column should map to Amount (for analytics), not price
        if col_lower in ['amount', 'total_amount', 'total', 'grand_total']:
            return 'Amount'
        
        # 2. Unit Price should map to price (internal use)
        if col_lower in ['unit_price', 'unit price', 'price_per_unit', 'cost_per_unit']:
            return 'price'
        
        # 3. Date columns should always map to Date
        if col_lower in ['date', 'time', 'timestamp', 'datetime', 'created_at', 'updated_at']:
            return 'Date'
        
        # 4. Product ID should map to Product
        if col_lower in ['product_id', 'product id', 'item_id', 'item id', 'sku', 'product_code']:
            return 'Product'
        
        # 5. Quantity should map to Quantity
        if col_lower in ['quantity', 'qty', 'units', 'volume', 'count']:
            return 'Quantity'
        
        # 6. Customer ID should be ignored or mapped to a generic ID type
        if col_lower in ['customer_id', 'customer id', 'client_id', 'client id']:
            return 'customer_id'  # Keep as is for internal use
        
        # 7. Transaction ID should map to order_id
        if col_lower in ['transaction_id', 'transaction id', 'order_id', 'order id', 'invoice_id']:
            return 'order_id'
        
        # 8. Brand should map to Region (for regional analysis) or be ignored
        if col_lower in ['brand', 'company', 'manufacturer', 'supplier']:
            return 'Region'  # Map brand to region for regional analysis
        
        # 9. Sales/Revenue columns should map to Sales
        if col_lower in ['sales', 'revenue', 'income', 'earnings', 'turnover']:
            return 'Sales'
        
        # If no specific conflict resolution, return None to use normal process
        return None
    
    def _combine_mapping_results(self, column_name: str, fuzzy_result: Dict, 
                                semantic_result: Optional[Dict], value_analysis: Dict) -> Dict[str, Any]:
        """Combine fuzzy, semantic, and value analysis results intelligently."""
        
        # Weight the different methods
        weights = {
            'fuzzy': 0.4,
            'semantic': 0.4,
            'value': 0.2
        }
        
        candidates = {}
        
        # Add fuzzy result
        if fuzzy_result and fuzzy_result.get('matched_type'):
            canonical = fuzzy_result['matched_type']
            if canonical not in candidates:
                candidates[canonical] = {'score': 0.0, 'methods': []}
            candidates[canonical]['score'] += fuzzy_result['confidence'] * weights['fuzzy']
            candidates[canonical]['methods'].append('fuzzy')
        
        # Add semantic result
        if semantic_result and semantic_result.get('matched_type'):
            canonical = semantic_result['matched_type']
            if canonical not in candidates:
                candidates[canonical] = {'score': 0.0, 'methods': []}
            candidates[canonical]['score'] += semantic_result['confidence'] * weights['semantic']
            candidates[canonical]['methods'].append('semantic')
        
        # Adjust based on value analysis
        for canonical, candidate_info in candidates.items():
            adjustment = self._get_value_adjustment(canonical, value_analysis)
            candidate_info['score'] += adjustment
            if adjustment != 0:
                candidate_info['methods'].append('value_analysis')
        
        # CRITICAL FIX: Handle specific column mapping conflicts
        mapped_column = self._resolve_column_conflicts(column_name, candidates, value_analysis)
        
        if mapped_column:
            # Get confidence for the resolved mapping
            if mapped_column in candidates:
                confidence = min(100.0, candidates[mapped_column]['score'])
                methods = '+'.join(candidates[mapped_column]['methods'])
            else:
                # Direct mapping based on column name patterns
                confidence = 95.0
                methods = 'direct_pattern_match'
        else:
            # Get best candidate from normal process
            if candidates:
                best_canonical = max(candidates.items(), key=lambda x: x[1]['score'])
                mapped_column = best_canonical[0]
                confidence = min(100.0, best_canonical[1]['score'])
                methods = '+'.join(best_canonical[1]['methods'])
            else:
                mapped_column = None
                confidence = 0.0
                methods = 'none'
        
        # Generate suggestions if confidence is low
        suggestions = []
        if confidence < self.confidence_threshold:
            suggestions = self._generate_suggestions(column_name, candidates, value_analysis)
        
        # Smart confidence threshold based on context
        effective_threshold = self._get_effective_threshold(column_name, candidates, value_analysis)
        
        # Determine status
        if confidence >= effective_threshold:
            status = 'mapped'
        elif confidence >= 50.0:
            status = 'uncertain'
        else:
            status = 'unmapped'
        
        return {
            'original_column': column_name,
            'mapped_column': mapped_column,
            'confidence': confidence,
            'method': methods,
            'status': status,
            'suggestions': suggestions,
            'value_analysis': value_analysis
        }
    
    def _get_value_adjustment(self, canonical: str, value_analysis: Dict) -> float:
        """Get confidence adjustment based on value analysis."""
        adjustment = 0.0
        patterns = value_analysis.get('patterns', [])
        
        # Boost confidence if patterns match
        pattern_matches = {
            'Date': ['date_like'],
            'Amount': ['numeric_like', 'currency_like'],
            'Sales': ['numeric_like', 'currency_like'],
            'Quantity': ['numeric_like'],
            'Product': ['id_like'],
            'Region': ['id_like'],
            # Legacy mappings for backward compatibility
            'date': ['date_like'],
            'price': ['numeric_like', 'currency_like'],
            'quantity': ['numeric_like'],
            'sales': ['numeric_like', 'currency_like'],
            'id': ['id_like'],
            'order_id': ['id_like'],
            'customer_id': ['id_like']
        }
        
        if canonical in pattern_matches:
            expected_patterns = pattern_matches[canonical]
            if any(pattern in patterns for pattern in expected_patterns):
                adjustment += 15.0  # Significant boost
        
        return adjustment
    
    def _get_effective_threshold(self, column_name: str, candidates: Dict, value_analysis: Dict) -> float:
        """Get effective confidence threshold based on context and data quality."""
        base_threshold = self.confidence_threshold
        col_lower = column_name.lower()
        
        # CRITICAL FIX: Much lower threshold for obvious mappings
        if col_lower in ['quantity', 'qty', 'amount', 'price', 'cost', 'revenue', 'sales', 'unit_price', 'unit price']:
            return 50.0  # Very low threshold for obvious numeric fields
        
        if col_lower in ['date', 'time', 'created', 'updated', 'timestamp']:
            return 50.0  # Very low threshold for obvious date fields
        
        if col_lower in ['product', 'item', 'name', 'title', 'description', 'product_id', 'product id']:
            return 55.0  # Low threshold for obvious categorical fields
        
        if col_lower in ['transaction_id', 'transaction id', 'order_id', 'order id']:
            return 50.0  # Low threshold for ID fields
        
        if col_lower in ['customer_id', 'customer id', 'client_id']:
            return 50.0  # Low threshold for customer ID fields
        
        if col_lower in ['brand', 'company', 'manufacturer']:
            return 55.0  # Low threshold for brand fields
        
        # Lower threshold if data analysis strongly supports the mapping
        if value_analysis.get('patterns'):
            patterns = value_analysis['patterns']
            if 'numeric_like' in patterns and any('numeric' in str(c).lower() for c in candidates.keys()):
                return base_threshold - 15.0
            if 'date_like' in patterns and any('date' in str(c).lower() for c in candidates.keys()):
                return base_threshold - 15.0
        
        # Lower threshold for high semantic similarity
        if candidates:
            best_candidate = max(candidates.items(), key=lambda x: x[1]['score'])
            if best_candidate[1]['score'] > 0.85:  # Very high semantic similarity
                return base_threshold - 20.0  # 50% for very high semantic similarity
        
        return base_threshold
    
    def _generate_suggestions(self, column_name: str, candidates: Dict, 
                            value_analysis: Dict) -> List[Dict]:
        """Generate mapping suggestions for uncertain columns."""
        suggestions = []
        
        # Sort candidates by score
        sorted_candidates = sorted(candidates.items(), key=lambda x: x[1]['score'], reverse=True)
        
        for canonical, info in sorted_candidates[:5]:  # Top 5 suggestions
            suggestions.append({
                'type': canonical,
                'confidence': min(100.0, info['score']),
                'reason': f"Matched by: {', '.join(info['methods'])}",
                'methods': info['methods']
            })
        
        # Add pattern-based suggestions
        patterns = value_analysis.get('patterns', [])
        if 'date_like' in patterns and not any(s['type'] == 'date' for s in suggestions):
            suggestions.append({
                'type': 'date',
                'confidence': 75,
                'reason': 'Values look like dates'
            })
        
        return suggestions[:5]  # Return top 5
    
    def _update_knowledge_base(self, mapped_columns: List[Dict]):
        """Update SQLite knowledge base with successful mappings."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for mapping in mapped_columns:
                if mapping['confidence'] >= self.confidence_threshold:
                    col_lower = mapping['original_column'].lower()
                    mapped_col = mapping['mapped_column']
                    confidence = mapping['confidence']
                    method = mapping['method']
                    timestamp = datetime.now().isoformat()
                    
                    # Insert or update mapping
                    cursor.execute('''
                        INSERT OR REPLACE INTO column_mappings 
                        (original_column, mapped_column, confidence, method, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (col_lower, mapped_col, confidence, method, timestamp, timestamp))
            
            conn.commit()
            conn.close()
            print(f"✅ Updated knowledge base with {len(mapped_columns)} mappings")
            
        except Exception as e:
            print(f"⚠️ Failed to update knowledge base: {e}")
    
    def _save_confirmation(self, column_name: str, mapped_type: str, confidence: float, 
                         user_id: str = None, feedback_score: int = 5):
        """Save user confirmation to knowledge base."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            col_lower = column_name.lower()
            
            # Insert confirmation
            cursor.execute('''
                INSERT INTO mapping_confirmations 
                (original_column, mapped_column, confidence, user_id, timestamp, feedback_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (col_lower, mapped_type, confidence, user_id, timestamp, feedback_score))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Failed to save confirmation: {e}")
    
    def confirm_mapping(self, column_name: str, mapped_type: str, 
                       user_confidence: float = 100.0, user_id: str = None) -> bool:
        """Record user confirmation of a column mapping."""
        try:
            self._save_confirmation(column_name, mapped_type, user_confidence, user_id)
            
            # Also update the main mappings table
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            col_lower = column_name.lower()
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO column_mappings 
                (original_column, mapped_column, confidence, method, created_at, updated_at)
                VALUES (?, ?, ?, 'user_confirmed', ?, ?)
            ''', (col_lower, mapped_type, user_confidence, timestamp, timestamp))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to confirm mapping: {e}")
            return False
    
    def get_mapping_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the mapping knowledge base."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total mappings
            cursor.execute('SELECT COUNT(*) FROM column_mappings')
            total_mappings = cursor.fetchone()[0]
            
            # Get total confirmations
            cursor.execute('SELECT COUNT(*) FROM mapping_confirmations')
            total_confirmations = cursor.fetchone()[0]
            
            # Get average confidence
            cursor.execute('SELECT AVG(confidence) FROM column_mappings')
            avg_confidence = cursor.fetchone()[0] or 0
            
            # Get method distribution
            cursor.execute('SELECT method, COUNT(*) FROM column_mappings GROUP BY method')
            method_distribution = dict(cursor.fetchall())
            
            # Get most common mappings
            cursor.execute('''
                SELECT mapped_column, COUNT(*) as count 
                FROM column_mappings 
                GROUP BY mapped_column 
                ORDER BY count DESC 
                LIMIT 10
            ''')
            most_common_types = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_mappings': total_mappings,
                'total_confirmations': total_confirmations,
                'average_confidence': round(avg_confidence, 2),
                'method_distribution': method_distribution,
                'most_common_types': most_common_types,
                'semantic_enabled': self.semantic_enabled,
                'database_path': self.db_path
            }
            
        except Exception as e:
            print(f"⚠️ Failed to get statistics: {e}")
            return {}
    
    def export_knowledge_base(self, output_path: str = "knowledge_base_export.json") -> bool:
        """Export knowledge base to JSON for backup or sharing."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Export mappings
            mappings_df = pd.read_sql_query('SELECT * FROM column_mappings', conn)
            confirmations_df = pd.read_sql_query('SELECT * FROM mapping_confirmations', conn)
            
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'mappings': mappings_df.to_dict('records'),
                'confirmations': confirmations_df.to_dict('records'),
                'statistics': self.get_mapping_statistics()
            }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            conn.close()
            print(f"✅ Knowledge base exported to {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to export knowledge base: {e}")
            return False
    
    def get_dropdown_options(self) -> List[str]:
        """
        Get the list of dropdown options for column mapping.
        Returns the 5 required columns + Ignore option.
        
        Returns:
            List of column type options
        """
        try:
            from analytics_config import get_dropdown_options
            return get_dropdown_options()
        except ImportError:
            return ['Date', 'Sales', 'Amount', 'Product', 'Quantity', 'Region', 'Ignore']
    
    def get_knowledge_base_stats(self) -> int:
        """Get the size of the knowledge base."""
        try:
            stats = self.get_mapping_statistics()
            return stats.get('total_mappings', 0)
        except:
            return 0

