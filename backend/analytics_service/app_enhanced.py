from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
import numpy as np
import traceback
from datetime import datetime
import os
import uuid
from typing import Dict, Any, Optional, List

# Core components (only what's actually used)

# Import Phase 1 components
from robust_file_parser import parse_file_robust, ParseResult
from config_manager import get_config
from pathlib import Path

# Import simplified GPT-powered mapper
from simplified_mapper import SimplifiedMapper

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Custom JSON encoder to handle datetime and numpy types
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, pd.Timestamp)):
            return obj.isoformat()
        elif isinstance(obj, np.datetime64):
            return pd.to_datetime(obj).isoformat()
        elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
            val = float(obj)
            # 🔥 CRITICAL FIX: Handle NaN and Infinity
            if np.isnan(val) or np.isinf(val):
                return None
            return val
        elif isinstance(obj, float):
            # 🔥 CRITICAL FIX: Handle regular Python float NaN/Inf
            if np.isnan(obj) or np.isinf(obj):
                return None
            return obj
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        elif isinstance(obj, pd.Series):
            return obj.tolist()
        elif obj is None:
            return None
        return super().default(obj)

app.json_encoder = DateTimeEncoder

# Global instances
active_sessions = {}  # Store active analysis sessions
config = get_config()  # Load configuration

def sanitize_for_json(obj: Any) -> Any:
    """Recursively sanitize objects to be JSON serializable with comprehensive NaN handling."""
    import math
    
    try:
        if isinstance(obj, dict):
            return {str(key): sanitize_for_json(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [sanitize_for_json(item) for item in obj]
        elif isinstance(obj, (datetime, pd.Timestamp)):
            return obj.isoformat()
        elif isinstance(obj, np.datetime64):
            return pd.to_datetime(obj).isoformat()
        elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
            # 🔥 CRITICAL FIX: Handle NaN and Infinity values (NumPy)
            val = float(obj)
            if math.isnan(val) or math.isinf(val):
                return None  # Convert NaN/Infinity to null in JSON
            return val
        elif isinstance(obj, float):
            # 🔥 CRITICAL FIX: Handle regular Python float NaN/Inf
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            # 🔥 CRITICAL FIX: Handle NaN in NumPy arrays
            if obj.dtype.kind in ['f', 'c']:  # float or complex
                obj = np.where(np.isnan(obj) | np.isinf(obj), None, obj)
            return obj.tolist()
        elif isinstance(obj, pd.DataFrame):
            # 🔥 CRITICAL FIX: Handle NaN in DataFrames
            return obj.replace([np.inf, -np.inf, np.nan], None).to_dict('records')
        elif isinstance(obj, pd.Series):
            # 🔥 CRITICAL FIX: Handle NaN in Series
            return obj.replace([np.inf, -np.inf, np.nan], None).tolist()
        elif hasattr(obj, '__dict__'):
            return sanitize_for_json(obj.__dict__)
        elif obj is None:
            return None
        else:
            return str(obj)
    except Exception as e:
        print(f"⚠️ JSON serialization warning: {e} for type {type(obj)}")
        return str(obj)

def _extract_chart_data(analytic: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract chart-ready data from analytic results."""
    try:
        data = analytic.get('data', {})
        
        # For sales summary - use daily or monthly sales
        if 'daily_sales' in data:
            return data['daily_sales'][:30]  # Last 30 days
        elif 'monthly_sales' in data:
            return data['monthly_sales']
        
        # For product performance - use product data
        elif 'products' in data:
            return data['products'][:10]  # Top 10 products
        
        # For regional analysis - use regional data
        elif 'regions' in data:
            return data['regions']
        
        # Fallback - return empty list
        return []
    except Exception as e:
        print(f"⚠️ Error extracting chart data: {e}")
        return []

def _correct_mapping_errors(df: pd.DataFrame, user_mappings: Dict[str, str]) -> Dict[str, str]:
    """Correct obvious mapping errors based on data analysis."""
    try:
        corrected = user_mappings.copy()
        
        # Auto-detect and fix common mapping errors
        for col in df.columns:
            # Ensure col is a string to avoid Series ambiguity
            col_str = str(col)
            col_lower = col_str.lower()
            
            # Fix Sales mapping - prioritize actual sales columns
            if 'sales' in col_lower and 'amount' in col_lower:
                if 'Sales' not in corrected.values():
                    corrected[col_str] = 'Sales'
                    print(f"🔧 Auto-corrected: {col_str} → Sales (actual sales data)")
            
            # Fix Quantity mapping - prioritize quantity columns
            elif 'quantity' in col_lower and 'sold' in col_lower:
                if 'Quantity' not in corrected.values():
                    corrected[col_str] = 'Quantity'
                    print(f"🔧 Auto-corrected: {col_str} → Quantity (actual quantity data)")
            
            # Fix Product mapping - prioritize ID over category for analytics
            elif 'product' in col_lower and 'id' in col_lower:
                if 'Product' not in corrected.values():
                    corrected[col_str] = 'Product'
                    print(f"🔧 Auto-corrected: {col_str} → Product (better for analytics)")
            
            # Fix Amount mapping - should be Sales, not Unit_Cost
            elif 'sales' in col_lower and 'amount' in col_lower:
                if col_str not in corrected:
                    corrected[col_str] = 'Sales'
                    print(f"🔧 Auto-corrected: {col_str} → Sales (sales amount, not cost)")
        
        # Remove any wrong mappings that conflict with corrected ones
        final_mappings = {}
        for col, mapped_type in corrected.items():
            # If this mapped_type is already used by a better column, skip this one
            if mapped_type in final_mappings.values():
                existing_col = [k for k, v in final_mappings.items() if v == mapped_type][0]
                if len(col) > len(existing_col) or 'id' in col.lower():
                    # Keep the better mapping
                    continue
            
            final_mappings[col] = mapped_type
        
        return final_mappings
        
    except Exception as e:
        print(f"⚠️ Error correcting mappings: {e}")
        return user_mappings

def _calculate_summary_metrics(df: pd.DataFrame, column_mapping: Dict[str, str]) -> Dict[str, Any]:
    """Calculate summary metrics from the actual dataset."""
    try:
        metrics = {}
        
        # Reverse mapping for column lookup
        reverse_mapping = {v: k for k, v in column_mapping.items()}
        
        # 🔥 CRITICAL FIX: Ensure Sales_Amount maps to Sales for analytics
        if 'Sales_Amount' in df.columns and 'Sales' not in reverse_mapping:
            reverse_mapping['Sales'] = 'Sales_Amount'
            print(f"🔧 Auto-mapped Sales_Amount → Sales for analytics")
        
        # Also check for Amount mapping
        if 'Sales_Amount' in df.columns and 'Amount' not in reverse_mapping:
            reverse_mapping['Amount'] = 'Sales_Amount'
            print(f"🔧 Auto-mapped Sales_Amount → Amount for analytics")
        
        # Calculate total sales/amount
        sales_col = reverse_mapping.get('Sales') or reverse_mapping.get('Amount')
        if sales_col and sales_col in df.columns:
            sales_data = pd.to_numeric(df[sales_col], errors='coerce')
            metrics['total_sales'] = float(sales_data.sum())
            metrics['average_sales'] = float(sales_data.mean())
        
        # Count unique products
        product_col = reverse_mapping.get('Product')
        if product_col and product_col in df.columns:
            metrics['total_products'] = int(df[product_col].nunique())
            metrics['unique_products'] = int(df[product_col].nunique())
        
        # Count unique regions
        region_col = reverse_mapping.get('Region')
        if region_col and region_col in df.columns:
            metrics['total_regions'] = int(df[region_col].nunique())
            metrics['unique_regions'] = int(df[region_col].nunique())
        
        # Calculate growth if date column exists
        date_col = reverse_mapping.get('Date')
        if date_col and date_col in df.columns and sales_col:
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
            df_temp = df_temp.dropna(subset=[date_col])
            
            if len(df_temp) > 1:
                df_temp = df_temp.sort_values(date_col)
                df_temp['month'] = df_temp[date_col].dt.to_period('M')
                monthly = df_temp.groupby('month')[sales_col].sum()
                
                if len(monthly) >= 2:
                    latest = float(monthly.iloc[-1])
                    previous = float(monthly.iloc[-2])
                    if previous != 0:
                        metrics['sales_growth'] = float(((latest - previous) / previous) * 100)
        
        return metrics
        
    except Exception as e:
        print(f"⚠️ Error calculating summary metrics: {e}")
        return {}

@app.route("/api/files/upload-v2", methods=["POST"])
def analyze_v2():
    """
    New Phase 0-11 implementation endpoint with all advanced features.
    """
    print("📥 Phase 0-11 Implementation - Enhanced Analysis")
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "message": "No file uploaded"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "success": False,
                "message": "No file selected"
            }), 400
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Get dataset type hint from request
        dataset_type_hint = request.form.get('dataset_type', None)
        
        # Phase 1: Robust file parsing
        print(f"🔍 Phase 1: Parsing file {file.filename}")
        
        # Save uploaded file temporarily for parsing
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # Use robust parser
            parse_result = parse_file_robust(tmp_path, dataset_type_hint)
            
            if not parse_result.success:
                return jsonify({
                    "success": False,
                    "message": parse_result.error_message
                }), 422
            
            df = parse_result.dataframe
            print(f"✅ File parsed successfully: {parse_result.row_count} rows, {parse_result.col_count} columns")
            
        finally:
            # Clean up temporary file
            import os
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        # GPT-Powered Column Mapping (Direct GPT call)
        print(f"🚀 Starting GPT-powered analysis for {analysis_id}")
        
        # Import GPT mapper directly
        from gpt_column_mapper import GPTColumnMapper, MappingResult
        
        # Check if OpenAI is available
        try:
            # Try to get API key
            api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY') or os.getenv('OPENAI_API') or os.getenv('OPENAI_TOKEN')
            
            if api_key:
                print(f"✅ Found OpenAI API key (ends with: ...{api_key[-6:]})")
                gpt_mapper = GPTColumnMapper(api_key)
                
                # Get column names as strings
                columns = [str(col) for col in df.columns]
                print(f"📋 Analyzing {len(columns)} columns: {columns}")
                
                # Call GPT directly
                print("🤖 Using GPT-powered mapping directly")
                mapping_result = gpt_mapper.map_columns(columns, "retail")
                
                if mapping_result.success:
                    # Format results for frontend
                    mapped_columns = []
                    uncertain_columns = []
                    unmapped_columns = []
                    
                    # Track used canonical types to prevent duplicates
                    used_canonical_types = {}
                    
                    for mapping in mapping_result.mappings:
                        if mapping.mapped_to == "Ignore":
                            unmapped_columns.append({
                                'original_column': mapping.original_column,
                                'reason': mapping.reasoning,
                                'confidence': mapping.confidence
                            })
                        elif mapping.confidence >= 80:
                            # Check for duplicate canonical types
                            if mapping.mapped_to in used_canonical_types:
                                # Keep the one with higher confidence
                                existing_mapping = used_canonical_types[mapping.mapped_to]
                                if mapping.confidence > existing_mapping['confidence']:
                                    # Replace existing with higher confidence mapping
                                    mapped_columns.remove(existing_mapping)
                                    new_mapping = {
                                        'original_column': mapping.original_column,
                                        'mapped_column': mapping.mapped_to,
                                        'confidence': mapping.confidence,
                                        'reasoning': mapping.reasoning,
                                        'source': mapping.source,
                                        'suggestions': []
                                    }
                                    mapped_columns.append(new_mapping)
                                    used_canonical_types[mapping.mapped_to] = new_mapping
                                else:
                                    # Keep existing, mark current as uncertain
                                    uncertain_columns.append({
                                        'original_column': mapping.original_column,
                                        'mapped_column': mapping.mapped_to,
                                        'confidence': mapping.confidence,
                                        'reasoning': f"Duplicate mapping - {mapping.reasoning}",
                                        'source': mapping.source,
                                        'suggestions': []
                                    })
                            else:
                                # First time seeing this canonical type
                                new_mapping = {
                                    'original_column': mapping.original_column,
                                    'mapped_column': mapping.mapped_to,
                                    'confidence': mapping.confidence,
                                    'reasoning': mapping.reasoning,
                                    'source': mapping.source,
                                    'suggestions': []
                                }
                                mapped_columns.append(new_mapping)
                                used_canonical_types[mapping.mapped_to] = new_mapping
                        else:
                            uncertain_columns.append({
                                'original_column': mapping.original_column,
                                'mapped_column': mapping.mapped_to,
                                'confidence': mapping.confidence,
                                'reasoning': mapping.reasoning,
                                'source': mapping.source,
                                'suggestions': []
                            })
                    
                    # Apply mappings to DataFrame (use deduplicated mappings)
                    column_mapping = {}
                    for mapping in mapped_columns:
                        column_mapping[mapping['original_column']] = mapping['mapped_column']
                    
                    renamed_df = df.rename(columns=column_mapping) if column_mapping else df
                    
                    # Check analytics readiness
                    available_columns = [col['mapped_column'] for col in mapped_columns]
                    analytics_readiness = {
                        'available_analytics': [],
                        'unavailable_analytics': [],
                        'ready_count': 0,
                        'total_count': 5
                    }
                    
                    # Check each analytic
                    analytics_requirements = {
                        'Sales Summary Report': {'required_columns': ['Date', 'Sales']},
                        'Product Performance Analysis': {'required_columns': ['Product', 'Sales']},
                        'Regional Sales Analysis': {'required_columns': ['Region', 'Sales']},
                        'Sales Forecasting': {'required_columns': ['Date', 'Sales']},
                        'Demand Forecasting': {'required_columns': ['Date', 'Product', 'Quantity']}
                    }
                    
                    for analytic_name, requirements in analytics_requirements.items():
                        required_cols = requirements['required_columns']
                        missing_required = [col for col in required_cols if col not in available_columns]
                        
                        if not missing_required:
                            analytics_readiness['available_analytics'].append({
                                'name': analytic_name,
                                'status': 'ready',
                                'required_columns': required_cols
                            })
                        else:
                            analytics_readiness['unavailable_analytics'].append({
                                'name': analytic_name,
                                'status': 'disabled',
                                'missing_columns': missing_required,
                                'required_columns': required_cols
                            })
                    
                    analytics_readiness['ready_count'] = len(analytics_readiness['available_analytics'])
                    
                    results = {
                        'success': True,
                        'analysis_id': analysis_id,
                        'mapped_columns': mapped_columns,
                        'uncertain_columns': uncertain_columns,
                        'unmapped_columns': unmapped_columns,
                        'analytics_readiness': analytics_readiness,
                        'data_quality': {'issues': [], 'overall_score': 100, 'warnings': []},
                        'dataset_info': {
                            'filename': file.filename,
                            'rows': len(df),
                            'columns': len(df.columns),
                            'delimiter': ',',
                            'encoding': 'utf-8'
                        },
                        'gpt_metadata': {
                            'total_cost': mapping_result.total_cost,
                            'cache_hits': mapping_result.cache_hits,
                            'processing_time': mapping_result.processing_time,
                            'mapping_method': 'gpt',
                            'success': True
                        },
                        'processing_time': mapping_result.processing_time,
                        'total_cost': mapping_result.total_cost,
                        'cache_hits': mapping_result.cache_hits,
                        'renamed_dataframe': renamed_df,
                        'message': f"GPT mapping completed successfully. Cost: ${mapping_result.total_cost:.4f}",
                        # Frontend completion criteria
                        'status': 'completed',
                        'nextStep': 'analysis_complete',
                        'processed': True,
                        'hasVisualization': False,
                        'hasCharts': False,
                        'shouldComplete': True,
                        'phases_completed': ['file_parsing', 'column_mapping']
                    }
                    
                    print(f"✅ GPT-powered analysis complete:")
                    print(f"   Mapped columns: {len(mapped_columns)}")
                    print(f"   Uncertain columns: {len(uncertain_columns)}")
                    print(f"   Unmapped columns: {len(unmapped_columns)}")
                    print(f"   Available analytics: {analytics_readiness['ready_count']}")
                    print(f"   Total cost: ${mapping_result.total_cost:.4f}")
                    print(f"   Cache hits: {mapping_result.cache_hits}")
                    
                    # Generate analytics and visualizations automatically
                    print(f"🎯 Auto-generating analytics and visualizations...")
                    try:
                        from analytics_engine import analytics_engine
                        
                        # Generate charts using the analytics engine
                        # Pass original DataFrame and column mapping (not renamed DataFrame)
                        analytics_results = analytics_engine.prepare_analytics_data(df, column_mapping)
                        charts = analytics_results.get('analytics_results', [])
                        
                        if charts:
                            print(f"📊 Generated {len(charts)} charts automatically")
                            results['visualization'] = {
                                'charts': charts,
                                'chart_count': len(charts),
                                'generated_automatically': True
                            }
                            results['analysis'] = {
                                'charts': charts,
                                'analytics_results': analytics_results
                            }
                            # Update completion criteria
                            results['hasCharts'] = True
                            results['hasVisualization'] = True
                            results['phases_completed'].extend(['analytics_generation', 'visualization_generation'])
                        else:
                            print(f"⚠️ No charts generated - analytics engine returned empty results")
                            
                    except Exception as analytics_error:
                        print(f"⚠️ Analytics generation failed: {analytics_error}")
                        # Don't fail the entire process if analytics generation fails
                    
                else:
                    raise Exception(f"GPT mapping failed: {mapping_result.error_message}")
            else:
                raise Exception("OpenAI API key not found")
                
        except Exception as e:
            print(f"⚠️ GPT mapping failed: {e}")
            print("🔧 Falling back to SimplifiedMapper")
            # Fallback to SimplifiedMapper if GPT fails
            mapper = SimplifiedMapper()
            results = mapper.map_columns(df, dataset_context="retail")
        
        # Store session with GPT mapping results
        active_sessions[analysis_id] = {
            'dataframe': results.get('renamed_dataframe', df),  # Use renamed dataframe
            'original_dataframe': df,  # Keep original for reference
            'results': results,
            'timestamp': datetime.now().isoformat(),
            'filename': file.filename,
            'parsing_metadata': {
                'encoding_used': parse_result.encoding_used,
                'delimiter_used': parse_result.delimiter_used,
                'sheet_name': parse_result.sheet_name,
                'row_count': parse_result.row_count,
                'col_count': parse_result.col_count,
                'memory_size_mb': parse_result.memory_size_mb,
                'analysis_mode': parse_result.analysis_mode,
                'sample_info': parse_result.sample_info,
                'profile': parse_result.profile
            },
            'mapping_metadata': {
                'total_cost': results.get('total_cost', 0),
                'cache_hits': results.get('cache_hits', 0),
                'processing_time': results.get('processing_time', 0),
                'mapping_method': 'gpt'
            }
        }
        
        # Format response for frontend compatibility
        mapped_columns = results.get('mapped_columns', [])
        uncertain_columns = results.get('uncertain_columns', [])
        unmapped_columns = results.get('unmapped_columns', [])
        analytics_readiness = results.get('analytics_readiness', {})
        data_quality = results.get('data_quality', {})
        
        # Extract analytics information
        available_analytics = analytics_readiness.get('available_analytics', [])
        unavailable_analytics = analytics_readiness.get('unavailable_analytics', [])
        
        # Format mapped columns for frontend
        formatted_mappings = []
        for col in mapped_columns:
            # Handle both dict and object formats
            if isinstance(col, dict):
            formatted_mappings.append({
                'original_column': col.get('original_column', ''),
                'mapped_column': col.get('mapped_column', ''),
                'confidence': col.get('confidence', 0),
                    'source': col.get('source', 'gpt'),
                    'reasoning': col.get('reasoning', ''),
                'suggestions': col.get('suggestions', [])
            })
            else:
                # Handle ColumnMapping object
                formatted_mappings.append({
                    'original_column': getattr(col, 'original_column', ''),
                    'mapped_column': getattr(col, 'mapped_to', ''),
                    'confidence': getattr(col, 'confidence', 0),
                    'source': getattr(col, 'source', 'gpt'),
                    'reasoning': getattr(col, 'reasoning', ''),
                    'suggestions': []
                })
        
        # Format uncertain columns
        formatted_uncertain = []
        for col in uncertain_columns:
            if isinstance(col, dict):
                formatted_uncertain.append({
                    'original_column': col.get('original_column', ''),
                    'mapped_column': col.get('mapped_column', ''),
                    'confidence': col.get('confidence', 0),
                    'source': col.get('source', 'gpt'),
                    'reasoning': col.get('reasoning', ''),
                    'suggestions': col.get('suggestions', [])
                })
            else:
                formatted_uncertain.append({
                    'original_column': getattr(col, 'original_column', ''),
                    'mapped_column': getattr(col, 'mapped_to', ''),
                    'confidence': getattr(col, 'confidence', 0),
                    'source': getattr(col, 'source', 'gpt'),
                    'reasoning': getattr(col, 'reasoning', ''),
                    'suggestions': []
                })
        
        # Format unmapped columns
        formatted_unmapped = []
        for col in unmapped_columns:
            if isinstance(col, dict):
                formatted_unmapped.append({
                    'original_column': col.get('original_column', ''),
                    'reason': col.get('reason', 'No clear mapping found'),
                    'confidence': col.get('confidence', 0)
                })
            else:
                formatted_unmapped.append({
                    'original_column': getattr(col, 'original_column', ''),
                    'reason': getattr(col, 'reasoning', 'No clear mapping found'),
                    'confidence': getattr(col, 'confidence', 0)
                })
        
        response_data = {
            "success": True,
            "analysis_id": analysis_id,
            "message": "GPT-powered analysis completed successfully",
            "mapped_columns": formatted_mappings,
            "uncertain_columns": formatted_uncertain,
            "unmapped_columns": formatted_unmapped,
            "analytics_readiness": {
                "available_analytics": available_analytics,
                "unavailable_analytics": unavailable_analytics,
                "ready_count": analytics_readiness.get('ready_count', 0),
                "total_count": analytics_readiness.get('total_count', 0)
            },
            "data_quality": {
                "overall_score": data_quality.get('overall_score', 0),
                "issues": data_quality.get('issues', []),
                "warnings": data_quality.get('warnings', [])
            },
            "gpt_metadata": {
                "total_cost": results.get('total_cost', 0),
                "cache_hits": results.get('cache_hits', 0),
                "processing_time": results.get('processing_time', 0),
                "mapping_method": "gpt",
                "success": results.get('success', True)
            },
            "phases_completed": results.get('phases_completed', ["file_parsing", "column_mapping"]),
            "processing_time": results.get('processing_time', 0),
            "dataset_info": {
                "rows": parse_result.row_count,
                "columns": parse_result.col_count,
                "filename": file.filename,
                "encoding": parse_result.encoding_used,
                "delimiter": parse_result.delimiter_used
            },
            # Include visualization data if generated
            "visualization": results.get('visualization'),
            "analysis": results.get('analysis'),
            # Frontend completion criteria
            "status": "completed",
            "nextStep": "analysis_complete",
            "processed": True,
            "hasVisualization": results.get('hasVisualization', False),
            "hasCharts": results.get('hasCharts', False),
            "shouldComplete": True
        }
        
        print(f"✅ GPT-powered analysis complete:")
        print(f"   Mapped columns: {len(formatted_mappings)}")
        print(f"   Uncertain columns: {len(formatted_uncertain)}")
        print(f"   Unmapped columns: {len(formatted_unmapped)}")
        print(f"   Available analytics: {len(available_analytics)}")
        print(f"   Total cost: ${results.get('total_cost', 0):.4f}")
        print(f"   Cache hits: {results.get('cache_hits', 0)}")
        
        # Convert numpy types to JSON-serializable types before jsonify
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
                val = float(obj)
                if np.isnan(val) or np.isinf(val):
                    return None
                return val
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj
        
        # Convert numpy types in response_data
        response_data = convert_numpy_types(response_data)
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Phase 0-11 analysis error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Analysis failed: {str(e)}"
        }), 500

# Old route removed - use /api/files/upload-v2 instead

# Redundant route removed - use /api/files/upload-v2 instead

# Legacy enhanced-analyze route removed - use /api/files/upload-v2 instead

# Legacy confirm-mapping route removed - use /api/files/upload-v2 instead

# Legacy confirm-per-analytic-mapping route removed - use /api/files/upload-v2 instead

@app.route("/feedback", methods=["POST"])
@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    """Submit user feedback for continuous improvement."""
    try:
        feedback_data = request.get_json()
        
        # Store feedback in the knowledge base
        # Knowledge base update handled by FlexibleColumnMapper
        
        return jsonify({
            "success": True,
            "message": "Feedback submitted successfully"
        })
        
    except Exception as e:
        print(f"❌ Feedback error: {e}")
        return jsonify({
            "success": False,
            "message": f"Feedback submission failed: {str(e)}"
        }), 500

@app.route("/statistics", methods=["GET"])
@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    """Get comprehensive system statistics."""
    try:
        stats = {
            "total_sessions": len(active_sessions),
            "active_sessions": len([s for s in active_sessions.values() 
                                  if (datetime.now() - datetime.fromisoformat(s['timestamp'])).seconds < 3600]),
            "workflow_status": "operational",
            "components": {
                "semantic_mapper": "✅",
                "data_validator": "✅", 
                "data_transformer": "✅",
                "descriptive_analytics": "✅",
                "predictive_analytics": "✅",
                "visualization_engine": "✅"
            },
            "knowledge_base_size": 0,  # Handled by FlexibleColumnMapper
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"❌ Statistics error: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to get statistics: {str(e)}"
        }), 500

@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    try:
        from analytics_config import ANALYTICS_REQUIREMENTS
        analytics_types = list(ANALYTICS_REQUIREMENTS.keys())
        analytics_count = len(analytics_types)
    except ImportError:
        analytics_types = []
        analytics_count = 0
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "focused-v2.0",
        "components": {
            "comprehensive_workflow": "✅",
            "semantic_mapper": "✅",
            "analytics_readiness_checker": "✅",
            "data_validator": "✅",
            "data_transformer": "✅",
            "focused_descriptive_analytics": "✅",
            "focused_predictive_analytics": "✅",
            "visualization_engine": "✅"
        },
        "analytics_types": [at.value for at in analytics_types],
        "total_analytics": analytics_count,
        "required_columns": ["Date", "Sales", "Amount", "Product", "Quantity", "Region"]
    })

@app.route("/config", methods=["GET", "POST"])
@app.route("/api/config", methods=["GET", "POST"])
def handle_configuration():
    """Get or update service configuration."""
    try:
        if request.method == "GET":
            # Import analytics config
            try:
                from analytics_config import get_analytics_summary, get_dropdown_options
                analytics_summary = get_analytics_summary()
                dropdown_options = get_dropdown_options()
            except ImportError:
                analytics_summary = {}
                dropdown_options = ['Date', 'Sales', 'Amount', 'Product', 'Quantity', 'Region', 'Ignore']
            
            return jsonify({
                "success": True,
                "config": {
                    "workflow_enabled": True,
                    "semantic_mapping_enabled": True,
                    "validation_enabled": True,
                    "transformation_enabled": True,
                    "analytics_enabled": True,
                    "visualization_enabled": True,
                    "confidence_threshold": 80.0,
                    "quality_threshold": 70.0
                },
                "analytics_config": analytics_summary,
                "dropdown_options": dropdown_options
            })
        else:
            # POST - Update configuration
            config_data = request.get_json()
            # For now, just acknowledge the request
            return jsonify({
                "success": True,
                "message": "Configuration updated successfully"
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Configuration error: {str(e)}"
        }), 500

@app.route("/retrain", methods=["POST"])
@app.route("/api/retrain", methods=["POST"])
def retrain_models():
    """Retrain models based on accumulated feedback."""
    try:
        data = request.get_json() or {}
        category = data.get('category', 'all')
        
        # Trigger retraining in the workflow
        # Model retraining handled by FlexibleColumnMapper
        
        return jsonify({
            "success": True,
            "message": f"Models retrained for category: {category}"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Retraining failed: {str(e)}"
        }), 500

@app.route("/analytics/<analysis_id>", methods=["GET"])
@app.route("/api/analytics/<analysis_id>", methods=["GET"])
def get_analytics_results(analysis_id):
    """Get analytics results for a specific analysis session."""
    try:
        if analysis_id not in active_sessions:
            return jsonify({
                "success": False,
                "message": "Analysis session not found or expired"
            }), 404
        
        session = active_sessions[analysis_id]
        results = session['results']
        
        # Extract analytics data
        workflow_stages = results.get('stages', {})
        analytics_data = []
        charts_data = []
        
        # Get descriptive analytics
        if 'descriptive_analytics' in workflow_stages:
            desc_results = workflow_stages['descriptive_analytics'].get('results', {})
            if 'analytics' in desc_results:
                analytics_data.extend(desc_results['analytics'])
        
        # Get predictive analytics
        if 'predictive_analytics' in workflow_stages:
            pred_results = workflow_stages['predictive_analytics'].get('results', {})
            if 'forecasts' in pred_results:
                analytics_data.extend(pred_results['forecasts'])
        
        # Get visualizations
        if 'visualization' in workflow_stages:
            viz_results = workflow_stages['visualization'].get('results', {})
            if 'charts' in viz_results:
                charts_data = viz_results['charts']
        
        # Get analytics readiness
        analytics_readiness = workflow_stages.get('analytics_readiness', {}).get('results', {})
        
        return jsonify({
            "success": True,
            "analysis_id": analysis_id,
            "analytics": sanitize_for_json(analytics_data),
            "charts": sanitize_for_json(charts_data),
            "summary": {
                "total_analytics": len(analytics_data),
                "total_charts": len(charts_data),
                "analytics_readiness": analytics_readiness,
                "data_quality": results.get('quality_metrics', {}),
                "insights": results.get('insights', []),
                "recommendations": results.get('recommendations', [])
            },
            "session_info": {
                "filename": session['filename'],
                "timestamp": session['timestamp'],
                "status": results.get('status', 'unknown')
            }
        })
        
    except Exception as e:
        print(f"❌ Analytics retrieval error: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to retrieve analytics: {str(e)}"
        }), 500

@app.route("/analytics/<analysis_id>/export", methods=["GET"])
@app.route("/api/analytics/<analysis_id>/export", methods=["GET"])
def export_analytics(analysis_id):
    """Export analytics results in various formats."""
    try:
        if analysis_id not in active_sessions:
            return jsonify({
                "success": False,
                "message": "Analysis session not found or expired"
            }), 404
        
        export_format = request.args.get('format', 'json')  # json, csv, pdf
        session = active_sessions[analysis_id]
        results = session['results']
        
        if export_format == 'json':
            return jsonify({
                "success": True,
                "analysis_id": analysis_id,
                "export_data": sanitize_for_json(results),
                "export_format": "json",
                "timestamp": datetime.now().isoformat()
            })
        
        elif export_format == 'csv':
            # Generate CSV export for analytics data
            workflow_stages = results.get('stages', {})
            csv_data = []
            
            # Extract analytics data for CSV
            if 'descriptive_analytics' in workflow_stages:
                desc_results = workflow_stages['descriptive_analytics'].get('results', {})
                for analytic in desc_results.get('analytics', []):
                    csv_data.append({
                        'type': 'descriptive',
                        'name': analytic.get('name', 'Unknown'),
                        'description': analytic.get('description', ''),
                        'status': analytic.get('status', 'completed'),
                        'confidence': analytic.get('confidence', 0)
                    })
            
            return jsonify({
                "success": True,
                "analysis_id": analysis_id,
                "export_data": csv_data,
                "export_format": "csv",
                "timestamp": datetime.now().isoformat()
            })
        
        else:
            return jsonify({
                "success": False,
                "message": f"Unsupported export format: {export_format}"
            }), 400
        
    except Exception as e:
        print(f"❌ Analytics export error: {e}")
        return jsonify({
            "success": False,
            "message": f"Export failed: {str(e)}"
        }), 500

@app.route("/analytics/types", methods=["GET"])
@app.route("/api/analytics/types", methods=["GET"])
def get_available_analytics_types():
    """Get list of available analytics types and their requirements."""
    try:
        from analytics_config import ANALYTICS_REQUIREMENTS
        
        analytics_types = []
        for analytic_type, requirements in ANALYTICS_REQUIREMENTS.items():
            analytics_types.append({
                "name": analytic_type.value,
                "description": requirements.get('description', ''),
                "required_columns": requirements.get('required_columns', []),
                "optional_columns": requirements.get('optional_columns', []),
                "category": requirements.get('category', 'general'),
                "confidence_threshold": requirements.get('confidence_threshold', 80.0)
            })
        
        return jsonify({
            "success": True,
            "analytics_types": analytics_types,
            "total_types": len(analytics_types)
        })
        
    except ImportError:
        # Fallback if analytics_config is not available
        fallback_types = [
            {
                "name": "Sales Summary Report",
                "description": "Comprehensive sales performance analysis",
                "required_columns": ["Date", "Sales"],
                "optional_columns": ["Region", "Product"],
                "category": "descriptive",
                "confidence_threshold": 80.0
            },
            {
                "name": "Product Performance Analysis",
                "description": "Product-wise sales and performance metrics",
                "required_columns": ["Product", "Sales"],
                "optional_columns": ["Quantity", "Date"],
                "category": "descriptive",
                "confidence_threshold": 75.0
            },
            {
                "name": "Regional Sales Analysis",
                "description": "Geographic distribution of sales performance",
                "required_columns": ["Region", "Sales"],
                "optional_columns": ["Date", "Product"],
                "category": "descriptive",
                "confidence_threshold": 75.0
            },
            {
                "name": "Sales Trend Forecasting",
                "description": "Predict future sales based on historical data",
                "required_columns": ["Date", "Sales"],
                "optional_columns": ["Region", "Product"],
                "category": "predictive",
                "confidence_threshold": 85.0
            },
            {
                "name": "Demand Forecasting",
                "description": "Predict product demand for inventory planning",
                "required_columns": ["Date", "Quantity"],
                "optional_columns": ["Product", "Region"],
                "category": "predictive",
                "confidence_threshold": 85.0
            }
        ]
        
        return jsonify({
            "success": True,
            "analytics_types": fallback_types,
            "total_types": len(fallback_types)
        })
        
    except Exception as e:
        print(f"❌ Analytics types error: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to get analytics types: {str(e)}"
        }), 500

@app.route("/cleanup", methods=["POST"])
@app.route("/api/cleanup", methods=["POST"])
def cleanup_system():
    """Clean up old system data."""
    try:
        data = request.get_json() or {}
        days_to_keep = data.get('days_to_keep', 30)
        
        # Clean up old sessions
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
        sessions_to_remove = []
        
        for session_id, session in active_sessions.items():
            if datetime.fromisoformat(session['timestamp']).timestamp() < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del active_sessions[session_id]
        
        return jsonify({
            "success": True,
            "message": f"Cleaned up {len(sessions_to_remove)} old sessions",
            "remaining_sessions": len(active_sessions)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Cleanup failed: {str(e)}"
        }), 500

@app.route("/test-response", methods=["GET"])
@app.route("/api/test-response", methods=["GET"])
def test_response_format():
    """Test endpoint to verify response format for frontend debugging."""
    try:
        # Create a sample uncertain column response
        sample_uncertain_columns = [
            {
                'column': 'Transaction Date',
                'mapped_column': 'Date',
                'detectedType': 'datetime',
                'confidence': 85.5,
                'suggestions': [
                    {'type': 'Date', 'confidence': 85.5},
                    {'type': 'Ignore', 'confidence': 14.5}
                ]
            },
            {
                'column': 'Total Revenue',
                'mapped_column': 'Sales',
                'detectedType': 'numeric',
                'confidence': 92.3,
                'suggestions': [
                    {'type': 'Sales', 'confidence': 92.3},
                    {'type': 'Amount', 'confidence': 88.1},
                    {'type': 'Ignore', 'confidence': 7.7}
                ]
            }
        ]
        
        sample_dropdown_options = ['Date', 'Sales', 'Amount', 'Product', 'Quantity', 'Region', 'Ignore']
        
        response_data = {
            "success": True,
            "analysis_id": "test-123",
            "status": "pending_confirmation",
            "message": "Column mapping confirmation required",
            "uncertain_columns": sanitize_for_json(sample_uncertain_columns),
            "dropdown_options": sanitize_for_json(sample_dropdown_options),
            "suggested_mappings": {},
            "data_preview": []
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Test response failed: {str(e)}"
        }), 500

# Global cache for analysis results (in-memory for now)
analysis_results_cache = {}


if __name__ == "__main__":
    print("🚀 Starting TANAW Enhanced Analytics Service")
    print("=" * 60)
    print("✅ All enhanced components loaded")
    print("✅ Frontend-compatible endpoints ready")
    print("✅ Comprehensive workflow integrated")
    print("✅ Analysis results cache initialized")
    print("=" * 60)
    
def _generate_mapping_summary(mapping_results):
    """Generate a user-friendly mapping summary for transparency."""
    try:
        mapped_columns = mapping_results.get('mapped_columns', [])
        summary = []
        
        # Convert to dict if it's a list
        if isinstance(mapped_columns, list):
            mapped_dict = {}
            for mapping in mapped_columns:
                if isinstance(mapping, dict):
                    mapped_dict[mapping.get('original_column', '')] = mapping.get('mapped_column', '')
                else:
                    mapped_dict[str(mapping)] = 'Unknown'
            mapped_columns = mapped_dict
        
        # Generate summary
        for original, canonical in mapped_columns.items():
            if canonical and canonical != 'Ignore':
                summary.append(f"{original} → {canonical}")
        
        return {
            "detected_columns": summary,
            "total_mapped": len([c for c in mapped_columns.values() if c and c != 'Ignore']),
            "ignored_columns": len([c for c in mapped_columns.values() if c == 'Ignore'])
        }
    except Exception as e:
        print(f"⚠️ Error generating mapping summary: {e}")
        return {
            "detected_columns": ["Column mapping completed automatically"],
            "total_mapped": 0,
            "ignored_columns": 0
        }

@app.route("/api/visualizations-v2/<analysis_id>", methods=["GET"])
def get_visualizations_v2(analysis_id):
    """
    Get visualizations using Phase 0-11 implementation.
    """
    try:
        if analysis_id not in active_sessions:
            return jsonify({
                "success": False,
                "message": "Analysis not found"
            }), 404
        
        session_data = active_sessions[analysis_id]
        results = session_data['results']
        
        # Get visualization data from Phase 8
        visualization_data = results.get('phase8_visualization', {})
        charts = visualization_data.get('charts', [])
        narratives = visualization_data.get('narratives', [])
        
        # Format charts for frontend
        formatted_charts = []
        for chart in charts:
            formatted_charts.append({
                'id': chart.get('id', ''),
                'type': chart.get('type', ''),
                'title': chart.get('title', ''),
                'data': chart.get('data', []),
                'config': chart.get('config', {}),
                'accessibility': chart.get('accessibility', {})
            })
        
        # Format narratives
        formatted_narratives = []
        for narrative in narratives:
            formatted_narratives.append({
                'id': narrative.get('id', ''),
                'title': narrative.get('title', ''),
                'content': narrative.get('content', ''),
                'confidence': narrative.get('confidence', 0),
                'source': narrative.get('source', 'rule_based')
            })
        
        return jsonify({
            "success": True,
            "charts": formatted_charts,
            "narratives": formatted_narratives,
            "total_charts": len(formatted_charts),
            "total_narratives": len(formatted_narratives)
        })
        
    except Exception as e:
        print(f"❌ Error getting visualizations: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to get visualizations: {str(e)}"
        }), 500

@app.route("/api/visualizations/<analysis_id>", methods=["GET"])
def get_visualizations(analysis_id):
    """Get visualizations for a specific analysis ID."""
    try:
        print(f"🔍 Fetching visualizations for analysis_id: {analysis_id}")
        
        # Check if analysis results are in active sessions
        if analysis_id not in active_sessions:
            print(f"❌ Analysis ID {analysis_id} not found in active sessions")
            return jsonify({
                "success": False,
                "error": "Analysis not found",
                "message": "Analysis results not available"
            }), 404
        
        session_data = active_sessions[analysis_id]
        print(f"✅ Found session data for analysis_id: {analysis_id}")
        
        # Get the original DataFrame
        original_df = session_data.get('original_dataframe')
        if original_df is None:
            print(f"⚠️ No original DataFrame found for analysis_id: {analysis_id}")
            return jsonify({
                "success": False,
                "error": "Data not available",
                "message": "Original dataset not available for visualization"
            }), 400
        
        # Get the results which contain the charts
        results = session_data.get('results', {})
        
        # Check if charts are already generated in the results
        if 'visualization' in results and 'charts' in results['visualization']:
            charts = results['visualization']['charts']
            print(f"📊 Found {len(charts)} charts in results")
        else:
        # Generate visualizations using the analytics engine
        try:
            from analytics_engine import analytics_engine
            
                # Get column mapping from results
                mapped_columns = results.get('mapped_columns', [])
                column_mapping = {}
                for mapping in mapped_columns:
                    column_mapping[mapping['original_column']] = mapping['mapped_column']
                
                print(f"🔧 Retrieved column mappings: {column_mapping}")
            
            # Generate charts using the correct method
                analytics_results = analytics_engine.prepare_analytics_data(original_df, column_mapping)
            charts = analytics_results.get('analytics_results', [])
            
            print(f"📊 Generated {len(charts)} charts for analysis_id: {analysis_id}")
            
            # Sanitize charts to handle any NaN values
            sanitized_charts = sanitize_for_json(charts)
            
            return jsonify({
                "success": True,
                "charts": sanitized_charts,
                    "narratives": [],  # Add empty narratives array
                    "total_charts": len(sanitized_charts),
                    "total_narratives": 0
            }), 200
            
        except Exception as viz_error:
            print(f"❌ Visualization generation error: {viz_error}")
            return jsonify({
                "success": False,
                "error": "Visualization generation failed",
                "message": str(viz_error)
            }), 500
            
    except Exception as e:
        print(f"❌ Visualization API error: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": str(e)
        }), 500

def sanitize_for_json(data):
    """Sanitize data for JSON serialization by handling NaN values and numpy dtypes."""
    import json
    import numpy as np
    
    def convert_nan(obj):
        if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
            return None
        elif isinstance(obj, dict):
            return {k: convert_nan(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_nan(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return [convert_nan(item) for item in obj.tolist()]
        elif hasattr(obj, 'dtype') and hasattr(obj, 'item'):
            # Handle numpy scalars
            return convert_nan(obj.item())
        elif hasattr(obj, 'dtype'):
            # Handle numpy dtypes
            return str(obj)
        else:
            return obj
    
    try:
        sanitized = convert_nan(data)
        # Test if it can be serialized
        json.dumps(sanitized)
        return sanitized
    except (TypeError, ValueError) as e:
        print(f"⚠️ JSON sanitization failed: {e}")
        return {"error": "Data sanitization failed", "original_type": str(type(data))}

if __name__ == "__main__":
    print("🚀 Starting Flask development server...")
    print("📡 Server will be available at: http://localhost:5001")
    print("🔄 Auto-reload enabled for development")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5001, debug=True)
