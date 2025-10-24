"""
Phase 11: Errors, Messages, UX & Remediation
Implements meaningful feedback and remediation paths for users.

Features:
- Plain-language error messages
- One-click remediation paths
- Automated remediation
- User-friendly UX guidelines
- Comprehensive error handling
- Advanced observability
"""

import json
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import base64
import io
from pathlib import Path

# Import existing configuration
from config_manager import get_config

@dataclass
class ErrorMessage:
    """Represents a user-friendly error message."""
    error_type: str
    severity: str  # 'error', 'warning', 'info'
    title: str
    message: str
    actionable_steps: List[str]
    remediation_options: List[Dict[str, Any]]
    context: Dict[str, Any]

@dataclass
class RemediationOption:
    """Represents a remediation option."""
    option_id: str
    title: str
    description: str
    action_type: str  # 'remap', 'rerun', 'download', 'manual'
    parameters: Dict[str, Any]
    confidence: float
    one_click: bool

@dataclass
class UXResult:
    """Represents a UX operation result."""
    success: bool
    error_messages: List[ErrorMessage] = None
    remediation_options: List[RemediationOption] = None
    processing_time_seconds: float = 0.0
    error_message: Optional[str] = None

class UXRemediation:
    """
    Phase 11: UX and remediation system for meaningful feedback and remediation paths.
    
    Features:
    - Plain-language error messages
    - One-click remediation paths
    - Automated remediation
    - User-friendly UX guidelines
    - Comprehensive error handling
    - Advanced observability
    """
    
    def __init__(self, config=None):
        """Initialize UX remediation with configuration."""
        self.config = config or get_config()
        self.ux_version = "11.0.0"
        
        # Configuration
        self.max_remediation_options = getattr(self.config, 'max_remediation_options', 3)
        self.auto_remediation_threshold = getattr(self.config, 'auto_remediation_threshold', 0.8)
        self.message_templates = self._load_message_templates()
        
        # Metrics tracking
        self.metrics = {
            'error_messages_generated': 0,
            'remediation_options_provided': 0,
            'one_click_actions': 0,
            'automated_remediations': 0,
            'user_satisfaction_score': 0.0,
            'processing_time_ms': 0.0
        }
    
    def _load_message_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load message templates for different error types."""
        return {
            'missing_date_column': {
                'title': 'Date Column Not Found',
                'message': 'We couldn\'t find a Date column — forecasting disabled. If your file has a date column, rename it to \'OrderDate\' or tell us which column it is using \'Report wrong mapping\'.',
                'severity': 'warning',
                'actionable_steps': [
                    'Check if your file has a date column with a different name',
                    'Rename your date column to \'OrderDate\' or \'Date\'',
                    'Use the \'Report wrong mapping\' button to specify the correct column'
                ],
                'remediation_options': [
                    {
                        'option_id': 'remap_date',
                        'title': 'Remap Date Column',
                        'description': 'Select the correct date column from your file',
                        'action_type': 'remap',
                        'one_click': True
                    },
                    {
                        'option_id': 'download_sample',
                        'title': 'Download Sample',
                        'description': 'Download a sanitized sample to check your data',
                        'action_type': 'download',
                        'one_click': True
                    }
                ]
            },
            'low_confidence_mapping': {
                'title': 'Low Confidence Mapping',
                'message': 'Some columns have low confidence mappings. We can improve accuracy by re-running the analysis.',
                'severity': 'info',
                'actionable_steps': [
                    'Review the suggested mappings below',
                    'Confirm or correct the mappings',
                    'Re-run the analysis for better results'
                ],
                'remediation_options': [
                    {
                        'option_id': 'confirm_mappings',
                        'title': 'Confirm Mappings',
                        'description': 'Review and confirm the suggested mappings',
                        'action_type': 'manual',
                        'one_click': False
                    },
                    {
                        'option_id': 'rerun_analysis',
                        'title': 'Re-run Analysis',
                        'description': 'Re-run the full analysis for better accuracy',
                        'action_type': 'rerun',
                        'one_click': True
                    }
                ]
            },
            'parse_failure': {
                'title': 'File Parse Failed',
                'message': 'We couldn\'t parse your file. This might be due to encoding issues, delimiter problems, or file format.',
                'severity': 'error',
                'actionable_steps': [
                    'Check if your file is in CSV format',
                    'Ensure proper encoding (UTF-8 recommended)',
                    'Download the sanitized sample to verify your data'
                ],
                'remediation_options': [
                    {
                        'option_id': 'download_sanitized',
                        'title': 'Download Sanitized Sample',
                        'description': 'Download a cleaned version of your file',
                        'action_type': 'download',
                        'one_click': True
                    },
                    {
                        'option_id': 'manual_upload',
                        'title': 'Manual Upload',
                        'description': 'Upload a corrected version of your file',
                        'action_type': 'manual',
                        'one_click': False
                    }
                ]
            },
            'data_quality_issues': {
                'title': 'Data Quality Issues',
                'message': 'We found some data quality issues that might affect analysis accuracy.',
                'severity': 'warning',
                'actionable_steps': [
                    'Review the data quality report',
                    'Clean your data if necessary',
                    'Re-run the analysis after cleaning'
                ],
                'remediation_options': [
                    {
                        'option_id': 'view_quality_report',
                        'title': 'View Quality Report',
                        'description': 'See detailed data quality information',
                        'action_type': 'manual',
                        'one_click': False
                    },
                    {
                        'option_id': 'auto_clean',
                        'title': 'Auto Clean Data',
                        'description': 'Let us automatically clean your data',
                        'action_type': 'automated',
                        'one_click': True
                    }
                ]
            }
        }
    
    def generate_error_messages(self, analysis_results: Dict[str, Any]) -> UXResult:
        """Generate meaningful error messages based on analysis results."""
        start_time = datetime.now()
        
        try:
            error_messages = []
            remediation_options = []
            
            # Check for missing date column
            if self._has_missing_date_column(analysis_results):
                error_msg = self._create_error_message('missing_date_column', analysis_results)
                error_messages.append(error_msg)
                remediation_options.extend(error_msg.remediation_options)
            
            # Check for low confidence mappings
            if self._has_low_confidence_mappings(analysis_results):
                error_msg = self._create_error_message('low_confidence_mapping', analysis_results)
                error_messages.append(error_msg)
                remediation_options.extend(error_msg.remediation_options)
            
            # Check for parse failures
            if self._has_parse_failures(analysis_results):
                error_msg = self._create_error_message('parse_failure', analysis_results)
                error_messages.append(error_msg)
                remediation_options.extend(error_msg.remediation_options)
            
            # Check for data quality issues
            if self._has_data_quality_issues(analysis_results):
                error_msg = self._create_error_message('data_quality_issues', analysis_results)
                error_messages.append(error_msg)
                remediation_options.extend(error_msg.remediation_options)
            
            # Limit remediation options
            remediation_options = remediation_options[:self.max_remediation_options]
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics['error_messages_generated'] += len(error_messages)
            self.metrics['remediation_options_provided'] += len(remediation_options)
            self.metrics['processing_time_ms'] = processing_time * 1000
            
            return UXResult(
                success=True,
                error_messages=error_messages,
                remediation_options=remediation_options,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            return UXResult(
                success=False,
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def _has_missing_date_column(self, analysis_results: Dict[str, Any]) -> bool:
        """Check if date column is missing."""
        try:
            # Check if Date column exists in mapped columns
            mapped_columns = analysis_results.get('mapped_columns', [])
            date_columns = [col for col in mapped_columns if col.get('mapped_column', '').lower() == 'date']
            return len(date_columns) == 0
        except Exception:
            return False
    
    def _has_low_confidence_mappings(self, analysis_results: Dict[str, Any]) -> bool:
        """Check if there are low confidence mappings."""
        try:
            mapped_columns = analysis_results.get('mapped_columns', [])
            low_confidence_count = sum(1 for col in mapped_columns if col.get('confidence', 100) < 80)
            return low_confidence_count > 0
        except Exception:
            return False
    
    def _has_parse_failures(self, analysis_results: Dict[str, Any]) -> bool:
        """Check if there were parse failures."""
        try:
            # Check for parse errors in the results
            return 'parse_error' in analysis_results or 'file_error' in analysis_results
        except Exception:
            return False
    
    def _has_data_quality_issues(self, analysis_results: Dict[str, Any]) -> bool:
        """Check if there are data quality issues."""
        try:
            data_quality = analysis_results.get('data_quality', {})
            return data_quality.get('has_issues', False)
        except Exception:
            return False
    
    def _create_error_message(self, error_type: str, analysis_results: Dict[str, Any]) -> ErrorMessage:
        """Create an error message for a specific error type."""
        template = self.message_templates.get(error_type, {})
        
        # Customize message based on analysis results
        context = self._get_error_context(error_type, analysis_results)
        
        return ErrorMessage(
            error_type=error_type,
            severity=template.get('severity', 'error'),
            title=template.get('title', 'Error'),
            message=template.get('message', 'An error occurred'),
            actionable_steps=template.get('actionable_steps', []),
            remediation_options=self._create_remediation_options(template.get('remediation_options', []), context),
            context=context
        )
    
    def _get_error_context(self, error_type: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get context information for error messages."""
        context = {}
        
        if error_type == 'missing_date_column':
            context['available_columns'] = [col.get('original_column', '') for col in analysis_results.get('mapped_columns', [])]
            context['suggested_date_columns'] = self._find_potential_date_columns(analysis_results)
        
        elif error_type == 'low_confidence_mapping':
            context['low_confidence_columns'] = [
                col for col in analysis_results.get('mapped_columns', [])
                if col.get('confidence', 100) < 80
            ]
        
        elif error_type == 'parse_failure':
            context['file_info'] = analysis_results.get('file_info', {})
            context['parse_errors'] = analysis_results.get('parse_errors', [])
        
        elif error_type == 'data_quality_issues':
            context['quality_issues'] = analysis_results.get('data_quality', {}).get('issues', [])
            context['quality_score'] = analysis_results.get('data_quality', {}).get('score', 0)
        
        return context
    
    def _find_potential_date_columns(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Find potential date columns in the data."""
        potential_columns = []
        
        try:
            mapped_columns = analysis_results.get('mapped_columns', [])
            for col in mapped_columns:
                original_name = col.get('original_column', '').lower()
                if any(keyword in original_name for keyword in ['date', 'time', 'created', 'updated', 'order']):
                    potential_columns.append(col.get('original_column', ''))
        except Exception:
            pass
        
        return potential_columns
    
    def _create_remediation_options(self, template_options: List[Dict[str, Any]], context: Dict[str, Any]) -> List[RemediationOption]:
        """Create remediation options from templates."""
        options = []
        
        for template in template_options:
            option = RemediationOption(
                option_id=template.get('option_id', ''),
                title=template.get('title', ''),
                description=template.get('description', ''),
                action_type=template.get('action_type', 'manual'),
                parameters=self._get_remediation_parameters(template, context),
                confidence=self._calculate_remediation_confidence(template, context),
                one_click=template.get('one_click', False)
            )
            options.append(option)
        
        return options
    
    def _get_remediation_parameters(self, template: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Get parameters for remediation options."""
        parameters = {}
        
        if template.get('action_type') == 'remap':
            parameters['available_columns'] = context.get('available_columns', [])
            parameters['suggested_columns'] = context.get('suggested_date_columns', [])
        
        elif template.get('action_type') == 'download':
            parameters['file_type'] = 'sanitized_sample'
            parameters['include_instructions'] = True
        
        elif template.get('action_type') == 'rerun':
            parameters['analysis_type'] = 'full_rerun'
            parameters['include_improvements'] = True
        
        return parameters
    
    def _calculate_remediation_confidence(self, template: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate confidence for remediation options."""
        base_confidence = 0.7
        
        if template.get('action_type') == 'remap' and context.get('suggested_date_columns'):
            base_confidence = 0.9
        
        elif template.get('action_type') == 'automated':
            base_confidence = 0.8
        
        elif template.get('one_click'):
            base_confidence = 0.85
        
        return min(base_confidence, 1.0)
    
    def create_remap_ui(self, column_mapping: Dict[str, str], available_columns: List[str]) -> Dict[str, Any]:
        """Create minimal UI for remapping columns."""
        try:
            # Get top 3 best guesses for each column
            remap_options = {}
            
            for original_col, current_mapping in column_mapping.items():
                # Find best alternatives
                alternatives = self._find_column_alternatives(original_col, available_columns)
                remap_options[original_col] = {
                    'current_mapping': current_mapping,
                    'alternatives': alternatives[:3],  # Top 3 alternatives
                    'confidence': self._calculate_mapping_confidence(original_col, current_mapping)
                }
            
            return {
                'remap_options': remap_options,
                'ui_type': 'minimal_remap',
                'instructions': 'Select the correct mapping for each column',
                'one_click': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'ui_type': 'error',
                'message': 'Unable to create remap UI'
            }
    
    def _find_column_alternatives(self, original_col: str, available_columns: List[str]) -> List[Dict[str, Any]]:
        """Find alternative mappings for a column."""
        alternatives = []
        
        for col in available_columns:
            if col != original_col:
                confidence = self._calculate_similarity(original_col, col)
                if confidence > 0.3:  # Minimum similarity threshold
                    alternatives.append({
                        'column': col,
                        'confidence': confidence,
                        'reason': self._get_similarity_reason(original_col, col)
                    })
        
        # Sort by confidence
        alternatives.sort(key=lambda x: x['confidence'], reverse=True)
        return alternatives
    
    def _calculate_similarity(self, col1: str, col2: str) -> float:
        """Calculate similarity between two column names."""
        try:
            # Simple similarity calculation
            col1_lower = col1.lower()
            col2_lower = col2.lower()
            
            # Check for exact match
            if col1_lower == col2_lower:
                return 1.0
            
            # Check for substring match
            if col1_lower in col2_lower or col2_lower in col1_lower:
                return 0.8
            
            # Check for common keywords
            common_keywords = ['date', 'time', 'sales', 'amount', 'product', 'customer', 'region']
            col1_keywords = [kw for kw in common_keywords if kw in col1_lower]
            col2_keywords = [kw for kw in common_keywords if kw in col2_lower]
            
            if col1_keywords and col2_keywords:
                intersection = set(col1_keywords) & set(col2_keywords)
                if intersection:
                    return 0.6
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _get_similarity_reason(self, col1: str, col2: str) -> str:
        """Get reason for similarity between columns."""
        try:
            col1_lower = col1.lower()
            col2_lower = col2.lower()
            
            if col1_lower == col2_lower:
                return "Exact match"
            
            if col1_lower in col2_lower or col2_lower in col1_lower:
                return "Substring match"
            
            # Check for common keywords
            common_keywords = ['date', 'time', 'sales', 'amount', 'product', 'customer', 'region']
            col1_keywords = [kw for kw in common_keywords if kw in col1_lower]
            col2_keywords = [kw for kw in common_keywords if kw in col2_lower]
            
            if col1_keywords and col2_keywords:
                intersection = set(col1_keywords) & set(col2_keywords)
                if intersection:
                    return f"Common keywords: {', '.join(intersection)}"
            
            return "Low similarity"
            
        except Exception:
            return "Unknown"
    
    def _calculate_mapping_confidence(self, original_col: str, mapped_col: str) -> float:
        """Calculate confidence for a column mapping."""
        return self._calculate_similarity(original_col, mapped_col)
    
    def create_sanitized_sample(self, df: pd.DataFrame, issues: List[str]) -> Dict[str, Any]:
        """Create a sanitized sample with instructions."""
        try:
            # Create sanitized version
            sanitized_df = df.copy()
            
            # Apply basic sanitization
            for col in sanitized_df.columns:
                if sanitized_df[col].dtype == 'object':
                    # Clean string columns
                    sanitized_df[col] = sanitized_df[col].astype(str).str.strip()
                    sanitized_df[col] = sanitized_df[col].replace('', np.nan)
            
            # Create instructions based on issues
            instructions = self._generate_sanitization_instructions(issues)
            
            # Convert to CSV
            csv_buffer = io.StringIO()
            sanitized_df.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()
            
            # Encode for download
            encoded_content = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
            
            return {
                'sanitized_data': encoded_content,
                'filename': 'sanitized_sample.csv',
                'instructions': instructions,
                'issues_fixed': issues,
                'download_ready': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Unable to create sanitized sample'
            }
    
    def _generate_sanitization_instructions(self, issues: List[str]) -> List[str]:
        """Generate instructions for sanitizing data."""
        instructions = [
            "This sanitized sample has been cleaned to address common data issues:",
            "",
            "1. Removed extra whitespace from text columns",
            "2. Standardized missing values",
            "3. Cleaned up formatting issues",
            "",
            "To use this sample:",
            "1. Download the sanitized_sample.csv file",
            "2. Review the changes made",
            "3. Apply similar cleaning to your original file",
            "4. Re-upload the cleaned file"
        ]
        
        if 'encoding' in issues:
            instructions.append("5. Ensure your file is saved as UTF-8 encoding")
        
        if 'delimiter' in issues:
            instructions.append("6. Use comma (,) as the delimiter")
        
        return instructions
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            'error_messages_generated': 0,
            'remediation_options_provided': 0,
            'one_click_actions': 0,
            'automated_remediations': 0,
            'user_satisfaction_score': 0.0,
            'processing_time_ms': 0.0
        }
    
    def emit_metrics(self):
        """Emit metrics for observability."""
        try:
            metrics = {
                "ux.error_messages_generated": self.metrics['error_messages_generated'],
                "ux.remediation_options_provided": self.metrics['remediation_options_provided'],
                "ux.one_click_actions": self.metrics['one_click_actions'],
                "ux.automated_remediations": self.metrics['automated_remediations'],
                "ux.user_satisfaction_score": self.metrics['user_satisfaction_score'],
                "ux.processing_time_ms": self.metrics['processing_time_ms']
            }
            
            # In a real implementation, you would send these to your metrics system
            print(f"📊 UX remediation metrics: {metrics}")
            return metrics
            
        except Exception as e:
            print(f"⚠️ Error emitting UX remediation metrics: {e}")
            return {"ux.metrics_error": str(e)}

# Global UX remediation instance
ux_remediation = UXRemediation()

def generate_error_messages(analysis_results: Dict[str, Any]) -> UXResult:
    """Convenience function to generate error messages."""
    return ux_remediation.generate_error_messages(analysis_results)

def create_remap_ui(column_mapping: Dict[str, str], available_columns: List[str]) -> Dict[str, Any]:
    """Convenience function to create remap UI."""
    return ux_remediation.create_remap_ui(column_mapping, available_columns)

def create_sanitized_sample(df: pd.DataFrame, issues: List[str]) -> Dict[str, Any]:
    """Convenience function to create sanitized sample."""
    return ux_remediation.create_sanitized_sample(df, issues)

if __name__ == "__main__":
    # Test the UX remediation
    print("🧪 Testing UX Remediation")
    print("=" * 50)
    
    # Test error message generation
    test_results = {
        'mapped_columns': [
            {'original_column': 'prod_desc', 'mapped_column': 'Product', 'confidence': 95},
            {'original_column': 'sales_amt', 'mapped_column': 'Sales', 'confidence': 90}
        ],
        'data_quality': {'has_issues': True, 'issues': ['missing_values', 'inconsistent_formatting']}
    }
    
    result = generate_error_messages(test_results)
    
    if result.success:
        print(f"✅ Successfully generated {len(result.error_messages)} error messages")
        print(f"✅ Provided {len(result.remediation_options)} remediation options")
        for msg in result.error_messages:
            print(f"   - {msg.title}: {msg.message}")
    else:
        print(f"❌ Error: {result.error_message}")
    
    # Test remap UI creation
    remap_ui = create_remap_ui(
        {'prod_desc': 'Product', 'sales_amt': 'Sales'},
        ['prod_desc', 'sales_amt', 'order_date', 'customer_name']
    )
    
    if 'error' not in remap_ui:
        print(f"✅ Successfully created remap UI")
        print(f"   - UI type: {remap_ui['ui_type']}")
        print(f"   - One click: {remap_ui['one_click']}")
    else:
        print(f"❌ Error creating remap UI: {remap_ui['error']}")
