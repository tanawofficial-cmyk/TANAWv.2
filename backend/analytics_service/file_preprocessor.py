"""
File Upload & Preprocessing Module
Phase 2: Extract headers, normalize, and store metadata

This module handles the initial processing of uploaded datasets:
- Extracts column headers (never sends actual data)  
- Normalizes headers for consistent processing
- Stores file metadata for tracking and reference
- Prepares data for the hybrid mapping pipeline
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import json
import re
import os
from pathlib import Path

try:
    from .hybrid_mapping_config import HybridMappingConfig, hybrid_config
except ImportError:
    from hybrid_mapping_config import HybridMappingConfig, hybrid_config

@dataclass
class FileMetadata:
    """Metadata extracted from uploaded file."""
    file_id: str
    original_filename: str
    file_size_bytes: int
    upload_timestamp: datetime
    user_id: Optional[str]
    
    # Dataset characteristics
    total_rows: int
    total_columns: int
    column_headers: List[str]
    normalized_headers: List[str]
    
    # Data type information
    column_data_types: Dict[str, str]
    null_percentages: Dict[str, float]
    sample_values: Dict[str, List[Any]]  # First few non-null values per column
    
    # Processing metadata
    preprocessing_timestamp: datetime
    preprocessing_version: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Handle datetime serialization
        result['upload_timestamp'] = self.upload_timestamp.isoformat()
        result['preprocessing_timestamp'] = self.preprocessing_timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileMetadata':
        """Create instance from dictionary."""
        # Handle datetime deserialization
        data['upload_timestamp'] = datetime.fromisoformat(data['upload_timestamp'])
        data['preprocessing_timestamp'] = datetime.fromisoformat(data['preprocessing_timestamp'])
        return cls(**data)

@dataclass
class HeaderNormalization:
    """Results of header normalization process."""
    original: str
    normalized: str
    transformations_applied: List[str]
    potential_issues: List[str]

class FilePreprocessor:
    """
    Handles file upload preprocessing for the hybrid mapping pipeline.
    
    Key Features:
    - Privacy-first: Never stores or transmits actual data values
    - Intelligent header extraction and normalization
    - Comprehensive metadata collection
    - Error handling and validation
    - Support for multiple file formats
    """
    
    def __init__(self, config: Optional[HybridMappingConfig] = None):
        self.config = config or hybrid_config
        self.supported_extensions = {'.csv', '.xlsx', '.xls', '.tsv', '.json'}
        self.preprocessing_version = "1.0.0"
    
    def process_uploaded_file(
        self,
        file_path: str,
        user_id: Optional[str] = None,
        original_filename: Optional[str] = None
    ) -> Tuple[FileMetadata, List[HeaderNormalization]]:
        """
        Process an uploaded file and extract metadata and normalized headers.
        
        Args:
            file_path: Path to the uploaded file
            user_id: Optional user identifier for tracking
            original_filename: Original filename if different from file_path
            
        Returns:
            Tuple of (FileMetadata, HeaderNormalization results)
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file doesn't exist
            Exception: For other processing errors
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_path = Path(file_path)
        if file_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        # Extract basic file info
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        upload_time = datetime.fromtimestamp(file_stats.st_mtime)
        
        # Generate unique file ID
        file_id = self._generate_file_id(file_path, user_id)
        
        # Load dataset and extract information
        df = self._load_dataset(file_path)
        
        # Extract headers and metadata
        headers = list(df.columns)
        normalized_results = self._normalize_headers(headers)
        normalized_headers = [nr.normalized for nr in normalized_results]
        
        # Analyze data types and characteristics
        column_info = self._analyze_columns(df)
        
        # Create metadata object
        metadata = FileMetadata(
            file_id=file_id,
            original_filename=original_filename or file_path.name,
            file_size_bytes=file_size,
            upload_timestamp=upload_time,
            user_id=user_id,
            total_rows=len(df),
            total_columns=len(df.columns),
            column_headers=headers,
            normalized_headers=normalized_headers,
            column_data_types=column_info['data_types'],
            null_percentages=column_info['null_percentages'],
            sample_values=column_info['sample_values'],
            preprocessing_timestamp=datetime.now(),
            preprocessing_version=self.preprocessing_version
        )
        
        return metadata, normalized_results
    
    def _load_dataset(self, file_path: Path) -> pd.DataFrame:
        """Load dataset from supported file formats."""
        try:
            extension = file_path.suffix.lower()
            
            if extension == '.csv':
                # Try multiple encodings and separators
                encodings = ['utf-8', 'latin-1', 'cp1252']
                separators = [',', ';', '\t']
                
                for encoding in encodings:
                    for sep in separators:
                        try:
                            df = pd.read_csv(file_path, encoding=encoding, sep=sep, nrows=1000)  # Limit rows for performance
                            if len(df.columns) > 1:  # Valid separation found
                                return pd.read_csv(file_path, encoding=encoding, sep=sep)
                        except:
                            continue
                
                # Fallback to default
                return pd.read_csv(file_path)
                
            elif extension in ['.xlsx', '.xls']:
                return pd.read_excel(file_path)
                
            elif extension == '.tsv':
                return pd.read_csv(file_path, sep='\t')
                
            elif extension == '.json':
                return pd.read_json(file_path)
                
            else:
                raise ValueError(f"Unsupported file extension: {extension}")
                
        except Exception as e:
            raise Exception(f"Failed to load dataset: {str(e)}")
    
    def _normalize_headers(self, headers: List[str]) -> List[HeaderNormalization]:
        """
        Normalize column headers for consistent processing.
        
        Normalization steps:
        1. Convert to lowercase
        2. Remove punctuation (except underscores)
        3. Replace spaces and hyphens with underscores
        4. Remove extra whitespace
        5. Handle special characters
        """
        results = []
        config = self.config.local_analyzer
        
        for header in headers:
            original = header
            normalized = header
            transformations = []
            issues = []
            
            # Track original for debugging
            if not isinstance(header, str):
                normalized = str(header)
                transformations.append("converted_to_string")
                if pd.isna(original):
                    issues.append("null_header_detected")
                    normalized = f"unnamed_column_{len(results)}"
                    transformations.append("null_header_replaced")
            
            # Convert to lowercase
            if config.normalize_case:
                if normalized != normalized.lower():
                    normalized = normalized.lower()
                    transformations.append("lowercased")
            
            # Trim whitespace
            if config.trim_whitespace:
                trimmed = normalized.strip()
                if trimmed != normalized:
                    normalized = trimmed
                    transformations.append("trimmed_whitespace")
            
            # Replace spaces and hyphens with underscores
            if config.replace_underscores:
                replaced = re.sub(r'[\s\-]+', '_', normalized)
                if replaced != normalized:
                    normalized = replaced
                    transformations.append("replaced_spaces_hyphens")
            
            # Remove punctuation (except underscores)
            if config.remove_punctuation:
                cleaned = re.sub(r'[^\w\s_]', '', normalized)
                if cleaned != normalized:
                    normalized = cleaned
                    transformations.append("removed_punctuation")
            
            # Handle multiple consecutive underscores
            deduplicated = re.sub(r'_+', '_', normalized)
            if deduplicated != normalized:
                normalized = deduplicated
                transformations.append("deduplicated_underscores")
            
            # Remove leading/trailing underscores
            stripped = normalized.strip('_')
            if stripped != normalized:
                normalized = stripped
                transformations.append("stripped_edge_underscores")
            
            # Check for potential issues
            if len(normalized) == 0:
                issues.append("empty_after_normalization")
                normalized = f"unnamed_column_{len(results)}"
                transformations.append("empty_header_replaced")
            
            if len(normalized) < config.alias_min_length and config.enable_partial_aliases:
                issues.append("very_short_header")
            
            if normalized.isdigit():
                issues.append("numeric_header")
            
            # Check for duplicates (basic check)
            existing_normalized = [r.normalized for r in results]
            if normalized in existing_normalized:
                issues.append("duplicate_normalized_header")
                counter = 1
                base_name = normalized
                while f"{base_name}_{counter}" in existing_normalized:
                    counter += 1
                normalized = f"{base_name}_{counter}"
                transformations.append("deduplicated_header")
            
            results.append(HeaderNormalization(
                original=original,
                normalized=normalized,
                transformations_applied=transformations,
                potential_issues=issues
            ))
        
        return results
    
    def _analyze_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze column characteristics without exposing sensitive data.
        
        Returns information about data types, null percentages, and 
        sanitized sample values for column mapping hints.
        """
        analysis = {
            'data_types': {},
            'null_percentages': {},
            'sample_values': {}
        }
        
        for column in df.columns:
            col_data = df[column]
            
            # Data type
            analysis['data_types'][column] = str(col_data.dtype)
            
            # Null percentage
            null_pct = (col_data.isnull().sum() / len(col_data)) * 100
            analysis['null_percentages'][column] = round(null_pct, 2)
            
            # Sample values (sanitized)
            non_null_values = col_data.dropna()
            if len(non_null_values) > 0:
                # Take up to 3 sample values for pattern recognition
                sample_size = min(3, len(non_null_values))
                samples = non_null_values.head(sample_size).tolist()
                
                # Sanitize samples (remove sensitive info, keep patterns)
                sanitized_samples = []
                for sample in samples:
                    sanitized = self._sanitize_sample_value(sample)
                    if sanitized:
                        sanitized_samples.append(sanitized)
                
                analysis['sample_values'][column] = sanitized_samples
            else:
                analysis['sample_values'][column] = []
        
        return analysis
    
    def _sanitize_sample_value(self, value: Any) -> Optional[str]:
        """
        Sanitize sample values to preserve patterns while protecting privacy.
        
        Returns pattern indicators rather than actual values.
        """
        if pd.isna(value):
            return None
            
        str_value = str(value)
        
        # Date patterns
        if re.match(r'\d{4}-\d{2}-\d{2}', str_value):
            return "YYYY-MM-DD_pattern"
        elif re.match(r'\d{2}/\d{2}/\d{4}', str_value):
            return "MM/DD/YYYY_pattern"
        elif re.match(r'\d{1,2}/\d{1,2}/\d{2,4}', str_value):
            return "date_pattern"
        
        # Numeric patterns
        if re.match(r'^\$?\d+\.?\d*$', str_value):
            return "currency_pattern" if '$' in str_value else "numeric_pattern"
        
        # ID patterns
        if re.match(r'^[A-Z0-9]{3,}-?[A-Z0-9]{3,}$', str_value.upper()):
            return "id_pattern"
        
        # Email pattern
        if '@' in str_value and '.' in str_value:
            return "email_pattern"
        
        # General text patterns
        if str_value.isalpha():
            return f"text_pattern_{len(str_value)}chars"
        elif str_value.isalnum():
            return f"alphanumeric_pattern_{len(str_value)}chars"
        elif str_value.isdigit():
            return f"number_pattern_{len(str_value)}digits"
        
        # Default pattern
        return f"mixed_pattern_{len(str_value)}chars"
    
    def _generate_file_id(self, file_path: Path, user_id: Optional[str]) -> str:
        """Generate unique file ID based on file content and metadata."""
        # Create hash from file path, size, and user
        hash_input = f"{file_path.name}_{file_path.stat().st_size}_{user_id or 'anonymous'}_{datetime.now().isoformat()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    def save_metadata(self, metadata: FileMetadata, output_dir: str = "metadata"):
        """Save file metadata to JSON for later use."""
        os.makedirs(output_dir, exist_ok=True)
        
        metadata_file = os.path.join(output_dir, f"{metadata.file_id}_metadata.json")
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)
        
        return metadata_file
    
    def load_metadata(self, file_id: str, metadata_dir: str = "metadata") -> Optional[FileMetadata]:
        """Load previously saved metadata."""
        metadata_file = os.path.join(metadata_dir, f"{file_id}_metadata.json")
        
        if not os.path.exists(metadata_file):
            return None
        
        with open(metadata_file, 'r') as f:
            data = json.load(f)
        
        return FileMetadata.from_dict(data)
    
    def get_preprocessing_summary(
        self, 
        metadata: FileMetadata, 
        normalization_results: List[HeaderNormalization]
    ) -> Dict[str, Any]:
        """Generate a summary of preprocessing results."""
        
        total_transformations = sum(len(nr.transformations_applied) for nr in normalization_results)
        total_issues = sum(len(nr.potential_issues) for nr in normalization_results)
        
        # Categorize issues
        issue_categories = {}
        for nr in normalization_results:
            for issue in nr.potential_issues:
                issue_categories[issue] = issue_categories.get(issue, 0) + 1
        
        # Data quality indicators
        high_null_columns = [
            col for col, pct in metadata.null_percentages.items() 
            if pct > self.config.analytics_activation.max_null_percentage * 100
        ]
        
        return {
            "file_info": {
                "file_id": metadata.file_id,
                "original_filename": metadata.original_filename,
                "size_mb": round(metadata.file_size_bytes / (1024 * 1024), 2),
                "rows": metadata.total_rows,
                "columns": metadata.total_columns
            },
            "header_processing": {
                "total_transformations": total_transformations,
                "total_issues": total_issues,
                "issue_breakdown": issue_categories,
                "normalization_success_rate": round(
                    (len(normalization_results) - len([nr for nr in normalization_results if nr.potential_issues])) / 
                    len(normalization_results) * 100, 1
                ) if normalization_results else 0
            },
            "data_quality": {
                "columns_with_high_nulls": len(high_null_columns),
                "high_null_columns": high_null_columns,
                "avg_null_percentage": round(
                    sum(metadata.null_percentages.values()) / len(metadata.null_percentages), 1
                ) if metadata.null_percentages else 0
            },
            "readiness_for_mapping": {
                "ready": total_issues == 0 and len(high_null_columns) == 0,
                "warnings": total_issues + len(high_null_columns),
                "recommendations": self._generate_preprocessing_recommendations(
                    normalization_results, high_null_columns
                )
            }
        }
    
    def _generate_preprocessing_recommendations(
        self, 
        normalization_results: List[HeaderNormalization],
        high_null_columns: List[str]
    ) -> List[str]:
        """Generate recommendations based on preprocessing analysis."""
        recommendations = []
        
        # Header recommendations
        problematic_headers = [nr for nr in normalization_results if nr.potential_issues]
        if problematic_headers:
            recommendations.append(f"Review {len(problematic_headers)} column headers with potential issues")
        
        # Data quality recommendations
        if high_null_columns:
            recommendations.append(f"Consider cleaning {len(high_null_columns)} columns with high null percentages")
        
        # Duplicate recommendations
        duplicates = [nr for nr in normalization_results if "duplicate_normalized_header" in nr.potential_issues]
        if duplicates:
            recommendations.append(f"Resolve {len(duplicates)} duplicate column names")
        
        # Short header recommendations
        short_headers = [nr for nr in normalization_results if "very_short_header" in nr.potential_issues]
        if short_headers:
            recommendations.append(f"Consider renaming {len(short_headers)} very short column headers")
        
        if not recommendations:
            recommendations.append("File is well-formatted and ready for column mapping")
        
        return recommendations

# Global instance for easy access
file_preprocessor = FilePreprocessor()
