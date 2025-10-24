"""
Local Analyzer - Phase 3: First Pass Column Mapping
Implements lightweight, cost-free column mapping using:
1. Rule-based alias dictionary matching
2. Fuzzy text similarity
3. Type heuristics based on data patterns  
4. Weighted confidence scoring

This runs BEFORE GPT to minimize costs and maximize privacy.
"""

import re
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass
from difflib import SequenceMatcher
import pandas as pd
import numpy as np

try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False

try:
    from .tanaw_canonical_schema import CanonicalColumnType, tanaw_schema
    from .hybrid_mapping_config import HybridMappingConfig, hybrid_config
    from .file_preprocessor import FileMetadata
except ImportError:
    from tanaw_canonical_schema import CanonicalColumnType, tanaw_schema
    from hybrid_mapping_config import HybridMappingConfig, hybrid_config
    from file_preprocessor import FileMetadata

@dataclass
class ColumnAnalysis:
    """Detailed analysis of a single column for mapping."""
    original_header: str
    normalized_header: str
    
    # Rule-based analysis
    rule_matches: Dict[str, float]  # canonical_type -> confidence
    best_rule_match: Optional[str]
    rule_confidence: float
    
    # Fuzzy matching analysis  
    fuzzy_matches: Dict[str, float]  # canonical_type -> similarity score
    best_fuzzy_match: Optional[str]
    fuzzy_confidence: float
    
    # Type heuristics analysis
    data_type: str
    sample_patterns: List[str]
    type_hints: Dict[str, float]  # canonical_type -> type confidence
    best_type_hint: Optional[str]
    type_confidence: float
    
    # Final weighted scoring
    final_scores: Dict[str, float]  # canonical_type -> final weighted score
    recommended_mapping: Optional[str]
    final_confidence: float
    
    # Metadata
    analysis_method: str
    confidence_breakdown: Dict[str, float]

@dataclass 
class LocalAnalysisResult:
    """Results from local analyzer for all columns."""
    file_metadata: FileMetadata
    column_analyses: List[ColumnAnalysis]
    
    # Summary statistics
    auto_mapped_columns: List[str]      # High confidence (≥0.90)
    suggested_columns: List[str]        # Medium confidence (0.70-0.89) 
    uncertain_columns: List[str]        # Low confidence (<0.70)
    
    # Processing metadata
    analysis_timestamp: str
    processing_time_seconds: float
    analyzer_version: str

class LocalColumnAnalyzer:
    """
    Local column analyzer - first pass in the hybrid mapping pipeline.
    
    Uses rule-based matching, fuzzy similarity, and type heuristics to 
    generate confident column mappings without external API calls.
    """
    
    def __init__(self, config: Optional[HybridMappingConfig] = None):
        self.config = config or hybrid_config
        self.canonical_schema = tanaw_schema
        self.analyzer_version = "1.0.0"
        
        # Load rule mappings from config
        self.rule_mappings = self._build_rule_mappings()
        
        # Prepare fuzzy matching targets
        self.fuzzy_targets = self._prepare_fuzzy_targets()
        
        # Type pattern definitions
        self.type_patterns = self._initialize_type_patterns()
    
    def analyze_columns(
        self, 
        file_metadata: FileMetadata,
        original_dataframe: Optional[pd.DataFrame] = None
    ) -> LocalAnalysisResult:
        """
        Analyze all columns and generate mapping recommendations.
        
        Args:
            file_metadata: Preprocessed file metadata
            original_dataframe: Optional full dataframe for enhanced type analysis
            
        Returns:
            Complete local analysis results
        """
        import time
        start_time = time.time()
        
        column_analyses = []
        
        # Analyze each column
        for i, (original_header, normalized_header) in enumerate(
            zip(file_metadata.column_headers, file_metadata.normalized_headers)
        ):
            
            # Gather additional context if dataframe provided
            additional_context = {}
            if original_dataframe is not None:
                additional_context = self._extract_column_context(
                    original_dataframe[original_header]
                )
            
            # Perform comprehensive analysis
            analysis = self._analyze_single_column(
                original_header=original_header,
                normalized_header=normalized_header,
                data_type=file_metadata.column_data_types.get(original_header, "unknown"),
                sample_patterns=file_metadata.sample_values.get(original_header, []),
                null_percentage=file_metadata.null_percentages.get(original_header, 0),
                additional_context=additional_context
            )
            
            column_analyses.append(analysis)
        
        # Categorize results by confidence
        auto_mapped = []
        suggested = []
        uncertain = []
        
        for analysis in column_analyses:
            if analysis.final_confidence >= self.config.thresholds.auto_map:
                auto_mapped.append(analysis.original_header)
            elif analysis.final_confidence >= self.config.thresholds.suggested_min:
                suggested.append(analysis.original_header)
            else:
                uncertain.append(analysis.original_header)
        
        processing_time = time.time() - start_time
        
        return LocalAnalysisResult(
            file_metadata=file_metadata,
            column_analyses=column_analyses,
            auto_mapped_columns=auto_mapped,
            suggested_columns=suggested,
            uncertain_columns=uncertain,
            analysis_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            processing_time_seconds=round(processing_time, 3),
            analyzer_version=self.analyzer_version
        )
    
    def _analyze_single_column(
        self,
        original_header: str,
        normalized_header: str,
        data_type: str,
        sample_patterns: List[str],
        null_percentage: float,
        additional_context: Dict[str, Any]
    ) -> ColumnAnalysis:
        """Perform comprehensive analysis of a single column."""
        
        # 1. Rule-based analysis
        rule_matches, best_rule, rule_conf = self._rule_based_analysis(normalized_header)
        
        # 2. Fuzzy matching analysis
        fuzzy_matches, best_fuzzy, fuzzy_conf = self._fuzzy_analysis(normalized_header)
        
        # 3. Type heuristics analysis
        type_hints, best_type, type_conf = self._type_analysis(
            normalized_header, data_type, sample_patterns, additional_context
        )
        
        # 4. Weighted final scoring
        final_scores, best_mapping, final_conf, breakdown = self._weighted_scoring(
            rule_matches, fuzzy_matches, type_hints, 
            rule_conf, fuzzy_conf, type_conf
        )
        
        return ColumnAnalysis(
            original_header=original_header,
            normalized_header=normalized_header,
            rule_matches=rule_matches,
            best_rule_match=best_rule,
            rule_confidence=rule_conf,
            fuzzy_matches=fuzzy_matches,
            best_fuzzy_match=best_fuzzy,
            fuzzy_confidence=fuzzy_conf,
            data_type=data_type,
            sample_patterns=sample_patterns,
            type_hints=type_hints,
            best_type_hint=best_type,
            type_confidence=type_conf,
            final_scores=final_scores,
            recommended_mapping=best_mapping,
            final_confidence=final_conf,
            analysis_method="local_hybrid",
            confidence_breakdown=breakdown
        )
    
    def _rule_based_analysis(self, normalized_header: str) -> Tuple[Dict[str, float], Optional[str], float]:
        """
        Rule-based alias dictionary matching.
        
        Returns: (all_matches_dict, best_match, confidence)
        """
        matches = {}
        best_match = None
        best_confidence = 0.0
        
        # Direct exact matching
        for canonical_type, aliases in self.rule_mappings.items():
            if normalized_header in aliases:
                matches[canonical_type] = 1.0
                if 1.0 > best_confidence:
                    best_match = canonical_type
                    best_confidence = 1.0
        
        # Partial matching (if enabled)
        if self.config.local_analyzer.enable_partial_aliases and not matches:
            for canonical_type, aliases in self.rule_mappings.items():
                for alias in aliases:
                    # Check if header contains alias or vice versa
                    if (len(alias) >= self.config.local_analyzer.alias_min_length and 
                        (alias in normalized_header or normalized_header in alias)):
                        
                        # Calculate partial match confidence
                        if alias == normalized_header:
                            confidence = 1.0
                        elif alias in normalized_header:
                            confidence = 0.8 * (len(alias) / len(normalized_header))
                        else:  # normalized_header in alias
                            confidence = 0.8 * (len(normalized_header) / len(alias))
                        
                        matches[canonical_type] = max(matches.get(canonical_type, 0), confidence)
                        
                        if confidence > best_confidence:
                            best_match = canonical_type
                            best_confidence = confidence
        
        return matches, best_match, best_confidence
    
    def _fuzzy_analysis(self, normalized_header: str) -> Tuple[Dict[str, float], Optional[str], float]:
        """
        Fuzzy text similarity analysis.
        
        Returns: (all_similarities_dict, best_match, confidence)
        """
        similarities = {}
        best_match = None
        best_similarity = 0.0
        
        for canonical_type, aliases in self.fuzzy_targets.items():
            max_similarity = 0.0
            
            for alias in aliases:
                if RAPIDFUZZ_AVAILABLE:
                    # Use rapidfuzz for better performance
                    similarity = fuzz.ratio(normalized_header, alias) / 100.0
                else:
                    # Fallback to difflib
                    similarity = SequenceMatcher(None, normalized_header, alias).ratio()
                
                max_similarity = max(max_similarity, similarity)
            
            # Only consider if above threshold
            if max_similarity >= self.config.local_analyzer.fuzzy_threshold:
                similarities[canonical_type] = max_similarity
                
                if max_similarity > best_similarity:
                    best_match = canonical_type
                    best_similarity = max_similarity
        
        return similarities, best_match, best_similarity
    
    def _type_analysis(
        self, 
        normalized_header: str, 
        data_type: str, 
        sample_patterns: List[str],
        additional_context: Dict[str, Any]
    ) -> Tuple[Dict[str, float], Optional[str], float]:
        """
        Type heuristics analysis based on data types and patterns.
        
        Returns: (type_hints_dict, best_hint, confidence)
        """
        type_hints = {}
        
        # Analyze data type
        dtype_hints = self._analyze_data_type(data_type)
        
        # Analyze sample patterns
        pattern_hints = self._analyze_sample_patterns(sample_patterns)
        
        # Analyze additional context (if available)
        context_hints = self._analyze_additional_context(additional_context)
        
        # Combine all type hints
        all_hint_sources = [dtype_hints, pattern_hints, context_hints]
        
        for hint_dict in all_hint_sources:
            for canonical_type, confidence in hint_dict.items():
                type_hints[canonical_type] = max(
                    type_hints.get(canonical_type, 0), 
                    confidence
                )
        
        # Find best type hint
        best_hint = None
        best_confidence = 0.0
        
        if type_hints:
            best_hint = max(type_hints, key=type_hints.get)
            best_confidence = type_hints[best_hint]
        
        return type_hints, best_hint, best_confidence
    
    def _analyze_data_type(self, data_type: str) -> Dict[str, float]:
        """Analyze pandas data type for column type hints."""
        hints = {}
        
        # Numeric types
        if data_type in ['int64', 'float64', 'int32', 'float32']:
            hints[CanonicalColumnType.SALES.value] = 0.6
            hints[CanonicalColumnType.AMOUNT.value] = 0.6
            hints[CanonicalColumnType.QUANTITY.value] = 0.7
            hints[CanonicalColumnType.TRANSACTION_ID.value] = 0.3  # Could be numeric ID
        
        # Object/String types  
        elif data_type in ['object', 'string']:
            hints[CanonicalColumnType.PRODUCT.value] = 0.5
            hints[CanonicalColumnType.REGION.value] = 0.5
            hints[CanonicalColumnType.CUSTOMER.value] = 0.5
            hints[CanonicalColumnType.TRANSACTION_ID.value] = 0.4
        
        # DateTime types
        elif 'datetime' in data_type.lower():
            hints[CanonicalColumnType.DATE.value] = 0.9
        
        return hints
    
    def _analyze_sample_patterns(self, sample_patterns: List[str]) -> Dict[str, float]:
        """Analyze sample data patterns for type hints."""
        hints = {}
        
        if not sample_patterns:
            return hints
        
        pattern_counts = {}
        for pattern in sample_patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Analyze most common patterns
        for pattern, count in pattern_counts.items():
            confidence = min(0.8, count / len(sample_patterns))
            
            if 'date' in pattern.lower():
                hints[CanonicalColumnType.DATE.value] = max(
                    hints.get(CanonicalColumnType.DATE.value, 0), 0.8
                )
            elif 'currency' in pattern.lower() or 'numeric' in pattern.lower():
                hints[CanonicalColumnType.SALES.value] = max(
                    hints.get(CanonicalColumnType.SALES.value, 0), confidence
                )
                hints[CanonicalColumnType.AMOUNT.value] = max(
                    hints.get(CanonicalColumnType.AMOUNT.value, 0), confidence
                )
            elif 'id_pattern' in pattern:
                hints[CanonicalColumnType.TRANSACTION_ID.value] = max(
                    hints.get(CanonicalColumnType.TRANSACTION_ID.value, 0), 0.6
                )
            elif 'text_pattern' in pattern:
                hints[CanonicalColumnType.PRODUCT.value] = max(
                    hints.get(CanonicalColumnType.PRODUCT.value, 0), 0.4
                )
                hints[CanonicalColumnType.REGION.value] = max(
                    hints.get(CanonicalColumnType.REGION.value, 0), 0.4
                )
        
        return hints
    
    def _analyze_additional_context(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Analyze additional context from full dataframe analysis."""
        hints = {}
        
        # Could add statistical analysis, value distributions, etc.
        # For now, return empty - this is for future enhancement
        
        return hints
    
    def _weighted_scoring(
        self,
        rule_matches: Dict[str, float],
        fuzzy_matches: Dict[str, float], 
        type_hints: Dict[str, float],
        rule_confidence: float,
        fuzzy_confidence: float,
        type_confidence: float
    ) -> Tuple[Dict[str, float], Optional[str], float, Dict[str, float]]:
        """
        Combine all analysis methods using weighted scoring.
        
        Returns: (final_scores, best_mapping, final_confidence, confidence_breakdown)
        """
        # Get weights from config
        rule_weight = self.config.local_analyzer.rule_weight
        fuzzy_weight = self.config.local_analyzer.fuzzy_weight
        type_weight = self.config.local_analyzer.type_weight
        
        # Normalize weights
        total_weight = rule_weight + fuzzy_weight + type_weight
        rule_weight /= total_weight
        fuzzy_weight /= total_weight  
        type_weight /= total_weight
        
        # Collect all possible canonical types
        all_types = set()
        all_types.update(rule_matches.keys())
        all_types.update(fuzzy_matches.keys())
        all_types.update(type_hints.keys())
        
        # Calculate weighted scores
        final_scores = {}
        
        for canonical_type in all_types:
            rule_score = rule_matches.get(canonical_type, 0.0)
            fuzzy_score = fuzzy_matches.get(canonical_type, 0.0)
            type_score = type_hints.get(canonical_type, 0.0)
            
            weighted_score = (
                rule_score * rule_weight +
                fuzzy_score * fuzzy_weight +
                type_score * type_weight
            )
            
            final_scores[canonical_type] = weighted_score
        
        # Find best mapping
        best_mapping = None
        final_confidence = 0.0
        
        if final_scores:
            best_mapping = max(final_scores, key=final_scores.get)
            final_confidence = final_scores[best_mapping]
        
        # Create confidence breakdown
        breakdown = {
            "rule_confidence": rule_confidence,
            "fuzzy_confidence": fuzzy_confidence,
            "type_confidence": type_confidence,
            "rule_weight": rule_weight,
            "fuzzy_weight": fuzzy_weight,
            "type_weight": type_weight
        }
        
        return final_scores, best_mapping, final_confidence, breakdown
    
    def _extract_column_context(self, column_series: pd.Series) -> Dict[str, Any]:
        """Extract additional context from full column data."""
        context = {}
        
        # Statistical measures (without exposing data)
        context['unique_count'] = column_series.nunique()
        context['total_count'] = len(column_series)
        context['uniqueness_ratio'] = context['unique_count'] / context['total_count']
        
        # Value characteristics
        if pd.api.types.is_numeric_dtype(column_series):
            context['is_integer'] = column_series.dtype in ['int64', 'int32']
            context['has_negatives'] = (column_series < 0).any()
            non_null = column_series.dropna()
            if len(non_null) > 0:
                context['value_range'] = {
                    'min': float(non_null.min()),
                    'max': float(non_null.max())
                }
        
        return context
    
    def _build_rule_mappings(self) -> Dict[str, Set[str]]:
        """Build rule mappings from configuration."""
        raw_mappings = self.config.get_local_analyzer_rules()
        
        # Convert to sets for faster lookup and normalize
        processed_mappings = {}
        for canonical_type, aliases in raw_mappings.items():
            processed_mappings[canonical_type] = {
                alias.lower().strip() for alias in aliases
            }
        
        return processed_mappings
    
    def _prepare_fuzzy_targets(self) -> Dict[str, List[str]]:
        """Prepare fuzzy matching targets from rule mappings."""
        return {
            canonical_type: list(aliases)
            for canonical_type, aliases in self.rule_mappings.items()
        }
    
    def _initialize_type_patterns(self) -> Dict[str, List[str]]:
        """Initialize type pattern definitions for heuristic matching."""
        return {
            'date_patterns': [
                r'\d{4}-\d{2}-\d{2}',
                r'\d{2}/\d{2}/\d{4}',
                r'\d{1,2}/\d{1,2}/\d{2,4}'
            ],
            'currency_patterns': [
                r'^\$\d+\.?\d*$',
                r'^\d+\.\d{2}$'
            ],
            'id_patterns': [
                r'^[A-Z0-9]{3,}-?[A-Z0-9]{3,}$'
            ]
        }
    
    def get_mapping_recommendations(
        self, 
        analysis_result: LocalAnalysisResult
    ) -> Dict[str, Any]:
        """Generate user-friendly mapping recommendations."""
        
        recommendations = {
            "summary": {
                "total_columns": len(analysis_result.column_analyses),
                "auto_mapped": len(analysis_result.auto_mapped_columns),
                "suggested": len(analysis_result.suggested_columns), 
                "uncertain": len(analysis_result.uncertain_columns),
                "processing_time": analysis_result.processing_time_seconds
            },
            "mappings": {},
            "next_actions": []
        }
        
        # Generate mapping details
        for analysis in analysis_result.column_analyses:
            recommendations["mappings"][analysis.original_header] = {
                "recommended": analysis.recommended_mapping,
                "confidence": round(analysis.final_confidence, 3),
                "confidence_level": self._get_confidence_level(analysis.final_confidence),
                "method": analysis.analysis_method,
                "alternatives": dict(sorted(
                    analysis.final_scores.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:3])  # Top 3 alternatives
            }
        
        # Generate next action recommendations
        if analysis_result.uncertain_columns:
            recommendations["next_actions"].append({
                "action": "gpt_analysis",
                "description": f"Send {len(analysis_result.uncertain_columns)} uncertain columns to GPT for analysis",
                "columns": analysis_result.uncertain_columns
            })
        
        if analysis_result.suggested_columns:
            recommendations["next_actions"].append({
                "action": "user_review",
                "description": f"Review {len(analysis_result.suggested_columns)} suggested mappings",
                "columns": analysis_result.suggested_columns
            })
        
        if analysis_result.auto_mapped_columns:
            recommendations["next_actions"].append({
                "action": "auto_apply",
                "description": f"Auto-apply {len(analysis_result.auto_mapped_columns)} high-confidence mappings",
                "columns": analysis_result.auto_mapped_columns
            })
        
        return recommendations
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Convert numeric confidence to descriptive level."""
        if confidence >= self.config.thresholds.auto_map:
            return "high"
        elif confidence >= self.config.thresholds.suggested_min:
            return "medium"
        else:
            return "low"

# Global instance for easy access
local_analyzer = LocalColumnAnalyzer()
