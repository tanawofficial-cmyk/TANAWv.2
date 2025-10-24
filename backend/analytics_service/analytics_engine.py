#!/usr/bin/env python3
"""
TANAW Analytics Engine
Automatically generates meaningful charts for each of the 5 core analytics
with fixed chart types and data preparation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import warnings
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

class TANAWAnalyticsEngine:
    """
    Core analytics engine that automatically generates visualizations
    for each of TANAW's 5 core analytics with fixed chart types.
    """
    
    def __init__(self):
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
    
    def check_analytics_readiness(self, mapped_columns: Dict[str, str]) -> Dict[str, Any]:
        """
        Check which analytics are ready based on mapped columns.
        
        Args:
            mapped_columns: Dictionary of {original_column: mapped_canonical_type}
            
        Returns:
            Dictionary with analytics readiness status
        """
        reverse_mapping = {v: k for k, v in mapped_columns.items()}
        readiness = {
            'available_analytics': [],
            'unavailable_analytics': [],
            'ready_count': 0,
            'total_count': len(self.analytics_config)
        }
        
        for analytic_name, config in self.analytics_config.items():
            required_cols = config['required_columns']
            has_required = all(col in reverse_mapping for col in required_cols)
            
            if has_required:
                readiness['available_analytics'].append({
                    'name': analytic_name,
                    'status': 'ready',
                    'required_columns': required_cols,
                    'chart_type': config['chart_type'],
                    'description': config['description'],
                    'icon': config['icon']
                })
                readiness['ready_count'] += 1
            else:
                missing_cols = [col for col in required_cols if col not in reverse_mapping]
                readiness['unavailable_analytics'].append({
                    'name': analytic_name,
                    'status': 'unavailable',
                    'missing_columns': missing_cols,
                    'reason': f'Missing required columns: {", ".join(missing_cols)}'
                })
        
        return readiness
    
    def prepare_analytics_data(self, df: pd.DataFrame, mapped_columns: Dict[str, str]) -> Dict[str, Any]:
        """
        Prepare data for all available analytics.
        
        Args:
            df: Original DataFrame
            mapped_columns: Column mapping dictionary
            
        Returns:
            Dictionary with prepared data for each analytic
        """
        print(f"\n🔧 Preparing Analytics Data")
        print(f"   Dataset: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"   Mapped columns: {mapped_columns}")
        
        # Create reverse mapping
        reverse_mapping = {v: k for k, v in mapped_columns.items()}
        
        # Check which analytics are available
        readiness = self.check_analytics_readiness(mapped_columns)
        available_analytics = readiness['available_analytics']
        
        results = {
            'analytics_results': [],
            'readiness': readiness,
            'data_quality': self._assess_data_quality(df, reverse_mapping)
        }
        
        # Process each available analytic
        for analytic in available_analytics:
            analytic_name = analytic['name']
            chart_type = analytic['chart_type']
            
            print(f"\n📊 Processing: {analytic_name}")
            
            try:
                if analytic_name == "Sales Summary Report":
                    chart_data = self._prepare_sales_summary(df, reverse_mapping)
                elif analytic_name == "Product Performance Analysis":
                    chart_data = self._prepare_product_performance(df, reverse_mapping)
                elif analytic_name == "Regional Sales Analysis":
                    chart_data = self._prepare_regional_sales(df, reverse_mapping)
                elif analytic_name == "Sales Forecasting":
                    chart_data = self._prepare_sales_forecasting(df, reverse_mapping)
                elif analytic_name == "Demand Forecasting":
                    chart_data = self._prepare_demand_forecasting(df, reverse_mapping)
                else:
                    continue
                
                # Add metadata without overriding the correct format
                chart_data['type'] = analytic_name
                chart_data['chart_type'] = chart_type
                chart_data['description'] = analytic['description']
                chart_data['icon'] = analytic['icon']
                chart_data['status'] = 'success'
                
                results['analytics_results'].append(chart_data)
                print(f"   ✅ {analytic_name} prepared successfully")
                
            except Exception as e:
                print(f"   ❌ {analytic_name} failed: {e}")
                results['analytics_results'].append({
                    'id': f'error_{analytic_name.lower().replace(" ", "_")}',
                    'title': f'{analytic_name} (Error)',
                    'type': chart_type,
                    'priority': 'low',
                    'data': {
                        'x': [],
                        'y': []
                    },
                    'config': {
                        'maintainAspectRatio': False,
                        'responsive': True
                    },
                    'status': 'error',
                    'error': str(e),
                    'description': analytic['description'],
                    'icon': analytic['icon']
                })
        
        print(f"\n✅ Analytics Data Preparation Complete")
        print(f"   Successful: {len([r for r in results['analytics_results'] if r['status'] == 'success'])}")
        print(f"   Failed: {len([r for r in results['analytics_results'] if r['status'] == 'error'])}")
        
        return results
    
    def _prepare_sales_summary(self, df: pd.DataFrame, reverse_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Prepare Sales Summary Report data (Line Chart)."""
        print(f"\n🔍 _sales_summary_report debug:")
        print(f"   Reverse mapping: {reverse_mapping}")
        
        date_col = reverse_mapping.get('Date')
        sales_col = reverse_mapping.get('Sales')
        
        print(f"   Date column: '{date_col}'")
        print(f"   Sales column: '{sales_col}'")
        print(f"   DataFrame columns: {list(df.columns)}")
        print(f"   Date in columns: {date_col in df.columns if date_col else False}")
        print(f"   Sales in columns: {sales_col in df.columns if sales_col else False}")
        
        if not date_col or not sales_col:
            print(f"   ✗ Missing required columns - returning None")
            return None
            
        if date_col not in df.columns or sales_col not in df.columns:
            print(f"   ✗ Missing columns - returning None")
            return None
        
        # Ensure date column is datetime
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # Group by date and sum sales
        daily_sales = df.groupby(date_col)[sales_col].sum().reset_index()
        daily_sales = daily_sales.sort_values(date_col)
        
        # Convert to proper chart format
        chart_data = []
        for _, row in daily_sales.iterrows():
            chart_data.append({
                'date': row[date_col].strftime('%Y-%m-%d') if pd.notna(row[date_col]) else None,
                'sales': float(row[sales_col]) if pd.notna(row[sales_col]) else 0
            })
        
        # Prepare chart data in the format expected by frontend
        return {
            'id': f'line_{date_col}_{sales_col}',
            'title': 'Sales Summary Report',
            'type': 'line',
            'priority': 'high',
            'data': {
                'x': [item['date'] for item in chart_data],
                'y': [item['sales'] for item in chart_data]
            },
            'config': {
                'maintainAspectRatio': False,
                'responsive': True,
                'scales': {
                    'y': {
                        'beginAtZero': False
                    }
                }
            }
        }
    
    def _prepare_product_performance(self, df: pd.DataFrame, reverse_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Prepare Product Performance Analysis data (Bar Chart)."""
        product_col = reverse_mapping.get('Product')
        sales_col = reverse_mapping.get('Sales')
        
        if not product_col or not sales_col:
            print(f"   ✗ Missing required columns - returning None")
            return None
            
        if product_col not in df.columns or sales_col not in df.columns:
            print(f"   ✗ Missing columns - returning None")
            return None
        
        # Group by product and sum sales
        product_sales = df.groupby(product_col)[sales_col].sum().reset_index()
        product_sales = product_sales.sort_values(sales_col, ascending=False)
        
        # Take top 10 products
        product_sales = product_sales.head(10)
        
        # Convert to proper chart format
        chart_data = []
        for _, row in product_sales.iterrows():
            chart_data.append({
                'product': str(row[product_col]) if pd.notna(row[product_col]) else 'Unknown',
                'sales': float(row[sales_col]) if pd.notna(row[sales_col]) else 0
            })
        
        # Prepare chart data in the format expected by frontend
        return {
            'id': f'bar_{product_col}_{sales_col}',
            'title': 'Product Performance Analysis',
            'type': 'bar',
            'priority': 'high',
            'data': {
                'x': [item['product'] for item in chart_data],
                'y': [item['sales'] for item in chart_data]
            },
            'config': {
                'maintainAspectRatio': False,
                'responsive': True,
                'scales': {
                    'y': {
                        'beginAtZero': True
                    }
                }
            }
        }
    
    def _prepare_regional_sales(self, df: pd.DataFrame, reverse_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Prepare Regional Sales Analysis data (Bar Chart)."""
        region_col = reverse_mapping.get('Region')
        sales_col = reverse_mapping.get('Sales')
        
        if not region_col or not sales_col:
            print(f"   ✗ Missing required columns - returning None")
            return None
            
        if region_col not in df.columns or sales_col not in df.columns:
            print(f"   ✗ Missing columns - returning None")
            return None
        
        # Group by region and sum sales
        regional_sales = df.groupby(region_col)[sales_col].sum().reset_index()
        regional_sales = regional_sales.sort_values(sales_col, ascending=False)
        
        # Convert to proper chart format
        chart_data = []
        for _, row in regional_sales.iterrows():
            chart_data.append({
                'region': str(row[region_col]) if pd.notna(row[region_col]) else 'Unknown',
                'sales': float(row[sales_col]) if pd.notna(row[sales_col]) else 0
            })
        
        # Prepare chart data in the format expected by frontend
        return {
            'id': f'bar_{region_col}_{sales_col}',
            'title': 'Regional Sales Analysis',
            'type': 'bar',
            'priority': 'high',
            'data': {
                'x': [item['region'] for item in chart_data],
                'y': [item['sales'] for item in chart_data]
            },
            'config': {
                'maintainAspectRatio': False,
                'responsive': True,
                'scales': {
                    'y': {
                        'beginAtZero': True
                    }
                }
            }
        }
    
    def _prepare_sales_forecasting(self, df: pd.DataFrame, reverse_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Prepare Sales Forecasting data (Line Chart with Forecast)."""
        date_col = reverse_mapping.get('Date')
        sales_col = reverse_mapping.get('Sales')
        
        if not date_col or not sales_col:
            print(f"   ✗ Missing required columns - returning None")
            return None
            
        if date_col not in df.columns or sales_col not in df.columns:
            print(f"   ✗ Missing columns - returning None")
            return None
        
        # Ensure date column is datetime
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # Group by date and sum sales
        daily_sales = df.groupby(date_col)[sales_col].sum().reset_index()
        daily_sales = daily_sales.sort_values(date_col)
        
        # Convert to proper chart format
        chart_data = []
        for _, row in daily_sales.iterrows():
            chart_data.append({
                'date': row[date_col].strftime('%Y-%m-%d') if pd.notna(row[date_col]) else None,
                'sales': float(row[sales_col]) if pd.notna(row[sales_col]) else 0
            })
        
        # Check if we have enough data for forecasting
        if len(daily_sales) < 7:
            return {
                'id': f'line_{date_col}_{sales_col}_forecast',
                'title': 'Sales Forecasting (Insufficient Data)',
                'type': 'line',
                'priority': 'high',
                'data': {
                    'x': [item['date'] for item in chart_data],
                    'y': [item['sales'] for item in chart_data]
                },
                'config': {
                    'maintainAspectRatio': False,
                    'responsive': True,
                    'scales': {
                        'y': {
                            'beginAtZero': False
                        }
                    }
                },
                'forecast_available': False,
                'warning': 'Not enough data for forecasting (minimum 7 data points required)'
            }
        
        # Prepare time series data
        daily_sales['day_number'] = (daily_sales[date_col] - daily_sales[date_col].min()).dt.days
        
        # Simple linear regression for forecasting
        X = daily_sales[['day_number']].values
        y = daily_sales[sales_col].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate forecast for next 7 days
        last_day = daily_sales['day_number'].max()
        forecast_days = np.arange(last_day + 1, last_day + 8)
        forecast_sales = model.predict(forecast_days.reshape(-1, 1))
        
        # Create forecast dates
        last_date = daily_sales[date_col].max()
        forecast_dates = [last_date + timedelta(days=i) for i in range(1, 8)]
        
        # Add forecast data to chart
        for date, sales in zip(forecast_dates, forecast_sales):
            chart_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'sales': float(sales)
            })
        
        # Prepare chart data in the format expected by frontend
        return {
            'id': f'line_{date_col}_{sales_col}_forecast',
            'title': 'Sales Forecasting',
            'type': 'line',
            'priority': 'high',
            'data': {
                'x': [item['date'] for item in chart_data],
                'y': [item['sales'] for item in chart_data]
            },
            'config': {
                'maintainAspectRatio': False,
                'responsive': True,
                'scales': {
                    'y': {
                        'beginAtZero': False
                    }
                }
            },
            'forecast_available': True,
            'forecast_period': '7 days'
        }
    
    def _prepare_demand_forecasting(self, df: pd.DataFrame, reverse_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Prepare Demand Forecasting data (Multi-Line Chart)."""
        date_col = reverse_mapping.get('Date')
        product_col = reverse_mapping.get('Product')
        quantity_col = reverse_mapping.get('Quantity')
        
        if not date_col or not product_col or not quantity_col:
            print(f"   ✗ Missing required columns - returning None")
            return None
            
        if date_col not in df.columns or product_col not in df.columns or quantity_col not in df.columns:
            print(f"   ✗ Missing columns - returning None")
            return None
        
        # Ensure date column is datetime
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # Group by date and product, sum quantities
        demand_data = df.groupby([date_col, product_col])[quantity_col].sum().reset_index()
        demand_data = demand_data.sort_values([date_col, product_col])
        
        # Convert to proper chart format
        chart_data = []
        for _, row in demand_data.iterrows():
            chart_data.append({
                'date': row[date_col].strftime('%Y-%m-%d') if pd.notna(row[date_col]) else None,
                'product': str(row[product_col]) if pd.notna(row[product_col]) else 'Unknown',
                'quantity': float(row[quantity_col]) if pd.notna(row[quantity_col]) else 0
            })
        
        # Check if we have enough data for forecasting
        if len(demand_data) < 14:  # Need at least 2 weeks of data
            return {
                'id': f'line_{date_col}_{quantity_col}_demand',
                'title': 'Demand Forecasting (Insufficient Data)',
                'type': 'line',
                'priority': 'high',
                'data': {
                    'x': [item['date'] for item in chart_data],
                    'y': [item['quantity'] for item in chart_data]
                },
                'config': {
                    'maintainAspectRatio': False,
                    'responsive': True,
                    'scales': {
                        'y': {
                            'beginAtZero': False
                        }
                    }
                },
                'forecast_available': False,
                'warning': 'Not enough data for demand forecasting (minimum 14 data points required)'
            }
        
        # Get top 5 products by total quantity
        top_products = demand_data.groupby(product_col)[quantity_col].sum().nlargest(5).index.tolist()
        demand_data_filtered = demand_data[demand_data[product_col].isin(top_products)]
        
        # Convert filtered data to proper format
        filtered_chart_data = []
        for _, row in demand_data_filtered.iterrows():
            filtered_chart_data.append({
                'date': row[date_col].strftime('%Y-%m-%d') if pd.notna(row[date_col]) else None,
                'product': str(row[product_col]) if pd.notna(row[product_col]) else 'Unknown',
                'quantity': float(row[quantity_col]) if pd.notna(row[quantity_col]) else 0
            })
        
        # Prepare chart data in the format expected by frontend
        return {
            'id': f'line_{date_col}_{quantity_col}_demand',
            'title': 'Demand Forecasting (Top 5 Products)',
            'type': 'line',
            'priority': 'high',
            'data': {
                'x': [item['date'] for item in filtered_chart_data],
                'y': [item['quantity'] for item in filtered_chart_data]
            },
            'config': {
                'maintainAspectRatio': False,
                'responsive': True,
                'scales': {
                    'y': {
                        'beginAtZero': False
                    }
                }
            },
            'forecast_available': True,
            'products_analyzed': len(top_products)
        }
    
    def _assess_data_quality(self, df: pd.DataFrame, reverse_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Assess data quality and provide insights."""
        quality_report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_data': {},
            'data_types': {},
            'warnings': [],
            'insights': []
        }
        
        # Check for missing data
        for canonical_type, original_col in reverse_mapping.items():
            if original_col in df.columns:
                missing_count = df[original_col].isnull().sum()
                missing_pct = (missing_count / len(df)) * 100
                quality_report['missing_data'][canonical_type] = {
                    'count': int(missing_count),
                    'percentage': round(missing_pct, 2)
                }
                
                if missing_pct > 10:
                    quality_report['warnings'].append(f"{canonical_type} column has {missing_pct:.1f}% missing data")
        
        # Check data types
        for canonical_type, original_col in reverse_mapping.items():
            if original_col in df.columns:
                quality_report['data_types'][canonical_type] = str(df[original_col].dtype)
        
        # Generate insights
        if len(df) < 30:
            quality_report['insights'].append("Small dataset - forecasting may be less accurate")
        
        if len(df) > 10000:
            quality_report['insights'].append("Large dataset - analytics will be comprehensive")
        
        return quality_report

# Global instance
analytics_engine = TANAWAnalyticsEngine()
