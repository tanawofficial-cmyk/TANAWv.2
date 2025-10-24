"""
TANAW Fallback Handler
Comprehensive fallback system for all chart types and analytics
Ensures graceful degradation when primary methods fail
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class TANAWFallbackHandler:
    """
    Comprehensive fallback system for TANAW analytics
    Provides alternative solutions when primary methods fail
    """
    
    def __init__(self):
        """Initialize fallback handler with fallback strategies"""
        self.fallback_strategies = {
            "bar_charts": {
                "primary": "enhanced_bar_chart",
                "fallback_1": "simple_bar_chart",
                "fallback_2": "basic_bar_chart",
                "fallback_3": "minimal_bar_chart"
            },
            "line_charts": {
                "primary": "enhanced_line_chart",
                "fallback_1": "simple_line_chart",
                "fallback_2": "basic_line_chart",
                "fallback_3": "minimal_line_chart"
            },
            "forecasts": {
                "primary": "prophet_forecast",
                "fallback_1": "linear_forecast",
                "fallback_2": "simple_trend_forecast",
                "fallback_3": "basic_forecast"
            },
            "inventory_analytics": {
                "primary": "full_inventory_analysis",
                "fallback_1": "basic_inventory_analysis",
                "fallback_2": "minimal_inventory_analysis",
                "fallback_3": "simple_stock_analysis"
            }
        }
    
    def handle_bar_chart_fallback(self, df: pd.DataFrame, chart_type: str, 
                                 primary_method: callable, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Handle bar chart generation with comprehensive fallbacks
        
        Args:
            df: DataFrame to analyze
            chart_type: Type of bar chart
            primary_method: Primary chart generation method
            **kwargs: Additional arguments
            
        Returns:
            Chart data or fallback chart
        """
        try:
            # Try primary method
            result = primary_method(df, **kwargs)
            if result and result.get('status') == 'success':
                return result
        except Exception as e:
            print(f"⚠️ Primary bar chart method failed: {e}")
        
        # Fallback 1: Simple bar chart
        try:
            return self._generate_simple_bar_chart(df, chart_type, **kwargs)
        except Exception as e:
            print(f"⚠️ Simple bar chart fallback failed: {e}")
        
        # Fallback 2: Basic bar chart
        try:
            return self._generate_basic_bar_chart(df, chart_type, **kwargs)
        except Exception as e:
            print(f"⚠️ Basic bar chart fallback failed: {e}")
        
        # Fallback 3: Minimal bar chart
        try:
            return self._generate_minimal_bar_chart(df, chart_type, **kwargs)
        except Exception as e:
            print(f"❌ All bar chart fallbacks failed: {e}")
            return self._generate_error_chart("Bar Chart", "Unable to generate chart")
    
    def handle_line_chart_fallback(self, df: pd.DataFrame, chart_type: str,
                                  primary_method: callable, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Handle line chart generation with comprehensive fallbacks
        
        Args:
            df: DataFrame to analyze
            chart_type: Type of line chart
            primary_method: Primary chart generation method
            **kwargs: Additional arguments
            
        Returns:
            Chart data or fallback chart
        """
        try:
            # Try primary method
            result = primary_method(df, **kwargs)
            if result and result.get('status') == 'success':
                return result
        except Exception as e:
            print(f"⚠️ Primary line chart method failed: {e}")
        
        # Fallback 1: Simple line chart
        try:
            return self._generate_simple_line_chart(df, chart_type, **kwargs)
        except Exception as e:
            print(f"⚠️ Simple line chart fallback failed: {e}")
        
        # Fallback 2: Basic line chart
        try:
            return self._generate_basic_line_chart(df, chart_type, **kwargs)
        except Exception as e:
            print(f"⚠️ Basic line chart fallback failed: {e}")
        
        # Fallback 3: Minimal line chart
        try:
            return self._generate_minimal_line_chart(df, chart_type, **kwargs)
        except Exception as e:
            print(f"❌ All line chart fallbacks failed: {e}")
            return self._generate_error_chart("Line Chart", "Unable to generate chart")
    
    def handle_forecast_fallback(self, df: pd.DataFrame, forecast_type: str,
                                primary_method: callable, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Handle forecast generation with comprehensive fallbacks
        
        Args:
            df: DataFrame to analyze
            forecast_type: Type of forecast
            primary_method: Primary forecast method
            **kwargs: Additional arguments
            
        Returns:
            Forecast data or fallback forecast
        """
        try:
            # Try primary method (Prophet)
            result = primary_method(df, **kwargs)
            if result and result.get('type') == 'line_forecast':
                return result
        except Exception as e:
            print(f"⚠️ Primary forecast method failed: {e}")
        
        # Fallback 1: Linear regression
        try:
            return self._generate_linear_forecast(df, forecast_type, **kwargs)
        except Exception as e:
            print(f"⚠️ Linear forecast fallback failed: {e}")
        
        # Fallback 2: Simple trend forecast
        try:
            return self._generate_simple_trend_forecast(df, forecast_type, **kwargs)
        except Exception as e:
            print(f"⚠️ Simple trend forecast fallback failed: {e}")
        
        # Fallback 3: Basic forecast
        try:
            return self._generate_basic_forecast(df, forecast_type, **kwargs)
        except Exception as e:
            print(f"❌ All forecast fallbacks failed: {e}")
            return self._generate_error_chart("Forecast", "Unable to generate forecast")
    
    def handle_inventory_fallback(self, df: pd.DataFrame, analysis_type: str,
                                 primary_method: callable, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Handle inventory analytics with comprehensive fallbacks
        
        Args:
            df: DataFrame to analyze
            analysis_type: Type of inventory analysis
            primary_method: Primary analysis method
            **kwargs: Additional arguments
            
        Returns:
            Analysis data or fallback analysis
        """
        try:
            # Try primary method
            result = primary_method(df, **kwargs)
            if result and result.get('status') == 'success':
                return result
        except Exception as e:
            print(f"⚠️ Primary inventory analysis failed: {e}")
        
        # Fallback 1: Basic inventory analysis
        try:
            return self._generate_basic_inventory_analysis(df, analysis_type, **kwargs)
        except Exception as e:
            print(f"⚠️ Basic inventory analysis fallback failed: {e}")
        
        # Fallback 2: Minimal inventory analysis
        try:
            return self._generate_minimal_inventory_analysis(df, analysis_type, **kwargs)
        except Exception as e:
            print(f"⚠️ Minimal inventory analysis fallback failed: {e}")
        
        # Fallback 3: Simple stock analysis
        try:
            return self._generate_simple_stock_analysis(df, analysis_type, **kwargs)
        except Exception as e:
            print(f"❌ All inventory analysis fallbacks failed: {e}")
            return self._generate_error_chart("Inventory Analysis", "Unable to generate analysis")
    
    def _generate_simple_bar_chart(self, df: pd.DataFrame, chart_type: str, **kwargs) -> Dict[str, Any]:
        """Generate simple bar chart with basic styling"""
        try:
            # Find numeric and categorical columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            if len(numeric_cols) == 0 or len(categorical_cols) == 0:
                raise ValueError("No suitable columns found")
            
            # Use first categorical and first numeric column
            x_col = categorical_cols[0]
            y_col = numeric_cols[0]
            
            # Simple aggregation
            if chart_type in ['product_comparison', 'stock_level']:
                grouped = df.groupby(x_col)[y_col].sum().reset_index()
            else:
                grouped = df.groupby(x_col)[y_col].mean().reset_index()
            
            grouped = grouped.sort_values(y_col, ascending=False).head(10)
            
            return {
                "id": f"simple_{chart_type}",
                "title": f"Simple {chart_type.replace('_', ' ').title()}",
                "type": "bar",
                "description": f"Basic {chart_type} analysis with simplified data",
                "brief_description": f"Simplified version of {chart_type} analysis using basic aggregation methods.",
                "icon": "📊",
                "status": "success",
                "data": {
                    "x": grouped[x_col].tolist(),
                    "y": grouped[y_col].tolist(),
                    "x_label": x_col,
                    "y_label": y_col
                },
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True,
                    "plugins": {
                        "legend": {"display": False},
                        "tooltip": {"enabled": True}
                    }
                },
                "meta": {
                    "fallback_type": "simple",
                    "original_columns": list(df.columns),
                    "used_columns": [x_col, y_col]
                }
            }
        except Exception as e:
            raise Exception(f"Simple bar chart generation failed: {e}")
    
    def _generate_basic_bar_chart(self, df: pd.DataFrame, chart_type: str, **kwargs) -> Dict[str, Any]:
        """Generate basic bar chart with minimal requirements"""
        try:
            # Use any available columns
            cols = list(df.columns)
            if len(cols) < 2:
                raise ValueError("Insufficient columns")
            
            x_col = cols[0]
            y_col = cols[1] if len(cols) > 1 else cols[0]
            
            # Convert to numeric if possible
            try:
                df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            except:
                pass
            
            # Simple count or sum
            if df[y_col].dtype in ['object', 'string']:
                grouped = df.groupby(x_col).size().reset_index(name='count')
                y_data = grouped['count']
            else:
                grouped = df.groupby(x_col)[y_col].sum().reset_index()
                y_data = grouped[y_col]
            
            grouped = grouped.sort_values(y_data.name, ascending=False).head(8)
            
            return {
                "id": f"basic_{chart_type}",
                "title": f"Basic {chart_type.replace('_', ' ').title()}",
                "type": "bar",
                "description": f"Basic {chart_type} analysis",
                "brief_description": f"Basic analysis using available data columns.",
                "icon": "📊",
                "status": "success",
                "data": {
                    "x": grouped[x_col].tolist(),
                    "y": grouped[y_data.name].tolist(),
                    "x_label": x_col,
                    "y_label": y_data.name
                },
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                },
                "meta": {
                    "fallback_type": "basic",
                    "warning": "Using basic fallback due to data limitations"
                }
            }
        except Exception as e:
            raise Exception(f"Basic bar chart generation failed: {e}")
    
    def _generate_minimal_bar_chart(self, df: pd.DataFrame, chart_type: str, **kwargs) -> Dict[str, Any]:
        """Generate minimal bar chart with any available data"""
        try:
            # Use first two columns
            cols = list(df.columns)
            x_col = cols[0]
            y_col = cols[1] if len(cols) > 1 else cols[0]
            
            # Simple count
            grouped = df.groupby(x_col).size().reset_index(name='count')
            grouped = grouped.head(5)  # Limit to 5 items
            
            return {
                "id": f"minimal_{chart_type}",
                "title": f"Minimal {chart_type.replace('_', ' ').title()}",
                "type": "bar",
                "description": f"Minimal {chart_type} analysis",
                "brief_description": f"Minimal analysis with limited data processing.",
                "icon": "📊",
                "status": "success",
                "data": {
                    "x": grouped[x_col].tolist(),
                    "y": grouped['count'].tolist(),
                    "x_label": x_col,
                    "y_label": "Count"
                },
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                },
                "meta": {
                    "fallback_type": "minimal",
                    "warning": "Using minimal fallback - limited functionality"
                }
            }
        except Exception as e:
            raise Exception(f"Minimal bar chart generation failed: {e}")
    
    def _generate_simple_line_chart(self, df: pd.DataFrame, chart_type: str, **kwargs) -> Dict[str, Any]:
        """Generate simple line chart with basic time series"""
        try:
            # Find date and numeric columns
            date_cols = []
            numeric_cols = []
            
            for col in df.columns:
                try:
                    pd.to_datetime(df[col].head(5), errors='coerce')
                    date_cols.append(col)
                except:
                    if pd.to_numeric(df[col], errors='coerce').notna().sum() > 0:
                        numeric_cols.append(col)
            
            if not date_cols or not numeric_cols:
                raise ValueError("No suitable date or numeric columns")
            
            date_col = date_cols[0]
            value_col = numeric_cols[0]
            
            # Convert to datetime and numeric
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
            
            # Remove nulls and sort
            df_clean = df.dropna(subset=[date_col, value_col])
            df_clean = df_clean.sort_values(date_col)
            
            return {
                "id": f"simple_{chart_type}",
                "title": f"Simple {chart_type.replace('_', ' ').title()}",
                "type": "line",
                "description": f"Basic {chart_type} trend analysis",
                "brief_description": f"Simplified time series analysis using available data.",
                "icon": "📈",
                "status": "success",
                "data": {
                    "x": df_clean[date_col].dt.strftime('%Y-%m-%d').tolist(),
                    "y": df_clean[value_col].tolist(),
                    "x_label": "Date",
                    "y_label": value_col
                },
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                },
                "meta": {
                    "fallback_type": "simple",
                    "data_points": len(df_clean)
                }
            }
        except Exception as e:
            raise Exception(f"Simple line chart generation failed: {e}")
    
    def _generate_basic_line_chart(self, df: pd.DataFrame, chart_type: str, **kwargs) -> Dict[str, Any]:
        """Generate basic line chart with minimal time series"""
        try:
            # Use first two columns as x and y
            cols = list(df.columns)
            x_col = cols[0]
            y_col = cols[1] if len(cols) > 1 else cols[0]
            
            # Try to convert to numeric
            try:
                df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            except:
                pass
            
            # Sort by x column
            df_sorted = df.sort_values(x_col).head(20)
            
            return {
                "id": f"basic_{chart_type}",
                "title": f"Basic {chart_type.replace('_', ' ').title()}",
                "type": "line",
                "description": f"Basic {chart_type} analysis",
                "brief_description": f"Basic line chart using available data.",
                "icon": "📈",
                "status": "success",
                "data": {
                    "x": df_sorted[x_col].astype(str).tolist(),
                    "y": df_sorted[y_col].tolist(),
                    "x_label": x_col,
                    "y_label": y_col
                },
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                },
                "meta": {
                    "fallback_type": "basic",
                    "warning": "Using basic fallback"
                }
            }
        except Exception as e:
            raise Exception(f"Basic line chart generation failed: {e}")
    
    def _generate_minimal_line_chart(self, df: pd.DataFrame, chart_type: str, **kwargs) -> Dict[str, Any]:
        """Generate minimal line chart with any data"""
        try:
            # Use first column as index, second as values
            cols = list(df.columns)
            x_data = list(range(len(df)))
            y_data = df[cols[0]].tolist() if len(cols) > 0 else [0] * len(df)
            
            return {
                "id": f"minimal_{chart_type}",
                "title": f"Minimal {chart_type.replace('_', ' ').title()}",
                "type": "line",
                "description": f"Minimal {chart_type} analysis",
                "brief_description": f"Minimal line chart with basic data.",
                "icon": "📈",
                "status": "success",
                "data": {
                    "x": x_data,
                    "y": y_data,
                    "x_label": "Index",
                    "y_label": "Value"
                },
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                },
                "meta": {
                    "fallback_type": "minimal",
                    "warning": "Using minimal fallback"
                }
            }
        except Exception as e:
            raise Exception(f"Minimal line chart generation failed: {e}")
    
    def _generate_linear_forecast(self, df: pd.DataFrame, forecast_type: str, **kwargs) -> Dict[str, Any]:
        """Generate linear regression forecast"""
        try:
            # Find date and value columns
            date_col = None
            value_col = None
            
            for col in df.columns:
                try:
                    pd.to_datetime(df[col].head(5), errors='coerce')
                    date_col = col
                    break
                except:
                    continue
            
            for col in df.columns:
                if col != date_col and pd.to_numeric(df[col], errors='coerce').notna().sum() > 0:
                    value_col = col
                    break
            
            if not date_col or not value_col:
                raise ValueError("No suitable date or value columns")
            
            # Prepare data
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
            df_clean = df.dropna(subset=[date_col, value_col]).sort_values(date_col)
            
            if len(df_clean) < 3:
                raise ValueError("Insufficient data for forecasting")
            
            # Simple linear regression
            x = np.arange(len(df_clean))
            y = df_clean[value_col].values
            
            # Calculate trend
            slope = np.polyfit(x, y, 1)[0]
            intercept = np.polyfit(x, y, 1)[1]
            
            # Generate forecast
            forecast_periods = kwargs.get('forecast_periods', 7)
            future_x = np.arange(len(df_clean), len(df_clean) + forecast_periods)
            forecast_y = slope * future_x + intercept
            
            # Create chart data
            historical_data = []
            for i, row in df_clean.iterrows():
                historical_data.append({
                    "x": row[date_col].strftime('%Y-%m-%d'),
                    "y": float(row[value_col]),
                    "type": "historical"
                })
            
            forecast_data = []
            for i, (x_val, y_val) in enumerate(zip(future_x, forecast_y)):
                future_date = df_clean[date_col].iloc[-1] + pd.Timedelta(days=i+1)
                forecast_data.append({
                    "x": future_date.strftime('%Y-%m-%d'),
                    "y": float(y_val),
                    "type": "forecast"
                })
            
            chart_data = historical_data + forecast_data
            
            return {
                "type": "line_forecast",
                "title": f"{forecast_type.title()} (Linear Regression)",
                "description": f"{forecast_type} forecast using linear regression",
                "brief_description": f"Linear regression forecast for {forecast_type} with {forecast_periods} days ahead.",
                "x_label": "Date",
                "y_label": value_col,
                "data": chart_data,
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                },
                "insights": {
                    "model_type": "Linear Regression (Fallback)",
                    "forecast_periods": forecast_periods,
                    "trend_slope": float(slope),
                    "model_accuracy": "Medium (Linear Regression)"
                },
                "meta": {
                    "fallback_type": "linear",
                    "warning": "Using linear regression fallback"
                }
            }
        except Exception as e:
            raise Exception(f"Linear forecast generation failed: {e}")
    
    def _generate_simple_trend_forecast(self, df: pd.DataFrame, forecast_type: str, **kwargs) -> Dict[str, Any]:
        """Generate simple trend-based forecast"""
        try:
            # Use any numeric column
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise ValueError("No numeric columns found")
            
            value_col = numeric_cols[0]
            values = df[value_col].dropna().tolist()
            
            if len(values) < 3:
                raise ValueError("Insufficient data")
            
            # Simple trend calculation
            recent_avg = np.mean(values[-3:])  # Last 3 values
            overall_avg = np.mean(values)
            trend = recent_avg - overall_avg
            
            # Generate forecast
            forecast_periods = kwargs.get('forecast_periods', 7)
            forecast_values = [recent_avg + (trend * i) for i in range(1, forecast_periods + 1)]
            
            # Create chart data
            historical_data = [{"x": f"Day {i+1}", "y": float(val), "type": "historical"} 
                             for i, val in enumerate(values)]
            forecast_data = [{"x": f"Day {len(values)+i+1}", "y": float(val), "type": "forecast"} 
                           for i, val in enumerate(forecast_values)]
            
            chart_data = historical_data + forecast_data
            
            return {
                "type": "line_forecast",
                "title": f"{forecast_type.title()} (Simple Trend)",
                "description": f"{forecast_type} forecast using simple trend analysis",
                "brief_description": f"Simple trend-based forecast for {forecast_type}.",
                "x_label": "Period",
                "y_label": value_col,
                "data": chart_data,
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                },
                "insights": {
                    "model_type": "Simple Trend (Fallback)",
                    "forecast_periods": forecast_periods,
                    "trend": float(trend),
                    "model_accuracy": "Low (Simple Trend)"
                },
                "meta": {
                    "fallback_type": "simple_trend",
                    "warning": "Using simple trend fallback"
                }
            }
        except Exception as e:
            raise Exception(f"Simple trend forecast generation failed: {e}")
    
    def _generate_basic_forecast(self, df: pd.DataFrame, forecast_type: str, **kwargs) -> Dict[str, Any]:
        """Generate basic forecast with minimal data"""
        try:
            # Use any available data
            cols = list(df.columns)
            if len(cols) == 0:
                raise ValueError("No data available")
            
            # Simple average-based forecast
            values = []
            for col in cols:
                try:
                    numeric_vals = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(numeric_vals) > 0:
                        values.extend(numeric_vals.tolist())
                except:
                    continue
            
            if not values:
                raise ValueError("No numeric data found")
            
            avg_value = np.mean(values)
            forecast_periods = kwargs.get('forecast_periods', 7)
            
            # Create simple forecast
            historical_data = [{"x": f"Period {i+1}", "y": float(val), "type": "historical"} 
                             for i, val in enumerate(values[:10])]  # Limit to 10 points
            forecast_data = [{"x": f"Period {len(values)+i+1}", "y": float(avg_value), "type": "forecast"} 
                           for i in range(forecast_periods)]
            
            chart_data = historical_data + forecast_data
            
            return {
                "type": "line_forecast",
                "title": f"{forecast_type.title()} (Basic)",
                "description": f"Basic {forecast_type} forecast",
                "brief_description": f"Basic forecast using average values.",
                "x_label": "Period",
                "y_label": "Value",
                "data": chart_data,
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                },
                "insights": {
                    "model_type": "Basic Average (Fallback)",
                    "forecast_periods": forecast_periods,
                    "average_value": float(avg_value),
                    "model_accuracy": "Very Low (Basic Average)"
                },
                "meta": {
                    "fallback_type": "basic",
                    "warning": "Using basic fallback - limited accuracy"
                }
            }
        except Exception as e:
            raise Exception(f"Basic forecast generation failed: {e}")
    
    def _generate_basic_inventory_analysis(self, df: pd.DataFrame, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """Generate basic inventory analysis"""
        try:
            # Find numeric columns for stock levels
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            if len(numeric_cols) == 0:
                raise ValueError("No numeric columns for inventory analysis")
            
            # Use first numeric column as stock level
            stock_col = numeric_cols[0]
            product_col = categorical_cols[0] if len(categorical_cols) > 0 else "Item"
            
            # Basic stock analysis
            if len(categorical_cols) > 0:
                grouped = df.groupby(product_col)[stock_col].sum().reset_index()
            else:
                # Create dummy product names
                df[product_col] = [f"Product {i+1}" for i in range(len(df))]
                grouped = df.groupby(product_col)[stock_col].sum().reset_index()
            
            grouped = grouped.sort_values(stock_col, ascending=False).head(10)
            
            return {
                "id": f"basic_{analysis_type}",
                "title": f"Basic {analysis_type.replace('_', ' ').title()}",
                "type": "bar",
                "description": f"Basic {analysis_type} analysis",
                "brief_description": f"Basic inventory analysis using available data.",
                "icon": "📦",
                "status": "success",
                "data": {
                    "x": grouped[product_col].tolist(),
                    "y": grouped[stock_col].tolist(),
                    "x_label": "Product",
                    "y_label": "Stock Level"
                },
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                },
                "meta": {
                    "fallback_type": "basic",
                    "warning": "Using basic inventory analysis fallback"
                }
            }
        except Exception as e:
            raise Exception(f"Basic inventory analysis generation failed: {e}")
    
    def _generate_minimal_inventory_analysis(self, df: pd.DataFrame, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """Generate minimal inventory analysis"""
        try:
            # Use any available data
            cols = list(df.columns)
            if len(cols) == 0:
                raise ValueError("No data available")
            
            # Create simple analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                # Use count as value
                values = [1] * len(df)
                labels = [f"Item {i+1}" for i in range(len(df))]
            else:
                values = df[numeric_cols[0]].tolist()
                labels = [f"Item {i+1}" for i in range(len(df))]
            
            # Limit to 5 items
            data_points = min(5, len(values))
            
            return {
                "id": f"minimal_{analysis_type}",
                "title": f"Minimal {analysis_type.replace('_', ' ').title()}",
                "type": "bar",
                "description": f"Minimal {analysis_type} analysis",
                "brief_description": f"Minimal inventory analysis with limited data.",
                "icon": "📦",
                "status": "success",
                "data": {
                    "x": labels[:data_points],
                    "y": values[:data_points],
                    "x_label": "Item",
                    "y_label": "Value"
                },
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                },
                "meta": {
                    "fallback_type": "minimal",
                    "warning": "Using minimal fallback - very limited functionality"
                }
            }
        except Exception as e:
            raise Exception(f"Minimal inventory analysis generation failed: {e}")
    
    def _generate_simple_stock_analysis(self, df: pd.DataFrame, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """Generate simple stock analysis"""
        try:
            # Use any numeric data
            numeric_data = []
            for col in df.columns:
                try:
                    vals = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(vals) > 0:
                        numeric_data.extend(vals.tolist())
                except:
                    continue
            
            if not numeric_data:
                numeric_data = [1] * len(df)
            
            # Simple summary
            summary_data = [
                {"x": "Total Items", "y": len(df)},
                {"x": "Average Value", "y": np.mean(numeric_data)},
                {"x": "Max Value", "y": np.max(numeric_data)},
                {"x": "Min Value", "y": np.min(numeric_data)}
            ]
            
            return {
                "id": f"simple_{analysis_type}",
                "title": f"Simple {analysis_type.replace('_', ' ').title()}",
                "type": "bar",
                "description": f"Simple {analysis_type} summary",
                "brief_description": f"Simple stock analysis summary.",
                "icon": "📦",
                "status": "success",
                "data": {
                    "x": [item["x"] for item in summary_data],
                    "y": [item["y"] for item in summary_data],
                    "x_label": "Metric",
                    "y_label": "Value"
                },
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                },
                "meta": {
                    "fallback_type": "simple",
                    "warning": "Using simple stock analysis fallback"
                }
            }
        except Exception as e:
            raise Exception(f"Simple stock analysis generation failed: {e}")
    
    def _generate_error_chart(self, chart_type: str, error_message: str) -> Dict[str, Any]:
        """Generate error chart when all fallbacks fail"""
        return {
            "id": f"error_{chart_type.lower().replace(' ', '_')}",
            "title": f"{chart_type} (Error)",
            "type": "bar",
            "description": f"Unable to generate {chart_type.lower()}",
            "brief_description": f"Error: {error_message}. Please check your data and try again.",
            "icon": "❌",
            "status": "error",
            "data": {
                "x": ["Error"],
                "y": [0],
                "x_label": "Status",
                "y_label": "Value"
            },
            "config": {
                "maintainAspectRatio": False,
                "responsive": True
            },
            "meta": {
                "fallback_type": "error",
                "error_message": error_message,
                "warning": "All fallback methods failed"
            }
        }
