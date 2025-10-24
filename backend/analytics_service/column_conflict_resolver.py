#!/usr/bin/env python3
"""
Column Conflict Resolver for TANAW Analytics
=============================================

Handles scenarios where multiple columns map to the same semantic meaning.
Implements multi-layer resolution strategy with statistical heuristics and
continuous learning.

Example Scenario:
- Product ID → Product (48% confidence)
- Product Name → Product (47% confidence)

The resolver:
1. Analyzes data characteristics (unique ratio, patterns, data type)
2. Re-ranks confidence using statistical heuristics
3. Provides smart recommendations
4. Learns from user decisions for future automation
"""

import pandas as pd
import numpy as np
import re
import json
import sqlite3
from typing import Dict, List, Tuple, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class ColumnCharacteristics:
    """Statistical characteristics of a column for conflict resolution."""
    column_name: str
    unique_ratio: float
    is_numeric: bool
    avg_string_length: float
    has_id_pattern: bool
    has_code_pattern: bool
    is_sequential: bool
    cardinality: int
    sample_values: List[Any]
    dtype: str


@dataclass
class ConflictResolution:
    """Represents a conflict resolution decision."""
    winner_column: str
    loser_columns: List[str]
    target_type: str
    confidence: float
    reasoning: str
    heuristic_scores: Dict[str, float]
    recommendation: str
    alternative_actions: List[Dict[str, Any]]


class ColumnConflictResolver:
    """
    Resolves conflicts when multiple columns map to the same semantic target.
    
    Features:
    - Statistical heuristics (unique ratio, data type, patterns)
    - Automatic re-ranking of confidence scores
    - Smart recommendations with explanations
    - Knowledge base learning for automation
    - Optional column merge strategies
    """
    
    def __init__(self, db_path: str = "universal_column_mapping.db"):
        self.db_path = db_path
        
        # Heuristic weights for different column types
        self.heuristic_weights = {
            'Product': {
                'unique_ratio': 0.15,      # Lower is better for names
                'is_numeric': -0.20,       # Numeric suggests ID, not name
                'avg_string_length': 0.25, # Longer suggests descriptive name
                'has_id_pattern': -0.25,   # ID pattern suggests ID, not name
                'has_code_pattern': -0.15  # Code pattern suggests ID
            },
            'Region': {
                'unique_ratio': 0.20,      # Moderate uniqueness
                'is_numeric': -0.30,       # Regions are usually text
                'avg_string_length': 0.15, # Longer might be descriptive
                'has_id_pattern': -0.20,   # ID pattern unlikely for regions
                'has_code_pattern': -0.10
            },
            'Date': {
                'unique_ratio': 0.10,      # High uniqueness expected
                'is_numeric': 0.05,        # Can be numeric (timestamps)
                'avg_string_length': 0.05,
                'has_id_pattern': -0.30,   # Shouldn't have ID patterns
                'has_code_pattern': -0.20
            },
            'Amount': {
                'unique_ratio': 0.15,      # High variance expected
                'is_numeric': 0.40,        # Should be numeric
                'avg_string_length': -0.10,
                'has_id_pattern': -0.25,
                'has_code_pattern': -0.20
            },
            'Quantity': {
                'unique_ratio': -0.10,     # Lower uniqueness expected
                'is_numeric': 0.40,        # Should be numeric
                'avg_string_length': -0.15,
                'has_id_pattern': -0.25,
                'has_code_pattern': -0.20
            },
            'Sales': {
                'unique_ratio': 0.15,
                'is_numeric': 0.40,
                'avg_string_length': -0.10,
                'has_id_pattern': -0.25,
                'has_code_pattern': -0.20
            }
        }
        
        # ID patterns for detection
        self.id_patterns = [
            r'^[A-Z]{2,4}\d{3,6}$',      # PEP642
            r'^\d{6,10}$',                # Numeric IDs
            r'^[A-Z]{2,4}-\d{3,6}$',      # Hyphenated
            r'^[A-Z]{2,4}_\d{3,6}$',      # Underscore
        ]
        
        self.code_patterns = [
            r'^[A-Z]{2,3}$',              # Two/three letter codes
            r'^\d{2,4}$',                  # Short numeric codes
            r'^[A-Z]\d{1,3}$',            # Letter + numbers
        ]
        
        # Initialize database
        self._init_conflict_database()
        
        print("✅ Column Conflict Resolver initialized")
    
    def _init_conflict_database(self):
        """Initialize database tables for conflict resolution learning."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create conflict resolutions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conflict_resolutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_type TEXT NOT NULL,
                    winner_column TEXT NOT NULL,
                    loser_columns TEXT NOT NULL,
                    reasoning TEXT,
                    confidence REAL,
                    user_confirmed BOOLEAN DEFAULT FALSE,
                    created_at TEXT,
                    frequency INTEGER DEFAULT 1,
                    UNIQUE(target_type, winner_column, loser_columns)
                )
            ''')
            
            # Create merge strategies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS merge_strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_type TEXT NOT NULL,
                    column1 TEXT NOT NULL,
                    column2 TEXT NOT NULL,
                    merge_type TEXT,
                    merge_formula TEXT,
                    user_confirmed BOOLEAN DEFAULT FALSE,
                    created_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            print("   ✅ Conflict resolution database initialized")
            
        except Exception as e:
            print(f"   ⚠️ Database initialization failed: {e}")
    
    def detect_conflicts(self, mapping_results: Dict[str, Any], 
                        df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect when multiple columns map to the same target.
        
        Args:
            mapping_results: Results from column mapper
            df: Original DataFrame
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Group mapped columns by target type
        target_groups = defaultdict(list)
        
        for mapping in mapping_results.get('mapped_columns', []):
            target = mapping['mapped_column']
            target_groups[target].append(mapping)
        
        # Also check uncertain columns
        for mapping in mapping_results.get('uncertain_columns', []):
            # Check the direct mapped_column field first
            if mapping.get('mapped_column'):
                target = mapping['mapped_column']
                uncertain_mapping = {
                    'original_column': mapping['original_column'],
                    'mapped_column': target,
                    'confidence': mapping.get('confidence', 0),
                    'method': mapping.get('method', 'uncertain'),
                    'status': 'uncertain'
                }
                target_groups[target].append(uncertain_mapping)
            
            # Also look at suggestions (for backward compatibility)
            for suggestion in mapping.get('suggestions', []):
                target = suggestion['type']
                # Create a mapping-like structure
                uncertain_mapping = {
                    'original_column': mapping['original_column'],
                    'mapped_column': target,
                    'confidence': suggestion['confidence'],
                    'method': 'suggestion',
                    'status': 'uncertain'
                }
                target_groups[target].append(uncertain_mapping)
        
        # Find conflicts (multiple columns → same target)
        for target, mappings in target_groups.items():
            if len(mappings) > 1:
                conflict = {
                    'target_type': target,
                    'conflicting_columns': mappings,
                    'conflict_count': len(mappings)
                }
                conflicts.append(conflict)
        
        if conflicts:
            print(f"\n⚠️  Detected {len(conflicts)} mapping conflicts")
            for conflict in conflicts:
                print(f"   • {conflict['target_type']}: "
                      f"{conflict['conflict_count']} columns competing")
        
        return conflicts
    
    def analyze_column_characteristics(self, column_name: str, 
                                      series: pd.Series) -> ColumnCharacteristics:
        """
        Analyze statistical characteristics of a column for conflict resolution.
        
        Args:
            column_name: Name of the column
            series: Column data
            
        Returns:
            ColumnCharacteristics object
        """
        # Basic statistics
        unique_ratio = series.nunique() / len(series) if len(series) > 0 else 0
        cardinality = series.nunique()
        
        # Check if numeric
        is_numeric = pd.api.types.is_numeric_dtype(series)
        
        # Average string length
        sample_values = series.dropna().head(50)
        if len(sample_values) > 0:
            avg_string_length = sample_values.astype(str).str.len().mean()
        else:
            avg_string_length = 0
        
        # Check for ID patterns
        has_id_pattern = False
        has_code_pattern = False
        
        if len(sample_values) > 0:
            sample_strs = sample_values.astype(str)
            
            # ID pattern check
            id_matches = 0
            for value in sample_strs:
                if any(re.match(pattern, value) for pattern in self.id_patterns):
                    id_matches += 1
            has_id_pattern = (id_matches / len(sample_strs)) >= 0.5
            
            # Code pattern check
            code_matches = 0
            for value in sample_strs:
                if any(re.match(pattern, value) for pattern in self.code_patterns):
                    code_matches += 1
            has_code_pattern = (code_matches / len(sample_strs)) >= 0.5
        
        # Check if sequential (for IDs)
        is_sequential = False
        if is_numeric and len(sample_values) > 5:
            try:
                numeric_values = pd.to_numeric(sample_values, errors='coerce').dropna()
                if len(numeric_values) > 5:
                    diffs = numeric_values.diff().dropna()
                    is_sequential = (diffs == 1).mean() >= 0.7
            except:
                pass
        
        return ColumnCharacteristics(
            column_name=column_name,
            unique_ratio=unique_ratio,
            is_numeric=is_numeric,
            avg_string_length=avg_string_length,
            has_id_pattern=has_id_pattern,
            has_code_pattern=has_code_pattern,
            is_sequential=is_sequential,
            cardinality=cardinality,
            sample_values=sample_values.head(10).tolist(),
            dtype=str(series.dtype)
        )
    
    def resolve_conflict(self, conflict: Dict[str, Any], df: pd.DataFrame,
                        auto_resolve: bool = True) -> ConflictResolution:
        """
        Resolve a conflict using statistical heuristics.
        
        Args:
            conflict: Conflict information
            df: Original DataFrame
            auto_resolve: If True, automatically select winner; if False, provide recommendations
            
        Returns:
            ConflictResolution object
        """
        target_type = conflict['target_type']
        conflicting_mappings = conflict['conflicting_columns']
        
        # 🔥 BUSINESS LOGIC PRIORITY RULES (Override statistical heuristics)
        business_winner = self._apply_business_logic_rules(target_type, conflicting_mappings)
        if business_winner:
            print(f"   🎯 Business logic override: {business_winner} wins for {target_type}")
            return self._create_business_logic_resolution(business_winner, conflicting_mappings, target_type)
        
        # Analyze characteristics of each conflicting column
        characteristics = {}
        for mapping in conflicting_mappings:
            col_name = mapping['original_column']
            characteristics[col_name] = self.analyze_column_characteristics(
                col_name, df[col_name]
            )
        
        # Calculate heuristic scores
        heuristic_scores = {}
        for col_name, chars in characteristics.items():
            score = self._calculate_heuristic_score(chars, target_type)
            heuristic_scores[col_name] = score
        
        # Find original confidence scores
        original_confidences = {}
        for mapping in conflicting_mappings:
            original_confidences[mapping['original_column']] = mapping['confidence']
        
        # Combine original confidence with heuristic boost
        final_scores = {}
        for col_name in heuristic_scores.keys():
            original_conf = original_confidences.get(col_name, 50.0)
            heuristic_boost = heuristic_scores[col_name]
            # Combine: 40% original + 60% heuristic boost (favor analytics-optimized choice)
            final_score = (0.4 * original_conf) + (0.6 * heuristic_boost)
            final_scores[col_name] = min(100.0, max(0.0, final_score))
        
        # Determine winner
        winner_column = max(final_scores.items(), key=lambda x: x[1])[0]
        winner_score = final_scores[winner_column]
        loser_columns = [col for col in final_scores.keys() if col != winner_column]
        
        # Build reasoning
        reasoning = self._build_reasoning(
            winner_column, 
            characteristics[winner_column],
            target_type,
            heuristic_scores
        )
        
        # Build recommendation
        recommendation = self._build_recommendation(
            winner_column,
            loser_columns,
            target_type,
            final_scores,
            characteristics
        )
        
        # Build alternative actions
        alternative_actions = self._build_alternative_actions(
            conflicting_mappings,
            final_scores,
            characteristics,
            target_type
        )
        
        resolution = ConflictResolution(
            winner_column=winner_column,
            loser_columns=loser_columns,
            target_type=target_type,
            confidence=winner_score,
            reasoning=reasoning,
            heuristic_scores=final_scores,
            recommendation=recommendation,
            alternative_actions=alternative_actions
        )
        
        # Check knowledge base for learned patterns
        learned_resolution = self._check_learned_patterns(conflict, df)
        if learned_resolution:
            print(f"   🧠 Found learned pattern for {target_type} conflict")
            resolution.confidence = min(95.0, resolution.confidence + 10.0)
            resolution.reasoning += " (Previously learned pattern)"
        
        return resolution
    
    def _apply_business_logic_rules(self, target_type: str, conflicting_mappings: List[Dict]) -> Optional[str]:
        """
        Apply business logic rules to override statistical heuristics.
        
        Returns the column name that should win based on business logic, or None if no override.
        """
        column_names = [mapping['original_column'] for mapping in conflicting_mappings]
        
        # Rule 1: For Amount/Sales conflicts, prioritize actual sales data
        if target_type in ['Amount', 'Sales']:
            # Sales_Amount should always win over Unit_Cost, Unit_Price
            for col in column_names:
                col_lower = col.lower()
                if 'sales' in col_lower and 'amount' in col_lower:
                    return col
            
            # If no Sales_Amount, prefer Amount over Cost/Price
            for col in column_names:
                col_lower = col.lower()
                if 'amount' in col_lower and 'total' not in col_lower:
                    return col
        
        # Rule 2: For Quantity conflicts, prioritize actual quantity data
        if target_type == 'Quantity':
            # Quantity_Sold should always win over Discount
            for col in column_names:
                col_lower = col.lower()
                if 'quantity' in col_lower and 'sold' in col_lower:
                    return col
                
                # Also prioritize columns with "qty", "units", "count"
                if any(word in col_lower for word in ['qty', 'units', 'count']):
                    return col
        
        # Rule 3: For Product conflicts, prioritize ID over Category
        if target_type == 'Product':
            # Product_ID should win over Product_Category for analytics
            for col in column_names:
                col_lower = col.lower()
                if 'product' in col_lower and 'id' in col_lower:
                    return col
                
                # Also prioritize SKU, item_id
                if any(word in col_lower for word in ['sku', 'item_id', 'item id']):
                    return col
        
        # Rule 4: For Region conflicts, prioritize clean region names
        if target_type == 'Region':
            # Region should win over Region_and_Sales_Rep
            for col in column_names:
                col_lower = col.lower()
                if col_lower == 'region':
                    return col
        
        return None  # No business logic override
    
    def _create_business_logic_resolution(self, winner_column: str, conflicting_mappings: List[Dict], target_type: str) -> ConflictResolution:
        """Create a conflict resolution based on business logic override."""
        loser_columns = [mapping['original_column'] for mapping in conflicting_mappings if mapping['original_column'] != winner_column]
        
        # High confidence for business logic decisions
        confidence = 95.0
        
        # Build reasoning based on business logic
        reasoning = f"'{winner_column}' selected based on business logic priority for {target_type}"
        
        # Generate recommendation
        recommendation = f"Recommended: Map '{winner_column}' to {target_type} (95% confidence). "
        if loser_columns:
            recommendation += f"Consider ignoring {', '.join(loser_columns)} or using as supplementary data."
        
        # Generate alternative actions
        alternative_actions = []
        
        # Primary action: map winner
        alternative_actions.append({
            "action": "map_winner",
            "column": winner_column,
            "confidence": confidence,
            "description": f"Map '{winner_column}' to {target_type} (recommended)",
            "target": target_type
        })
        
        # Secondary action: ignore losers
        if loser_columns:
            alternative_actions.append({
                "action": "ignore_losers",
                "columns": loser_columns,
                "description": f"Mark {', '.join(loser_columns)} as 'Ignore'"
            })
        
        # Manual selection option
        alternative_actions.append({
            "action": "manual_select",
            "columns": [winner_column] + loser_columns,
            "description": "Manually choose which column to use"
        })
        
        return ConflictResolution(
            winner_column=winner_column,
            loser_columns=loser_columns,
            target_type=target_type,
            confidence=confidence,
            reasoning=reasoning,
            heuristic_scores={winner_column: confidence},
            recommendation=recommendation,
            alternative_actions=alternative_actions
        )
    
    def _calculate_heuristic_score(self, chars: ColumnCharacteristics, 
                                   target_type: str) -> float:
        """
        Calculate heuristic score based on column characteristics.
        
        Args:
            chars: Column characteristics
            target_type: Target column type (Product, Region, etc.)
            
        Returns:
            Heuristic score (0-100)
        """
        if target_type not in self.heuristic_weights:
            return 50.0  # Neutral score
        
        weights = self.heuristic_weights[target_type]
        
        score = 50.0  # Base score
        
        # Apply unique ratio heuristic
        if 'unique_ratio' in weights:
            # For Product: lower unique ratio = likely Product Name (repeated)
            #              higher unique ratio = likely Product ID (unique)
            unique_contribution = chars.unique_ratio * weights['unique_ratio'] * 100
            score += unique_contribution
        
        # Apply numeric heuristic
        if 'is_numeric' in weights:
            if chars.is_numeric:
                score += weights['is_numeric'] * 100
        
        # Apply string length heuristic
        if 'avg_string_length' in weights:
            # Normalize string length (assume 50 chars is max meaningful)
            normalized_length = min(chars.avg_string_length / 50.0, 1.0)
            score += normalized_length * weights['avg_string_length'] * 100
        
        # Apply ID pattern heuristic
        if 'has_id_pattern' in weights:
            if chars.has_id_pattern:
                score += weights['has_id_pattern'] * 100
        
        # Apply code pattern heuristic
        if 'has_code_pattern' in weights:
            if chars.has_code_pattern:
                score += weights['has_code_pattern'] * 100
        
        # Special boost for sequential IDs
        if chars.is_sequential and target_type in ['Product', 'Region']:
            score -= 15.0  # Sequential suggests ID, not descriptive name
        
        return max(0.0, min(100.0, score))
    
    def _build_reasoning(self, winner_column: str, winner_chars: ColumnCharacteristics,
                        target_type: str, heuristic_scores: Dict[str, float]) -> str:
        """Build human-readable reasoning for the resolution."""
        reasons = []
        
        # Analyze winner characteristics
        if winner_chars.has_id_pattern:
            reasons.append("shows unique ID patterns suitable for identifiers")
        elif winner_chars.has_code_pattern:
            reasons.append("contains code patterns")
        
        if winner_chars.unique_ratio > 0.8:
            reasons.append(f"high uniqueness ({winner_chars.unique_ratio:.0%})")
        elif winner_chars.unique_ratio < 0.2:
            reasons.append(f"low uniqueness ({winner_chars.unique_ratio:.0%}), typical for categories")
        
        if winner_chars.is_numeric:
            reasons.append("numeric data type")
        
        if winner_chars.avg_string_length > 30:
            reasons.append("longer descriptive text")
        elif winner_chars.avg_string_length < 10:
            reasons.append("short identifier format")
        
        if winner_chars.is_sequential:
            reasons.append("sequential values suggesting ID field")
        
        if reasons:
            return f"'{winner_column}' {', '.join(reasons[:3])}"
        else:
            return f"'{winner_column}' best matches {target_type} characteristics"
    
    def _build_recommendation(self, winner_column: str, loser_columns: List[str],
                             target_type: str, final_scores: Dict[str, float],
                             characteristics: Dict[str, ColumnCharacteristics]) -> str:
        """Build recommendation message for UI."""
        winner_score = final_scores[winner_column]
        
        rec = f"Recommended: Map '{winner_column}' to {target_type} ({winner_score:.0f}% confidence). "
        
        if loser_columns:
            loser_names = "', '".join(loser_columns)
            rec += f"Consider ignoring '{loser_names}' or using as supplementary data."
        
        return rec
    
    def _build_alternative_actions(self, conflicting_mappings: List[Dict],
                                   final_scores: Dict[str, float],
                                   characteristics: Dict[str, ColumnCharacteristics],
                                   target_type: str) -> List[Dict[str, Any]]:
        """Build list of alternative actions for the user."""
        actions = []
        
        # Sort columns by final score
        sorted_columns = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Action 1: Accept recommended winner
        winner = sorted_columns[0][0]
        actions.append({
            'action': 'map_winner',
            'column': winner,
            'target': target_type,
            'confidence': sorted_columns[0][1],
            'description': f"Map '{winner}' to {target_type} (recommended)"
        })
        
        # Action 2: Ignore all but winner
        if len(sorted_columns) > 1:
            losers = [col for col, _ in sorted_columns[1:]]
            loser_names = ', '.join([f"'{c}'" for c in losers])
            actions.append({
                'action': 'ignore_losers',
                'columns': losers,
                'description': f"Mark {loser_names} as 'Ignore'"
            })
        
        # Action 3: Merge columns (if applicable)
        if len(sorted_columns) == 2:
            col1, col2 = sorted_columns[0][0], sorted_columns[1][0]
            chars1 = characteristics[col1]
            chars2 = characteristics[col2]
            
            # Suggest merge if one is ID and one is Name
            if chars1.has_id_pattern and not chars2.has_id_pattern:
                actions.append({
                    'action': 'merge_columns',
                    'column1': col1,
                    'column2': col2,
                    'merge_type': 'id_with_label',
                    'description': f"Merge '{col1}' (ID) with '{col2}' (label) for richer analytics"
                })
        
        # Action 4: Manual selection
        actions.append({
            'action': 'manual_select',
            'columns': [col for col, _ in sorted_columns],
            'description': "Manually choose which column to use"
        })
        
        return actions
    
    def _check_learned_patterns(self, conflict: Dict[str, Any], 
                               df: pd.DataFrame) -> Optional[Dict]:
        """Check if this conflict matches a previously learned pattern."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            target_type = conflict['target_type']
            column_names = sorted([m['original_column'] for m in conflict['conflicting_columns']])
            losers_json = json.dumps(column_names[1:])
            
            # Look for exact match
            cursor.execute('''
                SELECT winner_column, reasoning, confidence
                FROM conflict_resolutions
                WHERE target_type = ? AND user_confirmed = TRUE
                ORDER BY frequency DESC
                LIMIT 1
            ''', (target_type,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'winner': result[0],
                    'reasoning': result[1],
                    'confidence': result[2]
                }
            
        except Exception as e:
            print(f"   ⚠️ Error checking learned patterns: {e}")
        
        return None
    
    def save_resolution(self, resolution: ConflictResolution, 
                       user_confirmed: bool = False):
        """
        Save conflict resolution to knowledge base for learning.
        
        Args:
            resolution: ConflictResolution object
            user_confirmed: Whether this was confirmed by user
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            losers_json = json.dumps(resolution.loser_columns)
            
            # Check if this pattern exists
            cursor.execute('''
                SELECT id, frequency FROM conflict_resolutions
                WHERE target_type = ? AND winner_column = ? AND loser_columns = ?
            ''', (resolution.target_type, resolution.winner_column, losers_json))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update frequency
                new_frequency = existing[1] + 1
                cursor.execute('''
                    UPDATE conflict_resolutions
                    SET frequency = ?, user_confirmed = ?, created_at = ?
                    WHERE id = ?
                ''', (new_frequency, user_confirmed or False, timestamp, existing[0]))
            else:
                # Insert new
                cursor.execute('''
                    INSERT INTO conflict_resolutions
                    (target_type, winner_column, loser_columns, reasoning, confidence, 
                     user_confirmed, created_at, frequency)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                ''', (
                    resolution.target_type,
                    resolution.winner_column,
                    losers_json,
                    resolution.reasoning,
                    resolution.confidence,
                    user_confirmed,
                    timestamp
                ))
            
            conn.commit()
            conn.close()
            
            print(f"   ✅ Saved conflict resolution for {resolution.target_type}")
            
        except Exception as e:
            print(f"   ⚠️ Failed to save resolution: {e}")
    
    def get_resolution_statistics(self) -> Dict[str, Any]:
        """Get statistics about conflict resolutions."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total resolutions
            cursor.execute('SELECT COUNT(*) FROM conflict_resolutions')
            total = cursor.fetchone()[0]
            
            # User confirmed resolutions
            cursor.execute('SELECT COUNT(*) FROM conflict_resolutions WHERE user_confirmed = TRUE')
            confirmed = cursor.fetchone()[0]
            
            # Most common conflicts
            cursor.execute('''
                SELECT target_type, COUNT(*) as count
                FROM conflict_resolutions
                GROUP BY target_type
                ORDER BY count DESC
                LIMIT 5
            ''')
            common_conflicts = cursor.fetchall()
            
            # Most learned patterns
            cursor.execute('''
                SELECT target_type, winner_column, frequency
                FROM conflict_resolutions
                WHERE user_confirmed = TRUE
                ORDER BY frequency DESC
                LIMIT 10
            ''')
            learned_patterns = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_resolutions': total,
                'user_confirmed': confirmed,
                'common_conflict_types': common_conflicts,
                'learned_patterns': learned_patterns
            }
            
        except Exception as e:
            print(f"⚠️ Failed to get statistics: {e}")
            return {}
    
    def merge_columns(self, df: pd.DataFrame, column1: str, column2: str,
                     merge_strategy: str = 'prefer_first') -> pd.Series:
        """
        Merge two conflicting columns into one.
        
        Strategies:
        - 'prefer_first': Use column1, fill nulls with column2
        - 'prefer_second': Use column2, fill nulls with column1
        - 'concatenate': Combine both columns (e.g., "ID: value (Name)")
        - 'prefer_non_null': Use whichever value is non-null
        
        Args:
            df: DataFrame containing the columns
            column1: First column name
            column2: Second column name
            merge_strategy: Strategy to use for merging
            
        Returns:
            Merged series
        """
        col1 = df[column1]
        col2 = df[column2]
        
        if merge_strategy == 'prefer_first':
            merged = col1.fillna(col2)
            
        elif merge_strategy == 'prefer_second':
            merged = col2.fillna(col1)
            
        elif merge_strategy == 'concatenate':
            # Create descriptive combination
            merged = pd.Series(index=df.index, dtype='object')
            for idx in df.index:
                val1 = col1.iloc[idx] if pd.notna(col1.iloc[idx]) else ''
                val2 = col2.iloc[idx] if pd.notna(col2.iloc[idx]) else ''
                
                if val1 and val2:
                    merged.iloc[idx] = f"{val1} ({val2})"
                elif val1:
                    merged.iloc[idx] = val1
                else:
                    merged.iloc[idx] = val2
                    
        elif merge_strategy == 'prefer_non_null':
            merged = pd.Series(index=df.index, dtype='object')
            for idx in df.index:
                if pd.notna(col1.iloc[idx]):
                    merged.iloc[idx] = col1.iloc[idx]
                elif pd.notna(col2.iloc[idx]):
                    merged.iloc[idx] = col2.iloc[idx]
                else:
                    merged.iloc[idx] = None
        
        else:
            raise ValueError(f"Unknown merge strategy: {merge_strategy}")
        
        return merged
    
    def save_merge_strategy(self, target_type: str, column1: str, column2: str,
                           merge_type: str, merge_formula: str = None,
                           user_confirmed: bool = False):
        """
        Save a column merge strategy to the knowledge base.
        
        Args:
            target_type: Target column type (Product, Region, etc.)
            column1: First column name
            column2: Second column name
            merge_type: Type of merge (prefer_first, concatenate, etc.)
            merge_formula: Optional formula or description
            user_confirmed: Whether user confirmed this strategy
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO merge_strategies
                (target_type, column1, column2, merge_type, merge_formula, user_confirmed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (target_type, column1, column2, merge_type, merge_formula or '', user_confirmed, timestamp))
            
            conn.commit()
            conn.close()
            
            print(f"   ✅ Saved merge strategy: {column1} + {column2} → {target_type}")
            
        except Exception as e:
            print(f"   ⚠️ Failed to save merge strategy: {e}")
    
    def get_merge_recommendations(self, conflict: Dict[str, Any], df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generate merge recommendations for conflicting columns.
        
        Args:
            conflict: Conflict information
            df: DataFrame
            
        Returns:
            List of merge recommendations
        """
        recommendations = []
        conflicting_columns = conflict['conflicting_columns']
        
        if len(conflicting_columns) != 2:
            # Only support 2-column merges for now
            return recommendations
        
        col1_name = conflicting_columns[0]['original_column']
        col2_name = conflicting_columns[1]['original_column']
        
        # Analyze characteristics
        chars1 = self.analyze_column_characteristics(col1_name, df[col1_name])
        chars2 = self.analyze_column_characteristics(col2_name, df[col2_name])
        
        # Recommendation 1: If one is ID and one is descriptive
        if chars1.has_id_pattern and not chars2.has_id_pattern:
            recommendations.append({
                'merge_type': 'concatenate',
                'column1': col1_name,
                'column2': col2_name,
                'description': f"Merge {col1_name} (ID) with {col2_name} (description) for richer data",
                'example': f"Example: 'PEP001 (Pepsi Cola)'",
                'confidence': 85.0
            })
        elif chars2.has_id_pattern and not chars1.has_id_pattern:
            recommendations.append({
                'merge_type': 'concatenate',
                'column1': col2_name,
                'column2': col1_name,
                'description': f"Merge {col2_name} (ID) with {col1_name} (description) for richer data",
                'example': f"Example: 'PEP001 (Pepsi Cola)'",
                'confidence': 85.0
            })
        
        # Recommendation 2: Prefer higher uniqueness (more informative)
        if chars1.unique_ratio > chars2.unique_ratio * 1.5:
            recommendations.append({
                'merge_type': 'prefer_first',
                'column1': col1_name,
                'column2': col2_name,
                'description': f"Use {col1_name} (higher uniqueness: {chars1.unique_ratio:.1%})",
                'confidence': 70.0
            })
        elif chars2.unique_ratio > chars1.unique_ratio * 1.5:
            recommendations.append({
                'merge_type': 'prefer_first',
                'column1': col2_name,
                'column2': col1_name,
                'description': f"Use {col2_name} (higher uniqueness: {chars2.unique_ratio:.1%})",
                'confidence': 70.0
            })
        
        # Recommendation 3: Generic fallback
        recommendations.append({
            'merge_type': 'prefer_non_null',
            'column1': col1_name,
            'column2': col2_name,
            'description': f"Use whichever value is available from {col1_name} or {col2_name}",
            'confidence': 60.0
        })
        
        return recommendations


def format_conflict_for_ui(conflict: Dict[str, Any], 
                          resolution: ConflictResolution,
                          merge_recommendations: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Format conflict and resolution for UI display.
    
    Returns a structured response for the frontend with recommendations,
    confidence scores, merge options, and alternative actions.
    """
    ui_response = {
        'conflict_detected': True,
        'target_type': conflict['target_type'],
        'conflicting_columns': [
            {
                'column_name': m['original_column'],
                'original_confidence': m['confidence'],
                'updated_confidence': resolution.heuristic_scores.get(m['original_column'], m['confidence']),
                'is_recommended': m['original_column'] == resolution.winner_column
            }
            for m in conflict['conflicting_columns']
        ],
        'resolution': {
            'recommended_column': resolution.winner_column,
            'confidence': resolution.confidence,
            'reasoning': resolution.reasoning,
            'recommendation_text': resolution.recommendation
        },
        'alternative_actions': resolution.alternative_actions,
        'explanation': {
            'title': f"Multiple columns detected for {conflict['target_type']}",
            'message': f"We found {conflict['conflict_count']} columns that could map to {conflict['target_type']}. "
                      f"Based on data analysis, we recommend using '{resolution.winner_column}'.",
            'tooltip': resolution.reasoning
        }
    }
    
    # Add merge recommendations if provided
    if merge_recommendations:
        ui_response['merge_options'] = {
            'available': True,
            'recommendations': merge_recommendations,
            'description': "You can also merge these columns for richer analytics"
        }
    else:
        ui_response['merge_options'] = {
            'available': False
        }
    
    return ui_response


if __name__ == "__main__":
    # Test the conflict resolver
    print("🧪 Testing Column Conflict Resolver")
    print("=" * 60)
    
    # Create test data with conflict scenario
    test_data = {
        'Product ID': ['PEP642', 'PEP186', 'PEP394', 'PEP123', 'PEP456'],
        'Product Name': ['Pepsi Cola', 'Pepsi Max', 'Pepsi Zero', 'Pepsi Cola', 'Pepsi Max'],
        'Quantity': [2, 3, 1, 4, 2],
        'Amount': [146, 321, 66, 200, 150]
    }
    
    df = pd.DataFrame(test_data)
    
    # Simulate a conflict
    conflict = {
        'target_type': 'Product',
        'conflicting_columns': [
            {
                'original_column': 'Product ID',
                'mapped_column': 'Product',
                'confidence': 48.0,
                'method': 'pattern_recognition'
            },
            {
                'original_column': 'Product Name',
                'mapped_column': 'Product',
                'confidence': 47.0,
                'method': 'fuzzy_matching'
            }
        ],
        'conflict_count': 2
    }
    
    # Initialize resolver
    resolver = ColumnConflictResolver()
    
    # Resolve conflict
    resolution = resolver.resolve_conflict(conflict, df)
    
    print("\n✅ CONFLICT RESOLUTION RESULT:")
    print("=" * 60)
    print(f"Target Type: {resolution.target_type}")
    print(f"Winner: {resolution.winner_column} ({resolution.confidence:.1f}%)")
    print(f"Losers: {', '.join(resolution.loser_columns)}")
    print(f"\n💡 Reasoning: {resolution.reasoning}")
    print(f"\n📊 Recommendation: {resolution.recommendation}")
    
    print("\n📋 Heuristic Scores:")
    for col, score in resolution.heuristic_scores.items():
        print(f"   • {col}: {score:.1f}%")
    
    print("\n🎯 Alternative Actions:")
    for i, action in enumerate(resolution.alternative_actions, 1):
        print(f"   {i}. {action['action']}: {action['description']}")
    
    # Format for UI
    ui_response = format_conflict_for_ui(conflict, resolution)
    print("\n📱 UI Response:")
    print(json.dumps(ui_response, indent=2))
    
    # Save resolution
    resolver.save_resolution(resolution, user_confirmed=False)
    
    print("\n" + "=" * 60)
    print("✅ Test completed successfully")

