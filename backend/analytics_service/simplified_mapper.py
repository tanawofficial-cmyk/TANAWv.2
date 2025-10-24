"""
Simplified Column Mapper for TANAW
Replaces the complex 11-phase system with OpenAI-led mapping.

This is the main interface that TANAW will use instead of FlexibleColumnMapper.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
import os
from datetime import datetime

# Try to import GPT mapper, fallback to FlexibleColumnMapper if not available
try:
    from gpt_column_mapper import GPTColumnMapper, MappingResult
    GPT_AVAILABLE = True
except ImportError:
    print("⚠️ OpenAI module not available, using FlexibleColumnMapper as fallback")
    GPT_AVAILABLE = False

# Import FlexibleColumnMapper as fallback
from flexible_column_mapper import FlexibleColumnMapper

class SimplifiedMapper:
    """
    Simplified column mapper that uses GPT for accurate mapping.
    
    This replaces the complex FlexibleColumnMapper with a focused,
    cost-effective solution for retail analytics.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the simplified mapper.
        
        Args:
            openai_api_key: OpenAI API key. If None, will try to get from environment.
        """
        # Check if GPT is available
        if GPT_AVAILABLE:
            # Get API key
            if openai_api_key:
                self.api_key = openai_api_key
                print(f"✅ Using provided OpenAI API key (ends with: ...{openai_api_key[-6:]})")
            else:
                # Try multiple environment variable names
                self.api_key = (os.getenv('OPENAI_API_KEY') or 
                               os.getenv('OPENAI_KEY') or 
                               os.getenv('OPENAI_API') or
                               os.getenv('OPENAI_TOKEN'))
                
                if self.api_key:
                    print(f"✅ Found OpenAI API key in environment (ends with: ...{self.api_key[-6:]})")
                else:
                    print("⚠️ OpenAI API key not found in environment variables")
                    print("   Checked: OPENAI_API_KEY, OPENAI_KEY, OPENAI_API, OPENAI_TOKEN")
                    self.use_gpt = False
                    self.fallback_mapper = FlexibleColumnMapper()
                    return
            
            # Initialize GPT mapper
            try:
                self.gpt_mapper = GPTColumnMapper(self.api_key)
                self.use_gpt = True
                print("✅ GPT mapper initialized successfully")
            except Exception as e:
                print(f"⚠️ GPT mapper initialization failed: {e}, using FlexibleColumnMapper fallback")
                self.use_gpt = False
                self.fallback_mapper = FlexibleColumnMapper()
        else:
            print("⚠️ Using FlexibleColumnMapper fallback (OpenAI not available)")
            self.use_gpt = False
            self.fallback_mapper = FlexibleColumnMapper()
        
        # TANAW's 5 core analytics requirements
        self.analytics_requirements = {
            'Sales Summary Report': {
                'required_columns': ['Date', 'Sales'],
                'optional_columns': ['Product', 'Region'],
                'priority': 1
            },
            'Product Performance Analysis': {
                'required_columns': ['Product', 'Sales'],
                'optional_columns': ['Quantity', 'Date', 'Region'],
                'priority': 1
            },
            'Regional Sales Analysis': {
                'required_columns': ['Region', 'Sales'],
                'optional_columns': ['Date', 'Product'],
                'priority': 1
            },
            'Sales Forecasting': {
                'required_columns': ['Date', 'Sales'],
                'optional_columns': ['Region', 'Product'],
                'priority': 2
            },
            'Demand Forecasting': {
                'required_columns': ['Date', 'Product', 'Quantity'],
                'optional_columns': ['Region'],
                'priority': 2
            }
        }
    
    def map_columns(self, df: pd.DataFrame, dataset_context: str = "retail") -> Dict[str, Any]:
        """
        Main mapping function that replaces FlexibleColumnMapper.
        
        Args:
            df: DataFrame to analyze
            dataset_context: Context about the dataset
            
        Returns:
            Dictionary with mapping results in TANAW format
        """
        print("🚀 Simplified Column Mapping - GPT-Powered")
        
        try:
            # Step 1: Get column names (ensure they are strings)
            columns = [str(col) for col in df.columns]
            print(f"📋 Analyzing {len(columns)} columns: {columns}")
            
            # Step 2: Get mappings (GPT or FlexibleColumnMapper fallback)
            if self.use_gpt:
                print("🤖 Using GPT-powered mapping")
                mapping_result = self.gpt_mapper.map_columns(columns, dataset_context)
            else:
                print("🔧 Using FlexibleColumnMapper fallback")
                # Use FlexibleColumnMapper as fallback
                flexible_result = self.fallback_mapper.map_columns(df)
                
                # Convert FlexibleColumnMapper result to MappingResult format
                from gpt_column_mapper import MappingResult, ColumnMapping
                mappings = []
                
                for col in flexible_result.get('mapped_columns', []):
                    mappings.append(ColumnMapping(
                        original_column=col.get('original_column', ''),
                        mapped_to=col.get('mapped_column', ''),
                        confidence=col.get('confidence', 80.0),
                        reasoning=col.get('reasoning', 'FlexibleColumnMapper mapping'),
                        source="flexible"
                    ))
                
                mapping_result = MappingResult(
                    mappings=mappings,
                    total_cost=0.0,
                    cache_hits=0,
                    processing_time=flexible_result.get('processing_time', 0),
                    success=True
                )
            
            if not mapping_result.success:
                raise Exception(f"Mapping failed: {mapping_result.error_message}")
            
            # Step 3: Format results for TANAW
            formatted_results = self._format_results(mapping_result, df)
            
            # Step 4: Check analytics readiness
            analytics_readiness = self._check_analytics_readiness(formatted_results['mapped_columns'])
            
            # Step 5: Apply mappings to DataFrame
            renamed_df = self._apply_mappings(df, formatted_results['mapped_columns'])
            
            # Step 6: Return complete results
            return {
                'success': True,
                'mapped_columns': formatted_results['mapped_columns'],
                'uncertain_columns': formatted_results['uncertain_columns'],
                'unmapped_columns': formatted_results['unmapped_columns'],
                'analytics_readiness': analytics_readiness,
                'data_quality': self._assess_data_quality(renamed_df),
                'processing_time': mapping_result.processing_time,
                'total_cost': mapping_result.total_cost,
                'cache_hits': mapping_result.cache_hits,
                'renamed_dataframe': renamed_df,
                'message': f"{'GPT' if self.use_gpt else 'FlexibleColumnMapper'} mapping completed successfully. Cost: ${mapping_result.total_cost:.4f}"
            }
            
        except Exception as e:
            print(f"❌ Simplified mapping failed: {e}")
            return {
                'success': False,
                'error_message': str(e),
                'mapped_columns': [],
                'uncertain_columns': [],
                'unmapped_columns': columns,
                'analytics_readiness': {'available_analytics': [], 'unavailable_analytics': []},
                'data_quality': {'overall_score': 0, 'issues': []},
                'processing_time': 0,
                'total_cost': 0,
                'cache_hits': 0
            }
    
    def _format_results(self, mapping_result: MappingResult, df: pd.DataFrame) -> Dict[str, Any]:
        """Format GPT mapping results for TANAW compatibility."""
        
        mapped_columns = []
        uncertain_columns = []
        unmapped_columns = []
        
        for mapping in mapping_result.mappings:
            if mapping.mapped_to == "Ignore":
                unmapped_columns.append({
                    'original_column': mapping.original_column,
                    'reason': mapping.reasoning,
                    'confidence': mapping.confidence
                })
            elif mapping.confidence >= 80:
                mapped_columns.append({
                    'original_column': mapping.original_column,
                    'mapped_column': mapping.mapped_to,
                    'confidence': mapping.confidence,
                    'reasoning': mapping.reasoning,
                    'source': mapping.source,
                    'suggestions': []
                })
            else:
                uncertain_columns.append({
                    'original_column': mapping.original_column,
                    'mapped_column': mapping.mapped_to,
                    'confidence': mapping.confidence,
                    'reasoning': mapping.reasoning,
                    'source': mapping.source,
                    'suggestions': [{
                        'type': mapping.mapped_to,
                        'confidence': mapping.confidence,
                        'reasoning': mapping.reasoning
                    }]
                })
        
        return {
            'mapped_columns': mapped_columns,
            'uncertain_columns': uncertain_columns,
            'unmapped_columns': unmapped_columns
        }
    
    def _check_analytics_readiness(self, mapped_columns: List[Dict]) -> Dict[str, Any]:
        """Check which analytics are ready based on mapped columns."""
        
        # Get available canonical columns
        available_columns = [col['mapped_column'] for col in mapped_columns]
        
        available_analytics = []
        unavailable_analytics = []
        
        for analytic_name, requirements in self.analytics_requirements.items():
            required_cols = requirements['required_columns']
            optional_cols = requirements.get('optional_columns', [])
            
            # Check if all required columns are available
            missing_required = [col for col in required_cols if col not in available_columns]
            
            if not missing_required:
                # All required columns present
                available_optional = [col for col in optional_cols if col in available_columns]
                
                available_analytics.append({
                    'name': analytic_name,
                    'status': 'ready',
                    'required_columns': required_cols,
                    'available_optional': available_optional,
                    'total_optional': len(optional_cols),
                    'priority': requirements['priority']
                })
            else:
                # Missing required columns
                unavailable_analytics.append({
                    'name': analytic_name,
                    'status': 'disabled',
                    'missing_columns': missing_required,
                    'required_columns': required_cols,
                    'priority': requirements['priority']
                })
        
        return {
            'available_analytics': available_analytics,
            'unavailable_analytics': unavailable_analytics,
            'ready_count': len(available_analytics),
            'total_count': len(self.analytics_requirements),
            'analytics_readiness': {
                'ready_analytics': len(available_analytics),
                'disabled_analytics': len(unavailable_analytics),
                'total_analytics': len(self.analytics_requirements)
            }
        }
    
    def _apply_mappings(self, df: pd.DataFrame, mapped_columns: List[Dict]) -> pd.DataFrame:
        """Apply column mappings to DataFrame."""
        
        # Create mapping dictionary
        column_mapping = {}
        for mapping in mapped_columns:
            column_mapping[mapping['original_column']] = mapping['mapped_column']
        
        # Apply mappings
        renamed_df = df.rename(columns=column_mapping)
        
        return renamed_df
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess data quality of the mapped DataFrame."""
        
        issues = []
        quality_score = 100
        
        # Check for missing values
        for col in df.columns:
            # Ensure col is a string to avoid Series ambiguity
            col_str = str(col)
            null_count = df[col_str].isnull().sum()
            null_percentage = (null_count / len(df)) * 100
            
            if null_percentage > 50:
                issues.append(f"Column '{col_str}' has {null_percentage:.1f}% missing values")
                quality_score -= 20
            elif null_percentage > 20:
                issues.append(f"Column '{col_str}' has {null_percentage:.1f}% missing values")
                quality_score -= 10
        
        # Check for duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            duplicate_percentage = (duplicate_count / len(df)) * 100
            issues.append(f"{duplicate_count} duplicate rows ({duplicate_percentage:.1f}%)")
            quality_score -= 5
        
        # Check data types
        for col in df.columns:
            if col == 'Date' and not pd.api.types.is_datetime64_any_dtype(df[col]):
                issues.append(f"Date column '{col}' is not in datetime format")
                quality_score -= 5
            elif col in ['Sales', 'Quantity'] and not pd.api.types.is_numeric_dtype(df[col]):
                issues.append(f"Numeric column '{col}' contains non-numeric data")
                quality_score -= 10
        
        return {
            'overall_score': max(0, quality_score),
            'issues': issues,
            'warnings': issues if quality_score < 80 else []
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics and cost information."""
        return self.gpt_mapper.get_cache_stats()
