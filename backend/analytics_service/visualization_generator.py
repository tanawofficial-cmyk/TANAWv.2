"""
Phase 8: Visualization & Narrative (UI-ready)
Implements chart data generation and narrative creation for analytics results.

Features:
- Chart data shapes and JSON structures
- Rule-based narrative generation
- Optional GPT narrative generation for high confidence
- Chart fallbacks with CSV download
- Accessibility features (alt text, descriptions)
- Comprehensive error handling
- Advanced observability
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
import json
import csv
import io
import base64

# Import existing configuration
from config_manager import get_config

@dataclass
class ChartData:
    """Represents chart data structure."""
    chart_type: str
    title: str
    x_axis: List[Any]
    y_axis: List[Any]
    series: List[Dict[str, Any]]
    meta: Dict[str, Any]
    alt_text: str
    description: str

@dataclass
class NarrativeResult:
    """Represents narrative generation result."""
    narrative_type: str  # 'rule_based' or 'gpt_generated'
    content: str
    confidence: float
    generation_time_seconds: float
    success: bool
    error_message: Optional[str] = None

@dataclass
class VisualizationResult:
    """Results from visualization generation."""
    charts: Dict[str, ChartData]
    narratives: Dict[str, NarrativeResult]
    csv_fallbacks: Dict[str, str]  # Base64 encoded CSV data
    processing_time_seconds: float
    metrics: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

class VisualizationGenerator:
    """
    Phase 8: Visualization and narrative generation system.
    
    Features:
    - Chart data shapes and JSON structures
    - Rule-based narrative generation
    - Optional GPT narrative generation for high confidence
    - Chart fallbacks with CSV download
    - Accessibility features (alt text, descriptions)
    - Comprehensive error handling
    - Advanced observability
    """
    
    def __init__(self, config=None):
        """Initialize visualization generator with configuration."""
        self.config = config or get_config()
        self.generator_version = "8.0.0"
        
        # Chart types and configurations
        self.chart_types = {
            'sales_summary': 'bar',
            'product_performance': 'bar',
            'regional_sales': 'pie',
            'sales_forecasting': 'line',
            'demand_forecasting': 'line'
        }
        
        # Narrative templates
        self.narrative_templates = {
            'sales_summary': {
                'high_performance': "Sales are performing well with a total of {total_sales:,.0f} and an average of {average_sales:,.0f} per transaction.",
                'moderate_performance': "Sales show moderate performance with a total of {total_sales:,.0f} and an average of {average_sales:,.0f} per transaction.",
                'low_performance': "Sales performance is below expectations with a total of {total_sales:,.0f} and an average of {average_sales:,.0f} per transaction."
            },
            'product_performance': {
                'top_product': "The top-performing product is {top_product} with {top_sales:,.0f} in sales.",
                'balanced_products': "Product performance is well-balanced across {total_products} products.",
                'concentrated_products': "Product performance is concentrated in a few key products."
            },
            'regional_sales': {
                'top_region': "The top-performing region is {top_region} with {top_sales:,.0f} in sales.",
                'balanced_regions': "Regional sales are well-distributed across {total_regions} regions.",
                'concentrated_regions': "Regional sales are concentrated in a few key regions."
            },
            'sales_forecasting': {
                'positive_trend': "Sales forecasting shows a positive trend with predicted growth.",
                'stable_trend': "Sales forecasting shows a stable trend with consistent performance.",
                'negative_trend': "Sales forecasting shows a declining trend that requires attention."
            },
            'demand_forecasting': {
                'high_demand': "Demand forecasting indicates high demand for key products.",
                'stable_demand': "Demand forecasting shows stable demand patterns.",
                'low_demand': "Demand forecasting indicates declining demand that requires attention."
            }
        }
        
        # Metrics tracking
        self.metrics = {
            'charts_generated': 0,
            'narratives_generated': 0,
            'csv_fallbacks_created': 0,
            'processing_time_ms': 0.0,
            'visualization_errors': 0,
            'accessibility_features_added': 0
        }
    
    def generate_visualizations(self, analytics_results: Dict[str, Any], 
                              analytics_readiness: Dict[str, Any]) -> VisualizationResult:
        """
        Generate visualizations and narratives for analytics results.
        
        Args:
            analytics_results: Results from Phase 7 analytics execution
            analytics_readiness: Analytics readiness information
            
        Returns:
            VisualizationResult with charts, narratives, and fallbacks
        """
        start_time = datetime.now()
        
        try:
            charts = {}
            narratives = {}
            csv_fallbacks = {}
            
            # Generate charts for each successful analytic
            for analytic_name, analytic_result in analytics_results.items():
                if analytic_result.get('success', False):
                    try:
                        # Generate chart data
                        chart_data = self._generate_chart_data(analytic_name, analytic_result)
                        charts[analytic_name] = chart_data
                        self.metrics['charts_generated'] += 1
                        
                        # Generate narrative
                        narrative_result = self._generate_narrative(analytic_name, analytic_result, analytics_readiness)
                        narratives[analytic_name] = narrative_result
                        self.metrics['narratives_generated'] += 1
                        
                        # Generate CSV fallback
                        csv_data = self._generate_csv_fallback(analytic_name, analytic_result)
                        csv_fallbacks[analytic_name] = csv_data
                        self.metrics['csv_fallbacks_created'] += 1
                        
                    except Exception as e:
                        print(f"⚠️ Error generating visualization for {analytic_name}: {e}")
                        self.metrics['visualization_errors'] += 1
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics['processing_time_ms'] = processing_time * 1000
            
            return VisualizationResult(
                charts=charts,
                narratives=narratives,
                csv_fallbacks=csv_fallbacks,
                processing_time_seconds=processing_time,
                metrics=self.metrics.copy(),
                success=True
            )
            
        except Exception as e:
            return VisualizationResult(
                charts={},
                narratives={},
                csv_fallbacks={},
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                metrics=self.metrics.copy(),
                success=False,
                error_message=str(e)
            )
    
    def _generate_chart_data(self, analytic_name: str, analytic_result: Dict[str, Any]) -> ChartData:
        """Generate chart data for a specific analytic."""
        try:
            result_data = analytic_result.get('result_data', {})
            
            if analytic_name == 'sales_summary':
                return self._generate_sales_summary_chart(result_data)
            elif analytic_name == 'product_performance':
                return self._generate_product_performance_chart(result_data)
            elif analytic_name == 'regional_sales':
                return self._generate_regional_sales_chart(result_data)
            elif analytic_name == 'sales_forecasting':
                return self._generate_sales_forecasting_chart(result_data)
            elif analytic_name == 'demand_forecasting':
                return self._generate_demand_forecasting_chart(result_data)
            else:
                raise Exception(f"Unknown analytic: {analytic_name}")
                
        except Exception as e:
            raise Exception(f"Chart generation failed for {analytic_name}: {e}")
    
    def _generate_sales_summary_chart(self, result_data: Dict[str, Any]) -> ChartData:
        """Generate sales summary chart."""
        try:
            # Create bar chart for sales metrics
            metrics = ['Total Sales', 'Average Sales', 'Median Sales', 'Min Sales', 'Max Sales']
            values = [
                result_data.get('total_sales', 0),
                result_data.get('average_sales', 0),
                result_data.get('median_sales', 0),
                result_data.get('min_sales', 0),
                result_data.get('max_sales', 0)
            ]
            
            return ChartData(
                chart_type='bar',
                title='Sales Summary',
                x_axis=metrics,
                y_axis=values,
                series=[{
                    'name': 'Sales Metrics',
                    'data': values,
                    'color': '#3498db'
                }],
                meta={
                    'total_sales': result_data.get('total_sales', 0),
                    'count': result_data.get('count', 0),
                    'date_range': result_data.get('date_range', {})
                },
                alt_text='Bar chart showing sales summary metrics including total, average, median, minimum, and maximum sales values',
                description='This chart displays key sales performance metrics including total sales, average sales, median sales, minimum sales, and maximum sales values.'
            )
            
        except Exception as e:
            raise Exception(f"Sales summary chart generation failed: {e}")
    
    def _generate_product_performance_chart(self, result_data: Dict[str, Any]) -> ChartData:
        """Generate product performance chart."""
        try:
            product_performance = result_data.get('product_performance', [])
            
            if not product_performance:
                raise Exception("No product performance data available")
            
            # Extract top 10 products
            top_products = product_performance[:10]
            products = [item['product'] for item in top_products]
            sales = [item['total_sales'] for item in top_products]
            
            return ChartData(
                chart_type='bar',
                title='Product Performance',
                x_axis=products,
                y_axis=sales,
                series=[{
                    'name': 'Total Sales',
                    'data': sales,
                    'color': '#e74c3c'
                }],
                meta={
                    'total_products': result_data.get('total_products', 0),
                    'top_products': top_products
                },
                alt_text='Bar chart showing product performance with total sales for each product',
                description='This chart displays the performance of products ranked by total sales, showing the top 10 products.'
            )
            
        except Exception as e:
            raise Exception(f"Product performance chart generation failed: {e}")
    
    def _generate_regional_sales_chart(self, result_data: Dict[str, Any]) -> ChartData:
        """Generate regional sales chart."""
        try:
            regional_sales = result_data.get('regional_sales', [])
            
            if not regional_sales:
                raise Exception("No regional sales data available")
            
            # Extract regions and sales
            regions = [item['region'] for item in regional_sales]
            sales = [item['total_sales'] for item in regional_sales]
            
            return ChartData(
                chart_type='pie',
                title='Location-based Sales Distribution',
                x_axis=regions,
                y_axis=sales,
                series=[{
                    'name': 'Location Sales',
                    'data': [{'name': region, 'value': sale} for region, sale in zip(regions, sales)],
                    'color': '#2ecc71'
                }],
                meta={
                    'total_regions': result_data.get('total_regions', 0),
                    'regional_sales': regional_sales
                },
                alt_text='Pie chart showing location-based sales distribution with sales values for each location',
                description='This chart displays the distribution of sales across different locations, showing the proportion of sales for each location.'
            )
            
        except Exception as e:
            raise Exception(f"Regional sales chart generation failed: {e}")
    
    def _generate_sales_forecasting_chart(self, result_data: Dict[str, Any]) -> ChartData:
        """Generate sales forecasting chart."""
        try:
            forecast = result_data.get('forecast', [])
            
            if not forecast:
                raise Exception("No sales forecasting data available")
            
            # Extract dates and predictions
            dates = [item['date'] for item in forecast]
            predictions = [item['predicted_sales'] for item in forecast]
            
            return ChartData(
                chart_type='line',
                title='Sales Forecasting',
                x_axis=dates,
                y_axis=predictions,
                series=[{
                    'name': 'Predicted Sales',
                    'data': predictions,
                    'color': '#f39c12'
                }],
                meta={
                    'forecast_period': result_data.get('forecast_period', 0),
                    'model_accuracy': result_data.get('model_accuracy', 0),
                    'last_actual_date': result_data.get('last_actual_date', '')
                },
                alt_text='Line chart showing sales forecasting with predicted sales values over time',
                description='This chart displays the sales forecast with predicted sales values over the forecast period.'
            )
            
        except Exception as e:
            raise Exception(f"Sales forecasting chart generation failed: {e}")
    
    def _generate_demand_forecasting_chart(self, result_data: Dict[str, Any]) -> ChartData:
        """Generate demand forecasting chart."""
        try:
            product_forecasts = result_data.get('product_forecasts', {})
            
            if not product_forecasts:
                raise Exception("No demand forecasting data available")
            
            # Create multi-series line chart for top products
            products = list(product_forecasts.keys())[:5]  # Top 5 products
            series_data = []
            
            for product in products:
                forecast_data = product_forecasts[product].get('forecast', [])
                series_data.append({
                    'name': product,
                    'data': forecast_data,
                    'color': self._get_color_for_product(product)
                })
            
            # Generate time labels
            time_labels = [f"Day {i+1}" for i in range(len(forecast_data))]
            
            return ChartData(
                chart_type='line',
                title='Demand Forecasting by Product',
                x_axis=time_labels,
                y_axis=[],  # Multi-series chart
                series=series_data,
                meta={
                    'forecast_period': result_data.get('forecast_period', 0),
                    'products_forecasted': result_data.get('products_forecasted', 0),
                    'product_forecasts': product_forecasts
                },
                alt_text='Multi-line chart showing demand forecasting for different products over time',
                description='This chart displays the demand forecast for different products, showing predicted demand over the forecast period.'
            )
            
        except Exception as e:
            raise Exception(f"Demand forecasting chart generation failed: {e}")
    
    def _generate_narrative(self, analytic_name: str, analytic_result: Dict[str, Any], 
                          analytics_readiness: Dict[str, Any]) -> NarrativeResult:
        """Generate narrative for a specific analytic."""
        start_time = datetime.now()
        
        try:
            # Check if GPT narrative should be used
            confidence = analytics_readiness.get('success_rate', 0) / 100
            use_gpt = confidence >= 0.85 and self.config.get('gpt_narrative_enabled', False)
            
            if use_gpt:
                # Generate GPT narrative
                narrative_result = self._generate_gpt_narrative(analytic_name, analytic_result)
            else:
                # Generate rule-based narrative
                narrative_result = self._generate_rule_based_narrative(analytic_name, analytic_result)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            narrative_result.generation_time_seconds = generation_time
            
            return narrative_result
            
        except Exception as e:
            return NarrativeResult(
                narrative_type='rule_based',
                content=f"Unable to generate narrative for {analytic_name}",
                confidence=0.0,
                generation_time_seconds=(datetime.now() - start_time).total_seconds(),
                success=False,
                error_message=str(e)
            )
    
    def _generate_rule_based_narrative(self, analytic_name: str, analytic_result: Dict[str, Any]) -> NarrativeResult:
        """Generate rule-based narrative."""
        try:
            result_data = analytic_result.get('result_data', {})
            templates = self.narrative_templates.get(analytic_name, {})
            
            if analytic_name == 'sales_summary':
                total_sales = result_data.get('total_sales', 0)
                average_sales = result_data.get('average_sales', 0)
                
                if total_sales > 100000:
                    template = templates.get('high_performance', 'Sales are performing well.')
                elif total_sales > 50000:
                    template = templates.get('moderate_performance', 'Sales show moderate performance.')
                else:
                    template = templates.get('low_performance', 'Sales performance is below expectations.')
                
                content = template.format(total_sales=total_sales, average_sales=average_sales)
                
            elif analytic_name == 'product_performance':
                product_performance = result_data.get('product_performance', [])
                total_products = result_data.get('total_products', 0)
                
                if product_performance:
                    top_product = product_performance[0]['product']
                    top_sales = product_performance[0]['total_sales']
                    template = templates.get('top_product', 'The top-performing product is {top_product} with {top_sales:,.0f} in sales.')
                    content = template.format(top_product=top_product, top_sales=top_sales)
                else:
                    content = f"Product performance data is available for {total_products} products."
                
            elif analytic_name == 'regional_sales':
                regional_sales = result_data.get('regional_sales', [])
                total_regions = result_data.get('total_regions', 0)
                
                if regional_sales:
                    top_region = regional_sales[0]['region']
                    top_sales = regional_sales[0]['total_sales']
                    template = templates.get('top_region', 'The top-performing region is {top_region} with {top_sales:,.0f} in sales.')
                    content = template.format(top_region=top_region, top_sales=top_sales)
                else:
                    content = f"Regional sales data is available for {total_regions} regions."
                
            elif analytic_name == 'sales_forecasting':
                model_accuracy = result_data.get('model_accuracy', 0)
                forecast_period = result_data.get('forecast_period', 0)
                
                if model_accuracy > 0.8:
                    template = templates.get('positive_trend', 'Sales forecasting shows a positive trend with predicted growth.')
                elif model_accuracy > 0.5:
                    template = templates.get('stable_trend', 'Sales forecasting shows a stable trend with consistent performance.')
                else:
                    template = templates.get('negative_trend', 'Sales forecasting shows a declining trend that requires attention.')
                
                content = template
                
            elif analytic_name == 'demand_forecasting':
                products_forecasted = result_data.get('products_forecasted', 0)
                forecast_period = result_data.get('forecast_period', 0)
                
                if products_forecasted > 3:
                    template = templates.get('high_demand', 'Demand forecasting indicates high demand for key products.')
                elif products_forecasted > 1:
                    template = templates.get('stable_demand', 'Demand forecasting shows stable demand patterns.')
                else:
                    template = templates.get('low_demand', 'Demand forecasting indicates declining demand that requires attention.')
                
                content = template
                
            else:
                content = f"Analytics results are available for {analytic_name}."
            
            return NarrativeResult(
                narrative_type='rule_based',
                content=content,
                confidence=0.8,  # Rule-based narratives have high confidence
                generation_time_seconds=0.0,  # Will be set by caller
                success=True
            )
            
        except Exception as e:
            return NarrativeResult(
                narrative_type='rule_based',
                content=f"Unable to generate narrative for {analytic_name}",
                confidence=0.0,
                generation_time_seconds=0.0,
                success=False,
                error_message=str(e)
            )
    
    def _generate_gpt_narrative(self, analytic_name: str, analytic_result: Dict[str, Any]) -> NarrativeResult:
        """Generate GPT narrative for high confidence analytics."""
        try:
            # This would integrate with GPT API for narrative generation
            # For now, return a placeholder
            result_data = analytic_result.get('result_data', {})
            
            # Create a summary of key metrics for GPT
            summary = {
                'analytic_name': analytic_name,
                'key_metrics': result_data
            }
            
            # In a real implementation, this would call GPT API
            content = f"GPT-generated narrative for {analytic_name} based on analytics results."
            
            return NarrativeResult(
                narrative_type='gpt_generated',
                content=content,
                confidence=0.9,  # GPT narratives have high confidence
                generation_time_seconds=0.0,  # Will be set by caller
                success=True
            )
            
        except Exception as e:
            return NarrativeResult(
                narrative_type='gpt_generated',
                content=f"Unable to generate GPT narrative for {analytic_name}",
                confidence=0.0,
                generation_time_seconds=0.0,
                success=False,
                error_message=str(e)
            )
    
    def _generate_csv_fallback(self, analytic_name: str, analytic_result: Dict[str, Any]) -> str:
        """Generate CSV fallback data."""
        try:
            result_data = analytic_result.get('result_data', {})
            
            # Create CSV data based on analytic type
            if analytic_name == 'sales_summary':
                csv_data = self._create_sales_summary_csv(result_data)
            elif analytic_name == 'product_performance':
                csv_data = self._create_product_performance_csv(result_data)
            elif analytic_name == 'regional_sales':
                csv_data = self._create_regional_sales_csv(result_data)
            elif analytic_name == 'sales_forecasting':
                csv_data = self._create_sales_forecasting_csv(result_data)
            elif analytic_name == 'demand_forecasting':
                csv_data = self._create_demand_forecasting_csv(result_data)
            else:
                csv_data = "Analytic,Value\n" + f"{analytic_name},No data available"
            
            # Encode as base64
            encoded_data = base64.b64encode(csv_data.encode('utf-8')).decode('utf-8')
            return encoded_data
            
        except Exception as e:
            # Return error CSV
            error_csv = f"Error,Message\n{analytic_name},{str(e)}"
            encoded_data = base64.b64encode(error_csv.encode('utf-8')).decode('utf-8')
            return encoded_data
    
    def _create_sales_summary_csv(self, result_data: Dict[str, Any]) -> str:
        """Create CSV for sales summary."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Sales', result_data.get('total_sales', 0)])
        writer.writerow(['Average Sales', result_data.get('average_sales', 0)])
        writer.writerow(['Median Sales', result_data.get('median_sales', 0)])
        writer.writerow(['Min Sales', result_data.get('min_sales', 0)])
        writer.writerow(['Max Sales', result_data.get('max_sales', 0)])
        writer.writerow(['Count', result_data.get('count', 0)])
        
        return output.getvalue()
    
    def _create_product_performance_csv(self, result_data: Dict[str, Any]) -> str:
        """Create CSV for product performance."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        product_performance = result_data.get('product_performance', [])
        
        writer.writerow(['Product', 'Total Sales', 'Average Sales', 'Transaction Count'])
        for item in product_performance:
            writer.writerow([
                item.get('product', ''),
                item.get('total_sales', 0),
                item.get('average_sales', 0),
                item.get('transaction_count', 0)
            ])
        
        return output.getvalue()
    
    def _create_regional_sales_csv(self, result_data: Dict[str, Any]) -> str:
        """Create CSV for regional sales."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        regional_sales = result_data.get('regional_sales', [])
        
        writer.writerow(['Region', 'Total Sales', 'Average Sales', 'Transaction Count'])
        for item in regional_sales:
            writer.writerow([
                item.get('region', ''),
                item.get('total_sales', 0),
                item.get('average_sales', 0),
                item.get('transaction_count', 0)
            ])
        
        return output.getvalue()
    
    def _create_sales_forecasting_csv(self, result_data: Dict[str, Any]) -> str:
        """Create CSV for sales forecasting."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        forecast = result_data.get('forecast', [])
        
        writer.writerow(['Date', 'Predicted Sales'])
        for item in forecast:
            writer.writerow([
                item.get('date', ''),
                item.get('predicted_sales', 0)
            ])
        
        return output.getvalue()
    
    def _create_demand_forecasting_csv(self, result_data: Dict[str, Any]) -> str:
        """Create CSV for demand forecasting."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        product_forecasts = result_data.get('product_forecasts', {})
        
        writer.writerow(['Product', 'Day', 'Predicted Demand'])
        for product, forecast_data in product_forecasts.items():
            forecast = forecast_data.get('forecast', [])
            for i, demand in enumerate(forecast):
                writer.writerow([product, i+1, demand])
        
        return output.getvalue()
    
    def _get_color_for_product(self, product: str) -> str:
        """Get color for product in charts."""
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        return colors[hash(product) % len(colors)]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            'charts_generated': 0,
            'narratives_generated': 0,
            'csv_fallbacks_created': 0,
            'processing_time_ms': 0.0,
            'visualization_errors': 0,
            'accessibility_features_added': 0
        }
    
    def emit_metrics(self):
        """Emit metrics for observability."""
        try:
            metrics = {
                "visualization.gen_time": self.metrics['processing_time_ms'],
                "visualization.errors": self.metrics['visualization_errors'],
                "visualization.charts_generated": self.metrics['charts_generated'],
                "visualization.narratives_generated": self.metrics['narratives_generated'],
                "visualization.csv_fallbacks_created": self.metrics['csv_fallbacks_created'],
                "visualization.accessibility_features_added": self.metrics['accessibility_features_added']
            }
            
            # In a real implementation, you would send these to your metrics system
            print(f"📊 Visualization generator metrics: {metrics}")
            return metrics
            
        except Exception as e:
            print(f"⚠️ Error emitting visualization generator metrics: {e}")
            return {"visualization.metrics_error": str(e)}

# Global generator instance
visualization_generator = VisualizationGenerator()

def generate_visualizations(analytics_results: Dict[str, Any], 
                          analytics_readiness: Dict[str, Any]) -> VisualizationResult:
    """
    Convenience function to generate visualizations.
    
    Args:
        analytics_results: Results from Phase 7 analytics execution
        analytics_readiness: Analytics readiness information
        
    Returns:
        VisualizationResult with charts, narratives, and fallbacks
    """
    return visualization_generator.generate_visualizations(analytics_results, analytics_readiness)

if __name__ == "__main__":
    # Test the visualization generator
    print("🧪 Testing Visualization Generator")
    print("=" * 50)
    
    # Create test analytics results
    test_analytics_results = {
        'sales_summary': {
            'success': True,
            'result_data': {
                'total_sales': 50000.0,
                'average_sales': 500.0,
                'median_sales': 450.0,
                'min_sales': 100.0,
                'max_sales': 1000.0,
                'count': 100
            }
        },
        'product_performance': {
            'success': True,
            'result_data': {
                'product_performance': [
                    {'product': 'A', 'total_sales': 10000, 'average_sales': 500, 'transaction_count': 20},
                    {'product': 'B', 'total_sales': 8000, 'average_sales': 400, 'transaction_count': 20},
                    {'product': 'C', 'total_sales': 6000, 'average_sales': 300, 'transaction_count': 20}
                ],
                'total_products': 3
            }
        }
    }
    
    test_analytics_readiness = {
        'success_rate': 100.0,
        'ready_analytics': ['sales_summary', 'product_performance']
    }
    
    result = generate_visualizations(test_analytics_results, test_analytics_readiness)
    
    if result.success:
        print(f"✅ Successfully generated {len(result.charts)} charts")
        print(f"✅ Successfully generated {len(result.narratives)} narratives")
        print(f"✅ Successfully created {len(result.csv_fallbacks)} CSV fallbacks")
        print(f"⏱️ Processing time: {result.processing_time_seconds:.3f}s")
        
        for chart_name, chart_data in result.charts.items():
            print(f"\n📊 {chart_name}:")
            print(f"   Type: {chart_data.chart_type}")
            print(f"   Title: {chart_data.title}")
            print(f"   Alt text: {chart_data.alt_text[:50]}...")
    else:
        print(f"❌ Error: {result.error_message}")
