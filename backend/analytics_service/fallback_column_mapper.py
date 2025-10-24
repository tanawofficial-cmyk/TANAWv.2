"""
Fallback Column Mapper for TANAW
Provides intelligent column mapping without OpenAI dependency.
Uses pattern matching and retail-specific rules.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class ColumnMapping:
    """Represents a column mapping result."""
    original_column: str
    mapped_to: str
    confidence: float
    reasoning: str
    source: str = "fallback"

@dataclass
class MappingResult:
    """Complete mapping result for a dataset."""
    mappings: List[ColumnMapping]
    total_cost: float = 0.0
    cache_hits: int = 0
    processing_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None

class FallbackColumnMapper:
    """
    Intelligent fallback column mapper for retail analytics.
    
    Uses pattern matching and retail-specific rules to map columns
    to TANAW's canonical types without requiring OpenAI API.
    """
    
    def __init__(self):
        # TANAW's 5 core canonical types for retail
        self.canonical_types = [
            'Date',      # Time series data
            'Sales',     # Monetary values  
            'Product',   # Product identifiers
            'Region',    # Geographic locations
            'Quantity'   # Volume metrics
        ]
        
        # Retail-specific mapping patterns
        self.patterns = {
            'Date': {
                'keywords': ['date', 'time', 'created', 'order', 'transaction', 'period'],
                'patterns': [r'.*date.*', r'.*time.*', r'.*created.*', r'.*order.*'],
                'confidence': 95.0
            },
            'Sales': {
                'keywords': ['sales', 'amount', 'revenue', 'total', 'price', 'value', 'money'],
                'patterns': [r'.*sales.*', r'.*amount.*', r'.*revenue.*', r'.*total.*'],
                'confidence': 90.0
            },
            'Product': {
                'keywords': ['product', 'item', 'sku', 'category', 'brand', 'name'],
                'patterns': [r'.*product.*', r'.*item.*', r'.*sku.*', r'.*category.*'],
                'confidence': 90.0
            },
            'Region': {
                'keywords': ['region', 'location', 'store', 'city', 'country', 'area', 'zone'],
                'patterns': [r'.*region.*', r'.*location.*', r'.*store.*', r'.*city.*'],
                'confidence': 85.0
            },
            'Quantity': {
                'keywords': ['quantity', 'qty', 'units', 'demand', 'volume', 'count', 'number'],
                'patterns': [r'.*quantity.*', r'.*qty.*', r'.*units.*', r'.*demand.*'],
                'confidence': 85.0
            }
        }
        
        # Exclusion patterns (columns that should be ignored)
        self.exclusions = [
            'rep', 'representative', 'person', 'channel', 'method', 
            'type', '_and_', 'composite', 'payment', 'discount',
            'unit_', 'per_', 'each_', 'id_', 'code_'
        ]
    
    def map_columns(self, columns: List[str], dataset_context: str = "retail") -> MappingResult:
        """
        Map dataset columns to TANAW canonical types using pattern matching.
        
        Args:
            columns: List of column names from the dataset
            dataset_context: Context about the dataset (default: "retail")
            
        Returns:
            MappingResult with all mappings and metadata
        """
        start_time = datetime.now()
        
        try:
            print(f"🔧 Fallback Column Mapping - Pattern Matching")
            print(f"📋 Analyzing {len(columns)} columns: {columns}")
            
            mappings = []
            
            for column in columns:
                # Ensure column is a string
                if not isinstance(column, str):
                    column = str(column)
                
                mapping = self._map_single_column(column)
                if mapping:
                    mappings.append(mapping)
                    print(f"   ✅ {column} → {mapping.mapped_to} ({mapping.confidence:.1f}%)")
                else:
                    print(f"   ❌ {column} → Ignore (no clear pattern)")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return MappingResult(
                mappings=mappings,
                total_cost=0.0,  # No API cost for fallback
                cache_hits=0,
                processing_time=processing_time,
                success=True
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return MappingResult(
                mappings=[],
                total_cost=0.0,
                cache_hits=0,
                processing_time=processing_time,
                success=False,
                error_message=str(e)
            )
    
    def _map_single_column(self, column: str) -> Optional[ColumnMapping]:
        """Map a single column using pattern matching."""
        
        col_lower = column.lower()
        
        # Check exclusions first
        for exclusion in self.exclusions:
            if exclusion in col_lower:
                return None
        
        # Try each canonical type
        best_match = None
        best_confidence = 0.0
        
        for canonical_type, pattern_info in self.patterns.items():
            confidence = self._calculate_confidence(col_lower, pattern_info)
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = canonical_type
        
        # Only return mapping if confidence is high enough
        if best_confidence >= 70.0:
            return ColumnMapping(
                original_column=column,
                mapped_to=best_match,
                confidence=best_confidence,
                reasoning=f"Pattern match: contains {best_match.lower()} keywords",
                source="fallback"
            )
        
        return None
    
    def _calculate_confidence(self, column: str, pattern_info: Dict) -> float:
        """Calculate confidence score for a column against a pattern."""
        
        confidence = 0.0
        
        # Check keyword matches
        for keyword in pattern_info['keywords']:
            if keyword in column:
                confidence += 20.0  # Base score for keyword match
        
        # Check pattern matches
        for pattern in pattern_info['patterns']:
            if re.match(pattern, column):
                confidence += 15.0  # Bonus for pattern match
        
        # Apply base confidence
        confidence = min(confidence, pattern_info['confidence'])
        
        # Boost confidence for exact matches
        if any(keyword == column for keyword in pattern_info['keywords']):
            confidence = pattern_info['confidence']
        
        return confidence
