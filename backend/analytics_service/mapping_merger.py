"""
Phase 5: Merge Mappings and Apply Canonical Rename
Implements final mapping resolution and DataFrame column renaming to canonical names.

Features:
- Knowledge Base lookup for user-specific mappings
- Merge priority logic with effective scoring
- Collision resolution for duplicate canonical names
- Canonical rename and normalization
- Rename verification and fallback logic
- Comprehensive failure handling
- Advanced observability
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
import re

# Import existing configuration
from config_manager import get_config

@dataclass
class MappingSource:
    """Represents a mapping source with priority and confidence."""
    source_type: str  # 'user_confirmed', 'kb', 'gpt', 'local'
    canonical_name: str
    confidence: float
    effective_score: float
    reasoning: str
    timestamp: Optional[datetime] = None

@dataclass
class CollisionResolution:
    """Represents resolution of mapping collisions."""
    original_column: str
    canonical_name: str
    alias_suffix: Optional[str] = None
    resolution_reason: str = ""

@dataclass
class MappingMergeResult:
    """Results from mapping merge process."""
    final_mappings: Dict[str, str]
    collision_resolutions: List[CollisionResolution]
    canonical_columns: List[str]
    processing_time_seconds: float
    metrics: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

class MappingMerger:
    """
    Phase 5: Mapping merger and canonical rename system.
    
    Features:
    - Knowledge Base lookup for user-specific mappings
    - Merge priority logic with effective scoring
    - Collision resolution for duplicate canonical names
    - Canonical rename and normalization
    - Rename verification and fallback logic
    - Comprehensive failure handling
    - Advanced observability
    """
    
    def __init__(self, config=None):
        """Initialize mapping merger with configuration."""
        self.config = config or get_config()
        self.merger_version = "5.0.0"
        
        # Source weights for effective scoring
        self.source_weights = {
            'user_confirmed': 1.0,
            'kb': 0.98,
            'gpt': 0.9,
            'local': 0.85
        }
        
        # Canonical column names used by analytics
        self.canonical_columns = [
            'Date', 'Sales', 'Amount', 'Product', 'Quantity', 
            'Region', 'Customer', 'Transaction_ID'
        ]
        
        # Required canonical columns for analytics
        self.required_canonical = ['Date', 'Sales', 'Product']
        
        # Metrics tracking
        self.metrics = {
            'mappings_processed': 0,
            'kb_lookups': 0,
            'collisions_resolved': 0,
            'canonical_renames': 0,
            'fallbacks_applied': 0,
            'processing_time_ms': 0.0,
            'auto_mapped_count': 0,
            'suggested_count': 0,
            'unmapped_count': 0
        }
    
    def merge_mappings_and_rename(self, df: pd.DataFrame, 
                                phase_results: Dict[str, Any],
                                user_confirmed: Optional[Dict[str, str]] = None) -> MappingMergeResult:
        """
        Merge all mapping sources and apply canonical rename to DataFrame.
        
        Args:
            df: DataFrame to rename
            phase_results: Results from all previous phases
            user_confirmed: User-confirmed mappings
            
        Returns:
            MappingMergeResult with final mappings and renamed DataFrame
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Collect all mapping sources
            all_mappings = self._collect_all_mappings(phase_results, user_confirmed)
            
            # Step 2: Apply merge priority logic
            prioritized_mappings = self._apply_merge_priority(all_mappings)
            
            # Step 3: Resolve collisions
            final_mappings, collision_resolutions = self._resolve_collisions(prioritized_mappings)
            
            # Step 4: Apply canonical rename
            renamed_df = self._apply_canonical_rename(df, final_mappings)
            
            # Step 5: Verify rename
            verification_result = self._verify_rename(renamed_df, final_mappings)
            
            if not verification_result['success']:
                # Apply fallback logic
                renamed_df, final_mappings = self._apply_fallback_logic(df, final_mappings, verification_result)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics['processing_time_ms'] = processing_time * 1000
            self.metrics['mappings_processed'] = len(final_mappings)
            self.metrics['canonical_renames'] = len([c for c in renamed_df.columns if c in self.canonical_columns])
            
            return MappingMergeResult(
                final_mappings=final_mappings,
                collision_resolutions=collision_resolutions,
                canonical_columns=list(renamed_df.columns),
                processing_time_seconds=processing_time,
                metrics=self.metrics.copy(),
                success=True
            )
            
        except Exception as e:
            return MappingMergeResult(
                final_mappings={},
                collision_resolutions=[],
                canonical_columns=[],
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                metrics=self.metrics.copy(),
                success=False,
                error_message=str(e)
            )
    
    def _collect_all_mappings(self, phase_results: Dict[str, Any], 
                            user_confirmed: Optional[Dict[str, str]] = None) -> Dict[str, List[MappingSource]]:
        """Collect all mapping sources from all phases."""
        all_mappings = {}
        
        # User confirmed mappings (highest priority)
        if user_confirmed:
            for col, canonical in user_confirmed.items():
                if canonical.lower() != 'ignore':
                    all_mappings[col] = [MappingSource(
                        source_type='user_confirmed',
                        canonical_name=canonical,
                        confidence=100.0,
                        effective_score=100.0,
                        reasoning="User confirmed mapping",
                        timestamp=datetime.now()
                    )]
        
        # Knowledge Base mappings
        kb_mappings = self._lookup_kb_mappings(list(phase_results.get('phase2_normalization', {}).keys()))
        for col, kb_mapping in kb_mappings.items():
            if col not in all_mappings:
                all_mappings[col] = []
            all_mappings[col].append(kb_mapping)
        
        # GPT mappings (Phase 4)
        gpt_mappings = phase_results.get('phase4_gpt_escalation', {}).get('escalated_columns', {})
        for col, gpt_data in gpt_mappings.items():
            if col not in all_mappings:
                all_mappings[col] = []
            all_mappings[col].append(MappingSource(
                source_type='gpt',
                canonical_name=gpt_data['mapped_to'],
                confidence=gpt_data['confidence'],
                effective_score=gpt_data['confidence'] * self.source_weights['gpt'],
                reasoning=gpt_data['reason'],
                timestamp=datetime.now()
            ))
        
        # Local mappings (Phase 3)
        local_mappings = phase_results.get('phase3_value_analysis', {}).get('column_inferences', {})
        for col, local_data in local_mappings.items():
            if col not in all_mappings:
                all_mappings[col] = []
            all_mappings[col].append(MappingSource(
                source_type='local',
                canonical_name=local_data['best_candidate'],
                confidence=local_data['local_confidence'],
                effective_score=local_data['local_confidence'] * self.source_weights['local'],
                reasoning="Local inference from value analysis",
                timestamp=datetime.now()
            ))
        
        return all_mappings
    
    def _lookup_kb_mappings(self, columns: List[str]) -> Dict[str, MappingSource]:
        """Lookup Knowledge Base mappings for columns."""
        kb_mappings = {}
        
        try:
            # In a real implementation, this would query the knowledge base
            # For now, we'll simulate KB lookups
            for col in columns:
                # Simulate KB lookup logic
                if self._is_recent_high_confidence_kb_mapping(col):
                    kb_mappings[col] = MappingSource(
                        source_type='kb',
                        canonical_name=self._get_kb_canonical_name(col),
                        confidence=95.0,
                        effective_score=95.0 * self.source_weights['kb'],
                        reasoning="Knowledge Base mapping",
                        timestamp=datetime.now() - timedelta(days=1)
                    )
                    self.metrics['kb_lookups'] += 1
            
        except Exception as e:
            print(f"⚠️ KB lookup error: {e}")
        
        return kb_mappings
    
    def _is_recent_high_confidence_kb_mapping(self, column: str) -> bool:
        """Check if KB has recent high-confidence mapping for column."""
        # Simulate KB lookup logic
        # In real implementation, this would query the database
        return False  # Simplified for now
    
    def _get_kb_canonical_name(self, column: str) -> str:
        """Get canonical name from KB for column."""
        # Simulate KB canonical name lookup
        # In real implementation, this would query the database
        return "Unknown"
    
    def _apply_merge_priority(self, all_mappings: Dict[str, List[MappingSource]]) -> Dict[str, MappingSource]:
        """Apply merge priority logic to select best mapping for each column."""
        prioritized_mappings = {}
        
        for col, sources in all_mappings.items():
            if not sources:
                continue
            
            # Sort by effective score (descending)
            sources.sort(key=lambda x: x.effective_score, reverse=True)
            
            # Select the best mapping
            best_mapping = sources[0]
            prioritized_mappings[col] = best_mapping
            
            # Update metrics
            if best_mapping.source_type == 'user_confirmed':
                self.metrics['auto_mapped_count'] += 1
            elif best_mapping.source_type in ['kb', 'gpt']:
                self.metrics['suggested_count'] += 1
            else:
                self.metrics['unmapped_count'] += 1
        
        return prioritized_mappings
    
    def _resolve_collisions(self, prioritized_mappings: Dict[str, MappingSource]) -> Tuple[Dict[str, str], List[CollisionResolution]]:
        """Resolve collisions when multiple columns map to same canonical name."""
        final_mappings = {}
        collision_resolutions = []
        canonical_usage = {}
        
        for col, mapping in prioritized_mappings.items():
            canonical_name = mapping.canonical_name
            
            if canonical_name in canonical_usage:
                # Collision detected
                existing_col = canonical_usage[canonical_name]
                existing_mapping = prioritized_mappings[existing_col]
                
                # Compare effective scores
                if mapping.effective_score > existing_mapping.effective_score:
                    # New mapping is better, demote existing
                    final_mappings[existing_col] = f"{canonical_name}_1"
                    final_mappings[col] = canonical_name
                    canonical_usage[canonical_name] = col
                    
                    collision_resolutions.append(CollisionResolution(
                        original_column=existing_col,
                        canonical_name=f"{canonical_name}_1",
                        alias_suffix="_1",
                        resolution_reason=f"Demoted due to lower score ({existing_mapping.effective_score:.2f} vs {mapping.effective_score:.2f})"
                    ))
                    
                    collision_resolutions.append(CollisionResolution(
                        original_column=col,
                        canonical_name=canonical_name,
                        resolution_reason=f"Selected due to higher score ({mapping.effective_score:.2f})"
                    ))
                else:
                    # Existing mapping is better, demote new
                    final_mappings[col] = f"{canonical_name}_2"
                    
                    collision_resolutions.append(CollisionResolution(
                        original_column=col,
                        canonical_name=f"{canonical_name}_2",
                        alias_suffix="_2",
                        resolution_reason=f"Demoted due to lower score ({mapping.effective_score:.2f} vs {existing_mapping.effective_score:.2f})"
                    ))
                
                self.metrics['collisions_resolved'] += 1
            else:
                # No collision
                final_mappings[col] = canonical_name
                canonical_usage[canonical_name] = col
        
        return final_mappings, collision_resolutions
    
    def _apply_canonical_rename(self, df: pd.DataFrame, final_mappings: Dict[str, str]) -> pd.DataFrame:
        """Apply canonical rename to DataFrame."""
        try:
            # Convert keys to strings to handle numpy dtypes
            str_mappings = {str(k): v for k, v in final_mappings.items()}
            
            # Create a copy to avoid modifying original
            renamed_df = df.copy()
            
            # Apply rename
            renamed_df.rename(columns=str_mappings, inplace=True)
            
            return renamed_df
            
        except Exception as e:
            print(f"⚠️ Canonical rename error: {e}")
            return df
    
    def _verify_rename(self, df: pd.DataFrame, final_mappings: Dict[str, str]) -> Dict[str, Any]:
        """Verify that rename was successful and required columns exist."""
        try:
            # Check if expected canonical columns exist (case-insensitive)
            df_columns_lower = [col.lower() for col in df.columns]
            missing_required = []
            
            for required_col in self.required_canonical:
                if required_col.lower() not in df_columns_lower:
                    missing_required.append(required_col)
            
            # Check for duplicate canonical names
            duplicate_canonicals = []
            canonical_counts = {}
            for col in df.columns:
                if col in self.canonical_columns:
                    canonical_counts[col] = canonical_counts.get(col, 0) + 1
                    if canonical_counts[col] > 1:
                        duplicate_canonicals.append(col)
            
            success = len(missing_required) == 0 and len(duplicate_canonicals) == 0
            
            return {
                'success': success,
                'missing_required': missing_required,
                'duplicate_canonicals': duplicate_canonicals,
                'canonical_columns_found': [col for col in df.columns if col in self.canonical_columns]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'missing_required': self.required_canonical,
                'duplicate_canonicals': [],
                'canonical_columns_found': []
            }
    
    def _apply_fallback_logic(self, df: pd.DataFrame, final_mappings: Dict[str, str], 
                            verification_result: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """Apply fallback logic when rename verification fails."""
        try:
            # If missing required columns, try to find alternatives
            if verification_result.get('missing_required'):
                print(f"⚠️ Missing required columns: {verification_result['missing_required']}")
                # In a real implementation, this would trigger re-evaluation
                self.metrics['fallbacks_applied'] += 1
            
            # If duplicate canonicals, append suffixes
            if verification_result.get('duplicate_canonicals'):
                print(f"⚠️ Duplicate canonical columns: {verification_result['duplicate_canonicals']}")
                # Apply suffix logic
                df = self._apply_suffix_logic(df, verification_result['duplicate_canonicals'])
                self.metrics['fallbacks_applied'] += 1
            
            return df, final_mappings
            
        except Exception as e:
            print(f"⚠️ Fallback logic error: {e}")
            return df, final_mappings
    
    def _apply_suffix_logic(self, df: pd.DataFrame, duplicate_canonicals: List[str]) -> pd.DataFrame:
        """Apply suffix logic to resolve duplicate canonical names."""
        try:
            renamed_df = df.copy()
            suffix_counts = {}
            
            for col in renamed_df.columns:
                if col in duplicate_canonicals:
                    suffix_counts[col] = suffix_counts.get(col, 0) + 1
                    if suffix_counts[col] > 1:
                        new_name = f"{col}_{suffix_counts[col]}"
                        renamed_df.rename(columns={col: new_name}, inplace=True)
                        print(f"📝 Renamed duplicate column '{col}' to '{new_name}'")
            
            return renamed_df
            
        except Exception as e:
            print(f"⚠️ Suffix logic error: {e}")
            return df
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            'mappings_processed': 0,
            'kb_lookups': 0,
            'collisions_resolved': 0,
            'canonical_renames': 0,
            'fallbacks_applied': 0,
            'processing_time_ms': 0.0,
            'auto_mapped_count': 0,
            'suggested_count': 0,
            'unmapped_count': 0
        }
    
    def emit_metrics(self):
        """Emit metrics for observability."""
        try:
            metrics = {
                "mapping.mappings_processed": self.metrics['mappings_processed'],
                "mapping.kb_lookups": self.metrics['kb_lookups'],
                "mapping.collisions_resolved": self.metrics['collisions_resolved'],
                "mapping.canonical_renames": self.metrics['canonical_renames'],
                "mapping.fallbacks_applied": self.metrics['fallbacks_applied'],
                "mapping.processing_time_ms": self.metrics['processing_time_ms'],
                "mapping.auto_mapped_count": self.metrics['auto_mapped_count'],
                "mapping.suggested_count": self.metrics['suggested_count'],
                "mapping.unmapped_count": self.metrics['unmapped_count']
            }
            
            # In a real implementation, you would send these to your metrics system
            print(f"📊 Mapping merger metrics: {metrics}")
            return metrics
            
        except Exception as e:
            print(f"⚠️ Error emitting mapping merger metrics: {e}")
            return {"mapping.metrics_error": str(e)}

# Global merger instance
mapping_merger = MappingMerger()

def merge_mappings_and_rename(df: pd.DataFrame, phase_results: Dict[str, Any], 
                            user_confirmed: Optional[Dict[str, str]] = None) -> MappingMergeResult:
    """
    Convenience function to merge mappings and apply canonical rename.
    
    Args:
        df: DataFrame to rename
        phase_results: Results from all previous phases
        user_confirmed: User-confirmed mappings
        
    Returns:
        MappingMergeResult with final mappings and renamed DataFrame
    """
    return mapping_merger.merge_mappings_and_rename(df, phase_results, user_confirmed)

if __name__ == "__main__":
    # Test the mapping merger
    print("🧪 Testing Mapping Merger")
    print("=" * 50)
    
    # Create test DataFrame
    test_df = pd.DataFrame({
        'Transaction_Date': pd.date_range('2023-01-01', periods=10),
        'Sales_Amount': [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        'Product_ID': [f"SKU-{i:04d}" for i in range(10)],
        'Customer_Region': ['North', 'South', 'East', 'West'] * 3,
        'Quantity_Sold': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    })
    
    # Mock phase results
    phase_results = {
        'phase2_normalization': {
            'normalized_headers': {
                'Transaction_Date': {'best_candidate': 'Date', 'confidence': 90},
                'Sales_Amount': {'best_candidate': 'Sales', 'confidence': 85},
                'Product_ID': {'best_candidate': 'Product', 'confidence': 80},
                'Customer_Region': {'best_candidate': 'Region', 'confidence': 75},
                'Quantity_Sold': {'best_candidate': 'Quantity', 'confidence': 70}
            }
        },
        'phase3_value_analysis': {
            'column_inferences': {
                'Transaction_Date': {'best_candidate': 'Date', 'local_confidence': 90},
                'Sales_Amount': {'best_candidate': 'Sales', 'local_confidence': 85},
                'Product_ID': {'best_candidate': 'Product', 'local_confidence': 80},
                'Customer_Region': {'best_candidate': 'Region', 'local_confidence': 75},
                'Quantity_Sold': {'best_candidate': 'Quantity', 'local_confidence': 70}
            }
        },
        'phase4_gpt_escalation': {
            'escalated_columns': {},
            'local_fallbacks': {}
        }
    }
    
    result = merge_mappings_and_rename(test_df, phase_results)
    
    if result.success:
        print(f"✅ Successfully processed {len(result.final_mappings)} mappings")
        print(f"✅ Resolved {len(result.collision_resolutions)} collisions")
        print(f"⏱️ Processing time: {result.processing_time_seconds:.3f}s")
        
        print("\n📊 Final Mappings:")
        for orig, canonical in result.final_mappings.items():
            print(f"   {orig} → {canonical}")
        
        if result.collision_resolutions:
            print("\n🔧 Collision Resolutions:")
            for resolution in result.collision_resolutions:
                print(f"   {resolution.original_column} → {resolution.canonical_name} ({resolution.resolution_reason})")
    else:
        print(f"❌ Error: {result.error_message}")
