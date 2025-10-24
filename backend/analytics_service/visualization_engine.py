# visualization_engine.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import Plotly for interactive visualizations
try:
    import plotly.graph_objects as go
    import plotly.express as px
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Plotly not available. Interactive plots will not work. Install with: pip install plotly")

class VisualizationEngine:
    """
    Dynamic visualization logic for TANAW.
    Automatically detects best visualization types and generates chart configurations.
    """
    
    def __init__(self):
        self.chart_templates = {
            'line': self._generate_line_chart,
            'bar': self._generate_bar_chart,
            'scatter': self._generate_scatter_chart,
            'pie': self._generate_pie_chart,
            'histogram': self._generate_histogram_chart,
            'heatmap': self._generate_heatmap_chart,
            'box': self._generate_box_chart,
            'area': self._generate_area_chart
        }
        
        self.chart_rules = {
            'temporal_numeric': ['line', 'area'],
            'categorical_numeric': ['bar', 'pie'],
            'numeric_numeric': ['scatter', 'line'],
            'single_numeric': ['histogram', 'box'],
            'categorical_categorical': ['heatmap', 'bar'],
            'temporal_categorical': ['bar', 'line']
        }
    
    def generate_visualizations(self, df: pd.DataFrame, 
                              column_mapping: Dict[str, Any] = None,
                              analytics_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate comprehensive visualizations for the dataset.
        
        Args:
            df: DataFrame to visualize
            column_mapping: Column mapping information
            analytics_results: Results from descriptive/predictive analytics
            
        Returns:
            Dict containing all generated visualizations
        """
        visualization_results = {
            'charts': [],
            'dashboard_layout': {},
            'visualization_insights': [],
            'export_options': {}
        }
        
        try:
            # 1. Auto-generate basic visualizations
            basic_charts = self._generate_basic_visualizations(df, column_mapping)
            visualization_results['charts'].extend(basic_charts)
            
            # 2. Generate analytics-specific visualizations
            if analytics_results:
                analytics_charts = self._generate_analytics_visualizations(df, analytics_results)
                visualization_results['charts'].extend(analytics_charts)
            
            # 3. Generate dashboard layout
            visualization_results['dashboard_layout'] = self._generate_dashboard_layout(
                visualization_results['charts']
            )
            
            # 4. Generate visualization insights
            visualization_results['visualization_insights'] = self._generate_visualization_insights(
                visualization_results['charts']
            )
            
            # 5. Prepare export options
            visualization_results['export_options'] = self._prepare_export_options(
                visualization_results['charts']
            )
            
        except Exception as e:
            visualization_results['error'] = f"Visualization generation failed: {str(e)}"
        
        return visualization_results
    
    def _generate_basic_visualizations(self, df: pd.DataFrame, 
                                     column_mapping: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate basic visualizations based on data types."""
        charts = []
        
        # Analyze data types
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        temporal_cols = self._get_temporal_columns(df, column_mapping)
        
        # Debug information
        print(f"📊 Visualization Debug - DataFrame shape: {df.shape}")
        print(f"📊 Numeric columns found: {numeric_cols}")
        print(f"📊 Categorical columns found: {categorical_cols}")
        print(f"📊 Temporal columns found: {temporal_cols}")
        print(f"📊 All column types: {df.dtypes.to_dict()}")
        
        # If no numeric columns found, try to force numeric conversion for business columns
        if not numeric_cols and column_mapping:
            print("⚠️ No numeric columns found, attempting to identify business metrics...")
            mapped_columns = column_mapping.get('mapped_columns', [])
            for mapping in mapped_columns:
                original_col = mapping.get('original_column')
                mapped_type = mapping.get('mapped_column', '').lower()
                
                if mapped_type in ['quantity', 'price', 'amount', 'sales', 'revenue'] and original_col in df.columns:
                    print(f"🔄 Attempting to convert {original_col} to numeric for {mapped_type}")
                    try:
                        df[original_col] = pd.to_numeric(df[original_col], errors='coerce')
                        numeric_cols.append(original_col)
                    except Exception as e:
                        print(f"❌ Failed to convert {original_col}: {e}")
        
        # Generate charts based on data type combinations
        chart_combinations = self._identify_chart_opportunities(
            df, numeric_cols, categorical_cols, temporal_cols
        )
        
        print(f"📊 Chart combinations identified: {len(chart_combinations)}")
        
        for combination in chart_combinations:
            chart = self._create_chart_from_combination(df, combination, column_mapping)
            if chart:
                charts.append(chart)
        
        print(f"📊 Charts generated: {len(charts)}")
        return charts
    
    def _get_temporal_columns(self, df: pd.DataFrame, column_mapping: Dict[str, Any] = None) -> List[str]:
        """Get temporal columns from the dataset."""
        temporal_cols = []
        
        if column_mapping:
            for col in df.columns:
                mapped_type = column_mapping.get(col, {}).get('mapped_column', '').lower()
                if mapped_type in ['date', 'timestamp', 'time']:
                    temporal_cols.append(col)
        
        # Fallback: detect temporal columns by name
        if not temporal_cols:
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp', 'created', 'updated']):
                    temporal_cols.append(col)
        
        return temporal_cols
    
    def _identify_chart_opportunities(self, df: pd.DataFrame, numeric_cols: List[str], 
                                    categorical_cols: List[str], temporal_cols: List[str]) -> List[Dict[str, Any]]:
        """Identify opportunities for different chart types."""
        combinations = []
        
        # 1. Temporal + Numeric (time series)
        if temporal_cols and numeric_cols:
            for temp_col in temporal_cols:
                for num_col in numeric_cols:
                    combinations.append({
                        'type': 'temporal_numeric',
                        'chart_types': ['line', 'area'],
                        'x_column': temp_col,
                        'y_column': num_col,
                        'priority': 'high'
                    })
        
        # 2. Categorical + Numeric (comparisons)
        if categorical_cols and numeric_cols:
            for cat_col in categorical_cols:
                # Skip high-cardinality categorical columns
                if df[cat_col].nunique() > 20:
                    continue
                
                for num_col in numeric_cols:
                    combinations.append({
                        'type': 'categorical_numeric',
                        'chart_types': ['bar', 'pie'] if df[cat_col].nunique() <= 10 else ['bar'],
                        'x_column': cat_col,
                        'y_column': num_col,
                        'priority': 'high'
                    })
        
        # 3. Numeric + Numeric (correlations)
        if len(numeric_cols) >= 2:
            for i, num_col1 in enumerate(numeric_cols):
                for num_col2 in numeric_cols[i+1:]:
                    combinations.append({
                        'type': 'numeric_numeric',
                        'chart_types': ['scatter'],
                        'x_column': num_col1,
                        'y_column': num_col2,
                        'priority': 'medium'
                    })
        
        # 4. Single Numeric (distributions)
        for num_col in numeric_cols:
            combinations.append({
                'type': 'single_numeric',
                'chart_types': ['histogram', 'box'],
                'x_column': num_col,
                'y_column': None,
                'priority': 'medium'
            })
        
        # 5. Categorical + Categorical (cross-tabulations)
        if len(categorical_cols) >= 2:
            for i, cat_col1 in enumerate(categorical_cols):
                for cat_col2 in categorical_cols[i+1:]:
                    if df[cat_col1].nunique() <= 10 and df[cat_col2].nunique() <= 10:
                        combinations.append({
                            'type': 'categorical_categorical',
                            'chart_types': ['heatmap'],
                            'x_column': cat_col1,
                            'y_column': cat_col2,
                            'priority': 'low'
                        })
        
        # Sort by priority and limit number of charts
        combinations.sort(key=lambda x: ['low', 'medium', 'high'].index(x['priority']), reverse=True)
        return combinations[:10]  # Limit to top 10 combinations
    
    def _create_chart_from_combination(self, df: pd.DataFrame, 
                                     combination: Dict[str, Any], column_mapping: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Create a chart from a combination specification."""
        try:
            chart_type = combination['chart_types'][0]  # Use first recommended type
            x_col = combination['x_column']
            y_col = combination['y_column']
            
            if chart_type in self.chart_templates:
                return self.chart_templates[chart_type](df, x_col, y_col, combination, column_mapping)
            
        except Exception as e:
            print(f"Chart creation failed for {combination}: {e}")
        
        return None
    
    def _generate_meaningful_title(self, x_col: str, y_col: str, column_mapping: Dict[str, Any] = None, chart_type: str = 'line') -> str:
        """Generate meaningful chart titles based on column mapping."""
        if not column_mapping:
            return f"{y_col} over {x_col}"
        
        # Get mapped column types
        x_mapped = self._get_mapped_column_type(x_col, column_mapping)
        y_mapped = self._get_mapped_column_type(y_col, column_mapping)
        
        # Generate titles based on mapped types
        if chart_type == 'line':
            if x_mapped == 'date' and y_mapped == 'amount':
                return "Sales Amount Trend"
            elif x_mapped == 'date' and y_mapped == 'quantity':
                return "Sales Volume Trend"
            elif x_mapped == 'date' and y_mapped == 'unit_price':
                return "Price Trend Over Time"
            elif x_mapped == 'date' and y_mapped == 'transaction_id':
                return "Transaction Volume Trend"
            elif x_mapped == 'date' and y_mapped == 'customer_id':
                return "Customer Activity Trend"
            else:
                return f"{y_col.replace('_', ' ').title()} over Time"
        
        elif chart_type == 'bar':
            if x_mapped == 'brand' and y_mapped == 'amount':
                return "Sales by Brand"
            elif x_mapped == 'brand' and y_mapped == 'quantity':
                return "Volume by Brand"
            elif x_mapped == 'brand' and y_mapped == 'unit_price':
                return "Average Price by Brand"
            elif x_mapped == 'brand' and y_mapped == 'transaction_id':
                return "Transaction Count by Brand"
            elif x_mapped == 'brand' and y_mapped == 'customer_id':
                return "Customer Count by Brand"
            else:
                return f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}"
        
        else:
            return f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}"
    
    def _get_mapped_column_type(self, column_name: str, column_mapping: Dict[str, Any] = None) -> str:
        """Get the mapped column type for a given column name."""
        if not column_mapping:
            return column_name
        
        mapped_columns = column_mapping.get('mapped_columns', [])
        for mapping in mapped_columns:
            if mapping.get('original_column') == column_name:
                return mapping.get('mapped_column', column_name)
        
        return column_name

    def _generate_line_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                           combination: Dict[str, Any], column_mapping: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate line chart configuration."""
        try:
            # Prepare data
            if combination['type'] == 'temporal_numeric':
                # Sort by date for time series
                df_temp = df[[x_col, y_col]].copy()
                df_temp[x_col] = pd.to_datetime(df_temp[x_col], errors='coerce')
                df_temp = df_temp.dropna().sort_values(x_col)
                
                # Aggregate by date if needed
                if df_temp.duplicated(subset=[x_col]).any():
                    df_temp = df_temp.groupby(x_col)[y_col].sum().reset_index()
                
                # Format dates properly - handle both datetime and string dates
                if pd.api.types.is_datetime64_any_dtype(df_temp[x_col]):
                    x_data = df_temp[x_col].dt.strftime('%Y-%m-%d').tolist()
                else:
                    # If not datetime, try to convert and format
                    try:
                        x_data = pd.to_datetime(df_temp[x_col], errors='coerce').dt.strftime('%Y-%m-%d').tolist()
                    except:
                        x_data = df_temp[x_col].astype(str).tolist()
                
                y_data = df_temp[y_col].tolist()
                
            else:
                # Regular line chart
                df_temp = df[[x_col, y_col]].dropna()
                x_data = df_temp[x_col].astype(str).tolist()
                y_data = df_temp[y_col].tolist()
            
            # Generate meaningful title based on column mapping
            title = self._generate_meaningful_title(x_col, y_col, column_mapping, 'line')
            
            return {
                'id': f"line_{x_col}_{y_col}",
                'type': 'line',
                'title': title,
                'data': {
                    'x': x_data,
                    'y': y_data
                },
                'config': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'scales': {
                        'y': {'beginAtZero': False}
                    }
                },
                'priority': combination['priority']
            }
            
        except Exception as e:
            print(f"Line chart generation failed: {e}")
            return None
    
    def _generate_bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                          combination: Dict[str, Any], column_mapping: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate bar chart configuration."""
        try:
            if y_col is None:
                # Single variable bar chart (counts)
                value_counts = df[x_col].value_counts().head(10)
                
                # Format dates properly - handle both datetime and string dates
                if pd.api.types.is_datetime64_any_dtype(value_counts.index):
                    x_data = value_counts.index.strftime('%Y-%m-%d').tolist()
                else:
                    # If not datetime, try to convert and format
                    try:
                        x_data = pd.to_datetime(value_counts.index, errors='coerce').strftime('%Y-%m-%d').tolist()
                    except:
                        x_data = value_counts.index.astype(str).tolist()
                
                y_data = value_counts.values.tolist()
                title = f"Distribution of {x_col.replace('_', ' ').title()}"
            else:
                # Grouped bar chart
                grouped = df.groupby(x_col)[y_col].sum().sort_values(ascending=False).head(10)
                
                # Format dates properly - handle both datetime and string dates
                if pd.api.types.is_datetime64_any_dtype(grouped.index):
                    x_data = grouped.index.strftime('%Y-%m-%d').tolist()
                else:
                    # If not datetime, try to convert and format
                    try:
                        x_data = pd.to_datetime(grouped.index, errors='coerce').strftime('%Y-%m-%d').tolist()
                    except:
                        x_data = grouped.index.astype(str).tolist()
                
                y_data = grouped.values.tolist()
                title = self._generate_meaningful_title(x_col, y_col, column_mapping, 'bar')
            
            return {
                'id': f"bar_{x_col}_{y_col or 'count'}",
                'type': 'bar',
                'title': title,
                'data': {
                    'x': x_data,
                    'y': y_data
                },
                'config': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'scales': {
                        'y': {'beginAtZero': True}
                    }
                },
                'priority': combination['priority']
            }
            
        except Exception as e:
            print(f"Bar chart generation failed: {e}")
            return None
    
    def _generate_scatter_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                              combination: Dict[str, Any], column_mapping: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate scatter chart configuration."""
        try:
            df_temp = df[[x_col, y_col]].dropna()
            
            # Format dates properly - handle both datetime and string dates
            if pd.api.types.is_datetime64_any_dtype(df_temp[x_col]):
                x_data = df_temp[x_col].dt.strftime('%Y-%m-%d').tolist()
            else:
                # If not datetime, try to convert and format
                try:
                    x_data = pd.to_datetime(df_temp[x_col], errors='coerce').dt.strftime('%Y-%m-%d').tolist()
                except:
                    x_data = df_temp[x_col].astype(str).tolist()
            
            return {
                'id': f"scatter_{x_col}_{y_col}",
                'type': 'scatter',
                'title': f"{y_col} vs {x_col}",
                'data': {
                    'x': x_data,
                    'y': df_temp[y_col].tolist()
                },
                'config': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'scales': {
                        'x': {'beginAtZero': False},
                        'y': {'beginAtZero': False}
                    }
                },
                'priority': combination['priority']
            }
            
        except Exception as e:
            print(f"Scatter chart generation failed: {e}")
            return None
    
    def _generate_pie_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                          combination: Dict[str, Any], column_mapping: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate pie chart configuration."""
        try:
            if y_col is None:
                # Single variable pie chart (counts)
                value_counts = df[x_col].value_counts().head(8)  # Limit to 8 categories
                
                # Format dates properly - handle both datetime and string dates
                if pd.api.types.is_datetime64_any_dtype(value_counts.index):
                    labels = value_counts.index.strftime('%Y-%m-%d').tolist()
                else:
                    # If not datetime, try to convert and format
                    try:
                        labels = pd.to_datetime(value_counts.index, errors='coerce').strftime('%Y-%m-%d').tolist()
                    except:
                        labels = value_counts.index.astype(str).tolist()
                
                data = value_counts.values.tolist()
                title = f"Distribution of {x_col}"
            else:
                # Pie chart with values
                grouped = df.groupby(x_col)[y_col].sum().sort_values(ascending=False).head(8)
                
                # Format dates properly - handle both datetime and string dates
                if pd.api.types.is_datetime64_any_dtype(grouped.index):
                    labels = grouped.index.strftime('%Y-%m-%d').tolist()
                else:
                    # If not datetime, try to convert and format
                    try:
                        labels = pd.to_datetime(grouped.index, errors='coerce').strftime('%Y-%m-%d').tolist()
                    except:
                        labels = grouped.index.astype(str).tolist()
                
                data = grouped.values.tolist()
                title = f"{y_col} Distribution by {x_col}"
            
            return {
                'id': f"pie_{x_col}_{y_col or 'count'}",
                'type': 'pie',
                'title': title,
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'data': data,
                        'backgroundColor': self._generate_colors(len(data))
                    }]
                },
                'config': {
                    'responsive': True,
                    'maintainAspectRatio': False
                },
                'priority': combination['priority']
            }
            
        except Exception as e:
            print(f"Pie chart generation failed: {e}")
            return None
    
    def _generate_histogram_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                                combination: Dict[str, Any], column_mapping: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate histogram chart configuration."""
        try:
            data = df[x_col].dropna()
            
            # Create histogram bins
            bins = np.histogram(data, bins=min(20, len(data)//5))[1]
            hist, bin_edges = np.histogram(data, bins=bins)
            
            # Convert to bar chart format
            bin_centers = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(bin_edges)-1)]
            
            return {
                'id': f"histogram_{x_col}",
                'type': 'bar',
                'title': f"Distribution of {x_col}",
                'data': {
                    'x': [f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}" for i in range(len(bin_edges)-1)],
                    'y': hist.tolist()
                },
                'config': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'scales': {
                        'y': {'beginAtZero': True}
                    }
                },
                'priority': combination['priority']
            }
            
        except Exception as e:
            print(f"Histogram generation failed: {e}")
            return None
    
    def _generate_heatmap_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                              combination: Dict[str, Any], column_mapping: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate heatmap chart configuration."""
        try:
            # Create cross-tabulation
            crosstab = pd.crosstab(df[x_col], df[y_col])
            
            return {
                'id': f"heatmap_{x_col}_{y_col}",
                'type': 'heatmap',
                'title': f"{x_col} vs {y_col}",
                'data': {
                    'x_labels': crosstab.columns.tolist(),
                    'y_labels': crosstab.index.tolist(),
                    'values': crosstab.values.tolist()
                },
                'config': {
                    'responsive': True,
                    'maintainAspectRatio': False
                },
                'priority': combination['priority']
            }
            
        except Exception as e:
            print(f"Heatmap generation failed: {e}")
            return None
    
    def _generate_box_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                          combination: Dict[str, Any], column_mapping: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate box plot chart configuration."""
        try:
            data = df[x_col].dropna()
            
            # Calculate box plot statistics
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            median = data.quantile(0.5)
            iqr = q3 - q1
            lower_fence = q1 - 1.5 * iqr
            upper_fence = q3 + 1.5 * iqr
            
            # Get outliers
            outliers = data[(data < lower_fence) | (data > upper_fence)].tolist()
            
            return {
                'id': f"box_{x_col}",
                'type': 'box',
                'title': f"Box Plot of {x_col}",
                'data': {
                    'min': float(data.min()),
                    'q1': float(q1),
                    'median': float(median),
                    'q3': float(q3),
                    'max': float(data.max()),
                    'outliers': outliers
                },
                'config': {
                    'responsive': True,
                    'maintainAspectRatio': False
                },
                'priority': combination['priority']
            }
            
        except Exception as e:
            print(f"Box plot generation failed: {e}")
            return None
    
    def _generate_area_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                           combination: Dict[str, Any], column_mapping: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate area chart configuration."""
        try:
            # Similar to line chart but with filled area
            df_temp = df[[x_col, y_col]].copy()
            df_temp[x_col] = pd.to_datetime(df_temp[x_col], errors='coerce')
            df_temp = df_temp.dropna().sort_values(x_col)
            
            # Aggregate by date if needed
            if df_temp.duplicated(subset=[x_col]).any():
                df_temp = df_temp.groupby(x_col)[y_col].sum().reset_index()
            
            # Format dates properly - handle both datetime and string dates
            if pd.api.types.is_datetime64_any_dtype(df_temp[x_col]):
                x_data = df_temp[x_col].dt.strftime('%Y-%m-%d').tolist()
            else:
                # If not datetime, try to convert and format
                try:
                    x_data = pd.to_datetime(df_temp[x_col], errors='coerce').dt.strftime('%Y-%m-%d').tolist()
                except:
                    x_data = df_temp[x_col].astype(str).tolist()
            
            y_data = df_temp[y_col].tolist()
            
            return {
                'id': f"area_{x_col}_{y_col}",
                'type': 'line',
                'title': f"{y_col} Trend (Area)",
                'data': {
                    'x': x_data,
                    'y': y_data
                },
                'config': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'fill': True,
                    'scales': {
                        'y': {'beginAtZero': True}
                    }
                },
                'priority': combination['priority']
            }
            
        except Exception as e:
            print(f"Area chart generation failed: {e}")
            return None
    
    def _generate_analytics_visualizations(self, df: pd.DataFrame, 
                                         analytics_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate visualizations based on analytics results."""
        charts = []
        
        try:
            # Correlation heatmap
            correlation_analysis = analytics_results.get('correlation_analysis', {})
            if correlation_analysis.get('correlation_matrix'):
                charts.append(self._create_correlation_heatmap(correlation_analysis))
            
            # Trend visualizations
            trend_analysis = analytics_results.get('trend_analysis', {})
            if trend_analysis.get('time_series_trends'):
                charts.extend(self._create_trend_visualizations(trend_analysis))
            
            # Anomaly visualizations
            anomaly_detection = analytics_results.get('anomaly_detection', {})
            if anomaly_detection.get('statistical_anomalies'):
                charts.extend(self._create_anomaly_visualizations(df, anomaly_detection))
            
            # Distribution visualizations
            distribution_analysis = analytics_results.get('distribution_analysis', {})
            if distribution_analysis.get('distribution_types'):
                charts.extend(self._create_distribution_visualizations(df, distribution_analysis))
            
        except Exception as e:
            print(f"Analytics visualization generation failed: {e}")
        
        return charts
    
    def _create_correlation_heatmap(self, correlation_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create correlation heatmap visualization."""
        corr_matrix = correlation_analysis.get('correlation_matrix', {})
        
        # Extract variable names and correlation values
        variables = list(corr_matrix.keys())
        values = []
        for var1 in variables:
            row = []
            for var2 in variables:
                row.append(corr_matrix[var1].get(var2, 0))
            values.append(row)
        
        return {
            'id': 'correlation_heatmap',
            'type': 'heatmap',
            'title': 'Variable Correlation Matrix',
            'data': {
                'x_labels': variables,
                'y_labels': variables,
                'values': values
            },
            'config': {
                'responsive': True,
                'maintainAspectRatio': False,
                'colorScale': {
                    'min': -1,
                    'max': 1,
                    'colors': ['red', 'white', 'green']
                }
            },
            'priority': 'high'
        }
    
    def _create_trend_visualizations(self, trend_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create trend visualizations."""
        charts = []
        
        time_series_trends = trend_analysis.get('time_series_trends', {})
        for trend_key, trend_data in time_series_trends.items():
            charts.append({
                'id': f"trend_{trend_key}",
                'type': 'line',
                'title': f"Trend Analysis: {trend_key}",
                'data': {
                    'trend_direction': trend_data.get('trend_direction'),
                    'trend_strength': trend_data.get('trend_strength'),
                    'r_squared': trend_data.get('r_squared'),
                    'slope': trend_data.get('slope')
                },
                'config': {
                    'responsive': True,
                    'maintainAspectRatio': False
                },
                'priority': 'medium'
            })
        
        return charts
    
    def _create_anomaly_visualizations(self, df: pd.DataFrame, 
                                     anomaly_detection: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create anomaly visualizations."""
        charts = []
        
        statistical_anomalies = anomaly_detection.get('statistical_anomalies', {})
        for col, anomalies in statistical_anomalies.items():
            if anomalies.get('total_statistical_anomalies', 0) > 0:
                charts.append({
                    'id': f"anomalies_{col}",
                    'type': 'scatter',
                    'title': f"Anomalies in {col}",
                    'data': {
                        'total_anomalies': anomalies.get('total_statistical_anomalies'),
                        'z_score_anomalies': anomalies.get('z_score_anomalies'),
                        'iqr_anomalies': anomalies.get('iqr_anomalies')
                    },
                    'config': {
                        'responsive': True,
                        'maintainAspectRatio': False
                    },
                    'priority': 'high'
                })
        
        return charts
    
    def _create_distribution_visualizations(self, df: pd.DataFrame, 
                                          distribution_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create distribution visualizations."""
        charts = []
        
        distribution_types = distribution_analysis.get('distribution_types', {})
        for col, dist_type in distribution_types.items():
            charts.append({
                'id': f"distribution_{col}",
                'type': 'bar',
                'title': f"Distribution Type: {col} ({dist_type})",
                'data': {
                    'distribution_type': dist_type,
                    'column': col
                },
                'config': {
                    'responsive': True,
                    'maintainAspectRatio': False
                },
                'priority': 'low'
            })
        
        return charts
    
    def _generate_dashboard_layout(self, charts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate dashboard layout configuration."""
        # Sort charts by priority
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        sorted_charts = sorted(charts, key=lambda x: priority_order.get(x.get('priority', 'low'), 1), reverse=True)
        
        # Create grid layout
        layout = {
            'grid_columns': 3,
            'grid_rows': (len(sorted_charts) + 2) // 3,
            'chart_positions': []
        }
        
        for i, chart in enumerate(sorted_charts):
            row = i // layout['grid_columns']
            col = i % layout['grid_columns']
            
            layout['chart_positions'].append({
                'chart_id': chart['id'],
                'row': row,
                'col': col,
                'size': 'medium' if chart.get('priority') == 'high' else 'small'
            })
        
        return layout
    
    def _generate_visualization_insights(self, charts: List[Dict[str, Any]]) -> List[str]:
        """Generate insights about the visualizations."""
        insights = []
        
        chart_types = [chart['type'] for chart in charts]
        type_counts = {chart_type: chart_types.count(chart_type) for chart_type in set(chart_types)}
        
        insights.append(f"Generated {len(charts)} visualizations across {len(type_counts)} chart types")
        
        if 'line' in type_counts:
            insights.append(f"📈 {type_counts['line']} time series chart(s) showing trends over time")
        
        if 'bar' in type_counts:
            insights.append(f"📊 {type_counts['bar']} bar chart(s) for categorical comparisons")
        
        if 'scatter' in type_counts:
            insights.append(f"🔗 {type_counts['scatter']} scatter plot(s) showing variable relationships")
        
        if 'pie' in type_counts:
            insights.append(f"🥧 {type_counts['pie']} pie chart(s) showing proportional distributions")
        
        if 'heatmap' in type_counts:
            insights.append(f"🔥 {type_counts['heatmap']} heatmap(s) showing correlation patterns")
        
        return insights
    
    def _prepare_export_options(self, charts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare export options for visualizations."""
        return {
            'formats': ['png', 'svg', 'pdf', 'json'],
            'chart_count': len(charts),
            'total_size_estimate': len(json.dumps(charts)) * 1.2,  # Rough estimate
            'export_metadata': {
                'generated_at': datetime.now().isoformat(),
                'chart_types': list(set(chart['type'] for chart in charts)),
                'total_charts': len(charts)
            }
        }
    
    def _generate_colors(self, n: int) -> List[str]:
        """Generate n distinct colors for charts."""
        # Simple color palette
        colors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
        ]
        
        if n <= len(colors):
            return colors[:n]
        else:
            # Generate more colors if needed
            base_colors = colors
            extended_colors = base_colors.copy()
            for i in range(n - len(colors)):
                # Simple color variation
                color_index = i % len(base_colors)
                extended_colors.append(base_colors[color_index])
            return extended_colors[:n]
    
    def customize_chart(self, chart_id: str, customizations: Dict[str, Any]) -> Dict[str, Any]:
        """Customize a specific chart."""
        # This would integrate with the frontend to allow chart customization
        return {
            'chart_id': chart_id,
            'customizations': customizations,
            'status': 'customized'
        }
    
    def get_chart_recommendations(self, df: pd.DataFrame, 
                                column_mapping: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get recommendations for additional charts."""
        recommendations = []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Recommend drill-down charts for high-cardinality categorical columns
        for col in categorical_cols:
            if df[col].nunique() > 20:
                recommendations.append({
                    'type': 'drill_down',
                    'column': col,
                    'reason': 'High cardinality categorical column - consider grouping or filtering',
                    'suggestion': 'Create aggregated view or add filters'
                })
        
        # Recommend additional correlation analysis
        if len(numeric_cols) >= 3:
            recommendations.append({
                'type': 'correlation_network',
                'reason': 'Multiple numeric variables - correlation network visualization',
                'suggestion': 'Create correlation network diagram'
            })
        
        return recommendations
    
    def generate_interactive_charts(self, analytics_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate interactive Plotly charts for analytics results.
        
        Args:
            analytics_results: Results from descriptive/predictive analytics
            
        Returns:
            Dict containing interactive chart configurations
        """
        if not PLOTLY_AVAILABLE:
            return {
                'error': 'Plotly not available. Install with: pip install plotly',
                'charts': []
            }
        
        interactive_charts = []
        
        try:
            # Generate charts for each analytics type
            for analytics_type, results in analytics_results.items():
                if analytics_type == 'sales_summary':
                    interactive_charts.extend(self._generate_sales_summary_charts(results))
                elif analytics_type == 'product_performance':
                    interactive_charts.extend(self._generate_product_performance_charts(results))
                elif analytics_type == 'regional_analysis':
                    interactive_charts.extend(self._generate_regional_analysis_charts(results))
                elif analytics_type == 'time_series_forecasting':
                    interactive_charts.extend(self._generate_forecasting_charts(results))
                elif analytics_type == 'correlation_analysis':
                    interactive_charts.extend(self._generate_correlation_charts(results))
                elif analytics_type == 'anomaly_detection':
                    interactive_charts.extend(self._generate_anomaly_charts(results))
            
            return {
                'success': True,
                'charts': interactive_charts,
                'chart_count': len(interactive_charts)
            }
            
        except Exception as e:
            return {
                'error': f'Failed to generate interactive charts: {str(e)}',
                'charts': []
            }
    
    def _generate_sales_summary_charts(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate interactive charts for sales summary analytics."""
        charts = []
        
        try:
            # Sales trend chart
            trend_data = results.get('trend_analysis', {}).get('monthly_trend', [])
            if trend_data:
                df_trend = pd.DataFrame(trend_data)
                fig = px.line(df_trend, x='year_month', y='sales', 
                            title='Monthly Sales Trend',
                            labels={'sales': 'Sales Amount', 'year_month': 'Month'})
                
                charts.append({
                    'type': 'interactive_line',
                    'title': 'Monthly Sales Trend',
                    'plotly_config': fig.to_dict(),
                    'html': fig.to_html(include_plotlyjs='cdn')
                })
            
            # Product performance chart
            product_data = results.get('breakdowns', {}).get('product_performance', {})
            if product_data.get('top_products'):
                df_products = pd.DataFrame(product_data['top_products'])
                fig = px.bar(df_products.head(10), x='product', y='sum',
                           title='Top 10 Products by Sales',
                           labels={'sum': 'Total Sales', 'product': 'Product'})
                
                charts.append({
                    'type': 'interactive_bar',
                    'title': 'Top 10 Products by Sales',
                    'plotly_config': fig.to_dict(),
                    'html': fig.to_html(include_plotlyjs='cdn')
                })
            
        except Exception as e:
            print(f"Error generating sales summary charts: {e}")
        
        return charts
    
    def _generate_product_performance_charts(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate interactive charts for product performance analytics."""
        charts = []
        
        try:
            rankings = results.get('product_rankings', {})
            if rankings.get('top_by_sales'):
                df_products = pd.DataFrame(rankings['top_by_sales'])
                fig = px.bar(df_products.head(15), x='product', y='sales_sum',
                           title='Product Performance by Sales',
                           labels={'sales_sum': 'Total Sales', 'product': 'Product'})
                
                charts.append({
                    'type': 'interactive_bar',
                    'title': 'Product Performance by Sales',
                    'plotly_config': fig.to_dict(),
                    'html': fig.to_html(include_plotlyjs='cdn')
                })
            
        except Exception as e:
            print(f"Error generating product performance charts: {e}")
        
        return charts
    
    def _generate_regional_analysis_charts(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate interactive charts for regional analysis."""
        charts = []
        
        try:
            metrics = results.get('regional_metrics', {})
            if metrics.get('regional_performance'):
                df_regions = pd.DataFrame(metrics['regional_performance'])
                fig = px.pie(df_regions, values='sum', names='region',
                           title='Sales Distribution by Location')
                
                charts.append({
                    'type': 'interactive_pie',
                    'title': 'Sales Distribution by Location',
                    'plotly_config': fig.to_dict(),
                    'html': fig.to_html(include_plotlyjs='cdn')
                })
            
        except Exception as e:
            print(f"Error generating regional analysis charts: {e}")
        
        return charts
    
    def _generate_forecasting_charts(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate interactive charts for forecasting analytics."""
        charts = []
        
        try:
            forecasts = results.get('forecasts', {})
            for forecast_key, forecast_data in forecasts.items():
                if forecast_data.get('model_type') == 'prophet':
                    # Historical data
                    hist_data = forecast_data.get('historical_data', {})
                    forecast_values = forecast_data.get('forecast_data', {})
                    
                    if hist_data.get('dates') and forecast_values.get('dates'):
                        # Create combined dataframe
                        hist_df = pd.DataFrame({
                            'date': hist_data['dates'],
                            'value': hist_data['values'],
                            'type': 'Historical'
                        })
                        
                        forecast_df = pd.DataFrame({
                            'date': forecast_values['dates'],
                            'value': forecast_values['values'],
                            'type': 'Forecast'
                        })
                        
                        combined_df = pd.concat([hist_df, forecast_df])
                        
                        fig = px.line(combined_df, x='date', y='value', color='type',
                                    title=f'Forecast: {forecast_key}',
                                    labels={'value': 'Value', 'date': 'Date'})
                        
                        charts.append({
                            'type': 'interactive_forecast',
                            'title': f'Forecast: {forecast_key}',
                            'plotly_config': fig.to_dict(),
                            'html': fig.to_html(include_plotlyjs='cdn')
                        })
            
        except Exception as e:
            print(f"Error generating forecasting charts: {e}")
        
        return charts
    
    def _generate_correlation_charts(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate interactive charts for correlation analysis."""
        charts = []
        
        try:
            corr_matrix = results.get('correlation_matrix', {})
            if corr_matrix:
                # Convert correlation matrix to DataFrame
                df_corr = pd.DataFrame(corr_matrix)
                
                fig = px.imshow(df_corr, 
                              title='Correlation Matrix Heatmap',
                              color_continuous_scale='RdBu',
                              aspect='auto')
                
                charts.append({
                    'type': 'interactive_heatmap',
                    'title': 'Correlation Matrix Heatmap',
                    'plotly_config': fig.to_dict(),
                    'html': fig.to_html(include_plotlyjs='cdn')
                })
            
        except Exception as e:
            print(f"Error generating correlation charts: {e}")
        
        return charts
    
    def _generate_anomaly_charts(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate interactive charts for anomaly detection."""
        charts = []
        
        try:
            anomalies_by_column = results.get('anomalies_by_column', {})
            for column, anomaly_data in anomalies_by_column.items():
                if anomaly_data.get('anomaly_indices'):
                    # Create scatter plot showing anomalies
                    normal_data = anomaly_data.get('normal_values', [])
                    anomaly_indices = anomaly_data.get('anomaly_indices', [])
                    
                    if normal_data:
                        # Create sample data for visualization
                        indices = list(range(len(normal_data)))
                        fig = go.Figure()
                        
                        # Add normal points
                        fig.add_trace(go.Scatter(
                            x=indices, y=normal_data,
                            mode='markers',
                            name='Normal',
                            marker=dict(color='blue', size=4)
                        ))
                        
                        # Add anomaly points
                        if anomaly_indices:
                            anomaly_values = [normal_data[i] for i in anomaly_indices if i < len(normal_data)]
                            fig.add_trace(go.Scatter(
                                x=anomaly_indices, y=anomaly_values,
                                mode='markers',
                                name='Anomaly',
                                marker=dict(color='red', size=8)
                            ))
                        
                        fig.update_layout(
                            title=f'Anomaly Detection: {column}',
                            xaxis_title='Index',
                            yaxis_title='Value'
                        )
                        
                        charts.append({
                            'type': 'interactive_anomaly',
                            'title': f'Anomaly Detection: {column}',
                            'plotly_config': fig.to_dict(),
                            'html': fig.to_html(include_plotlyjs='cdn')
                        })
            
        except Exception as e:
            print(f"Error generating anomaly charts: {e}")
        
        return charts
