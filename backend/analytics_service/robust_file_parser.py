"""
Robust File Parser for TANAW Phase 1
Implements comprehensive file parsing with encoding detection, delimiter detection,
and fallback mechanisms for various file formats.

Features:
- Multi-encoding support with fallback chain
- Automatic delimiter detection
- Excel format support (.xlsx, .xls, .xlsm)
- Error handling with user-friendly messages
- Data profiling and sampling
- Memory-efficient processing
"""

import pandas as pd
import numpy as np
import csv
import chardet
import openpyxl
import xlrd
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
import warnings
import traceback
from datetime import datetime

# Import configuration
from config_manager import get_config

@dataclass
class ParseResult:
    """Result of file parsing operation."""
    success: bool
    dataframe: Optional[pd.DataFrame] = None
    error_message: Optional[str] = None
    encoding_used: Optional[str] = None
    delimiter_used: Optional[str] = None
    sheet_name: Optional[str] = None
    row_count: int = 0
    col_count: int = 0
    memory_size_mb: float = 0.0
    analysis_mode: str = "full"  # "full" or "sampled"
    sample_info: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None

@dataclass
class DataProfile:
    """Data profiling information."""
    row_count: int
    col_count: int
    memory_size_mb: float
    dtypes: Dict[str, str]
    null_pct: Dict[str, float]
    duplicate_rows: int
    analysis_mode: str
    sample_info: Optional[Dict[str, Any]] = None

class RobustFileParser:
    """
    Robust file parser with comprehensive error handling and fallback mechanisms.
    
    Implements Phase 1 requirements:
    - Robust parsing with encoding/delimiter detection
    - Multiple fallback strategies
    - Data profiling and sampling
    - User-friendly error messages
    """
    
    def __init__(self, config=None):
        """Initialize parser with configuration."""
        self.config = config or get_config()
        self.encoding_fallbacks = self.config.file_processing.encoding_fallbacks
        self.max_file_size_mb = self.config.file_processing.max_file_size_mb
        self.sample_rows_limit = self.config.file_processing.sample_rows_limit
        self.sample_min = self.config.file_processing.sample_min
        
    def parse_file(self, file_path: Union[str, Path], dataset_type_hint: Optional[str] = None) -> ParseResult:
        """
        Parse a file with comprehensive error handling and fallback mechanisms.
        
        Args:
            file_path: Path to the file to parse
            dataset_type_hint: Optional hint about dataset type
            
        Returns:
            ParseResult with parsing outcome and data
        """
        file_path = Path(file_path)
        start_time = datetime.now()
        
        try:
            # Validate file exists and size
            if not file_path.exists():
                self._emit_parse_metrics("file_not_found", 0, 0, 0, start_time)
                return ParseResult(
                    success=False,
                    error_message=f"File not found: {file_path}"
                )
            
            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                self._emit_parse_metrics("file_too_large", file_size_mb, 0, 0, start_time)
                return ParseResult(
                    success=False,
                    error_message=f"File too large: {file_size_mb:.1f}MB > {self.max_file_size_mb}MB limit"
                )
            
            # Determine parsing strategy based on file extension
            if file_path.suffix.lower() == '.csv':
                result = self._parse_csv(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls', '.xlsm']:
                result = self._parse_excel(file_path)
            elif file_path.suffix.lower() == '.tsv':
                result = self._parse_tsv(file_path)
            else:
                self._emit_parse_metrics("unsupported_format", file_size_mb, 0, 0, start_time)
                return ParseResult(
                    success=False,
                    error_message=f"Unsupported file format: {file_path.suffix}"
                )
            
            # Emit success metrics
            if result.success:
                self._emit_parse_metrics("success", file_size_mb, result.row_count, result.col_count, start_time)
            else:
                self._emit_parse_metrics("parse_error", file_size_mb, 0, 0, start_time)
            
            return result
                
        except Exception as e:
            self._emit_parse_metrics("unexpected_error", file_size_mb, 0, 0, start_time)
            return ParseResult(
                success=False,
                error_message=f"Unexpected error parsing file: {str(e)}"
            )
    
    def _parse_csv(self, file_path: Path) -> ParseResult:
        """Parse CSV file with encoding and delimiter detection."""
        try:
            # Try pandas default first
            df = pd.read_csv(file_path)
            encoding_used = "utf-8"  # pandas default
            delimiter_used = ","
            
        except (UnicodeDecodeError, UnicodeError) as e:
            print(f"⚠️ Unicode error with default encoding: {e}")
            # Try encoding fallbacks
            df = None
            encoding_used = None
            delimiter_used = None
            
            for encoding in self.encoding_fallbacks:
                try:
                    print(f"🔄 Trying encoding: {encoding}")
                    df = pd.read_csv(file_path, encoding=encoding)
                    encoding_used = encoding
                    delimiter_used = ","
                    print(f"✅ Success with encoding: {encoding}")
                    break
                except Exception as enc_error:
                    print(f"❌ Failed with {encoding}: {enc_error}")
                    continue
            
            if df is None:
                # Try with delimiter detection
                try:
                    print("🔄 Trying delimiter detection...")
                    with open(file_path, 'rb') as f:
                        sample = f.read(1024)
                        detected = chardet.detect(sample)
                        encoding = detected['encoding']
                    
                    # Try detected encoding with different delimiters
                    for delimiter in [',', ';', '\t', '|']:
                        try:
                            df = pd.read_csv(file_path, encoding=encoding, sep=delimiter)
                            encoding_used = encoding
                            delimiter_used = delimiter
                            print(f"✅ Success with detected encoding {encoding} and delimiter '{delimiter}'")
                            break
                        except Exception:
                            continue
                            
                except Exception as detect_error:
                    print(f"❌ Delimiter detection failed: {detect_error}")
            
            if df is None:
                return ParseResult(
                    success=False,
                    error_message="Unable to parse CSV file. Please ensure the file is properly encoded (UTF-8, UTF-16, Latin-1, or CP1252) and has a standard delimiter (comma, semicolon, tab, or pipe)."
                )
        
        except Exception as e:
            return ParseResult(
                success=False,
                error_message=f"Error parsing CSV file: {str(e)}"
            )
        
        # Profile and sample the data
        profile = self._profile_data(df)
        sampled_df, sample_info = self._create_sample(df)
        
        return ParseResult(
            success=True,
            dataframe=sampled_df,
            encoding_used=encoding_used,
            delimiter_used=delimiter_used,
            row_count=len(df),
            col_count=len(df.columns),
            memory_size_mb=df.memory_usage(deep=True).sum() / (1024 * 1024),
            analysis_mode=profile.analysis_mode,
            sample_info=sample_info,
            profile=self._serialize_profile(profile)
        )
    
    def _parse_excel(self, file_path: Path) -> ParseResult:
        """Parse Excel file with sheet selection."""
        try:
            # Try openpyxl first (for .xlsx)
            if file_path.suffix.lower() in ['.xlsx', '.xlsm']:
                try:
                    df = pd.read_excel(file_path, engine='openpyxl')
                    sheet_name = "Sheet1"  # Default sheet
                except Exception as e:
                    print(f"⚠️ openpyxl failed: {e}")
                    raise e
            else:
                # Try xlrd for .xls files
                try:
                    df = pd.read_excel(file_path, engine='xlrd')
                    sheet_name = "Sheet1"
                except Exception as e:
                    print(f"⚠️ xlrd failed: {e}")
                    # Fallback to openpyxl
                    df = pd.read_excel(file_path, engine='openpyxl')
                    sheet_name = "Sheet1"
            
            # Handle multiple sheets - select the one with most columns > 3
            if isinstance(df, dict):  # Multiple sheets
                best_sheet = None
                max_cols = 0
                for sheet_name, sheet_df in df.items():
                    if len(sheet_df.columns) > max_cols and len(sheet_df.columns) > 3:
                        max_cols = len(sheet_df.columns)
                        best_sheet = sheet_name
                        df = sheet_df
                
                if best_sheet:
                    sheet_name = best_sheet
                    print(f"📊 Selected sheet '{sheet_name}' with {max_cols} columns")
                else:
                    # Use first sheet if no good candidate
                    sheet_name = list(df.keys())[0]
                    df = df[sheet_name]
                    print(f"📊 Using first sheet '{sheet_name}'")
            
            # Handle merged header rows
            df = self._flatten_headers(df)
            
            # Profile and sample the data
            profile = self._profile_data(df)
            sampled_df, sample_info = self._create_sample(df)
            
            return ParseResult(
                success=True,
                dataframe=sampled_df,
                sheet_name=sheet_name,
                row_count=len(df),
                col_count=len(df.columns),
                memory_size_mb=df.memory_usage(deep=True).sum() / (1024 * 1024),
                analysis_mode=profile.analysis_mode,
                sample_info=sample_info,
                profile=self._serialize_profile(profile)
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                error_message=f"Error parsing Excel file: {str(e)}. Please ensure the file is not corrupted and contains valid data."
            )
    
    def _parse_tsv(self, file_path: Path) -> ParseResult:
        """Parse TSV (Tab-Separated Values) file."""
        try:
            df = pd.read_csv(file_path, sep='\t')
            
            # Profile and sample the data
            profile = self._profile_data(df)
            sampled_df, sample_info = self._create_sample(df)
            
            return ParseResult(
                success=True,
                dataframe=sampled_df,
                delimiter_used='\t',
                row_count=len(df),
                col_count=len(df.columns),
                memory_size_mb=df.memory_usage(deep=True).sum() / (1024 * 1024),
                analysis_mode=profile.analysis_mode,
                sample_info=sample_info,
                profile=self._serialize_profile(profile)
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                error_message=f"Error parsing TSV file: {str(e)}"
            )
    
    def _flatten_headers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Flatten merged header rows in Excel files."""
        try:
            # Check if first row has many NaN values (indicates merged headers)
            if df.iloc[0].isna().sum() > len(df.columns) * 0.5:
                # Use second row as headers
                df.columns = df.iloc[1]
                df = df.drop([0, 1]).reset_index(drop=True)
                print("🔧 Flattened merged header rows")
            
            # Clean column names
            df.columns = [str(col).strip() for col in df.columns]
            
            return df
        except Exception as e:
            print(f"⚠️ Header flattening failed: {e}")
            return df
    
    def _profile_data(self, df: pd.DataFrame) -> DataProfile:
        """Create comprehensive data profile."""
        try:
            # Basic metrics
            row_count = len(df)
            col_count = len(df.columns)
            memory_size_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
            
            # Data types
            dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
            
            # Null percentages
            null_pct = {col: (df[col].isna().sum() / len(df)) * 100 for col in df.columns}
            
            # Duplicate rows
            duplicate_rows = df.duplicated().sum()
            
            # Determine analysis mode
            analysis_mode = "full" if row_count < 100000 else "sampled"
            
            return DataProfile(
                row_count=row_count,
                col_count=col_count,
                memory_size_mb=memory_size_mb,
                dtypes=dtypes,
                null_pct=null_pct,
                duplicate_rows=duplicate_rows,
                analysis_mode=analysis_mode
            )
            
        except Exception as e:
            print(f"⚠️ Error profiling data: {e}")
            return DataProfile(
                row_count=len(df),
                col_count=len(df.columns),
                memory_size_mb=0.0,
                dtypes={},
                null_pct={},
                duplicate_rows=0,
                analysis_mode="full"
            )
    
    def _create_sample(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Create representative sample of data."""
        try:
            if len(df) <= self.sample_rows_limit:
                # No sampling needed
                return df, {"sampled": False, "original_rows": len(df)}
            
            # Create representative sample
            sample_size = min(self.sample_rows_limit, len(df))
            
            # Combine head, tail, and random sample
            head_size = min(20, sample_size // 3)
            tail_size = min(20, sample_size // 3)
            random_size = sample_size - head_size - tail_size
            
            samples = []
            
            # Add head
            if head_size > 0:
                samples.append(df.head(head_size))
            
            # Add tail
            if tail_size > 0:
                samples.append(df.tail(tail_size))
            
            # Add random sample
            if random_size > 0:
                random_indices = np.random.choice(
                    df.index[head_size:-tail_size] if tail_size > 0 else df.index[head_size:],
                    size=min(random_size, len(df) - head_size - tail_size),
                    replace=False
                )
                samples.append(df.loc[random_indices])
            
            # Combine samples
            sampled_df = pd.concat(samples, ignore_index=True)
            
            sample_info = {
                "sampled": True,
                "original_rows": len(df),
                "sample_rows": len(sampled_df),
                "head_size": head_size,
                "tail_size": tail_size,
                "random_size": random_size
            }
            
            return sampled_df, sample_info
            
        except Exception as e:
            print(f"⚠️ Error creating sample: {e}")
            return df, {"sampled": False, "error": str(e)}
    
    def _serialize_profile(self, profile: DataProfile) -> Dict[str, Any]:
        """Serialize profile for JSON response."""
        return {
            "row_count": profile.row_count,
            "col_count": profile.col_count,
            "memory_size_mb": round(profile.memory_size_mb, 2),
            "dtypes": profile.dtypes,
            "null_pct": {k: round(v, 2) for k, v in profile.null_pct.items()},
            "duplicate_rows": profile.duplicate_rows,
            "analysis_mode": profile.analysis_mode,
            "sample_info": profile.sample_info
        }
    
    def _emit_parse_metrics(self, status: str, file_size_mb: float, row_count: int, col_count: int, start_time: datetime):
        """Emit parsing metrics for observability."""
        try:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            metrics = {
                "parse.status": status,
                "parse.file_size_mb": round(file_size_mb, 2),
                "parse.row_count": row_count,
                "parse.col_count": col_count,
                "parse.duration_ms": round(duration_ms, 2),
                "parse.sample_mode": row_count > self.sample_rows_limit
            }
            
            # In a real implementation, you would send these to your metrics system
            print(f"📊 Parse metrics: {metrics}")
            return metrics
            
        except Exception as e:
            print(f"⚠️ Error emitting parse metrics: {e}")
            return {"parse.status": "error", "parse.error": str(e)}

# Global parser instance
robust_parser = RobustFileParser()

def parse_file_robust(file_path: Union[str, Path], dataset_type_hint: Optional[str] = None) -> ParseResult:
    """
    Convenience function to parse a file with robust error handling.
    
    Args:
        file_path: Path to the file to parse
        dataset_type_hint: Optional hint about dataset type
        
    Returns:
        ParseResult with parsing outcome and data
    """
    return robust_parser.parse_file(file_path, dataset_type_hint)

if __name__ == "__main__":
    # Test the parser
    print("🧪 Testing Robust File Parser")
    print("=" * 50)
    
    # Test with a sample file (if available)
    test_files = [
        "test_data/sample_sales.csv",
        "test_data/sample_sales.xlsx",
        "test_data/sample_sales.tsv"
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\n📁 Testing: {test_file}")
            result = parse_file_robust(test_file)
            
            if result.success:
                print(f"✅ Success!")
                print(f"   Rows: {result.row_count}")
                print(f"   Columns: {result.col_count}")
                print(f"   Encoding: {result.encoding_used}")
                print(f"   Delimiter: {result.delimiter_used}")
                print(f"   Analysis Mode: {result.analysis_mode}")
            else:
                print(f"❌ Failed: {result.error_message}")
        else:
            print(f"📁 Test file not found: {test_file}")
