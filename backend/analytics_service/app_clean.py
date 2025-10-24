#!/usr/bin/env python3
"""
TANAW Clean Architecture - OpenAI + TANAW Processing
Pure implementation: GPT for mapping, TANAW for everything else
"""

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
from pathlib import Path
import math

# Core components - only what we need
from robust_file_parser import parse_file_robust, ParseResult
from gpt_column_mapper import GPTColumnMapper, MappingResult
from config_manager import get_config

# Multi-domain analytics modules
from domain_detector import TANAWDomainDetector, DomainClassification
from inventory_analytics import TANAWInventoryAnalytics
from finance_analytics import TANAWFinanceAnalytics
from customer_analytics import TANAWCustomerAnalytics
from narrative_insights import TANAWNarrativeInsights
from conversational_insights import TANAWConversationalInsights
from anomaly_detector import TANAWAnomalyDetector

# Safe numeric data sanitization to prevent Infinity/NumPy types in JSON
def sanitize_numeric_data(data):
    """
    Safely sanitize numeric data to prevent Infinity/NaN and NumPy types in JSON responses.
    Converts NumPy types to native Python types and handles Infinity values.
    """
    # Handle NumPy types first
    if hasattr(data, 'dtype'):  # NumPy array or scalar
        if hasattr(data, 'item'):  # NumPy scalar
            return sanitize_numeric_data(data.item())
        else:  # NumPy array
            return [sanitize_numeric_data(item) for item in data]
    elif isinstance(data, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        # Convert NumPy integers to Python int
        return int(data)
    elif isinstance(data, (np.floating, np.float64, np.float32, np.float16)):
        # Convert NumPy floats to Python float, handle Infinity
        value = float(data)
        return 0 if not math.isfinite(value) else value
    elif isinstance(data, np.bool_):
        # Convert NumPy bool to Python bool
        return bool(data)
    elif isinstance(data, dict):
        # Recursively sanitize dictionary values
        return {key: sanitize_numeric_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        # Check if it's a numeric array (Y-axis data)
        if all(isinstance(x, (int, float, np.integer, np.floating)) for x in data):
            # Sanitize numeric array - convert NumPy types and replace Infinity/NaN with 0
            return [0 if not math.isfinite(float(x)) else int(x) if isinstance(x, (np.integer, np.int64, np.int32)) else float(x) for x in data]
        else:
            # Recursively sanitize list elements
            return [sanitize_numeric_data(item) for item in data]
    elif isinstance(data, (int, float)):
        # Sanitize individual numeric values
        return 0 if not math.isfinite(data) else data
    else:
        # Return other types unchanged (strings, booleans, etc.)
        return data
from predictive_analytics import TANAWPredictiveAnalytics
from data_profiler import TANAWDataProfiler
from axis_resolver import TANAWAxisResolver
from transformer import TANAWChartTransformer
from chart_validator import TANAWChartValidator
from bar_chart_generator import TANAWBarChartGenerator
from line_chart_generator import TANAWLineChartGenerator
from semantic_detector import TANAWSemanticDetector
from sales_forecast_generator import TANAWSalesForecastGenerator
from stock_forecast_generator import TANAWStockForecastGenerator
# from data_processor import TANAWDataProcessorCore  # Removed - using original method

app = Flask(__name__)
CORS(app)

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
            if np.isnan(val) or np.isinf(val):
                return None
            return val
        elif isinstance(obj, float):
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
active_sessions = {}

class TANAWDataProcessor:
    """
    TANAW Data Processing Engine
    Handles: Data cleaning, transformation, analytics, and visualization
    """
    
    def __init__(self):
        # Initialize domain detection and analytics modules
        self.domain_detector = TANAWDomainDetector()
        self.inventory_analytics = TANAWInventoryAnalytics()
        self.finance_analytics = TANAWFinanceAnalytics()
        self.customer_analytics = TANAWCustomerAnalytics()
        
        # Initialize narrative insights generator
        import os
        from pathlib import Path
        from dotenv import load_dotenv
        
        # Try to load .env file manually from multiple locations
        env_paths = [
            Path(__file__).parent / '.env',  # analytics_service/.env
            Path(__file__).parent.parent / '.env',  # backend/.env
        ]
        
        env_loaded = False
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                print(f"🔍 Loaded .env file from: {env_path}")
                env_loaded = True
                break
        
        if not env_loaded:
            print(f"🔍 No .env file found in any of: {env_paths}")
        
        # Try multiple ways to get the API key
        openai_key = (
            os.getenv('OPENAI_API_KEY') or 
            os.getenv('OPENAI_KEY') or 
            os.getenv('OPENAI_API') or 
            os.getenv('OPENAI_TOKEN') or
            getattr(get_config().openai, 'api_key', None)
        )
        
        # Store the OpenAI API key for use across modules
        self.openai_api_key = openai_key
        
        if openai_key and openai_key != "sk-your-openai-api-key-here":
            print(f"🔑 OpenAI key found: {openai_key[:10]}...")
            self.narrative_insights = TANAWNarrativeInsights(openai_key)
            self.conversational_insights = TANAWConversationalInsights(openai_key)
        else:
            print("⚠️ No OpenAI key found - narrative insights disabled")
            print(f"🔍 Debug: os.getenv('OPENAI_API_KEY') = {os.getenv('OPENAI_API_KEY')}")
            print(f"🔍 Debug: config.openai.api_key = {getattr(get_config().openai, 'api_key', None)}")
            self.narrative_insights = None
            self.conversational_insights = None
        
        # Initialize anomaly detector
        self.anomaly_detector = TANAWAnomalyDetector()
        
        # Initialize predictive analytics
        self.predictive_analytics = TANAWPredictiveAnalytics()
        
        # P1: Data Profiler (read-only)
        self.data_profiler = TANAWDataProfiler()
        # P2: Axis Resolver (non-blocking suggestions)
        self.axis_resolver = TANAWAxisResolver()
        self.chart_transformer = TANAWChartTransformer()
        self.chart_validator = TANAWChartValidator()
        
        # Semantic Detector (NEW! - Determines Sales vs Inventory context)
        self.semantic_detector = TANAWSemanticDetector(openai_api_key=self.openai_api_key)
        
        # Phase 1: Bar Chart Generator (focused development)
        self.bar_chart_generator = TANAWBarChartGenerator()
        
        # Phase 2: Line Chart Generator (time series analysis)
        self.line_chart_generator = TANAWLineChartGenerator()
        
        # Phase 3: Sales Forecast Generator (predictive analytics)
        self.sales_forecast_generator = TANAWSalesForecastGenerator()
        
        # Phase 4: Stock Forecast Generator (inventory predictive analytics)
        self.stock_forecast_generator = TANAWStockForecastGenerator()
        
        # Smart Analytics Engine removed - using simpler approach
        
        # Data processor removed - using original analytics generation
        
        # STEP 1: Define Analytic Profiles - Distinct X/Y/Group/Chart per Analytic
        # Updated to match real sales data column names with SMART PRIORITIZATION
        self.ANALYTIC_PROFILES = {
            "sales_summary": {
                "x": ["Sale_Date", "Date"],
                "y": ["Sales_Amount", "Sales", "Amount", "Revenue"],
                "group": "sum",
                "chart": "line",
                "description": "Shows trend of total sales over time",
                "icon": "📈"
            },
            "product_performance": {
                # PRIORITY: Actual product names over categories
                "x": ["name", "Product_Name", "Product", "Product_ID", "Item", "SKU", "Category"],
                "y": ["Sales_Amount", "Sales", "Amount", "Revenue"],
                "group": "sum",
                "chart": "bar",
                "description": "Compares sales performance across different products",
                "icon": "📊"
            },
            "regional_sales": {
                # PRIORITY: Only show if we have actual location columns
                "x": ["Location", "Region", "Branch", "Area", "City", "State"],
                "y": ["Sales_Amount", "Sales", "Amount", "Revenue"],
                "group": "sum",
                "chart": "bar",
                "description": "Analyzes sales distribution across different regions",
                "icon": "🌍"
            },
            "sales_forecast": {
                "x": ["Sale_Date", "Date"],
                "y": ["Sales_Amount", "Sales", "Amount", "Revenue"],
                "group": "sum",
                "chart": "line_forecast",
                "description": "Predicts future sales trends based on historical data",
                "icon": "🔮"
            },
            "product_demand_forecast": {
                "x": ["Sale_Date", "Date"],
                "y": ["Quantity_Sold", "Quantity", "Units_Sold", "Demand"],
                "group": "sum",
                "chart": "multi_line",
                "description": "Forecasts demand for top products over time",
                "icon": "📦"
            }
        }
        
        self.analytics_config = {
            "Sales Summary Report": {
                "required_columns": ["Date", "Sales"],
                "chart_type": "line",
                "description": "Shows trend of total sales over time",
                "icon": "🕒"
            },
            "Product Performance Analysis": {
                "required_columns": ["Product", "Sales"],
                "chart_type": "bar",
                "description": "Compares product performance",
                "icon": "📊"
            },
            "Regional Sales Analysis": {
                "required_columns": ["Region", "Sales"],
                "chart_type": "bar",
                "description": "Shows regional sales comparison",
                "icon": "🗺️"
            },
            "Sales Forecasting": {
                "required_columns": ["Date", "Sales"],
                "chart_type": "line_forecast",
                "description": "Plots past vs future trend",
                "icon": "📈"
            },
            "Demand Forecasting": {
                "required_columns": ["Date", "Product", "Quantity"],
                "chart_type": "multi_line",
                "description": "Forecasts demand per product",
                "icon": "📈"
            }
        }
    
    def clean_and_transform_data(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
        """Clean and transform data according to TANAW standards."""
        print(f"🧹 TANAW Data Cleaning & Transformation")
        
        try:
            # Apply column mappings, selecting the best column for each canonical type
            # Priority: Sales_Amount > Unit_Price > Unit_Cost > Discount for Sales
            # Priority: Product_ID > Product_Category for Product
            
            # 🔥 CRITICAL FIX: Combine columns BEFORE renaming to avoid data loss
            print(f"🔍 Original column mapping: {column_mapping}")
            
            # Filter out "Ignore" mappings and group by canonical type
            canonical_groups = {}
            ignored_columns = []
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == "Ignore":
                    ignored_columns.append(orig_col)
                    print(f"⏭️ Ignoring column: {orig_col}")
                else:
                    if canonical_col not in canonical_groups:
                        canonical_groups[canonical_col] = []
                    canonical_groups[canonical_col].append(orig_col)
            
            print(f"🔍 Canonical groups: {canonical_groups}")
            print(f"🔍 Ignored columns: {ignored_columns}")
            
            # Process each canonical group - now we should have only 1 column per type
            final_mapping = {}
            for canonical_col, orig_cols in canonical_groups.items():
                if len(orig_cols) == 1:
                    # Single column, direct mapping (this should be the norm now)
                    final_mapping[orig_cols[0]] = canonical_col
                    print(f"✅ Direct mapping: {orig_cols[0]} → {canonical_col}")
                else:
                    # Multiple columns - use intelligent prioritization
                    print(f"⚠️ Multiple columns for {canonical_col}: {orig_cols}")
                    
                    # CRITICAL FIX: Prioritize actual product names over categories
                    if canonical_col == "Product":
                        # Priority 1: Actual product name columns (highest priority)
                        product_name_candidates = [
                            "name", "Product_Name", "ProductName", "Product Name", "product_name",
                            "Item", "Item_Name", "ItemName", "Item Name", "item_name",
                            "SKU", "Product_Code", "ProductCode", "Code", "product_code",
                            "Product", "Product_Description", "ProductDescription", "Description"
                        ]
                        
                        # Priority 2: Brand columns (medium priority)
                        brand_candidates = [
                            "Brand", "Brand_Name", "BrandName", "Brand Name", "brand_name"
                        ]
                        
                        # Priority 3: Category columns (lowest priority - only if no better option)
                        category_candidates = [
                            "Category", "Category_Name", "CategoryName", "Category Name", "category_name"
                        ]
                        
                        # Find the BEST product column in order of priority
                        selected_col = None
                        
                        # First, try to find actual product name columns
                        for col in orig_cols:
                            col_lower = col.lower().replace(" ", "_").replace("-", "_")
                            if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                                   for candidate in product_name_candidates):
                                selected_col = col
                                print(f"✅ Found product name column: {col}")
                                break
                        
                        # If no product name found, try brand columns
                        if not selected_col:
                            for col in orig_cols:
                                col_lower = col.lower().replace(" ", "_").replace("-", "_")
                                if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                                       for candidate in brand_candidates):
                                    selected_col = col
                                    print(f"⚠️ Using brand column as product: {col}")
                                    break
                        
                        # Last resort: use category columns (but warn user)
                        if not selected_col:
                            for col in orig_cols:
                                col_lower = col.lower().replace(" ", "_").replace("-", "_")
                                if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                                       for candidate in category_candidates):
                                    selected_col = col
                                    print(f"⚠️ WARNING: Using category column as product (may show categories instead of specific products): {col}")
                                    break
                        
                        if selected_col:
                            final_mapping[selected_col] = canonical_col
                            print(f"✅ Selected product column: {selected_col}")
                            
                            # Keep other columns as additional data
                            for col in orig_cols:
                                if col != selected_col:
                                    df[f"{col}_additional"] = df[col]
                                    print(f"📊 Preserved additional column: {col}_additional")
                        else:
                            # Fallback: use first column
                            final_mapping[orig_cols[0]] = canonical_col
                            print(f"⚠️ No suitable product column found, using first: {orig_cols[0]}")
                    else:
                        # For non-Product columns, use the first one
                        final_mapping[orig_cols[0]] = canonical_col
                        print(f"⚠️ Multiple columns for {canonical_col}: {orig_cols} - using first one")
                        # Keep other columns as additional data
                        for i, col in enumerate(orig_cols[1:], 1):
                            df[f"{col}_additional"] = df[col]
                            print(f"📊 Preserved additional column: {col}_additional")
            
            print(f"🔍 Final mapping: {final_mapping}")
            
            # Apply the mapping
            cleaned_df = df.rename(columns=final_mapping)
            
            print(f"🔍 After mapping - columns: {list(cleaned_df.columns)}")
            
            # Clean data types
            cleaned_df = self._clean_data_types(cleaned_df)
            
            # Handle missing values
            cleaned_df = self._handle_missing_values(cleaned_df)
            
            # Remove duplicates
            cleaned_df = cleaned_df.drop_duplicates()
            
            print(f"✅ Data cleaned: {cleaned_df.shape[0]} rows × {cleaned_df.shape[1]} columns")
            return cleaned_df
            
        except Exception as e:
            print(f"⚠️ Data cleaning error: {e}")
            return df.rename(columns=column_mapping)  # Fallback to just renaming
    
    def _clean_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean data types for analytics."""
        for col in df.columns:
            if col == "Date":
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass
            elif col in ["Sales", "Amount", "Quantity"]:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    pass
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values intelligently."""
        for col in df.columns:
            if col in ["Sales", "Amount", "Quantity"]:
                # Fill numeric columns with median
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
            elif col in ["Product", "Region"]:
                # Fill categorical columns with "Unknown"
                df[col] = df[col].fillna("Unknown")
        return df
    
    def _generate_context_message(self, context: str, confidence: float) -> str:
        """
        Generate user-friendly message about detected dataset context
        
        Args:
            context: Detected context (SALES, INVENTORY, MIXED, UNKNOWN)
            confidence: Confidence score (0.0 to 1.0)
            
        Returns:
            Professional message string for users
        """
        # Context-specific messages
        messages = {
            "SALES": {
                "title": "Sales Dataset Detected",
                "message": "We've analyzed your dataset and identified it as sales transaction data. Here are the analytics we generated to help you understand your sales performance, identify top products, and forecast future trends.",
                "emoji": "📊"
            },
            "INVENTORY": {
                "title": "Inventory Dataset Detected",
                "message": "We've analyzed your dataset and identified it as inventory management data. Here are the analytics we generated to help you monitor stock levels, identify reorder needs, and track inventory efficiency.",
                "emoji": "📦"
            },
            "MIXED": {
                "title": "Integrated Business Dataset Detected",
                "message": "We've analyzed your dataset and identified it contains both sales and inventory data. Here are the comprehensive analytics we generated across both domains to give you a complete business overview.",
                "emoji": "📊📦"
            },
            "UNKNOWN": {
                "title": "Dataset Analysis Complete",
                "message": "We've analyzed your dataset and generated all relevant analytics based on the available data. Explore the charts below to gain insights from your data.",
                "emoji": "📈"
            }
        }
        
        context_info = messages.get(context, messages["UNKNOWN"])
        
        # Add confidence indicator
        confidence_text = ""
        if confidence >= 0.9:
            confidence_text = " (High Confidence)"
        elif confidence >= 0.7:
            confidence_text = " (Moderate Confidence)"
        elif confidence > 0:
            confidence_text = " (Low Confidence)"
        
        return {
            "title": context_info["title"] + confidence_text,
            "message": context_info["message"],
            "emoji": context_info["emoji"],
            "context": context,
            "confidence": confidence
        }
    
    def check_analytics_readiness(self, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Check which analytics are ready based on available columns."""
        available_columns = list(column_mapping.values())
        available_analytics = []
        unavailable_analytics = []
        
        for analytic_name, config in self.analytics_config.items():
            required_cols = config["required_columns"]
            missing_cols = [col for col in required_cols if col not in available_columns]
            
            if not missing_cols:
                available_analytics.append({
                    "name": analytic_name,
                    "status": "ready",
                    "required_columns": required_cols,
                    "chart_type": config["chart_type"],
                    "description": config["description"],
                    "icon": config["icon"]
                })
            else:
                unavailable_analytics.append({
                    "name": analytic_name,
                    "status": "disabled",
                    "missing_columns": missing_cols,
                    "required_columns": required_cols
                })
        
        return {
            "available_analytics": available_analytics,
            "unavailable_analytics": unavailable_analytics,
            "ready_count": len(available_analytics),
            "total_count": len(self.analytics_config)
        }
    
    def generate_analytics_and_charts(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Generate analytics and charts for available analytics using the original pipeline."""
        print(f"📊 TANAW Analytics Generation")
        print(f"🔍 DataFrame shape: {df.shape}")
        print(f"🔍 DataFrame columns: {list(df.columns)}")
        print(f"🔍 Column mapping: {column_mapping}")

        # Initialize profile and reqs with default values
        profile = None
        reqs = None
        
        try:
            # P1: Build non-blocking dataset profile (logs only)
            try:
                profile = self.data_profiler.build_profile(df)
                reqs = self.data_profiler.validate_requirements(df)
                print("🧪 Data profile summary:", {
                    "shape": profile.get("shape"),
                    "num_columns": len(profile.get("columns", [])),
                })
                print("🧪 Analytic requirements readiness (non-blocking):", {
                    k: {"ready": v.get("ready", False), "missing": v.get("missing_roles", [])}
                    for k, v in reqs.items()
                })
            except Exception as e:
                print(f"⚠️ Data profiling skipped: {e}")
                # Create fallback profile with basic info
                profile = {
                    "shape": [len(df), len(df.columns)],
                    "columns": list(df.columns),
                    "row_count": len(df),
                    "col_count": len(df.columns)
                }
                reqs = {}

            # Check analytics readiness (original readiness-driven flow)
            readiness = self.check_analytics_readiness(column_mapping)
            print(f"🔍 Analytics readiness: {readiness}")

            # SEMANTIC DETECTION: Determine if dataset is Sales or Inventory
            print("\n" + "="*80)
            print("🧠 STEP: SEMANTIC CONTEXT DETECTION")
            print("="*80)
            context_result = self.semantic_detector.detect_context(df, column_mapping)
            detected_context = context_result["context"]
            print(f"\n📊 Detected Context: {detected_context}")
            print(f"   Confidence: {context_result['confidence']:.2%}")
            print(f"   Method: {context_result['method']}")
            print(f"   Reasoning: {context_result['reasoning']}")
            print("="*80 + "\n")

            charts = []

            # Phase 1: Generate Bar Charts using dedicated module
            print("📊 Phase 1: Generating Bar Charts with dedicated module")
            bar_charts = self.bar_chart_generator.generate_all_bar_charts(df, column_mapping, context=detected_context)
            charts.extend(bar_charts)
            print(f"✅ Generated {len(bar_charts)} bar charts")
            
            # Phase 2: Generate Line Charts using dedicated module
            print("📈 Phase 2: Generating Line Charts with dedicated module")
            line_charts = self.line_chart_generator.generate_all_line_charts(df, column_mapping, context=detected_context)
            charts.extend(line_charts)
            print(f"✅ Generated {len(line_charts)} line charts")
            
            # Phase 3: Generate Sales Forecast using dedicated module
            print("🔮 Phase 3: Generating Sales Forecast with dedicated module")
            forecast_charts = self.sales_forecast_generator.generate_all_sales_forecasts(df)
            charts.extend(forecast_charts)
            print(f"✅ Generated {len(forecast_charts)} sales forecasts")
            
            # Phase 4: Generate Stock Forecast using dedicated module (for inventory context)
            if detected_context in ["INVENTORY", "MIXED", "UNKNOWN"]:
                print("📦 Phase 4: Generating Stock Forecast with dedicated module")
                stock_forecast_charts = self.stock_forecast_generator.generate_all_stock_forecasts(df)
                charts.extend(stock_forecast_charts)
                print(f"✅ Generated {len(stock_forecast_charts)} stock forecasts")
            else:
                print("⏭️ Skipping Stock Forecast (Sales context detected)")
            
            # TEMPORARILY DISABLED: Generate other charts using original method
            # This allows us to focus on testing bar, line, and forecast charts properly
            print("⏭️ Temporarily disabled other chart types (pie, multi-line)")
            # for analytic in readiness["available_analytics"]:
            #     # Skip bar charts since we're using dedicated module
            #     if analytic.get('chart_type') == 'bar':
            #         print(f"⏭️ Skipping {analytic['name']} - using dedicated bar chart module")
            #         continue
            #     print(f"🔍 Processing analytic: {analytic['name']}")
            #     # P2: suggest axes (non-blocking) for visibility
            #     try:
            #         suggestion = self.axis_resolver.suggest_axes(df, analytic['key'] if 'key' in analytic else analytic['name'])
            #         print(f"🧭 Axis suggestion for {analytic['name']}:", suggestion)
            #     except Exception as e:
            #         print(f"⚠️ Axis suggestion failed for {analytic['name']}: {e}")
            #     # P3: transformation preview (non-blocking)
            #     try:
            #         t_preview = self.chart_transformer.transform_for_analytic(
            #             df,
            #             analytic.get('key', analytic.get('name')),
            #             suggestion.get('x') if isinstance(suggestion, dict) else None,
            #             suggestion.get('y') if isinstance(suggestion, dict) else None,
            #             suggestion.get('group') if isinstance(suggestion, dict) else None,
            #         )
            #         print(f"🧹 Transform preview for {analytic['name']}:", {
            #             'status': t_preview.get('summary', {}).get('status'),
            #             'rows_in': t_preview.get('summary', {}).get('rows_in'),
            #             'rows_out': t_preview.get('summary', {}).get('rows_out'),
            #             'group_by': t_preview.get('summary', {}).get('group_by'),
            #             'agg': t_preview.get('summary', {}).get('agg'),
            #         })
            #     except Exception as e:
            #         t_preview = {"summary": {"status": "error", "reason": str(e)}}
            #         print(f"⚠️ Transform preview failed for {analytic['name']}: {e}")
            #     chart = self._generate_chart(df, analytic, column_mapping)
            #     print(f"🔍 Chart result for {analytic['name']}: {chart}")
            #     if chart:
            #         # Attach non-blocking axis suggestion for debugging/front-end dev tools
            #         if 'suggestion' not in chart:
            #             try:
            #                 chart['suggestion'] = suggestion  # may be None if exception above
            #             except Exception:
            #                 pass
            #         # Attach non-blocking transform summary
            #         try:
            #             chart['transform_summary'] = t_preview.get('summary') if isinstance(t_preview, dict) else None
            #         except Exception:
            #             pass
            #         charts.append(chart)

            print(f"✅ Generated {len(charts)} charts")

            # P4: Verify unique charts to prevent duplicates
            try:
                charts_dict = {f"chart_{i}": chart for i, chart in enumerate(charts)}
                unique_charts = self.verify_unique_charts(charts_dict)
                charts = list(unique_charts.values())
                print(f"🛡️ Duplicate detection: {len(charts)} unique charts after verification")
            except Exception as e:
                print(f"⚠️ Duplicate detection failed: {e}")

            # P5: Validate charts (no-dup + sanity) - non-blocking
            try:
                validation_report = self.chart_validator.validate(charts)
                print("🛡️ Chart validation:", validation_report.get('summary'))
            except Exception as e:
                validation_report = {"summary": {"error": str(e)}}
                print(f"⚠️ Chart validation failed: {e}")

            # Generate user-facing context message
            context_message = self._generate_context_message(detected_context, context_result.get("confidence", 0.0))
            print(f"💬 Context message for user: {context_message}")
            
            return {
                "charts": charts,
                "readiness": readiness,
                "context_detection": {
                    "detected_context": detected_context,
                    "confidence": context_result.get("confidence", 0.0),
                    "method": context_result.get("method", "unknown"),
                    "reasoning": context_result.get("reasoning", ""),
                    "user_message": context_message
                },
                "data_profile": {
                    "summary": {
                        "shape": profile.get("shape") if profile else None,
                        "num_columns": len(profile.get("columns", [])) if profile else None,
                        "row_count": profile.get("row_count") if profile else None,
                        "col_count": profile.get("col_count") if profile else None,
                    },
                    "requirements": reqs if reqs else {},
                },
                "axis_suggestions": {
                    (a['name'] if isinstance(a, dict) else str(a)): (
                        self.axis_resolver.suggest_axes(df, a.get('key', a.get('name'))) if isinstance(a, dict) else None
                    ) for a in readiness.get('available_analytics', [])
                },
                "transform_summaries": {
                    (a['name'] if isinstance(a, dict) else str(a)): (
                        self.chart_transformer.transform_for_analytic(
                            df,
                            a.get('key', a.get('name')) if isinstance(a, dict) else str(a),
                            None, None, None
                        ).get('summary') if isinstance(a, dict) else None
                    ) for a in readiness.get('available_analytics', [])
                },
                "validation_report": validation_report,
                "success": True
            }

        except Exception as e:
            print(f"❌ Analytics generation error: {e}")
            return {
                "charts": [],
                "readiness": {"available_analytics": [], "unavailable_analytics": [], "ready_count": 0, "total_count": 5},
                "success": False,
                "error": str(e)
            }
    
    
    def generate_domain_analytics(self, df: pd.DataFrame, column_mapping: Dict[str, str], domain_classification) -> Dict[str, Any]:
        """Generate domain-specific analytics and charts using the original method."""
        print(f"🎯 TANAW Domain Analytics: {domain_classification.domain.upper()}")
        print(f"🔍 DataFrame shape: {df.shape}")
        print(f"🔍 Domain confidence: {domain_classification.confidence:.2f}")
        
        try:
            # Clean and transform data using the original method
            cleaned_df = self.clean_and_transform_data(df, column_mapping)
            print(f"✅ Data cleaning completed: {cleaned_df.shape}")
            
            # Generate analytics and charts using the original method
            analytics_result = self.generate_analytics_and_charts(cleaned_df, column_mapping)
            charts = analytics_result.get('charts', [])
            summary_metrics = self.calculate_summary_metrics(cleaned_df, column_mapping)

            # Phase 1-4 artifacts (non-blocking)
            data_profile = analytics_result.get('data_profile')
            axis_suggestions = analytics_result.get('axis_suggestions')
            transform_summaries = analytics_result.get('transform_summaries')
            validation_report = analytics_result.get('validation_report')
            
            print(f"✅ Generated {len(charts)} charts using original method")
            
            # Generate domain-specific analytics based on detected domain
            domain = domain_classification.domain.lower()
            
            # SALES domain - Add Finance and Customer analytics (if data exists)
            # NOTE: Finance is no longer a separate domain - it's now integrated into SALES
            if domain == 'sales':
                print("📊 SALES Domain detected - Checking for financial analytics...")
                
                # ✅ Check for Finance indicators before generating
                print("\n💰 Checking for Expense column (for financial analytics)...")
                if self.domain_detector.has_finance_indicators(df, column_mapping):
                    print("✅ Expense data detected - generating Financial Sales analytics")
                    finance_charts = self.finance_analytics.generate_analytics(df, column_mapping)
                    if finance_charts:
                        charts.extend([self._convert_finance_chart(chart) for chart in finance_charts])
                        print(f"✅ Added {len(finance_charts)} Financial charts (Revenue/Expense, Profit, Cash Flow)")
                    else:
                        print("⚠️ Finance module returned no charts")
                else:
                    print("⏭️ No Expense column found - using standard sales charts only")
                
                # ✅ Check for Customer indicators before generating
                print("\n👥 Checking for Customer indicators...")
                if self.domain_detector.has_customer_indicators(df, column_mapping):
                    print("✅ Customer data detected - generating Customer analytics")
                    customer_charts = self.customer_analytics.generate_analytics(df, column_mapping)
                    if customer_charts:
                        charts.extend([self._convert_customer_chart(chart) for chart in customer_charts])
                        print(f"✅ Added {len(customer_charts)} Customer charts")
                    else:
                        print("⚠️ Customer module returned no charts")
                else:
                    print("⏭️ No customer indicators found - skipping Customer charts")
            
            # INVENTORY domain
            elif domain == 'inventory':
                print("📦 INVENTORY Domain detected - Generating Inventory analytics")
                inventory_charts = self.inventory_analytics.generate_analytics(df, column_mapping)
                if inventory_charts:
                    charts.extend([self._convert_inventory_chart(chart) for chart in inventory_charts])
                    print(f"✅ Added {len(inventory_charts)} Inventory charts")
                else:
                    print("⚠️ No Inventory charts generated")
                
                # ✅ Check for Finance indicators (for stock value perspective)
                print("\n💰 Checking for Finance indicators...")
                if self.domain_detector.has_finance_indicators(df, column_mapping):
                    print("✅ Finance data detected - adding Finance perspective")
                    finance_charts = self.finance_analytics.generate_analytics(df, column_mapping)
                    if finance_charts:
                        charts.extend([self._convert_finance_chart(chart) for chart in finance_charts])
                        print(f"✅ Added {len(finance_charts)} Finance charts")
                else:
                    print("⏭️ No finance indicators found - skipping Finance charts")
            
            # CUSTOMER domain
            elif domain == 'customer':
                print("👥 CUSTOMER Domain detected - Adding Customer analytics")
                customer_charts = self.customer_analytics.generate_analytics(df, column_mapping)
                if customer_charts:
                    charts.extend([self._convert_customer_chart(chart) for chart in customer_charts])
                    print(f"✅ Added {len(customer_charts)} Customer charts")
                else:
                    print("⚠️ No Customer charts generated")
            
            # MIXED domain - Combine analytics from multiple domains (smart routing)
            elif domain == 'mixed':
                print("🔀 MIXED Domain detected - Intelligently combining analytics")
                
                # ✅ Check and add Finance analytics if applicable
                print("\n💰 Checking for Finance indicators...")
                if self.domain_detector.has_finance_indicators(df, column_mapping):
                    print("✅ Finance data detected - generating Finance analytics")
                    finance_charts = self.finance_analytics.generate_analytics(df, column_mapping)
                    if finance_charts:
                        charts.extend([self._convert_finance_chart(chart) for chart in finance_charts])
                        print(f"✅ Added {len(finance_charts)} Finance charts")
                else:
                    print("⏭️ No finance indicators - skipping Finance charts")
                
                # ✅ Check and add Inventory analytics if applicable
                print("\n📦 Checking for Inventory indicators...")
                if self.domain_detector.has_inventory_indicators(df, column_mapping):
                    print("✅ Inventory data detected - generating Inventory analytics")
                    inventory_charts = self.inventory_analytics.generate_analytics(df, column_mapping)
                    if inventory_charts:
                        charts.extend([self._convert_inventory_chart(chart) for chart in inventory_charts])
                        print(f"✅ Added {len(inventory_charts)} Inventory charts")
                else:
                    print("⏭️ No inventory indicators - skipping Inventory charts")
                
                # ✅ Check and add Customer analytics if applicable
                print("\n👥 Checking for Customer indicators...")
                if self.domain_detector.has_customer_indicators(df, column_mapping):
                    print("✅ Customer data detected - generating Customer analytics")
                    customer_charts = self.customer_analytics.generate_analytics(df, column_mapping)
                    if customer_charts:
                        charts.extend([self._convert_customer_chart(chart) for chart in customer_charts])
                        print(f"✅ Added {len(customer_charts)} Customer charts")
                else:
                    print("⏭️ No customer indicators - skipping Customer charts")
            
            # Create readiness info
            readiness = {
                "available_analytics": [{"name": chart['title'], "status": "ready"} for chart in charts],
                "unavailable_analytics": [],
                "ready_count": len(charts),
                "total_count": len(charts)
            }
            
            # Generate conversational insights using batch processing
            if self.conversational_insights and charts:
                print("🗣️ Generating conversational insights...")
                print(f"🗣️ OpenAI client available: {self.conversational_insights is not None}")
                print(f"🗣️ Number of charts to process: {len(charts)}")
                
                try:
                    # Use conversational insights for personalized analysis
                    batch_insights = self.conversational_insights.generate_conversational_insights(charts, domain)
                    print(f"🗣️ Generated conversational insights for {len(batch_insights)} charts")
                    
                    # Apply insights to charts
                    charts_with_insights = []
                    print(f"🗣️ Available conversational insights: {list(batch_insights.keys())}")
                    
                    for i, chart in enumerate(charts):
                        chart_id = chart.get('id', f"chart_{i}")
                        print(f"🗣️ Processing chart {i}: {chart.get('title', 'Unknown')} with ID: {chart_id}")
                        
                        if chart_id in batch_insights:
                            chart['narrative_insights'] = batch_insights[chart_id]
                            print(f"🗣️ ✅ Applied conversational insights to {chart.get('title', 'Unknown')}")
                        else:
                            # Generate specific fallback insights based on chart type and title
                            chart_title = chart.get('title', 'chart')
                            chart_type = chart.get('type', 'line')
                            
                            if 'sales' in chart_title.lower() or 'forecast' in chart_title.lower():
                                # Extract actual data for specific insights
                                chart_data = chart.get('data', {})
                                if 'y' in chart_data and chart_data['y']:
                                    y_values = chart_data['y']
                                    max_sales = max(y_values)
                                    min_sales = min(y_values)
                                    avg_sales = sum(y_values) / len(y_values)
                                    total_sales = sum(y_values)
                                    
                                    trend = self._calculate_trend(y_values)
                                    variation = ((max_sales - min_sales) / avg_sales * 100) if avg_sales > 0 else 0
                                    insights_text = f"I can see your sales performance shows some interesting patterns. Your data spans {len(y_values)} periods with sales ranging from ₱{min_sales:,.0f} to ₱{max_sales:,.0f}, averaging ₱{avg_sales:,.0f} per period. What's particularly noteworthy is the {variation:.0f}% variation between your peak and low periods, which suggests {trend} trend. Based on this data, I'd recommend focusing on three key areas: first, set your revenue targets around ₱{avg_sales:,.0f} as your baseline; second, prepare for those peak periods when you hit ₱{max_sales:,.0f}; and third, look for opportunities to consistently reach ₱{avg_sales * 1.2:,.0f} or higher."
                                else:
                                    insights_text = f"Looking at your sales data, I can see this chart reveals your business growth trajectory and seasonal patterns. This is valuable information for understanding when your business performs best and planning for the future. I'd suggest using this data to set realistic revenue targets, plan your inventory for those peak periods, and identify growth opportunities in your trending months."
                                
                                key_points = [
                                    "Monitor sales trends to predict future performance",
                                    "Plan inventory and staffing based on seasonal patterns",
                                    "Set revenue targets based on historical growth rates"
                                ]
                            elif 'product' in chart_title.lower() or 'performance' in chart_title.lower():
                                insights_text = f"I can see this chart compares your product performance, which is really valuable for understanding what's driving your revenue. This data reveals your best-selling items and shows which categories might need more attention. Based on what I'm seeing, I'd recommend focusing your marketing efforts on those top performers, considering whether to discontinue the low-performing products, and using your successful products to cross-sell related items."
                                key_points = [
                                    "Identify your best-selling products for marketing focus",
                                    "Consider discontinuing underperforming products",
                                    "Use top performers to cross-sell related items"
                                ]
                            elif 'demand' in chart_title.lower():
                                insights_text = f"DESCRIPTION: This {chart_title} forecasts future demand for your products based on historical sales patterns. INSIGHT: Demand forecasting reveals which products will be popular and helps prevent stockouts or overstocking. RECOMMENDATION: Use these predictions to order inventory in advance, adjust pricing strategies for high-demand periods, and plan production schedules to meet customer needs."
                                key_points = [
                                    "Order inventory based on predicted demand",
                                    "Adjust pricing for high-demand periods",
                                    "Plan production to meet forecasted customer needs"
                                ]
                            elif 'components' in chart_title.lower():
                                insights_text = f"DESCRIPTION: This {chart_title} breaks down your sales data into trend and seasonal components, showing the underlying factors driving your business performance. INSIGHT: The trend shows your long-term growth direction, while seasonality reveals predictable patterns. RECOMMENDATION: Plan for seasonal fluctuations, invest in long-term growth strategies, and adjust business operations based on trend analysis."
                                key_points = [
                                    "Plan for seasonal fluctuations in your business",
                                    "Invest in long-term growth strategies",
                                    "Adjust operations based on trend analysis"
                                ]
                            else:
                                insights_text = f"This {chart_title} displays important business metrics that require attention and analysis. The visualization helps identify key patterns and trends in your data."
                                key_points = [
                                    "Data visualization reveals important business patterns",
                                    "Regular analysis helps identify opportunities",
                                    "Metrics provide actionable business insights"
                                ]
                            
                            chart['narrative_insights'] = {
                                "insights": insights_text,
                                "key_points": key_points,
                                "confidence": 0.7,
                                "generated_at": datetime.now().isoformat()
                            }
                            print(f"📝 ⚠️ Applied specific fallback insights to {chart.get('title', 'Unknown')}")
                        
                        # Debug: Check if insights were added
                        print(f"📝 Chart {i} has narrative_insights: {'narrative_insights' in chart}")
                        if 'narrative_insights' in chart:
                            print(f"📝 Insights content: {chart['narrative_insights'].get('insights', 'No insights text')[:100]}...")
                        
                        charts_with_insights.append(chart)
                    
                    print(f"📝 Processed {len(charts_with_insights)} charts with batch insights")
                    charts = charts_with_insights
                    
                except Exception as e:
                    print(f"⚠️ Batch insights generation failed: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
                    # Fallback: add specific insights to all charts
                    charts_with_insights = []
                    for i, chart in enumerate(charts):
                        chart_title = chart.get('title', 'chart')
                        
                        # Generate specific insights based on chart title
                        if 'sales' in chart_title.lower() or 'forecast' in chart_title.lower():
                            insights_text = f"DESCRIPTION: This {chart_title} shows sales performance over time with historical data and future predictions. INSIGHT: The sales trend reveals your business growth trajectory and seasonal patterns. RECOMMENDATION: Use this data to set realistic revenue targets, plan inventory for peak periods, and identify growth opportunities in trending months."
                            key_points = [
                                "Monitor sales trends to predict future performance",
                                "Plan inventory and staffing based on seasonal patterns",
                                "Set revenue targets based on historical growth rates"
                            ]
                        elif 'product' in chart_title.lower() or 'performance' in chart_title.lower():
                            insights_text = f"DESCRIPTION: This {chart_title} compares sales performance across different product categories, showing which products generate the most revenue. INSIGHT: Product performance reveals your best-selling items and underperforming categories. RECOMMENDATION: Focus marketing efforts on top performers, consider discontinuing low-performing products, and use successful products to cross-sell related items."
                            key_points = [
                                "Identify your best-selling products for marketing focus",
                                "Consider discontinuing underperforming products",
                                "Use top performers to cross-sell related items"
                            ]
                        elif 'demand' in chart_title.lower():
                            insights_text = f"DESCRIPTION: This {chart_title} forecasts future demand for your products based on historical sales patterns. INSIGHT: Demand forecasting reveals which products will be popular and helps prevent stockouts or overstocking. RECOMMENDATION: Use these predictions to order inventory in advance, adjust pricing strategies for high-demand periods, and plan production schedules to meet customer needs."
                            key_points = [
                                "Order inventory based on predicted demand",
                                "Adjust pricing for high-demand periods",
                                "Plan production to meet forecasted customer needs"
                            ]
                        elif 'components' in chart_title.lower():
                            insights_text = f"DESCRIPTION: This {chart_title} breaks down your sales data into trend and seasonal components, showing the underlying factors driving your business performance. INSIGHT: The trend shows your long-term growth direction, while seasonality reveals predictable patterns. RECOMMENDATION: Plan for seasonal fluctuations, invest in long-term growth strategies, and adjust business operations based on trend analysis."
                            key_points = [
                                "Plan for seasonal fluctuations in your business",
                                "Invest in long-term growth strategies",
                                "Adjust operations based on trend analysis"
                            ]
                        else:
                            insights_text = f"This {chart_title} displays important business metrics that require attention and analysis."
                            key_points = [
                                "Data visualization reveals important business patterns",
                                "Regular analysis helps identify opportunities",
                                "Metrics provide actionable business insights"
                            ]
                        
                        chart['narrative_insights'] = {
                            "insights": insights_text,
                            "key_points": key_points,
                            "confidence": 0.7,
                            "generated_at": datetime.now().isoformat()
                        }
                        print(f"📝 Applied specific fallback insights to chart {i}: {chart.get('title', 'Unknown')}")
                        charts_with_insights.append(chart)
                    
                    print(f"📝 Applied fallback insights to {len(charts_with_insights)} charts")
                    charts = charts_with_insights
            else:
                if not self.narrative_insights:
                    print("⚠️ Narrative insights not available (no OpenAI key)")
                if not charts:
                    print("⚠️ No charts to generate insights for")
                
                # Ensure all charts have insights even if narrative_insights is None
                if not self.narrative_insights:
                    print("📝 Adding specific fallback insights to all charts (no OpenAI key)")
                    for i, chart in enumerate(charts):
                        chart_title = chart.get('title', 'chart')
                        
                        # Generate specific insights based on chart title
                        if 'sales' in chart_title.lower() or 'forecast' in chart_title.lower():
                            insights_text = f"DESCRIPTION: This {chart_title} shows sales performance over time with historical data and future predictions. INSIGHT: The sales trend reveals your business growth trajectory and seasonal patterns. RECOMMENDATION: Use this data to set realistic revenue targets, plan inventory for peak periods, and identify growth opportunities in trending months."
                            key_points = [
                                "Monitor sales trends to predict future performance",
                                "Plan inventory and staffing based on seasonal patterns",
                                "Set revenue targets based on historical growth rates"
                            ]
                        elif 'product' in chart_title.lower() or 'performance' in chart_title.lower():
                            insights_text = f"DESCRIPTION: This {chart_title} compares sales performance across different product categories, showing which products generate the most revenue. INSIGHT: Product performance reveals your best-selling items and underperforming categories. RECOMMENDATION: Focus marketing efforts on top performers, consider discontinuing low-performing products, and use successful products to cross-sell related items."
                            key_points = [
                                "Identify your best-selling products for marketing focus",
                                "Consider discontinuing underperforming products",
                                "Use top performers to cross-sell related items"
                            ]
                        elif 'demand' in chart_title.lower():
                            insights_text = f"DESCRIPTION: This {chart_title} forecasts future demand for your products based on historical sales patterns. INSIGHT: Demand forecasting reveals which products will be popular and helps prevent stockouts or overstocking. RECOMMENDATION: Use these predictions to order inventory in advance, adjust pricing strategies for high-demand periods, and plan production schedules to meet customer needs."
                            key_points = [
                                "Order inventory based on predicted demand",
                                "Adjust pricing for high-demand periods",
                                "Plan production to meet forecasted customer needs"
                            ]
                        elif 'components' in chart_title.lower():
                            insights_text = f"DESCRIPTION: This {chart_title} breaks down your sales data into trend and seasonal components, showing the underlying factors driving your business performance. INSIGHT: The trend shows your long-term growth direction, while seasonality reveals predictable patterns. RECOMMENDATION: Plan for seasonal fluctuations, invest in long-term growth strategies, and adjust business operations based on trend analysis."
                            key_points = [
                                "Plan for seasonal fluctuations in your business",
                                "Invest in long-term growth strategies",
                                "Adjust operations based on trend analysis"
                            ]
                        else:
                            insights_text = f"This {chart_title} displays important business metrics that require attention and analysis."
                            key_points = [
                                "Data visualization reveals important business patterns",
                                "Regular analysis helps identify opportunities",
                                "Metrics provide actionable business insights"
                            ]
                        
                        chart['narrative_insights'] = {
                            "insights": insights_text,
                            "key_points": key_points,
                            "confidence": 0.7,
                            "generated_at": datetime.now().isoformat()
                        }
                        print(f"📝 Added specific fallback insights to chart {i}: {chart.get('title', 'Unknown')}")
            
            # Detect anomalies in the data
            print("🔍 Detecting anomalies...")
            anomalies = self.anomaly_detector.detect_anomalies(df, domain)
            
            # Generate predictive analytics
            print("🔮 Generating predictive analytics...")
            predictive_charts = []
            predictive_metrics = {}
            
            # TEMPORARILY DISABLED: Predictive analytics to focus on bar chart testing
            print("⏭️ Temporarily disabled predictive analytics to focus on bar chart testing")
            # try:
            #     # Check if we have the required columns for forecasting
            #     has_date = 'Date' in df.columns
            #     has_sales = 'Sales' in df.columns
            #     has_quantity = 'Quantity' in df.columns
            #     has_product = 'Product' in df.columns
            #     
            #     if has_date and has_sales:
            #         # Generate sales forecast
            #         print("📈 Generating sales forecast...")
            #         sales_forecast = self.predictive_analytics.generate_sales_forecast(df, forecast_periods=30)
            #         if sales_forecast.get('success'):
            #             predictive_charts.extend(sales_forecast.get('charts', []))
            #             predictive_metrics['sales_forecast'] = sales_forecast.get('metrics', {})
            #     
            #     if has_date and has_quantity and has_product:
            #         # Generate demand forecast
            #         print("📦 Generating demand forecast...")
            #         demand_forecast = self.predictive_analytics.generate_demand_forecast(df, 'Product', 'Quantity', 30)
            #         if demand_forecast.get('success'):
            #             predictive_charts.extend(demand_forecast.get('charts', []))
            #             predictive_metrics['demand_forecast'] = demand_forecast.get('model_info', {})
            #     
            #     if domain == 'inventory' and has_date and 'Stock' in df.columns:
            #         # Generate inventory forecast
            #         print("📦 Generating inventory forecast...")
            #         inventory_forecast = self.predictive_analytics.generate_inventory_forecast(df, 'Stock', 30)
            #         if inventory_forecast.get('success'):
            #             predictive_charts.extend(inventory_forecast.get('charts', []))
            #             predictive_metrics['inventory_forecast'] = inventory_forecast.get('reorder_analysis', {})
            #     
            #     if domain == 'finance' and has_date and 'Revenue' in df.columns and 'Expense' in df.columns:
            #         # Generate cash flow forecast
            #         print("💰 Generating cash flow forecast...")
            #         cash_flow_forecast = self.predictive_analytics.generate_cash_flow_forecast(df, 'Revenue', 'Expense', 30)
            #         if cash_flow_forecast.get('success'):
            #             predictive_charts.extend(cash_flow_forecast.get('charts', []))
            #             predictive_metrics['cash_flow_forecast'] = cash_flow_forecast.get('cash_flow_metrics', {})
            #     
            #     # Add predictive charts to main charts, avoiding duplicates
            #     existing_chart_titles = {chart.get('title', '') for chart in charts}
            #     for pred_chart in predictive_charts:
            #         if pred_chart.get('title', '') not in existing_chart_titles:
            #             charts.append(pred_chart)
            #         else:
            #             # Replace descriptive chart with predictive version if it's better
            #             for i, existing_chart in enumerate(charts):
            #                 if existing_chart.get('title') == pred_chart.get('title'):
            #                     if 'forecast' in pred_chart.get('title', '').lower():
            #                         charts[i] = pred_chart  # Replace with predictive version
            #                     break
            #     
            # except Exception as e:
            #     print(f"⚠️ Error generating predictive analytics: {str(e)}")
            
            print(f"✅ Generated {len(charts)} {domain} analytics charts")
            print(f"🔮 Generated {len(predictive_charts)} predictive analytics charts")
            print(f"🚨 Detected {anomalies['total_anomalies']} anomalies")
            
            return {
                "charts": charts,
                "readiness": readiness,
                "context_detection": analytics_result.get('context_detection'),  # NEW: Pass through semantic detection
                "domain": domain_classification.domain,
                "domain_confidence": domain_classification.confidence,
                "anomalies": anomalies,
                "predictive_metrics": predictive_metrics,
                # Phase 1-4 diagnostics propagated to the top-level response
                "data_profile": data_profile,
                "axis_suggestions": axis_suggestions,
                "transform_summaries": transform_summaries,
                "validation_report": validation_report,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Domain analytics error: {e}")
            return {
                "charts": [],
                "readiness": {"available_analytics": [], "unavailable_analytics": [], "ready_count": 0, "total_count": 0},
                "success": False,
                "error": str(e)
            }
    
    def _convert_inventory_chart(self, chart) -> Dict[str, Any]:
        """Convert inventory chart to standard format."""
        return {
            "id": chart.id,
            "title": chart.title,
            "type": chart.type,
            "description": chart.description,
            "icon": chart.icon,
            "data": chart.data,
            "config": chart.config,
            "status": "success"
        }
    
    def _convert_finance_chart(self, chart) -> Dict[str, Any]:
        """Convert finance chart to standard format."""
        return {
            "id": chart.id,
            "title": chart.title,
            "type": chart.type,
            "description": chart.description,
            "icon": chart.icon,
            "domain": getattr(chart, 'domain', 'finance'),  # Add domain identifier
            "data": chart.data,
            "config": chart.config,
            "status": "success"
        }
    
    def _convert_customer_chart(self, chart) -> Dict[str, Any]:
        """Convert customer chart to standard format."""
        return {
            "id": chart.id,
            "title": chart.title,
            "type": chart.type,
            "description": chart.description,
            "icon": chart.icon,
            "domain": getattr(chart, 'domain', 'customer'),  # Add domain identifier
            "data": chart.data,
            "config": chart.config,
            "status": "success"
        }
    
    def _generate_chart(self, df: pd.DataFrame, analytic: Dict[str, Any], column_mapping: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Generate a single chart for an analytic."""
        try:
            analytic_name = analytic["name"]
            chart_type = analytic["chart_type"]
            required_cols = analytic["required_columns"]
            
            print(f"🔍 Generating chart for {analytic_name}")
            print(f"🔍 Required columns: {required_cols}")
            print(f"🔍 DataFrame columns: {list(df.columns)}")
            print(f"🔍 Column mapping: {column_mapping}")
            
            # Get the actual column names from the DataFrame
            # Since DataFrame columns are already renamed to canonical names, check directly
            df_columns = {}
            for canonical_col in required_cols:
                if canonical_col in df.columns:
                    df_columns[canonical_col] = canonical_col
                    print(f"✅ Found column: {canonical_col}")
                else:
                    # Fallback: try to find original column names
                    for orig_col, mapped_col in column_mapping.items():
                        if mapped_col == canonical_col and orig_col in df.columns:
                            df_columns[canonical_col] = orig_col
                            print(f"✅ Found column: {canonical_col} -> {orig_col}")
                            break
            
            print(f"🔍 Mapped df_columns: {df_columns}")
            
            if len(df_columns) != len(required_cols):
                print(f"⚠️ Missing columns for {analytic_name}. Found: {list(df_columns.keys())}, Required: {required_cols}")
                return None
            
            # Generate chart data based on type
            print(f"🔍 Chart type for {analytic_name}: {chart_type}")
            if chart_type == "line":
                chart_data = self._generate_line_chart(df, df_columns, analytic_name)
            elif chart_type == "bar":
                chart_data = self._generate_bar_chart(df, df_columns, analytic_name)
            elif chart_type == "line_forecast":
                chart_data = self._generate_forecast_chart(df, df_columns, analytic_name)
            elif chart_type == "multi_line":
                chart_data = self._generate_multi_line_chart(df, df_columns, analytic_name)
            else:
                print(f"🔍 Unknown chart type '{chart_type}', defaulting to line chart")
                chart_data = self._generate_line_chart(df, df_columns, analytic_name)  # Default
            
            if chart_data:
                print(f"🔍 Generated chart data for {analytic_name}: type={chart_data.get('type')}")
            
            return chart_data
            
        except Exception as e:
            print(f"⚠️ Chart generation error for {analytic['name']}: {e}")
            return None
    

    # STEP 2: Modular Data Extraction Logic
    def choose_axis(self, df: pd.DataFrame, profile: Dict[str, Any]) -> tuple:
        """
        Choose optimal X and Y axes based on profile preferences and available columns.
        Returns (x_column, y_column) or (None, None) if not found.
        """
        try:
            # Find X-axis column
            x_column = None
            for preferred_x in profile["x"]:
                if preferred_x in df.columns:
                    x_column = preferred_x
                    break
            
            # Find Y-axis column  
            y_column = None
            for preferred_y in profile["y"]:
                if preferred_y in df.columns:
                    y_column = preferred_y
                    break
            
            if x_column and y_column:
                print(f"✅ Selected axes: X={x_column}, Y={y_column}")
                return x_column, y_column
            else:
                print(f"❌ Missing required columns: X={x_column}, Y={y_column}")
                return None, None
                
        except Exception as e:
            print(f"❌ Error in choose_axis: {e}")
            return None, None
    
    def clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean dataset for analytics - handle missing values, data types, etc.
        """
        try:
            df_clean = df.copy()
            
            # Handle missing values
            df_clean = df_clean.dropna()
            
            # Convert date columns
            for col in df_clean.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    try:
                        df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                    except:
                        pass
            
            # Convert numeric columns
            for col in df_clean.columns:
                if col not in ['Date', 'Product_Name', 'Product', 'Region', 'Sales_Rep']:
                    try:
                        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                    except:
                        pass
            
            print(f"✅ Dataset cleaned: {df_clean.shape}")
            return df_clean
            
        except Exception as e:
            print(f"❌ Error in clean_dataset: {e}")
            return df
    
    def aggregate_for_chart(self, df: pd.DataFrame, x: str, y: str, analytic_name: str) -> pd.DataFrame:
        """
        Apply analytic-specific aggregation rules.
        """
        try:
            if analytic_name in ["sales_summary", "sales_forecast"]:
                # Group by date and sum sales
                result = df.groupby(x, as_index=False)[y].sum().sort_values(by=x)
                print(f"✅ Sales summary aggregation: {result.shape}")
                
            elif analytic_name in ["product_performance", "regional_sales"]:
                # Group by category and sum, sort by value descending
                result = df.groupby(x, as_index=False)[y].sum().sort_values(by=y, ascending=False)
                print(f"✅ Performance aggregation: {result.shape}")
                print(f"🔍 Performance data sample: {result.head() if not result.empty else 'Empty result'}")
                
            elif analytic_name == "product_demand_forecast":
                # Group by both Date and Product for multi-line
                if 'Product' in df.columns:
                    result = df.groupby([x, 'Product'], as_index=False)[y].sum()
                else:
                    result = df.groupby(x, as_index=False)[y].sum()
                print(f"✅ Demand forecast aggregation: {result.shape}")
                
            else:
                # Default aggregation
                result = df.groupby(x, as_index=False)[y].sum()
                print(f"✅ Default aggregation: {result.shape}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in aggregate_for_chart: {e}")
            return df
    
    def build_analytic_dataset(self, df: pd.DataFrame, analytic_name: str) -> tuple:
        """
        Build dataset for specific analytic based on profile.
        Returns (df_grouped, error_message) or (None, error_message)
        """
        try:
            profile = self.ANALYTIC_PROFILES.get(analytic_name)
            if not profile:
                return None, f"Unknown analytic type: {analytic_name}"
            
            # Choose axes
            x, y = self.choose_axis(df, profile)
            if not x or not y:
                return None, f"Missing required columns for {analytic_name}"
            
            # Clean dataset
            df_clean = self.clean_dataset(df)
            
            # Aggregate for chart
            df_grouped = self.aggregate_for_chart(df_clean, x, y, analytic_name)
            
            if df_grouped.empty:
                return None, "No valid data after aggregation"
            
            print(f"✅ Built dataset for {analytic_name}: {df_grouped.shape}")
            return df_grouped, None
            
        except Exception as e:
            print(f"❌ Error in build_analytic_dataset: {e}")
            return None, str(e)
    
    def build_chart_payload(self, analytic_name: str, df_grouped: pd.DataFrame, x: str, y: str) -> Dict[str, Any]:
        """
        Build standardized chart payload for frontend.
        """
        try:
            profile = self.ANALYTIC_PROFILES[analytic_name]
            
            # Convert to chart data format
            if profile["chart"] == "multi_line":
                # Handle multi-line data structure
                lines_data = {}
                if 'Product' in df_grouped.columns:
                    for product in df_grouped['Product'].unique():
                        product_data = df_grouped[df_grouped['Product'] == product]
                        lines_data[product] = product_data[y].tolist()
                
                chart_data = {
                    "x": df_grouped[x].tolist(),
                    "lines": lines_data,
                    "x_label": self._get_standardized_axis_labels(analytic_name, profile["chart"])["x_label"],
                    "y_label": self._get_standardized_axis_labels(analytic_name, profile["chart"])["y_label"]
                }
            else:
                # Standard single-line/bar chart
                chart_data = {
                    "x": df_grouped[x].tolist(),
                    "y": df_grouped[y].tolist(),
                    "x_label": self._get_standardized_axis_labels(analytic_name, profile["chart"])["x_label"],
                    "y_label": self._get_standardized_axis_labels(analytic_name, profile["chart"])["y_label"]
                }
            
            return {
                "id": f"{analytic_name.lower().replace('_', '_')}",
                "title": analytic_name.replace('_', ' ').title(),
                "type": profile["chart"],
                "description": profile["description"],
                "icon": profile["icon"],
                "status": "success",
                "data": chart_data,
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                },
                "meta": {
                    "rows": len(df_grouped),
                    "distinct_x": df_grouped[x].nunique(),
                    "distinct_y": df_grouped[y].nunique(),
                }
            }
            
        except Exception as e:
            print(f"❌ Error in build_chart_payload: {e}")
            return None
    
    def run_all_analytics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Central dispatcher - builds each analytic separately to avoid duplication.
        """
        try:
            results = {}
            print(f"🔍 Running all analytics for {len(self.ANALYTIC_PROFILES)} analytic types")
            
            for analytic_name in self.ANALYTIC_PROFILES.keys():
                print(f"🔍 Processing {analytic_name}...")
                
                # Build dataset for this analytic
                df_grouped, error = self.build_analytic_dataset(df, analytic_name)
                
                if error:
                    results[analytic_name] = {"error": error}
                    print(f"❌ {analytic_name}: {error}")
                    continue
                
                # Get axes for this analytic
                profile = self.ANALYTIC_PROFILES[analytic_name]
                x, y = self.choose_axis(df, profile)
                
                # Build chart payload
                chart_payload = self.build_chart_payload(analytic_name, df_grouped, x, y)
                
                if chart_payload:
                    results[analytic_name] = chart_payload
                    print(f"✅ {analytic_name}: Generated chart with {len(df_grouped)} data points")
                else:
                    results[analytic_name] = {"error": "Failed to build chart payload"}
                    print(f"❌ {analytic_name}: Failed to build chart payload")
            
            return results
            
        except Exception as e:
            print(f"❌ Error in run_all_analytics: {e}")
            return {}
    
    def verify_unique_charts(self, charts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validation layer - ensure no chart duplicates content.
        """
        try:
            seen_hashes = set()
            unique_charts = {}
            duplicates_removed = 0
            
            for name, chart in charts.items():
                if "error" in chart:
                    unique_charts[name] = chart
                    continue
                
                # Create hash of chart data
                data_hash = hash(str(sorted(chart.get("data", {}).items())))
                
                if data_hash in seen_hashes:
                    print(f"⚠️ {name}: Duplicate chart removed")
                    duplicates_removed += 1
                else:
                    seen_hashes.add(data_hash)
                    unique_charts[name] = chart
                    print(f"✅ {name}: Unique content verified")
            
            print(f"🛡️ Removed {duplicates_removed} duplicate charts")
            return unique_charts
            
        except Exception as e:
            print(f"❌ Error in verify_unique_charts: {e}")
            return charts

    def _get_standardized_axis_labels(self, analytic_name: str, chart_type: str) -> Dict[str, str]:
        """Get standardized axis labels based on chart type and analytic name."""
        label_mapping = {
            "Sales Summary Report": {
                "x_label": "Date",
                "y_label": "Sales Amount (₱)"
            },
            "Product Performance Analysis": {
                "x_label": "Product Name", 
                "y_label": "Sales Amount (₱)"
            },
            "Regional Sales Analysis": {
                "x_label": "Region",
                "y_label": "Sales Amount (₱)"
            },
            "Sales Forecasting": {
                "x_label": "Date",
                "y_label": "Sales Amount (₱)"
            },
            "Product Demand Forecast": {
                "x_label": "Date",
                "y_label": "Quantity Demanded"
            },
            "Demand Forecasting": {
                "x_label": "Date", 
                "y_label": "Quantity Demanded"
            }
        }
        
        # Default labels if not found
        default_labels = {
            "x_label": "Date" if chart_type in ["line", "line_forecast"] else "Category",
            "y_label": "Value"
        }
        
        return label_mapping.get(analytic_name, default_labels)
    
    def _generate_line_chart(self, df: pd.DataFrame, df_columns: Dict[str, str], analytic_name: str) -> Dict[str, Any]:
        """Generate line chart data."""
        print(f"🔍 _generate_line_chart called for {analytic_name}")
        print(f"🔍 DataFrame shape: {df.shape}")
        print(f"🔍 DataFrame columns: {list(df.columns)}")
        print(f"🔍 df_columns: {df_columns}")
        
        date_col = df_columns.get("Date")
        sales_col = df_columns.get("Sales")
        
        print(f"🔍 date_col: {date_col}")
        print(f"🔍 sales_col: {sales_col}")
        
        if not date_col or not sales_col:
            print(f"❌ Missing required columns: date_col={date_col}, sales_col={sales_col}")
            return None
        
        # Check if columns exist in DataFrame
        if date_col not in df.columns:
            print(f"❌ Date column '{date_col}' not found in DataFrame")
            return None
        if sales_col not in df.columns:
            print(f"❌ Sales column '{sales_col}' not found in DataFrame")
            return None
        
        print(f"✅ Both columns found, proceeding with chart generation")
        
        # Group by date and sum sales
        chart_data = df.groupby(date_col)[sales_col].sum().reset_index()
        chart_data = chart_data.sort_values(date_col)
        
        print(f"🔍 Chart data shape: {chart_data.shape}")
        print(f"🔍 Chart data head: {chart_data.head()}")
        
        # Convert to list format
        try:
            if pd.api.types.is_datetime64_any_dtype(chart_data[date_col]):
                x_data = chart_data[date_col].dt.strftime('%Y-%m-%d').tolist()
            else:
                x_data = chart_data[date_col].tolist()
            
            # Handle the case where sales_col might be a Series or have multiple columns
            if isinstance(chart_data[sales_col], pd.Series):
                y_data = chart_data[sales_col].tolist()
            else:
                # If it's a DataFrame with multiple columns, take the first one
                y_data = chart_data[sales_col].iloc[:, 0].tolist()
            
            print(f"🔍 x_data length: {len(x_data)}")
            print(f"🔍 y_data length: {len(y_data)}")
            print(f"🔍 x_data sample: {x_data[:5]}")
            print(f"🔍 y_data sample: {y_data[:5]}")
            
        except Exception as e:
            print(f"❌ Error converting to lists: {e}")
            print(f"🔍 chart_data columns: {list(chart_data.columns)}")
            print(f"🔍 chart_data dtypes: {chart_data.dtypes}")
            return None
        
        # Standardized axis labels based on chart type
        axis_labels = self._get_standardized_axis_labels(analytic_name, "line")
        
        return {
            "id": f"{analytic_name.lower().replace(' ', '_')}",
            "title": analytic_name,
            "type": "line",
            "description": "Shows trend of total sales over time",
            "icon": "🕒",
            "status": "success",
            "data": {
                "x": chart_data[date_col].dt.strftime('%Y-%m-%d').tolist() if pd.api.types.is_datetime64_any_dtype(chart_data[date_col]) else chart_data[date_col].tolist(),
                "y": chart_data[sales_col].tolist(),
                "x_label": axis_labels["x_label"],
                "y_label": axis_labels["y_label"]
            },
            "config": {
                "maintainAspectRatio": False,
                "responsive": True
            }
        }
    
    def _generate_bar_chart(self, df: pd.DataFrame, df_columns: Dict[str, str], analytic_name: str) -> Dict[str, Any]:
        """Generate bar chart data."""
        if "Product" in df_columns:
            category_col = df_columns["Product"]
            icon = "📊"
            description = "Compares product performance"
        elif "Region" in df_columns:
            category_col = df_columns["Region"]
            icon = "🗺️"
            description = "Shows regional sales comparison"
        else:
            return None
        
        sales_col = df_columns.get("Sales")
        if not sales_col:
            return None
        
        # Group by category and sum sales
        chart_data = df.groupby(category_col)[sales_col].sum().reset_index()
        chart_data = chart_data.sort_values(sales_col, ascending=False)
        
        # Standardized axis labels based on chart type
        axis_labels = self._get_standardized_axis_labels(analytic_name, "bar")
        
        return {
            "id": f"{analytic_name.lower().replace(' ', '_')}",
            "title": analytic_name,
            "type": "bar",
            "description": description,
            "icon": icon,
            "status": "success",
            "data": {
                "x": chart_data[category_col].tolist(),
                "y": chart_data[sales_col].tolist(),
                "x_label": axis_labels["x_label"],
                "y_label": axis_labels["y_label"]
            },
            "config": {
                "maintainAspectRatio": False,
                "responsive": True
            }
        }
    
    def _generate_forecast_chart(self, df: pd.DataFrame, df_columns: Dict[str, str], analytic_name: str) -> Dict[str, Any]:
        """Generate forecast chart data (simplified)."""
        print(f"🔍 _generate_forecast_chart called for {analytic_name}")
        # For now, just generate a line chart but keep the forecast type
        line_chart = self._generate_line_chart(df, df_columns, analytic_name)
        if line_chart:
            line_chart['type'] = 'line_forecast'  # Keep the forecast type
        return line_chart
    
    def _generate_multi_line_chart(self, df: pd.DataFrame, df_columns: Dict[str, str], analytic_name: str) -> Dict[str, Any]:
        """Generate multi-line chart data for Product Demand Forecast."""
        print(f"🔍 _generate_multi_line_chart called for {analytic_name}")
        
        date_col = df_columns.get("Date")
        product_col = df_columns.get("Product")
        quantity_col = df_columns.get("Quantity")
        
        if not all([date_col, product_col, quantity_col]):
            print(f"❌ Missing required columns for multi-line chart")
            return None
        
        # Get top 5 products by total quantity
        top_products = df.groupby(product_col)[quantity_col].sum().nlargest(5).index.tolist()
        print(f"🔍 Top 5 products: {top_products}")
        
        # Create multi-line data structure
        lines_data = {}
        dates = sorted(df[date_col].unique())
        
        for product in top_products:
            product_data = df[df[product_col] == product].groupby(date_col)[quantity_col].sum()
            # Fill missing dates with 0
            product_series = pd.Series(0, index=dates)
            product_series.update(product_data)
            lines_data[product] = product_series.tolist()
        
        # Standardized axis labels
        axis_labels = self._get_standardized_axis_labels(analytic_name, "multi_line")
        
        return {
            "id": f"{analytic_name.lower().replace(' ', '_')}",
            "title": analytic_name,
            "type": "multi_line",
            "description": "Demand forecast for top 5 products",
            "icon": "📈",
            "status": "success",
            "data": {
                "x": [str(d) for d in dates],
                "lines": lines_data,
                "x_label": axis_labels["x_label"],
                "y_label": axis_labels["y_label"]
            },
            "config": {
                "maintainAspectRatio": False,
                "responsive": True
            }
        }
    
    def calculate_summary_metrics(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Calculate summary metrics from the actual dataset."""
        try:
            metrics = {}
            
            print(f"🔍 Calculating summary metrics")
            print(f"🔍 DataFrame columns: {list(df.columns)}")
            print(f"🔍 Column mapping: {column_mapping}")
            
            # Since DataFrame columns are already renamed to canonical names, use them directly
            print(f"🔍 Using canonical column names directly")
            
            # Calculate total sales/amount
            sales_col = 'Sales' if 'Sales' in df.columns else None
            print(f"🔍 Sales column: {sales_col}")
            if sales_col and sales_col in df.columns:
                try:
                    # Handle case where there might be multiple Sales columns
                    if isinstance(df[sales_col], pd.DataFrame):
                        # If it's a DataFrame (multiple columns), take the first one
                        sales_data = pd.to_numeric(df[sales_col].iloc[:, 0], errors='coerce')
                    else:
                        # If it's a Series
                        sales_data = pd.to_numeric(df[sales_col], errors='coerce')
                    
                    metrics['total_sales'] = float(sales_data.sum())
                    metrics['average_sales'] = float(sales_data.mean())
                    print(f"✅ Calculated total_sales: {metrics['total_sales']}")
                except Exception as e:
                    print(f"⚠️ Error calculating sales metrics: {e}")
                    print(f"🔍 Sales column type: {type(df[sales_col])}")
                    print(f"🔍 Sales column shape: {df[sales_col].shape if hasattr(df[sales_col], 'shape') else 'N/A'}")
            
            # Count unique products
            product_col = 'Product' if 'Product' in df.columns else None
            if product_col and product_col in df.columns:
                metrics['total_products'] = int(df[product_col].nunique())
                metrics['unique_products'] = int(df[product_col].nunique())
            
            # Count unique regions
            region_col = 'Region' if 'Region' in df.columns else None
            if region_col and region_col in df.columns:
                metrics['total_regions'] = int(df[region_col].nunique())
                metrics['unique_regions'] = int(df[region_col].nunique())
            
            # Calculate growth if date column exists
            date_col = 'Date' if 'Date' in df.columns else None
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

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for insights"""
        if len(values) < 2:
            return "stable"
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg * 1.1:
            return "upward"
        elif second_avg < first_avg * 0.9:
            return "downward"
        else:
            return "stable"
    

# Initialize TANAW processor
tanaw_processor = TANAWDataProcessor()

# Root endpoint
@app.route("/", methods=["GET"])
def root():
    """Root endpoint for health monitoring."""
    return jsonify({
        "status": "online",
        "service": "TANAW Analytics Service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200

# Health check endpoint
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "TANAW Analytics Service",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route("/api/files/upload-clean", methods=["POST"])
def analyze_clean():
    """
    Clean Architecture: OpenAI Column Mapping + TANAW Data Processing
    """
    print("🚀 TANAW Clean Architecture - OpenAI + TANAW Processing")
    
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
        print(f"📋 Analysis ID: {analysis_id}")
        
        # Step 1: Parse file
        print(f"🔍 Step 1: Parsing file {file.filename}")
        
        # Save uploaded file temporarily for parsing
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # Parse file
            parse_result = parse_file_robust(tmp_path, None)
            
            if not parse_result.success:
                return jsonify({
                    "success": False,
                    "message": parse_result.error_message
                }), 422
            
            df = parse_result.dataframe
            print(f"✅ File parsed: {parse_result.row_count} rows × {parse_result.col_count} columns")
            
        finally:
            # Clean up temporary file
            import os
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        # Step 2: OpenAI Column Mapping
        print(f"🤖 Step 2: OpenAI Column Mapping")
        
        try:
            # Get API key
            api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY') or os.getenv('OPENAI_API') or os.getenv('OPENAI_TOKEN')
            
            if not api_key:
                return jsonify({
                    "success": False,
                    "message": "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
                }), 500
            
            # Initialize GPT mapper
            gpt_mapper = GPTColumnMapper(api_key)
            
            # Get column names as strings
            columns = [str(col) for col in df.columns]
            print(f"📋 Mapping {len(columns)} columns: {columns}")
            
            # Map columns using GPT
            mapping_result = gpt_mapper.map_columns(columns, "retail")
            
            if not mapping_result.success:
                return jsonify({
                    "success": False,
                    "message": f"GPT mapping failed: {mapping_result.error_message}"
                }), 500
            
            print(f"✅ GPT mapping complete: {len(mapping_result.mappings)} mappings")
            
        except Exception as e:
            print(f"❌ GPT mapping error: {e}")
            return jsonify({
                "success": False,
                "message": f"GPT mapping failed: {str(e)}"
            }), 500
        
        # Step 3: TANAW Data Processing
        print(f"🧹 Step 3: TANAW Data Processing")
        
        try:
            # Create column mapping dictionary
            column_mapping = {}
            for mapping in mapping_result.mappings:
                if mapping.mapped_to != "Ignore":
                    column_mapping[mapping.original_column] = mapping.mapped_to
            
            print(f"📋 Column mappings: {column_mapping}")
            
            # Step 3.1: Domain Detection
            print(f"🎯 Step 3.1: Domain Detection")
            domain_classification = tanaw_processor.domain_detector.detect_domain(df, column_mapping)
            print(f"🎯 Detected Domain: {domain_classification.domain.upper()} (confidence: {domain_classification.confidence:.2f})")
            
            # Clean and transform data
            print(f"🔍 Starting data cleaning and transformation...")
            print(f"🔍 Original DataFrame shape: {df.shape}")
            print(f"🔍 Original DataFrame columns: {list(df.columns)}")
            cleaned_df = tanaw_processor.clean_and_transform_data(df, column_mapping)
            print(f"🔍 Cleaned DataFrame shape: {cleaned_df.shape}")
            print(f"🔍 Cleaned DataFrame columns: {list(cleaned_df.columns)}")
            
            # Generate domain-specific analytics and charts
            print(f"🔍 Starting {domain_classification.domain} analytics and chart generation...")
            analytics_result = tanaw_processor.generate_domain_analytics(cleaned_df, column_mapping, domain_classification)
            print(f"🔍 Analytics result: {analytics_result}")
            
            # Generate summary metrics
            print(f"🔍 Starting summary metrics calculation...")
            summary_metrics = tanaw_processor.calculate_summary_metrics(cleaned_df, column_mapping)
            print(f"🔍 Summary metrics: {summary_metrics}")
            analytics_result['summary_metrics'] = summary_metrics
            
            print(f"✅ TANAW processing complete")
            
        except Exception as e:
            print(f"❌ TANAW processing error: {e}")
            return jsonify({
                "success": False,
                "message": f"TANAW processing failed: {str(e)}"
            }), 500
        
        # Step 4: Prepare response
        print(f"📤 Step 4: Preparing response")
        
        # Format mappings for frontend
        formatted_mappings = []
        for mapping in mapping_result.mappings:
            if mapping.mapped_to != "Ignore":
                formatted_mappings.append({
                    'original_column': mapping.original_column,
                    'mapped_column': mapping.mapped_to,
                    'confidence': mapping.confidence,
                    'reasoning': mapping.reasoning,
                    'source': mapping.source,
                    'suggestions': []
                })
        
        # Prepare final response
        response_data = {
            "success": True,
            "analysis_id": analysis_id,
            "message": "Clean architecture analysis completed successfully",
            "mapped_columns": formatted_mappings,
            "analytics_readiness": analytics_result["readiness"],
            "data_quality": {
                "issues": [],
                "overall_score": 100,
                "warnings": []
            },
            "dataset_info": {
                "rows": parse_result.row_count,
                "columns": parse_result.col_count,
                "filename": file.filename,
                "encoding": parse_result.encoding_used,
                "delimiter": parse_result.delimiter_used
            },
            "gpt_metadata": {
                "total_cost": mapping_result.total_cost,
                "cache_hits": mapping_result.cache_hits,
                "processing_time": mapping_result.processing_time,
                "mapping_method": "gpt",
                "success": True
            },
            "processing_time": mapping_result.processing_time,
            "phases_completed": ["file_parsing", "column_mapping", "data_cleaning", "analytics_generation"],
            # Frontend completion criteria
            "status": "completed",
            "nextStep": "analysis_complete",
            "processed": True,
            "hasVisualization": len(analytics_result["charts"]) > 0,
            "hasCharts": len(analytics_result["charts"]) > 0,
            "shouldComplete": True,
            # Include charts directly
            "visualization": {
                "charts": analytics_result["charts"],
                "chart_count": len(analytics_result["charts"]),
                "generated_automatically": True
            },
            "analysis": {
                "charts": analytics_result["charts"],
                "analytics_results": analytics_result,
                "summary_metrics": analytics_result.get("summary_metrics", {}),
                "domain": analytics_result.get("domain", "sales"),
                "domain_confidence": analytics_result.get("domain_confidence", 0.0)
            }
        }
        
        # Store session data
        active_sessions[analysis_id] = {
            'dataframe': cleaned_df,
            'original_dataframe': df,
            'column_mapping': column_mapping,
            'results': response_data,
            'timestamp': datetime.now().isoformat(),
            'filename': file.filename
        }
        
        print(f"✅ Clean architecture analysis complete!")
        print(f"   📊 Generated {len(analytics_result['charts'])} charts")
        print(f"   💰 Total cost: ${mapping_result.total_cost:.4f}")
        print(f"   ⚡ Cache hits: {mapping_result.cache_hits}")
        
        # 🔧 SAFE SANITIZATION: Prevent Infinity values in JSON response
        print("🧹 Sanitizing numeric data to prevent Infinity in JSON...")
        sanitized_response = sanitize_numeric_data(response_data)
        
        return jsonify(sanitized_response), 200
        
    except Exception as e:
        print(f"❌ Clean architecture error: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"Analysis failed: {str(e)}"
        }), 500

@app.route("/api/visualizations-clean/<analysis_id>", methods=["GET"])
def get_visualizations_clean(analysis_id):
    """Get visualizations for clean architecture."""
    try:
        print(f"🔍 Fetching visualizations for analysis_id: {analysis_id}")
        
        if analysis_id not in active_sessions:
            return jsonify({
                "success": False,
                "error": "Analysis not found"
            }), 404
        
        session_data = active_sessions[analysis_id]
        results = session_data.get('results', {})
        
        # Get charts from results
        charts = results.get('visualization', {}).get('charts', [])
        
        return jsonify({
            "success": True,
            "charts": charts,
            "narratives": [],
            "total_charts": len(charts),
            "total_narratives": 0
        }), 200
        
    except Exception as e:
        print(f"❌ Visualization fetch error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    print("🚀 Starting TANAW Clean Architecture Server")
    print("📡 Server will be available at: http://localhost:5002")
    print("🔄 Auto-reload enabled for development")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5002)
