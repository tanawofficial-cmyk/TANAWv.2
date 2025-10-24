"""
Flexible Column Mapper for TANAW
Implements intelligent, adaptive column mapping with:
- Automatic column detection with confidence scoring
- Same-thought column detection (Product vs Product_ID)
- Dynamic dropdown generation
- Learning from user confirmations
- Intelligent "Ignore" handling
- Dynamic analytics determination
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass
from collections import defaultdict
import sqlite3
import json
import re
import time
from datetime import datetime
from difflib import SequenceMatcher

# Try to import optional dependencies
try:
    from rapidfuzz import fuzz, process as fuzz_process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False

# Import Phase 2 components
from header_normalizer import HeaderNormalizer, normalize_headers, HeaderNormalizationResult

# Import Phase 3 components
from value_analyzer import ValueAnalyzer, analyze_values, ValueAnalysisResult

# Import Phase 4 components
from gpt_escalation import GPTEscalation, escalate_columns, GPTEscalationResult

# Import Phase 5 components
from mapping_merger import MappingMerger, merge_mappings_and_rename, MappingMergeResult

# Import Phase 6 components
from data_cleaner import DataCleaner, clean_data, DataCleaningResult

# Import Phase 7 components
from analytics_executor import AnalyticsExecutor, execute_analytics, AnalyticsExecutionResult

# Import Phase 8 components
from visualization_generator import VisualizationGenerator, generate_visualizations, VisualizationResult

# Import Phase 9 components
from knowledge_base import KnowledgeBase, record_user_confirmation, get_user_mappings, KBResult

# Import Phase 10 components
from cache_manager import CacheManager, cache_analytics_output, get_cached_analytics, queue_background_job, CacheResult, JobResult

# Import Phase 11 components
from ux_remediation import UXRemediation, generate_error_messages, create_remap_ui, create_sanitized_sample, UXResult


@dataclass
class ColumnSuggestion:
    """Represents a mapping suggestion for a column."""
    canonical_type: str
    confidence: float
    method: str
    reasoning: str


@dataclass
class ColumnGroup:
    """Represents a group of same-thought columns."""
    columns: List[str]
    suggested_type: str
    confidence: float
    primary_column: str  # The recommended column to use
    action: str  # 'select_primary', 'merge', 'ignore_duplicates'
    reasoning: str


class FlexibleColumnMapper:
    """
    Advanced column mapper that handles diverse datasets with intelligence.
    """
    
    def __init__(self, db_path: str = "tanaw_column_knowledge.db"):
        self.db_path = db_path
        self.confidence_threshold = 70.0  # Lower threshold for flexibility
        
        # CORE TANAW column types (simplified for 5 core analytics)
        # Only these 5 types are required for all TANAW analytics
        self.canonical_types = [
            'Date',      # Time series data (required for all forecasting)
            'Sales',     # Monetary values (Sales, Amount, Revenue, Sales_Amount)
            'Product',   # Product identifiers (Product, Product_ID, Product_Category, Product_Name)
            'Region',    # Geographic locations (Region, Location, Store, City, Country)
            'Quantity'   # Volume metrics (Quantity, Quantity_Sold, Units, Demand)
        ]
        
        # Initialize knowledge base
        self._init_knowledge_base()
        
        # Initialize Phase 2 header normalizer
        self.header_normalizer = HeaderNormalizer()
        print("✅ Phase 2: Header normalizer initialized")
        
        # Initialize Phase 3 value analyzer
        self.value_analyzer = ValueAnalyzer()
        print("✅ Phase 3: Value analyzer initialized")
        
        # Initialize Phase 4 GPT escalation
        self.gpt_escalation = GPTEscalation()
        print("✅ Phase 4: GPT escalation initialized")
        
        # Initialize Phase 5 mapping merger
        self.mapping_merger = MappingMerger()
        print("✅ Phase 5: Mapping merger initialized")
        
        # Initialize Phase 6 data cleaner
        self.data_cleaner = DataCleaner()
        print("✅ Phase 6: Data cleaner initialized")
        
        # Initialize Phase 7 analytics executor
        self.analytics_executor = AnalyticsExecutor()
        print("✅ Phase 7: Analytics executor initialized")
        
        # Initialize Phase 8 visualization generator
        self.visualization_generator = VisualizationGenerator()
        print("✅ Phase 8: Visualization generator initialized")
        
        # Initialize Phase 9 knowledge base
        self.knowledge_base = KnowledgeBase()
        print("✅ Phase 9: Knowledge base initialized")
        
        # Initialize Phase 10 cache manager
        self.cache_manager = CacheManager()
        print("✅ Phase 10: Cache manager initialized")
        
        # Initialize Phase 11 UX remediation
        self.ux_remediation = UXRemediation()
        print("✅ Phase 11: UX remediation initialized")
        
        # Initialize semantic model (optional)
        self.semantic_model = None
        if SBERT_AVAILABLE:
            try:
                self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Semantic similarity enabled (SBERT)")
            except Exception as e:
                print(f"⚠️ Semantic model initialization failed: {e}")
        
        # Initialize pattern recognizers
        self._init_pattern_recognizers()
        
    def _init_knowledge_base(self):
        """Initialize SQLite knowledge base for learning."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table for learned mappings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learned_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_column TEXT NOT NULL,
                    canonical_type TEXT NOT NULL,
                    confidence REAL DEFAULT 100.0,
                    user_confirmed BOOLEAN DEFAULT 1,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    dataset_context TEXT,
                    usage_count INTEGER DEFAULT 1
                )
            ''')
            
            # Table for ignored patterns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ignored_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    column_pattern TEXT NOT NULL,
                    reason TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(column_pattern)
                )
            ''')
            
            # Table for same-thought column groups
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS column_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_signature TEXT NOT NULL,
                    columns TEXT NOT NULL,
                    recommended_action TEXT,
                    primary_column TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table for analytics requirements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analytic_name TEXT NOT NULL,
                    required_columns TEXT NOT NULL,
                    optional_columns TEXT,
                    priority INTEGER DEFAULT 1
                )
            ''')
            
            # Create indexes
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_learned_mappings_column 
                ON learned_mappings(original_column)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_ignored_patterns_column 
                ON ignored_patterns(column_pattern)
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Knowledge base initialized")
            
        except Exception as e:
            print(f"⚠️ Knowledge base initialization failed: {e}")
    
    def _init_pattern_recognizers(self):
        """Initialize pattern recognition rules."""
        
        # Date patterns
        self.date_patterns = [
            r'date', r'time', r'timestamp', r'dt', r'day', r'month', r'year',
            r'fecha', r'datum', r'created', r'modified', r'updated', r'posted'
        ]
        
        # Sales/Amount patterns (STRICT - only actual monetary values)
        self.sales_patterns = [
            r'sales?_amount', r'sales?_value', r'revenue', r'amount', r'total_sales?',
            r'sales?_total', r'value', r'earn', r'income', r'proceeds', r'receipts',
            r'total_amount', r'gross_sales?'
        ]
        
        # Patterns that should NOT be mapped to Sales (exclusion list)
        self.not_sales_patterns = [
            r'sales?_rep', r'sales?_person', r'sales?_man', r'sales?_channel',
            r'sales?_team', r'sales?_office', r'rep', r'channel', r'method',
            r'staff', r'employee', r'worker', r'team', r'group', r'agent',
            r'person', r'representative', r'manager', r'director',
            r'sales?_id', r'sales?_code', r'sales?_name', r'sales?_type',
            r'sales?_category', r'sales?_status', r'sales?_level'
        ]
        
        # Product patterns - prioritize category over ID
        self.product_patterns = [
            r'product.*category', r'product.*type', r'product.*name', r'category',
            r'item.*type', r'item.*category', r'goods?.*type', r'merchandise.*type',
            r'catalog.*type', r'modelo.*tipo', r'articulo.*tipo'
        ]
        
        # Product ID patterns (should be lower priority)
        self.product_id_patterns = [
            r'product.*id', r'item.*id', r'sku', r'article.*id', r'goods?.*id',
            r'catalog.*id', r'modelo.*id', r'articulo.*id'
        ]
        
        # Quantity patterns (STRICT - only actual quantity/volume metrics)
        self.quantity_patterns = [
            r'qty', r'quantity', r'quantity_sold', r'qty_sold', 
            r'volume', r'pieces?', r'cantidad', r'sold$', r'ordered$',
            r'^units_sold', r'^qty_', r'^quantity_'
        ]
        
        # Patterns that should NOT be mapped to Quantity (exclusion list)
        self.not_quantity_patterns = [
            r'unit_cost', r'unit_price', r'unit_value', r'discount', 
            r'price', r'cost', r'amount', r'value'
        ]
        
        # Region/Location patterns (STRICT - only actual geographic locations)
        self.region_patterns = [
            r'^region$', r'^location$', r'^city$', r'^state$', r'^country$', 
            r'^territory$', r'^area$', r'^zone$', r'^district$',
            r'^store$', r'^branch$', r'^outlet$', r'^market$'
        ]
        
        # Patterns that should NOT be mapped to Region (exclusion list)
        self.not_region_patterns = [
            r'sales?_rep', r'payment', r'channel', r'method', r'type',
            r'customer', r'discount', r'_and_', r'composite'
        ]
        
        # ID patterns (often secondary to descriptive columns)
        self.id_patterns = [
            r'_id$', r'id$', r'^id_', r'code', r'number', r'num', r'#'
        ]
        
        # Patterns indicating columns to potentially ignore
        self.ignore_hints = [
            r'unnamed', r'index', r'row', r'serial', r'sequence', r'^_', 
            r'temp', r'tmp', r'test', r'debug', r'internal'
        ]
    
    def map_columns(self, df: pd.DataFrame, 
                   user_confirmed: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Main mapping function with intelligent suggestions.
        
        Args:
            df: DataFrame to analyze
            user_confirmed: User-confirmed mappings from previous step
            
        Returns:
            Comprehensive mapping results with suggestions and groupings
        """
        print(f"\n🗺️ Starting Flexible Column Mapping")
        print(f"   Dataset: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"   Columns: {list(df.columns)}")
        
        results = {
            'mapped_columns': [],
            'uncertain_columns': [],
            'unmapped_columns': [],
            'column_groups': [],
            'ignored_columns': [],
            'requires_confirmation': False,
            'confidence_scores': {},
            'dropdown_options': self._get_dropdown_options(),
            'analytics_readiness': {},
            'phase2_normalization': {},  # Phase 2 header normalization results
            'phase3_value_analysis': {},  # Phase 3 value analysis results
            'phase4_gpt_escalation': {},  # Phase 4 GPT escalation results
            'phase5_mapping_merge': {},  # Phase 5 mapping merge results
            'phase6_data_cleaning': {},  # Phase 6 data cleaning results
            'phase7_analytics_execution': {},  # Phase 7 analytics execution results
            'phase8_visualization': {},  # Phase 8 visualization and narrative results
            'phase9_knowledge_base': {},  # Phase 9 knowledge base results
            'phase10_caching': {},  # Phase 10 caching and background jobs results
            'phase11_ux_remediation': {}  # Phase 11 UX remediation and error messages results
        }
        
        # Phase 2: Header normalization and candidate generation
        print(f"🔍 Phase 2: Normalizing headers and generating candidates")
        try:
            normalization_result = self.header_normalizer.normalize_headers(list(df.columns))
            if normalization_result.success:
                results['phase2_normalization'] = {
                    'normalized_headers': {k: {
                        'normalized': v.normalized_header,
                        'best_candidate': v.best_candidate.canonical_type if v.best_candidate else None,
                        'confidence': v.best_candidate.confidence if v.best_candidate else 0.0,
                        'source': v.best_candidate.source if v.best_candidate else None
                    } for k, v in normalization_result.normalized_headers.items()},
                    'processing_time_ms': normalization_result.processing_time_seconds * 1000,
                    'metrics': normalization_result.metrics
                }
                print(f"✅ Phase 2: Normalized {len(normalization_result.normalized_headers)} headers")
            else:
                print(f"⚠️ Phase 2: Header normalization failed: {normalization_result.error_message}")
        except Exception as e:
            print(f"⚠️ Phase 2: Header normalization error: {e}")
        
        # Phase 3: Value sampling and local inference
        print(f"🔍 Phase 3: Analyzing column values and performing local inference")
        try:
            # Get header candidates from Phase 2
            header_candidates = {}
            if 'phase2_normalization' in results and 'normalized_headers' in results['phase2_normalization']:
                for col, norm_data in results['phase2_normalization']['normalized_headers'].items():
                    if norm_data.get('best_candidate'):
                        header_candidates[col] = [{
                            'canonical_type': norm_data['best_candidate'],
                            'score': norm_data['confidence'] / 100.0,
                            'source': norm_data['source']
                        }]
            
            # Perform value analysis
            value_analysis_result = self.value_analyzer.analyze_values(df, header_candidates)
            if value_analysis_result.success:
                results['phase3_value_analysis'] = {
                    'column_inferences': {k: {
                        'best_candidate': v.best_candidate,
                        'local_confidence': v.local_confidence,
                        'weighted_score': v.weighted_score,
                        'signals': {
                            'numeric_pct': v.signals.numeric_pct,
                            'date_pct': v.signals.date_pct,
                            'currency_pct': v.signals.currency_pct,
                            'unique_pct': v.signals.unique_pct,
                            'id_pattern_pct': v.signals.id_pattern_pct,
                            'region_geo_pct': v.signals.region_geo_pct,
                            'sku_pattern_pct': v.signals.sku_pattern_pct,
                            'sample_size': v.signals.sample_size
                        },
                        'reasoning': v.reasoning
                    } for k, v in value_analysis_result.column_inferences.items()},
                    'processing_time_ms': value_analysis_result.processing_time_seconds * 1000,
                    'metrics': value_analysis_result.metrics
                }
                print(f"✅ Phase 3: Analyzed {len(value_analysis_result.column_inferences)} columns")
            else:
                print(f"⚠️ Phase 3: Value analysis failed: {value_analysis_result.error_message}")
        except Exception as e:
            print(f"⚠️ Phase 3: Value analysis error: {e}")
        
        # Phase 4: GPT Escalation for low-confidence columns
        print(f"🔍 Phase 4: Escalating low-confidence columns to GPT")
        try:
            # Get Phase 3 results for escalation
            phase3_results = results.get('phase3_value_analysis', {})
            column_inferences = phase3_results.get('column_inferences', {})
            
            if column_inferences:
                # Escalate columns with low confidence
                escalation_result = self.gpt_escalation.escalate_columns(
                    column_inferences, 
                    local_confidence_threshold=75.0
                )
                
                if escalation_result.success:
                    results['phase4_gpt_escalation'] = {
                        'escalated_columns': {k: {
                            'mapped_to': v.mapped_to,
                            'confidence': v.confidence,
                            'reason': v.reason,
                            'source': 'gpt'
                        } for k, v in escalation_result.escalated_columns.items()},
                        'local_fallbacks': escalation_result.local_fallbacks,
                        'processing_time_ms': escalation_result.processing_time_seconds * 1000,
                        'metrics': escalation_result.metrics
                    }
                    print(f"✅ Phase 4: Escalated {len(escalation_result.escalated_columns)} columns to GPT")
                    print(f"✅ Phase 4: {len(escalation_result.local_fallbacks)} local fallbacks")
                else:
                    print(f"⚠️ Phase 4: GPT escalation failed: {escalation_result.error_message}")
            else:
                print("⚠️ Phase 4: No column inferences available for escalation")
        except Exception as e:
            print(f"⚠️ Phase 4: GPT escalation error: {e}")
        
        # Phase 5: Merge mappings and apply canonical rename
        print(f"🔍 Phase 5: Merging mappings and applying canonical rename")
        try:
            # Collect all phase results for merging
            phase_results = {
                'phase2_normalization': results.get('phase2_normalization', {}),
                'phase3_value_analysis': results.get('phase3_value_analysis', {}),
                'phase4_gpt_escalation': results.get('phase4_gpt_escalation', {})
            }
            
            # Apply mapping merge and canonical rename
            merge_result = self.mapping_merger.merge_mappings_and_rename(
                df, phase_results, user_confirmed
            )
            
            if merge_result.success:
                results['phase5_mapping_merge'] = {
                    'final_mappings': merge_result.final_mappings,
                    'collision_resolutions': [
                        {
                            'original_column': r.original_column,
                            'canonical_name': r.canonical_name,
                            'alias_suffix': r.alias_suffix,
                            'resolution_reason': r.resolution_reason
                        } for r in merge_result.collision_resolutions
                    ],
                    'canonical_columns': merge_result.canonical_columns,
                    'processing_time_ms': merge_result.processing_time_seconds * 1000,
                    'metrics': merge_result.metrics
                }
                
                # Update DataFrame with canonical names
                df = self.mapping_merger._apply_canonical_rename(df, merge_result.final_mappings)
                
                print(f"✅ Phase 5: Merged {len(merge_result.final_mappings)} mappings")
                print(f"✅ Phase 5: Resolved {len(merge_result.collision_resolutions)} collisions")
                print(f"✅ Phase 5: Applied canonical rename to DataFrame")
            else:
                print(f"⚠️ Phase 5: Mapping merge failed: {merge_result.error_message}")
        except Exception as e:
            print(f"⚠️ Phase 5: Mapping merge error: {e}")
        
        # Phase 6: Data cleaning (post-rename)
        print(f"🔍 Phase 6: Cleaning data for canonical columns")
        try:
            # Get canonical columns from Phase 5
            canonical_columns = []
            if 'phase5_mapping_merge' in results and 'canonical_columns' in results['phase5_mapping_merge']:
                canonical_columns = results['phase5_mapping_merge']['canonical_columns']
            else:
                # Fallback to standard canonical columns
                canonical_columns = ['Date', 'Sales', 'Amount', 'Product', 'Quantity', 'Region', 'Customer', 'Transaction_ID']
            
            # Apply data cleaning
            cleaning_result = self.data_cleaner.clean_data(df, canonical_columns)
            
            if cleaning_result.success:
                results['phase6_data_cleaning'] = {
                    'cleaning_results': {k: {
                        'original_type': v.original_type,
                        'cleaned_type': v.cleaned_type,
                        'null_count': v.null_count,
                        'null_percentage': v.null_percentage,
                        'duplicates_count': v.duplicates_count,
                        'outliers_count': v.outliers_count,
                        'quality_score': v.quality_score,
                        'cleaning_applied': v.cleaning_applied,
                        'warnings': v.warnings
                    } for k, v in cleaning_result.cleaning_results.items()},
                    'processing_time_ms': cleaning_result.processing_time_seconds * 1000,
                    'metrics': cleaning_result.metrics
                }
                
                # Update DataFrame with cleaned data
                df = cleaning_result.cleaned_df
                
                print(f"✅ Phase 6: Cleaned {len(cleaning_result.cleaning_results)} columns")
                print(f"✅ Phase 6: Applied {cleaning_result.metrics.get('type_conversions', 0)} type conversions")
                print(f"✅ Phase 6: Detected {cleaning_result.metrics.get('outliers_detected', 0)} outliers")
            else:
                print(f"⚠️ Phase 6: Data cleaning failed: {cleaning_result.error_message}")
        except Exception as e:
            print(f"⚠️ Phase 6: Data cleaning error: {e}")
        
        # Phase 7: Analytics readiness and execution
        print(f"🔍 Phase 7: Checking analytics readiness and executing analytics")
        try:
            # Get cleaning results from Phase 6
            cleaning_results = {}
            if 'phase6_data_cleaning' in results and 'cleaning_results' in results['phase6_data_cleaning']:
                cleaning_results = results['phase6_data_cleaning']['cleaning_results']
            
            # Execute analytics
            analytics_result = self.analytics_executor.execute_analytics(df, cleaning_results)
            
            if analytics_result.success:
                results['phase7_analytics_execution'] = {
                    'analytics_results': {k: {
                        'mode': v.mode,
                        'success': v.success,
                        'result_data': v.result_data,
                        'execution_time_seconds': v.execution_time_seconds,
                        'fallback_used': v.fallback_used,
                        'error_message': v.error_message
                    } for k, v in analytics_result.analytics_results.items()},
                    'processing_time_ms': analytics_result.processing_time_seconds * 1000,
                    'metrics': analytics_result.metrics
                }
                
                # Update analytics readiness
                results['analytics_readiness'] = {
                    'ready_analytics': [k for k, v in analytics_result.analytics_results.items() if v.success],
                    'failed_analytics': [k for k, v in analytics_result.analytics_results.items() if not v.success],
                    'fallback_analytics': [k for k, v in analytics_result.analytics_results.items() if v.fallback_used],
                    'total_analytics': len(analytics_result.analytics_results),
                    'success_rate': len([v for v in analytics_result.analytics_results.values() if v.success]) / len(analytics_result.analytics_results) * 100 if analytics_result.analytics_results else 0
                }
                
                print(f"✅ Phase 7: Executed {len([v for v in analytics_result.analytics_results.values() if v.success])} analytics")
                print(f"✅ Phase 7: {len([v for v in analytics_result.analytics_results.values() if v.fallback_used])} used fallbacks")
                print(f"✅ Phase 7: Analytics success rate: {results['analytics_readiness']['success_rate']:.1f}%")
            else:
                print(f"⚠️ Phase 7: Analytics execution failed: {analytics_result.error_message}")
        except Exception as e:
            print(f"⚠️ Phase 7: Analytics execution error: {e}")
        
        # Phase 8: Visualization and narrative generation
        print(f"🔍 Phase 8: Generating visualizations and narratives")
        try:
            # Get analytics results from Phase 7
            analytics_results = {}
            if 'phase7_analytics_execution' in results and 'analytics_results' in results['phase7_analytics_execution']:
                analytics_results = results['phase7_analytics_execution']['analytics_results']
            
            # Get analytics readiness
            analytics_readiness = results.get('analytics_readiness', {})
            
            # Generate visualizations and narratives
            visualization_result = self.visualization_generator.generate_visualizations(
                analytics_results, analytics_readiness
            )
            
            if visualization_result.success:
                results['phase8_visualization'] = {
                    'charts': {k: {
                        'chart_type': v.chart_type,
                        'title': v.title,
                        'x_axis': v.x_axis,
                        'y_axis': v.y_axis,
                        'series': v.series,
                        'meta': v.meta,
                        'alt_text': v.alt_text,
                        'description': v.description
                    } for k, v in visualization_result.charts.items()},
                    'narratives': {k: {
                        'narrative_type': v.narrative_type,
                        'content': v.content,
                        'confidence': v.confidence,
                        'generation_time_seconds': v.generation_time_seconds,
                        'success': v.success,
                        'error_message': v.error_message
                    } for k, v in visualization_result.narratives.items()},
                    'csv_fallbacks': visualization_result.csv_fallbacks,
                    'processing_time_ms': visualization_result.processing_time_seconds * 1000,
                    'metrics': visualization_result.metrics
                }
                
                print(f"✅ Phase 8: Generated {len(visualization_result.charts)} charts")
                print(f"✅ Phase 8: Generated {len(visualization_result.narratives)} narratives")
                print(f"✅ Phase 8: Created {len(visualization_result.csv_fallbacks)} CSV fallbacks")
            else:
                print(f"⚠️ Phase 8: Visualization generation failed: {visualization_result.error_message}")
        except Exception as e:
            print(f"⚠️ Phase 8: Visualization generation error: {e}")
        
        # Phase 9: Knowledge Base operations
        print(f"🔍 Phase 9: Recording mappings and updating knowledge base")
        try:
            # Record user confirmations in knowledge base
            kb_operations = []
            user_id = "default_user"  # In a real implementation, this would come from user context
            
            if user_confirmed:
                for original_header, canonical in user_confirmed.items():
                    if canonical.lower() != 'ignore':
                        kb_result = self.knowledge_base.record_user_confirmation(
                            user_id, original_header, canonical, "USER"
                        )
                        kb_operations.append({
                            'original_header': original_header,
                            'canonical': canonical,
                            'success': kb_result.success,
                            'operation': 'user_confirmation'
                        })
            
            # Get user mappings for future auto-mapping
            user_mappings = self.knowledge_base.get_user_mappings(user_id)
            
            # Perform confidence decay
            decay_result = self.knowledge_base.decay_confidence()
            
            results['phase9_knowledge_base'] = {
                'kb_operations': kb_operations,
                'user_mappings_count': len(user_mappings.entries) if user_mappings.success else 0,
                'decay_operation': {
                    'success': decay_result.success,
                    'processing_time_seconds': decay_result.processing_time_seconds
                },
                'processing_time_ms': (user_mappings.processing_time_seconds + decay_result.processing_time_seconds) * 1000,
                'metrics': self.knowledge_base.get_metrics()
            }
            
            print(f"✅ Phase 9: Recorded {len(kb_operations)} KB operations")
            print(f"✅ Phase 9: Found {len(user_mappings.entries) if user_mappings.success else 0} user mappings")
            print(f"✅ Phase 9: Confidence decay {'successful' if decay_result.success else 'failed'}")
        except Exception as e:
            print(f"⚠️ Phase 9: Knowledge base error: {e}")
        
        # Phase 10: Caching and background jobs
        print(f"🔍 Phase 10: Caching analytics outputs and managing background jobs")
        try:
            # Generate analysis ID for caching
            analysis_id = f"analysis_{int(time.time())}_{hash(str(df.columns.tolist()))}"
            
            # Check if we have cached results
            cached_result = self.cache_manager.get_cached_analytics(analysis_id)
            
            if cached_result.success and cached_result.cache_hit:
                # Use cached results
                results['phase10_caching'] = {
                    'cache_hit': True,
                    'analysis_id': analysis_id,
                    'cached_data': cached_result.data,
                    'processing_time_ms': cached_result.processing_time_seconds * 1000,
                    'metrics': self.cache_manager.get_metrics()
                }
                print(f"✅ Phase 10: Using cached results for analysis {analysis_id}")
            else:
                # Cache current results
                cache_data = {
                    'phase2_normalization': results.get('phase2_normalization', {}),
                    'phase3_value_analysis': results.get('phase3_value_analysis', {}),
                    'phase4_gpt_escalation': results.get('phase4_gpt_escalation', {}),
                    'phase5_mapping_merge': results.get('phase5_mapping_merge', {}),
                    'phase6_data_cleaning': results.get('phase6_data_cleaning', {}),
                    'phase7_analytics_execution': results.get('phase7_analytics_execution', {}),
                    'phase8_visualization': results.get('phase8_visualization', {}),
                    'phase9_knowledge_base': results.get('phase9_knowledge_base', {})
                }
                
                cache_metadata = {
                    'file_columns': df.columns.tolist(),
                    'file_shape': df.shape,
                    'processing_timestamp': datetime.now().isoformat(),
                    'user_confirmations': user_confirmed or {}
                }
                
                cache_result = self.cache_manager.cache_analytics_output(analysis_id, cache_data, cache_metadata)
                
                # Queue background jobs for heavy tasks
                background_jobs = []
                
                # Queue full file re-run job
                rerun_job = self.cache_manager.queue_background_job(
                    'full_file_rerun', analysis_id, {'file_path': 'current_file'}, priority=3
                )
                if rerun_job.success:
                    background_jobs.append(rerun_job.job_id)
                
                # Queue KB reconciliation job
                kb_job = self.cache_manager.queue_background_job(
                    'kb_reconciliation', analysis_id, {'user_id': 'default_user'}, priority=2
                )
                if kb_job.success:
                    background_jobs.append(kb_job.job_id)
                
                # Queue GPT re-evaluation job if needed
                if results.get('phase4_gpt_escalation', {}).get('low_confidence_columns'):
                    gpt_job = self.cache_manager.queue_background_job(
                        'gpt_reevaluation', analysis_id, {
                            'low_confidence_columns': results['phase4_gpt_escalation']['low_confidence_columns']
                        }, priority=1
                    )
                    if gpt_job.success:
                        background_jobs.append(gpt_job.job_id)
                
                results['phase10_caching'] = {
                    'cache_hit': False,
                    'analysis_id': analysis_id,
                    'cache_result': {
                        'success': cache_result.success,
                        'processing_time_seconds': cache_result.processing_time_seconds
                    },
                    'background_jobs': background_jobs,
                    'processing_time_ms': cache_result.processing_time_seconds * 1000,
                    'metrics': self.cache_manager.get_metrics()
                }
                
                print(f"✅ Phase 10: Cached results for analysis {analysis_id}")
                print(f"✅ Phase 10: Queued {len(background_jobs)} background jobs")
        except Exception as e:
            print(f"⚠️ Phase 10: Caching error: {e}")
        
        # Phase 11: UX Remediation and Error Messages
        print(f"🔍 Phase 11: Generating error messages and remediation paths")
        try:
            # Generate meaningful error messages and remediation options
            ux_result = self.ux_remediation.generate_error_messages(results)
            
            if ux_result.success:
                # Create remap UI for low confidence mappings
                remap_ui = None
                if ux_result.error_messages:
                    low_confidence_columns = []
                    for msg in ux_result.error_messages:
                        if msg.error_type == 'low_confidence_mapping':
                            low_confidence_columns = msg.context.get('low_confidence_columns', [])
                            break
                    
                    if low_confidence_columns:
                        column_mapping = {col['original_column']: col['mapped_column'] for col in low_confidence_columns}
                        available_columns = [col['original_column'] for col in low_confidence_columns]
                        remap_ui = self.ux_remediation.create_remap_ui(column_mapping, available_columns)
                
                # Create sanitized sample if needed
                sanitized_sample = None
                if ux_result.error_messages:
                    for msg in ux_result.error_messages:
                        if msg.error_type == 'parse_failure':
                            issues = msg.context.get('parse_errors', [])
                            if issues:
                                sanitized_sample = self.ux_remediation.create_sanitized_sample(df, issues)
                            break
                
                results['phase11_ux_remediation'] = {
                    'error_messages': [
                        {
                            'error_type': msg.error_type,
                            'severity': msg.severity,
                            'title': msg.title,
                            'message': msg.message,
                            'actionable_steps': msg.actionable_steps,
                            'remediation_options': [
                                {
                                    'option_id': opt.option_id,
                                    'title': opt.title,
                                    'description': opt.description,
                                    'action_type': opt.action_type,
                                    'confidence': opt.confidence,
                                    'one_click': opt.one_click
                                } for opt in msg.remediation_options
                            ],
                            'context': msg.context
                        } for msg in ux_result.error_messages
                    ],
                    'remediation_options': [
                        {
                            'option_id': opt.option_id,
                            'title': opt.title,
                            'description': opt.description,
                            'action_type': opt.action_type,
                            'confidence': opt.confidence,
                            'one_click': opt.one_click
                        } for opt in ux_result.remediation_options
                    ],
                    'remap_ui': remap_ui,
                    'sanitized_sample': sanitized_sample,
                    'processing_time_ms': ux_result.processing_time_seconds * 1000,
                    'metrics': self.ux_remediation.get_metrics()
                }
                
                print(f"✅ Phase 11: Generated {len(ux_result.error_messages)} error messages")
                print(f"✅ Phase 11: Provided {len(ux_result.remediation_options)} remediation options")
                if remap_ui:
                    print(f"✅ Phase 11: Created remap UI for {len(remap_ui.get('remap_options', {}))} columns")
                if sanitized_sample:
                    print(f"✅ Phase 11: Created sanitized sample")
            else:
                print(f"⚠️ Phase 11: UX remediation failed: {ux_result.error_message}")
        except Exception as e:
            print(f"⚠️ Phase 11: UX remediation error: {e}")
        
        # Track all column mappings
        all_mappings = {}
        
        # Process each column
        for col in df.columns:
            # Check if user already confirmed this column
            if user_confirmed and col in user_confirmed:
                confirmed_type = user_confirmed[col]
                
                if confirmed_type.lower() == 'ignore':
                    results['ignored_columns'].append({
                        'original_column': col,
                        'reason': 'User selected to ignore',
                        'confidence': 100.0
                    })
                    self._save_ignored_pattern(col, "User ignored")
                else:
                    results['mapped_columns'].append({
                        'original_column': col,
                        'mapped_column': confirmed_type,
                        'confidence': 100.0,
                        'method': 'user_confirmed',
                        'status': 'mapped'
                    })
                    all_mappings[col] = confirmed_type
                    self._save_learned_mapping(col, confirmed_type, 100.0, user_confirmed=True)
                continue
            
            # Analyze the column
            suggestions = self._analyze_column(col, df[col])
            
            if not suggestions:
                # No suggestions - check if it's an excluded column
                col_lower = col.lower()
                strict_exclusion_keywords = [
                    'unit_cost', 'unit_price', 'unit_value', 'price_per', 'cost_per',
                    'per_unit', 'each_price', 'each_cost', 'item_price', 'item_cost',
                    'discount', 'margin', 'markup', 'sales_rep', 'rep',
                    'representative', 'person'
                ]
                
                if any(keyword in col_lower for keyword in strict_exclusion_keywords):
                    # Excluded column - mark as uncertain with Ignore suggestion
                    results['uncertain_columns'].append({
                        'original_column': col,
                        'column': col,  # For backward compatibility
                        'mapped_column': 'Ignore',
                        'detectedType': self._detect_data_type(df[col]),
                        'confidence': 0.0,
                        'reasoning': f'Column "{col}" matches exclusion pattern and should be ignored',
                        'suggestions': [
                            {
                                'type': 'Ignore',
                                'confidence': 100.0,
                                'reasoning': f'Column "{col}" should be ignored (matches exclusion pattern)'
                            }
                        ],
                        'status': 'uncertain'
                    })
                else:
                    # Truly unmapped - mark as unmapped
                    results['unmapped_columns'].append({
                        'original_column': col,
                        'reason': 'No confident match found',
                        'suggestions': []
                    })
                results['requires_confirmation'] = True
                continue
            
            # Get best suggestion
            best_suggestion = suggestions[0]
            
            # Determine mapping status based on confidence
            if best_suggestion.confidence >= self.confidence_threshold:
                # High confidence - auto-map
                results['mapped_columns'].append({
                    'original_column': col,
                    'mapped_column': best_suggestion.canonical_type,
                    'confidence': best_suggestion.confidence,
                    'method': best_suggestion.method,
                    'reasoning': best_suggestion.reasoning,
                    'status': 'mapped',
                    'suggestions': [
                        {
                            'type': s.canonical_type,
                            'confidence': s.confidence,
                            'reasoning': s.reasoning
                        } for s in suggestions[:3]
                    ]
                })
                all_mappings[col] = best_suggestion.canonical_type
                results['confidence_scores'][col] = best_suggestion.confidence
            else:
                # Low confidence - require user confirmation
                results['uncertain_columns'].append({
                    'original_column': col,
                    'column': col,  # For backward compatibility
                    'mapped_column': best_suggestion.canonical_type,
                    'detectedType': self._detect_data_type(df[col]),
                    'confidence': best_suggestion.confidence,
                    'reasoning': best_suggestion.reasoning,
                    'suggestions': [
                        {
                            'type': s.canonical_type,
                            'confidence': s.confidence,
                            'reasoning': s.reasoning
                        } for s in suggestions[:5]
                    ],
                    'status': 'uncertain'
                })
                results['requires_confirmation'] = True
        
        # Detect same-thought column groups (both from mappings and uncertain columns)
        # This should happen BEFORE user confirmation as per the workflow
        groups = self._detect_same_thought_columns(df, all_mappings, results.get('uncertain_columns', []))
        results['column_groups'] = groups
        
        # If groups detected, require confirmation
        if groups:
            results['requires_confirmation'] = True
        
        # Check analytics readiness
        results['analytics_readiness'] = self._check_analytics_readiness(all_mappings, df)
        
        print(f"\n✅ Mapping Complete:")
        print(f"   Mapped: {len(results['mapped_columns'])}")
        print(f"   Uncertain: {len(results['uncertain_columns'])}")
        print(f"   Unmapped: {len(results['unmapped_columns'])}")
        print(f"   Ignored: {len(results['ignored_columns'])}")
        print(f"   Groups: {len(results['column_groups'])}")
        print(f"   Requires Confirmation: {results['requires_confirmation']}")
        
        return results
    
    def _analyze_column(self, col_name: str, series: pd.Series) -> List[ColumnSuggestion]:
        """Analyze a column and generate mapping suggestions."""
        suggestions = []
        
        # 0. Check for strict exclusion patterns (only truly problematic columns)
        col_lower = col_name.lower()
        strict_exclusion_keywords = [
            'unit_cost', 'unit_price', 'unit_value', 'price_per', 'cost_per',
            'per_unit', 'each_price', 'each_cost', 'item_price', 'item_cost',
            'discount', 'margin', 'markup', 'sales_rep', 'rep',
            'representative', 'person'
        ]
        
        if any(keyword in col_lower for keyword in strict_exclusion_keywords):
            print(f"   ⚠️ Column '{col_name}' matches strict exclusion pattern - will be marked as uncertain for user confirmation")
            # Don't return empty - let it continue to be marked as uncertain
            # This allows user to confirm the exclusion
        
        # 1. Check knowledge base first (highest priority)
        kb_suggestion = self._check_knowledge_base(col_name)
        if kb_suggestion:
            suggestions.append(kb_suggestion)
        
        # 2. Pattern-based matching (skip if strict exclusion pattern detected)
        if not any(keyword in col_lower for keyword in strict_exclusion_keywords):
            pattern_suggestions = self._pattern_match(col_name)
            suggestions.extend(pattern_suggestions)
        
        # 3. Value-based analysis
        value_suggestion = self._analyze_values(col_name, series)
        if value_suggestion:
            suggestions.append(value_suggestion)
        
        # 4. Fuzzy string matching (skip if strict exclusion pattern detected)
        if RAPIDFUZZ_AVAILABLE and not any(keyword in col_lower for keyword in strict_exclusion_keywords):
            fuzzy_suggestions = self._fuzzy_match(col_name)
            suggestions.extend(fuzzy_suggestions)
        
        # 5. Semantic similarity (skip if strict exclusion pattern detected)
        if self.semantic_model and not any(keyword in col_lower for keyword in strict_exclusion_keywords):
            semantic_suggestion = self._semantic_match(col_name)
            if semantic_suggestion:
                suggestions.append(semantic_suggestion)
        
        # 6. GPT escalation for uncertain columns (if confidence is low)
        if not suggestions or max(s.confidence for s in suggestions) < 70.0:
            gpt_suggestion = self._gpt_escalation(col_name)
            if gpt_suggestion:
                suggestions.append(gpt_suggestion)
        
        # Deduplicate and sort by confidence
        suggestions = self._deduplicate_suggestions(suggestions)
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        return suggestions[:5]  # Return top 5
    
    def _check_knowledge_base(self, col_name: str) -> Optional[ColumnSuggestion]:
        """Check if this column has been learned before."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Exact match
            cursor.execute('''
                SELECT canonical_type, AVG(confidence), COUNT(*) as usage_count
                FROM learned_mappings
                WHERE LOWER(original_column) = LOWER(?)
                GROUP BY canonical_type
                ORDER BY usage_count DESC, AVG(confidence) DESC
                LIMIT 1
            ''', (col_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                canonical_type, avg_confidence, usage_count = result
                # Boost confidence based on usage
                boosted_confidence = min(avg_confidence + (usage_count * 2), 100.0)
                
                return ColumnSuggestion(
                    canonical_type=canonical_type,
                    confidence=boosted_confidence,
                    method='knowledge_base',
                    reasoning=f'Learned from {usage_count} previous occurrence(s)'
                )
        except Exception as e:
            print(f"⚠️ Knowledge base check failed: {e}")
        
        return None
    
    def _check_patterns(self, col_lower: str, patterns: List[str]) -> float:
        """Check if column name matches any of the given patterns."""
        for pattern in patterns:
            try:
                if re.search(pattern, col_lower):
                    # Calculate confidence based on pattern match strength
                    match_strength = len(pattern) / len(col_lower) if len(col_lower) > 0 else 0
                    return min(85.0 + (match_strength * 15), 100.0)
            except re.error as e:
                print(f"   ⚠️ Regex error in pattern '{pattern}': {e}")
                continue
        return 0.0
    
    def _pattern_match(self, col_name: str) -> List[ColumnSuggestion]:
        """Match column name against known patterns."""
        suggestions = []
        col_lower = col_name.lower()
        
        # Check each pattern category (ONLY 5 core types for TANAW)
        pattern_checks = [
            (self.date_patterns, 'Date', 'Date pattern detected'),
            (self.sales_patterns, 'Sales', 'Sales/revenue pattern detected'),
            (self.product_patterns, 'Product', 'Product pattern detected'),
            (self.product_id_patterns, 'Product_ID', 'Product ID pattern detected'),  # Lower priority
            (self.quantity_patterns, 'Quantity', 'Quantity pattern detected'),
            (self.region_patterns, 'Region', 'Region/location pattern detected'),
            # Customer removed - not in TANAW's 5 core analytics
        ]
        
        for patterns, canonical_type, reasoning in pattern_checks:
            # Skip patterns if column matches exclusion lists
            if canonical_type == 'Sales':
                if any(re.search(excl, col_lower) for excl in self.not_sales_patterns):
                    print(f"   ⚠️ Skipping Sales pattern for '{col_name}' (matches exclusion)")
                    continue
            
            # Special logic for Product mapping - prioritize category over ID
            if canonical_type == 'Product':
                # Check if this is a category column (higher priority)
                category_score = self._check_patterns(col_lower, self.product_patterns)
                if category_score > 0:
                    suggestions.append(ColumnSuggestion(
                        canonical_type='Product',
                        confidence=min(category_score * 1.5, 100),  # Strong boost for category
                        reasoning=f"Product category pattern detected: {col_name}",
                        method='pattern_match'
                    ))
                    print(f"   ✅ Product category pattern match: {col_name} -> Product (strongly boosted)")
                    continue
                else:
                    # Check if this is an ID column (much lower priority)
                    id_score = self._check_patterns(col_lower, self.product_id_patterns)
                    if id_score > 0:
                        suggestions.append(ColumnSuggestion(
                            canonical_type='Product_ID',  # Map to separate type
                            confidence=min(id_score * 0.5, 100),  # Much lower score
                            reasoning=f"Product ID pattern detected: {col_name}",
                            method='pattern_match'
                        ))
                        print(f"   ⚠️ Product ID pattern match: {col_name} -> Product_ID (low priority)")
                        continue
            
            if canonical_type == 'Quantity':
                if any(re.search(excl, col_lower) for excl in self.not_quantity_patterns):
                    print(f"   ⚠️ Skipping Quantity pattern for '{col_name}' (matches exclusion)")
                    continue
            
            if canonical_type == 'Region':
                if any(re.search(excl, col_lower) for excl in self.not_region_patterns):
                    print(f"   ⚠️ Skipping Region pattern for '{col_name}' (matches exclusion)")
                    continue
            
            for pattern in patterns:
                if re.search(pattern, col_lower):
                    # Calculate confidence based on pattern specificity
                    confidence = 85.0
                    
                    # Boost for exact word match
                    if pattern.strip('^$').replace('\\', '') == col_lower:
                        confidence = 95.0
                    
                    # Special handling: Map Product_ID and Product_Category to Product
                    if any(re.search(id_pat, col_lower) for id_pat in self.id_patterns):
                        if canonical_type == 'Product':
                            # Keep as Product, just note it's an ID
                            confidence = 90.0
                        elif canonical_type == 'Product_ID':
                            # Keep as Product_ID (don't add _ID again)
                            confidence = 90.0
                        else:
                            # Only add _ID for other types, not Product_ID
                            canonical_type = canonical_type + '_ID'
                            confidence -= 10.0
                    
                    suggestions.append(ColumnSuggestion(
                        canonical_type=canonical_type,
                        confidence=confidence,
                        method='pattern_match',
                        reasoning=f'{reasoning}: "{pattern}"'
                    ))
                    break  # Only use first matching pattern per category
        
        return suggestions
    
    def _analyze_values(self, col_name: str, series: pd.Series) -> Optional[ColumnSuggestion]:
        """Analyze column values to infer type using enhanced value-based analysis."""
        try:
            # Skip if too many nulls
            if series.isnull().sum() / len(series) > 0.9:
                return None
            
            col_lower = col_name.lower()
            
            # CRITICAL FIX: Skip value analysis for unit prices/costs
            # These should NEVER be mapped as Sales amounts
            unit_price_keywords = [
                'unit_cost', 'unit_price', 'unit_value', 'price_per', 'cost_per',
                'per_unit', 'each_price', 'each_cost', 'item_price', 'item_cost',
                'discount', 'margin', 'markup'
            ]
            
            if any(keyword in col_lower for keyword in unit_price_keywords):
                print(f"   ⚠️ Skipping value analysis for '{col_name}' (unit price/cost/discount)")
                return None
            
            # Use enhanced value analyzer for comprehensive analysis
            print(f"   🔍 Running enhanced value analysis for '{col_name}'")
            try:
                from enhanced_value_analyzer import enhanced_analyzer
                analysis_result = enhanced_analyzer.analyze_column(col_name, series)
            except ImportError:
                print(f"   ⚠️ Enhanced value analyzer not available, skipping")
                analysis_result = None
            
            if analysis_result and analysis_result.get('confidence', 0) > 0.5:
                # Convert confidence from 0-1 scale to 0-100 scale
                confidence_100 = analysis_result['confidence'] * 100
                return ColumnSuggestion(
                    canonical_type=analysis_result['canonical_type'],
                    confidence=confidence_100,
                    method='enhanced_value_analysis',
                    reasoning=analysis_result['reasoning']
                )
            
            # Fallback to original analysis if enhanced fails
            print(f"   ⚠️ Enhanced analysis failed, using fallback for '{col_name}'")
            return self._fallback_value_analysis(col_name, series)
            
        except Exception as e:
            print(f"   ⚠️ Value analysis failed for '{col_name}': {e}")
            return None

    def _fallback_value_analysis(self, col_name: str, series: pd.Series) -> Optional[ColumnSuggestion]:
        """Fallback value analysis using original methods."""
        try:
            # Try to infer from data type and values
            if pd.api.types.is_datetime64_any_dtype(series):
                return ColumnSuggestion(
                    canonical_type='Date',
                    confidence=95.0,
                    method='value_analysis',
                    reasoning='Column has datetime type'
                )
            
            # Try to parse as datetime
            if series.dtype == 'object':
                try:
                    parsed = pd.to_datetime(series, errors='coerce')
                    if parsed.notna().sum() / len(series) > 0.7:
                        return ColumnSuggestion(
                            canonical_type='Date',
                            confidence=90.0,
                            method='value_analysis',
                            reasoning='Values successfully parse as dates'
                        )
                except:
                    pass
            
            # Check numeric patterns (only for non-unit-price columns)
            if pd.api.types.is_numeric_dtype(series):
                # Check if values look like money
                if (series > 0).all() and series.mean() > 10:
                    # Could be sales, price, or quantity
                    if series.mean() > 100:
                        return ColumnSuggestion(
                            canonical_type='Sales',
                            confidence=70.0,
                            method='value_analysis',
                            reasoning='Numeric values with high average (likely monetary)'
                        )
                    else:
                        return ColumnSuggestion(
                            canonical_type='Quantity',
                            confidence=70.0,
                            method='value_analysis',
                            reasoning='Numeric values with low average (likely quantity)'
                        )
            
            # DISABLED: Low cardinality logic causes too many false positives
            # (Sales_Rep, Payment_Method, Sales_Channel were wrongly mapped to Region)
            # 
            # Instead, rely on pattern matching and semantic similarity only
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ Fallback analysis failed for '{col_name}': {e}")
            return None

    def _gpt_escalation(self, col_name: str) -> Optional[ColumnSuggestion]:
        """Escalate uncertain columns to GPT for AI-powered mapping."""
        try:
            print(f"   🤖 GPT escalation for '{col_name}'")
            
            # Import GPT escalator
            from gpt_escalator import GPTEscalator
            
            # Initialize GPT escalator
            gpt_escalator = GPTEscalator()
            
            # Escalate to GPT
            gpt_result = gpt_escalator.escalate_uncertain_columns([col_name])
            
            if gpt_result and col_name in gpt_result:
                mapping = gpt_result[col_name]
                if mapping.get('mapped_to') and mapping.get('confidence', 0) > 0.5:
                    # Convert confidence from 0-1 scale to 0-100 scale
                    confidence_100 = mapping['confidence'] * 100
                    return ColumnSuggestion(
                        canonical_type=mapping['mapped_to'],
                        confidence=confidence_100,
                        method='gpt_escalation',
                        reasoning=f"GPT analysis: {mapping.get('reasoning', 'AI-powered mapping')}"
                    )
            
            print(f"   ⚠️ GPT escalation failed for '{col_name}'")
            return None
            
        except Exception as e:
            print(f"   ⚠️ GPT escalation error for '{col_name}': {e}")
            return None
            # 
            # if series.dtype == 'object' or series.dtype.name == 'category':
            #     unique_ratio = series.nunique() / len(series)
            #     if unique_ratio < 0.1:
            #         return ColumnSuggestion(
            #             canonical_type='Region',
            #             confidence=65.0,
            #             method='value_analysis',
            #             reasoning=f'Low cardinality ({unique_ratio:.1%}) suggests categorical'
            #         )
        
        except Exception as e:
            print(f"⚠️ Value analysis failed for {col_name}: {e}")
        
        return None
    
    def _fuzzy_match(self, col_name: str) -> List[ColumnSuggestion]:
        """Use fuzzy string matching to find similar canonical types."""
        if not RAPIDFUZZ_AVAILABLE:
            return []
        
        suggestions = []
        
        try:
            # Get fuzzy matches
            matches = fuzz_process.extract(
                col_name, 
                self.canonical_types, 
                scorer=fuzz.ratio,
                limit=3
            )
            
            for match_text, score, _ in matches:
                if score >= 60:  # Minimum fuzzy match score
                    suggestions.append(ColumnSuggestion(
                        canonical_type=match_text,
                        confidence=score * 0.8,  # Scale down fuzzy confidence
                        method='fuzzy_match',
                        reasoning=f'Fuzzy match with "{match_text}" (score: {score})'
                    ))
        
        except Exception as e:
            print(f"⚠️ Fuzzy matching failed: {e}")
        
        return suggestions
    
    def _semantic_match(self, col_name: str) -> Optional[ColumnSuggestion]:
        """Use semantic similarity to find matching canonical type."""
        if not self.semantic_model:
            return None
        
        try:
            col_lower = col_name.lower()
            
            # CRITICAL FIX: Skip semantic matching for problematic column names
            # These cause false positives even with semantic similarity
            semantic_exclusions = [
                'rep', 'representative', 'person', 'channel', 'method', 
                'type', '_and_', 'composite', 'payment', 'discount',
                'unit_', 'per_', 'each_'
            ]
            
            if any(keyword in col_lower for keyword in semantic_exclusions):
                print(f"   ⚠️ Skipping semantic matching for '{col_name}' (matches exclusion)")
                return None
            
            # Encode column name
            col_embedding = self.semantic_model.encode([col_name])[0]
            
            # Encode canonical types
            canonical_embeddings = self.semantic_model.encode(self.canonical_types)
            
            # Calculate cosine similarities
            from numpy import dot
            from numpy.linalg import norm
            
            similarities = []
            for i, canonical_type in enumerate(self.canonical_types):
                similarity = dot(col_embedding, canonical_embeddings[i]) / (
                    norm(col_embedding) * norm(canonical_embeddings[i])
                )
                similarities.append((canonical_type, similarity))
            
            # Get best match
            best_match = max(similarities, key=lambda x: x[1])
            canonical_type, similarity = best_match
            
            # Convert similarity to confidence (0-1 → 0-100)
            confidence = similarity * 100
            
            # INCREASED THRESHOLD: Only suggest if confidence >= 75% (was 60%)
            # This prevents low-quality suggestions like "Sales_Rep" → "Sales"
            if confidence >= 75:
                return ColumnSuggestion(
                    canonical_type=canonical_type,
                    confidence=confidence,
                    method='semantic_similarity',
                    reasoning=f'Semantic similarity with "{canonical_type}" ({similarity:.2f})'
                )
        
        except Exception as e:
            print(f"⚠️ Semantic matching failed: {e}")
        
        return None
    
    def _deduplicate_suggestions(self, suggestions: List[ColumnSuggestion]) -> List[ColumnSuggestion]:
        """Remove duplicate suggestions, keeping the highest confidence."""
        seen = {}
        for suggestion in suggestions:
            key = suggestion.canonical_type
            if key not in seen or suggestion.confidence > seen[key].confidence:
                seen[key] = suggestion
        
        return list(seen.values())
    
    def _detect_same_thought_columns(self, df: pd.DataFrame, 
                                    mappings: Dict[str, str],
                                    uncertain_columns: List[Dict] = None) -> List[Dict[str, Any]]:
        """
        Detect columns that represent the same concept.
        E.g., 'Product' and 'Product_ID', 'Sales' and 'Sales_Amount'
        """
        groups = []
        
        # Group columns by their canonical type (from both mappings and uncertain columns)
        type_groups = defaultdict(list)
        
        # Add confirmed mappings
        for col, canonical_type in mappings.items():
            type_groups[canonical_type].append(col)
        
        # Add uncertain columns with their suggested mappings
        if uncertain_columns:
            for col_info in uncertain_columns:
                col_name = col_info.get('original_column') or col_info.get('column')
                suggested_type = col_info.get('mapped_column')
                if col_name and suggested_type:
                    type_groups[suggested_type].append(col_name)
        
        # Check for related types (e.g., Product and Product_ID)
        related_pairs = [
            ('Product', 'Product_ID'),
            ('Product', 'Product_Name'),
            ('Product', 'Product_Category'),
            ('Customer', 'Customer_ID'),
            ('Customer', 'Customer_Name'),
            ('Sales', 'Sales_Amount'),
            ('Sales', 'Revenue'),
            ('Region', 'Location'),
            ('Region', 'Store'),
        ]
        
        for base_type, related_type in related_pairs:
            base_cols = type_groups.get(base_type, [])
            related_cols = type_groups.get(related_type, [])
            
            if base_cols and related_cols:
                # Found related columns
                all_cols = base_cols + related_cols
                
                # Determine which is primary (prefer descriptive over ID)
                is_id_pattern = lambda c: any(re.search(p, c.lower()) for p in self.id_patterns)
                
                primary_candidates = [c for c in all_cols if not is_id_pattern(c)]
                primary_col = primary_candidates[0] if primary_candidates else all_cols[0]
                
                groups.append({
                    'columns': all_cols,
                    'suggested_type': base_type,
                    'primary_column': primary_col,
                    'action': 'select_primary',
                    'confidence': 85.0,
                    'reasoning': f'Multiple columns detected for {base_type}. Recommend using {primary_col} as primary.'
                })
        
        # Also check for exact duplicates in same canonical type
        for canonical_type, cols in type_groups.items():
            if len(cols) > 1:
                # Analyze similarity between columns
                similarity_scores = []
                
                for i, col1 in enumerate(cols):
                    for col2 in cols[i+1:]:
                        # Check value similarity
                        if col1 in df.columns and col2 in df.columns:
                            # Compare values
                            matching_ratio = (df[col1] == df[col2]).sum() / len(df)
                            similarity_scores.append((col1, col2, matching_ratio))
                
                # If columns are very similar, suggest handling
                for col1, col2, ratio in similarity_scores:
                    if ratio > 0.8:  # 80% similar
                        groups.append({
                            'columns': [col1, col2],
                            'suggested_type': canonical_type,
                            'primary_column': col1,  # Prefer first alphabetically
                            'action': 'ignore_duplicates',
                            'confidence': ratio * 100,
                            'reasoning': f'Columns are {ratio:.1%} identical. Consider keeping only one.'
                        })
        
        # Additional detection: Check for columns with similar names that might be same-thought
        # This catches cases like "Product" and "Product_ID" even if mapped differently
        all_columns = list(mappings.keys()) + [col.get('original_column', col.get('column')) for col in (uncertain_columns or [])]
        
        for i, col1 in enumerate(all_columns):
            for col2 in all_columns[i+1:]:
                col1_lower = col1.lower()
                col2_lower = col2.lower()
                
                # Check for name-based relationships
                if self._are_related_columns(col1_lower, col2_lower):
                    # Determine which should be primary
                    primary = self._determine_primary_column(col1, col2, df)
                    
                    groups.append({
                        'columns': [col1, col2],
                        'suggested_type': 'Related_Columns',
                        'primary_column': primary,
                        'action': 'select_primary',
                        'confidence': 75.0,
                        'reasoning': f'"{col1}" and "{col2}" appear to represent the same concept. Recommend using "{primary}" as primary.'
                    })
        
        # Deduplicate groups to prevent showing the same column pair multiple times
        deduplicated_groups = []
        seen_pairs = set()
        
        for group in groups:
            # Create a normalized key for the column pair
            columns = sorted(group['columns'])
            pair_key = tuple(columns)
            
            if pair_key not in seen_pairs:
                seen_pairs.add(pair_key)
                deduplicated_groups.append(group)
            else:
                # If duplicate found, keep the one with higher confidence
                for i, existing_group in enumerate(deduplicated_groups):
                    existing_columns = sorted(existing_group['columns'])
                    if tuple(existing_columns) == pair_key:
                        if group['confidence'] > existing_group['confidence']:
                            deduplicated_groups[i] = group
                        break
        
        return deduplicated_groups
    
    def _are_related_columns(self, col1: str, col2: str) -> bool:
        """Check if two column names are related (same-thought)."""
        # Remove common separators and normalize
        col1_clean = re.sub(r'[_\-\s]+', '', col1.lower())
        col2_clean = re.sub(r'[_\-\s]+', '', col2.lower())
        
        # Check for one being a subset of the other with ID suffix
        if col1_clean + 'id' == col2_clean or col2_clean + 'id' == col1_clean:
            return True
        
        # Check for common base words
        base_words = ['product', 'customer', 'sales', 'order', 'item', 'region', 'store']
        for base in base_words:
            if (base in col1_clean and base in col2_clean and 
                (col1_clean.replace(base, '') in ['id', 'name', 'code', 'number'] or
                 col2_clean.replace(base, '') in ['id', 'name', 'code', 'number'])):
                return True
        
        return False
    
    def _determine_primary_column(self, col1: str, col2: str, df: pd.DataFrame) -> str:
        """Determine which column should be primary based on data characteristics."""
        # Prefer descriptive names over IDs
        id_indicators = ['id', 'code', 'number', 'num']
        
        col1_has_id = any(indicator in col1.lower() for indicator in id_indicators)
        col2_has_id = any(indicator in col2.lower() for indicator in id_indicators)
        
        if col1_has_id and not col2_has_id:
            return col2
        elif col2_has_id and not col1_has_id:
            return col1
        
        # If both or neither have ID indicators, prefer the one with more unique values
        if col1 in df.columns and col2 in df.columns:
            col1_unique = df[col1].nunique()
            col2_unique = df[col2].nunique()
            
            if col1_unique != col2_unique:
                return col1 if col1_unique > col2_unique else col2
        
        # Default to first alphabetically
        return col1 if col1 < col2 else col2
    
    def _check_analytics_readiness(self, mappings: Dict[str, str], 
                                   df: pd.DataFrame) -> Dict[str, Any]:
        """
        Determine which analytics can be performed based on available columns.
        """
        # Get reverse mapping (canonical_type -> original_column)
        reverse_mapping = {v: k for k, v in mappings.items()}
        
        # Define TANAW's 5 CORE analytics requirements (SIMPLIFIED)
        analytics_requirements = {
            # DESCRIPTIVE ANALYTICS (3)
            'Sales Summary Report': {
                'required': ['Date', 'Sales'],
                'optional': ['Product', 'Region'],
                'priority': 1,
                'description': 'Total and average sales per period'
            },
            'Product Performance Analysis': {
                'required': ['Product', 'Sales'],  # Sales OR Quantity
                'optional': ['Quantity', 'Date', 'Region'],
                'priority': 1,
                'description': 'Best and worst performing products'
            },
            'Regional Sales Analysis': {
                'required': ['Region', 'Sales'],
                'optional': ['Date', 'Product'],
                'priority': 1,
                'description': 'Sales comparison across regions'
            },
            # PREDICTIVE ANALYTICS (2)
            'Sales Forecasting': {
                'required': ['Date', 'Sales'],
                'optional': ['Region', 'Product'],
                'priority': 2,
                'description': 'Future revenue trend prediction'
            },
            'Demand Forecasting': {
                'required': ['Date', 'Product', 'Quantity'],
                'optional': ['Region'],
                'priority': 2,
                'description': 'Future product demand prediction'
            }
        }
        
        readiness = {
            'available_analytics': [],
            'unavailable_analytics': [],
            'partial_analytics': [],
            'ready_count': 0,
            'total_count': len(analytics_requirements)
        }
        
        for analytic_name, requirements in analytics_requirements.items():
            required_cols = requirements['required']
            optional_cols = requirements.get('optional', [])
            
            # Check if all required columns are available
            has_required = all(col in reverse_mapping for col in required_cols)
            
            if has_required:
                # Count available optional columns
                available_optional = sum(1 for col in optional_cols if col in reverse_mapping)
                
                readiness['available_analytics'].append({
                    'name': analytic_name,
                    'status': 'ready',
                    'required_columns': required_cols,
                    'available_optional': available_optional,
                    'total_optional': len(optional_cols),
                    'priority': requirements['priority']
                })
                readiness['ready_count'] += 1
            else:
                # Check which required columns are missing
                missing_required = [col for col in required_cols if col not in reverse_mapping]
                
                readiness['unavailable_analytics'].append({
                    'name': analytic_name,
                    'status': 'unavailable',
                    'missing_columns': missing_required,
                    'reason': f'Missing required columns: {", ".join(missing_required)}'
                })
        
        return readiness
    
    def _detect_data_type(self, series: pd.Series) -> str:
        """Detect the data type of a series."""
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'datetime'
        elif pd.api.types.is_numeric_dtype(series):
            return 'numeric'
        elif pd.api.types.is_bool_dtype(series):
            return 'boolean'
        else:
            return 'text'
    
    def _get_dropdown_options(self) -> List[str]:
        """Get all available dropdown options for mapping."""
        options = self.canonical_types.copy()
        options.append('Ignore')  # Always include Ignore option
        return sorted(set(options))
    
    def _save_learned_mapping(self, original_column: str, canonical_type: str, 
                             confidence: float, user_confirmed: bool = False):
        """Save a learned mapping to the knowledge base."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if mapping already exists
            cursor.execute('''
                SELECT id, usage_count FROM learned_mappings
                WHERE LOWER(original_column) = LOWER(?) 
                AND canonical_type = ?
            ''', (original_column, canonical_type))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update usage count
                mapping_id, usage_count = existing
                cursor.execute('''
                    UPDATE learned_mappings
                    SET usage_count = usage_count + 1,
                        confidence = ?,
                        timestamp = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (confidence, mapping_id))
            else:
                # Insert new mapping
                cursor.execute('''
                    INSERT INTO learned_mappings 
                    (original_column, canonical_type, confidence, user_confirmed)
                    VALUES (?, ?, ?, ?)
                ''', (original_column, canonical_type, confidence, user_confirmed))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Failed to save learned mapping: {e}")
    
    def _save_ignored_pattern(self, column_pattern: str, reason: str):
        """Save an ignored column pattern."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO ignored_patterns (column_pattern, reason)
                VALUES (?, ?)
            ''', (column_pattern.lower(), reason))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Failed to save ignored pattern: {e}")
    
    def get_mapping_statistics(self) -> Dict[str, Any]:
        """Get statistics about learned mappings."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total mappings
            cursor.execute('SELECT COUNT(*) FROM learned_mappings')
            total_mappings = cursor.fetchone()[0]
            
            # Get total ignored patterns
            cursor.execute('SELECT COUNT(*) FROM ignored_patterns')
            total_ignored = cursor.fetchone()[0]
            
            # Get top mappings
            cursor.execute('''
                SELECT canonical_type, COUNT(*) as count
                FROM learned_mappings
                GROUP BY canonical_type
                ORDER BY count DESC
                LIMIT 5
            ''')
            top_mappings = [{'type': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'total_learned_mappings': total_mappings,
                'total_ignored_patterns': total_ignored,
                'top_canonical_types': top_mappings
            }
            
        except Exception as e:
            print(f"⚠️ Failed to get statistics: {e}")
            return {}
    
    def update_from_user_feedback(self, feedback: Dict[str, Any]):
        """Update knowledge base from user feedback."""
        try:
            mappings = feedback.get('confirmed_mappings', {})
            ignored = feedback.get('ignored_columns', [])
            
            # Save confirmed mappings
            for col, canonical_type in mappings.items():
                if canonical_type.lower() != 'ignore':
                    self._save_learned_mapping(col, canonical_type, 100.0, user_confirmed=True)
            
            # Save ignored patterns
            for col in ignored:
                self._save_ignored_pattern(col, 'User ignored')
            
            print(f"✅ Knowledge base updated with {len(mappings)} mappings and {len(ignored)} ignored patterns")
            
        except Exception as e:
            print(f"⚠️ Failed to update from feedback: {e}")
    
    def get_dropdown_options(self) -> List[str]:
        """Get dropdown options for the UI."""
        return self._get_dropdown_options()
    
    def update_mappings(self, mappings: Dict[str, str]):
        """Update the mapper with new mappings for auto-mapping functionality."""
        try:
            # Store the mappings for use in subsequent operations
            self._auto_mappings = mappings
            print(f"✅ Updated mapper with {len(mappings)} auto-mappings")
            return True
        except Exception as e:
            print(f"⚠️ Failed to update mappings: {e}")
            return False


# Convenience function
def create_flexible_mapper(db_path: str = "tanaw_column_knowledge.db") -> FlexibleColumnMapper:
    """Create a new flexible column mapper instance."""
    return FlexibleColumnMapper(db_path=db_path)

