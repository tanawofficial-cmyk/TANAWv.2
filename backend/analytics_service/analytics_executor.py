"""
Phase 7: Analytics Readiness & Execution
Implements analytics readiness checking and execution with fallbacks.

Features:
- Analytics readiness checking for each analytic
- Analytic mode setting (full/degraded/disabled)
- Analytics execution with try/except isolation
- Fallback mechanisms for failed analytics
- Specific analytics implementation
- Comprehensive error handling
- Advanced observability
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from scipy import stats
import json

# Import existing configuration
from config_manager import get_config

@dataclass
class AnalyticResult:
    """Represents the result of an analytic execution."""
    analytic_name: str
    mode: str  # 'full', 'degraded', 'disabled'
    success: bool
    result_data: Dict[str, Any]
    execution_time_seconds: float
    fallback_used: bool
    error_message: Optional[str] = None

@dataclass
class AnalyticsExecutionResult:
    """Results from analytics execution."""
    analytics_results: Dict[str, AnalyticResult]
    processing_time_seconds: float
    metrics: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

class AnalyticsExecutor:
    """
    Phase 7: Analytics readiness and execution system.
    
    Features:
    - Analytics readiness checking for each analytic
    - Analytic mode setting (full/degraded/disabled)
    - Analytics execution with try/except isolation
    - Fallback mechanisms for failed analytics
    - Specific analytics implementation
    - Comprehensive error handling
    - Advanced observability
    """
    
    def __init__(self, config=None):
        """Initialize analytics executor with configuration."""
        self.config = config or get_config()
        self.executor_version = "7.0.0"
        
        # Analytics requirements
        self.analytics_requirements = {
            'sales_summary': {
                'required_columns': ['Date', 'Sales'],
                'optional_columns': ['Amount'],
                'min_numeric_pct': 80.0,
                'min_timepoints': 1
            },
            'product_performance': {
                'required_columns': ['Product', 'Sales'],
                'optional_columns': ['Quantity'],
                'min_timepoints': 1
            },
            'regional_sales': {
                'required_columns': ['Region', 'Sales'],
                'optional_columns': ['Amount'],
                'min_timepoints': 1
            },
            'sales_forecasting': {
                'required_columns': ['Date', 'Sales'],
                'optional_columns': ['Amount'],
                'min_timepoints': 10
            },
            'demand_forecasting': {
                'required_columns': ['Date', 'Product', 'Quantity'],
                'min_timepoints': 5
            }
        }
        
        # Metrics tracking
        self.metrics = {
            'analytics_ready_count': 0,
            'analytics_failed': 0,
            'analytics_fallback_rate': 0.0,
            'processing_time_ms': 0.0,
            'sales_summary_executed': 0,
            'product_performance_executed': 0,
            'regional_sales_executed': 0,
            'sales_forecasting_executed': 0,
            'demand_forecasting_executed': 0
        }
    
    def execute_analytics(self, df: pd.DataFrame, cleaning_results: Dict[str, Any]) -> AnalyticsExecutionResult:
        """
        Execute analytics based on data readiness.
        
        Args:
            df: Cleaned DataFrame with canonical columns
            cleaning_results: Results from Phase 6 data cleaning
            
        Returns:
            AnalyticsExecutionResult with executed analytics
        """
        start_time = datetime.now()
        
        try:
            analytics_results = {}
            
            # Check readiness for each analytic
            readiness_results = self._check_analytics_readiness(df, cleaning_results)
            
            # Execute analytics based on readiness
            for analytic_name, readiness in readiness_results.items():
                if readiness['mode'] != 'disabled':
                    try:
                        result = self._execute_single_analytic(df, analytic_name, readiness)
                        analytics_results[analytic_name] = result
                        
                        if result.success:
                            self.metrics[f'{analytic_name}_executed'] += 1
                        else:
                            self.metrics['analytics_failed'] += 1
                            
                    except Exception as e:
                        # Mark as failed and continue
                        analytics_results[analytic_name] = AnalyticResult(
                            analytic_name=analytic_name,
                            mode=readiness['mode'],
                            success=False,
                            result_data={},
                            execution_time_seconds=0.0,
                            fallback_used=False,
                            error_message=str(e)
                        )
                        self.metrics['analytics_failed'] += 1
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics['processing_time_ms'] = processing_time * 1000
            self.metrics['analytics_ready_count'] = len([r for r in analytics_results.values() if r.success])
            
            # Calculate fallback rate
            fallback_count = len([r for r in analytics_results.values() if r.fallback_used])
            total_executed = len([r for r in analytics_results.values() if r.success])
            if total_executed > 0:
                self.metrics['analytics_fallback_rate'] = (fallback_count / total_executed) * 100
            
            return AnalyticsExecutionResult(
                analytics_results=analytics_results,
                processing_time_seconds=processing_time,
                metrics=self.metrics.copy(),
                success=True
            )
            
        except Exception as e:
            return AnalyticsExecutionResult(
                analytics_results={},
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                metrics=self.metrics.copy(),
                success=False,
                error_message=str(e)
            )
    
    def _check_analytics_readiness(self, df: pd.DataFrame, cleaning_results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Check readiness for each analytic."""
        readiness_results = {}
        
        for analytic_name, requirements in self.analytics_requirements.items():
            readiness = {
                'mode': 'disabled',
                'readiness_score': 0.0,
                'missing_columns': [],
                'quality_issues': [],
                'timepoints_available': 0
            }
            
            try:
                # Check required columns
                missing_columns = []
                for col in requirements['required_columns']:
                    if col not in df.columns:
                        missing_columns.append(col)
                
                if missing_columns:
                    readiness['missing_columns'] = missing_columns
                    readiness['mode'] = 'disabled'
                    readiness_results[analytic_name] = readiness
                    continue
                
                # Check optional columns
                optional_columns = requirements.get('optional_columns', [])
                available_optional = [col for col in optional_columns if col in df.columns]
                
                # Check numeric percentage for numeric columns
                numeric_columns = [col for col in requirements['required_columns'] + available_optional 
                                 if col in ['Sales', 'Amount', 'Quantity']]
                
                quality_issues = []
                for col in numeric_columns:
                    if col in cleaning_results:
                        cleaning_result = cleaning_results[col]
                        numeric_pct = 100 - cleaning_result.get('null_percentage', 0)
                        if numeric_pct < requirements.get('min_numeric_pct', 80):
                            quality_issues.append(f'{col}_low_numeric_percentage')
                
                # Check timepoints
                if 'Date' in df.columns:
                    timepoints = len(df['Date'].dropna().unique())
                    readiness['timepoints_available'] = timepoints
                    
                    if timepoints < requirements.get('min_timepoints', 1):
                        quality_issues.append('insufficient_timepoints')
                
                # Determine mode
                if quality_issues:
                    readiness['mode'] = 'degraded'
                    readiness['quality_issues'] = quality_issues
                else:
                    readiness['mode'] = 'full'
                
                # Calculate readiness score
                readiness['readiness_score'] = self._calculate_readiness_score(
                    missing_columns, quality_issues, timepoints, requirements
                )
                
            except Exception as e:
                readiness['mode'] = 'disabled'
                readiness['error'] = str(e)
            
            readiness_results[analytic_name] = readiness
        
        return readiness_results
    
    def _calculate_readiness_score(self, missing_columns: List[str], quality_issues: List[str], 
                                 timepoints: int, requirements: Dict[str, Any]) -> float:
        """Calculate readiness score for an analytic."""
        try:
            score = 100.0
            
            # Penalize missing columns
            score -= len(missing_columns) * 25
            
            # Penalize quality issues
            score -= len(quality_issues) * 10
            
            # Penalize insufficient timepoints
            min_timepoints = requirements.get('min_timepoints', 1)
            if timepoints < min_timepoints:
                score -= (min_timepoints - timepoints) * 5
            
            return max(0.0, min(100.0, score))
            
        except Exception:
            return 0.0
    
    def _execute_single_analytic(self, df: pd.DataFrame, analytic_name: str, 
                               readiness: Dict[str, Any]) -> AnalyticResult:
        """Execute a single analytic with fallback handling."""
        start_time = datetime.now()
        
        try:
            # Try primary execution
            result_data = self._execute_analytic_primary(df, analytic_name, readiness)
            fallback_used = False
            
        except Exception as e:
            # Try fallback execution
            try:
                result_data = self._execute_analytic_fallback(df, analytic_name, readiness, str(e))
                fallback_used = True
            except Exception as fallback_error:
                raise Exception(f"Primary failed: {e}, Fallback failed: {fallback_error}")
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return AnalyticResult(
            analytic_name=analytic_name,
            mode=readiness['mode'],
            success=True,
            result_data=result_data,
            execution_time_seconds=execution_time,
            fallback_used=fallback_used
        )
    
    def _execute_analytic_primary(self, df: pd.DataFrame, analytic_name: str, 
                                readiness: Dict[str, Any]) -> Dict[str, Any]:
        """Execute primary analytic logic."""
        if analytic_name == 'sales_summary':
            return self._execute_sales_summary(df)
        elif analytic_name == 'product_performance':
            return self._execute_product_performance(df)
        elif analytic_name == 'regional_sales':
            return self._execute_regional_sales(df)
        elif analytic_name == 'sales_forecasting':
            return self._execute_sales_forecasting(df)
        elif analytic_name == 'demand_forecasting':
            return self._execute_demand_forecasting(df)
        else:
            raise Exception(f"Unknown analytic: {analytic_name}")
    
    def _execute_analytic_fallback(self, df: pd.DataFrame, analytic_name: str, 
                                 readiness: Dict[str, Any], primary_error: str) -> Dict[str, Any]:
        """Execute fallback analytic logic."""
        if analytic_name == 'sales_summary':
            return self._execute_sales_summary_fallback(df)
        elif analytic_name == 'product_performance':
            return self._execute_product_performance_fallback(df)
        elif analytic_name == 'regional_sales':
            return self._execute_regional_sales_fallback(df)
        elif analytic_name == 'sales_forecasting':
            return self._execute_sales_forecasting_fallback(df)
        elif analytic_name == 'demand_forecasting':
            return self._execute_demand_forecasting_fallback(df)
        else:
            raise Exception(f"Unknown analytic: {analytic_name}")
    
    def _execute_sales_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Execute sales summary analytic."""
        try:
            # Get sales column
            sales_col = 'Sales' if 'Sales' in df.columns else 'Amount'
            sales_data = df[sales_col].dropna()
            
            # Calculate summary statistics
            summary = {
                'total_sales': float(sales_data.sum()),
                'average_sales': float(sales_data.mean()),
                'median_sales': float(sales_data.median()),
                'min_sales': float(sales_data.min()),
                'max_sales': float(sales_data.max()),
                'std_sales': float(sales_data.std()),
                'count': len(sales_data),
                'date_range': {
                    'start': df['Date'].min().isoformat() if 'Date' in df.columns else None,
                    'end': df['Date'].max().isoformat() if 'Date' in df.columns else None
                }
            }
            
            return summary
            
        except Exception as e:
            raise Exception(f"Sales summary execution failed: {e}")
    
    def _execute_sales_summary_fallback(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Execute sales summary fallback."""
        try:
            # Simple aggregation fallback
            sales_col = 'Sales' if 'Sales' in df.columns else 'Amount'
            sales_data = df[sales_col].dropna()
            
            return {
                'total_sales': float(sales_data.sum()),
                'average_sales': float(sales_data.mean()),
                'count': len(sales_data),
                'fallback_used': True,
                'fallback_reason': 'Primary execution failed'
            }
            
        except Exception as e:
            raise Exception(f"Sales summary fallback failed: {e}")
    
    def _execute_product_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Execute product performance analytic."""
        try:
            # Group by product and calculate performance metrics
            if 'Sales' in df.columns:
                performance = df.groupby('Product')['Sales'].agg(['sum', 'mean', 'count']).reset_index()
                performance.columns = ['product', 'total_sales', 'average_sales', 'transaction_count']
            else:
                performance = df.groupby('Product').size().reset_index()
                performance.columns = ['product', 'transaction_count']
            
            # Sort by performance
            if 'total_sales' in performance.columns:
                performance = performance.sort_values('total_sales', ascending=False)
            else:
                performance = performance.sort_values('transaction_count', ascending=False)
            
            return {
                'product_performance': performance.to_dict('records'),
                'top_products': performance.head(10).to_dict('records'),
                'total_products': len(performance)
            }
            
        except Exception as e:
            raise Exception(f"Product performance execution failed: {e}")
    
    def _execute_product_performance_fallback(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Execute product performance fallback."""
        try:
            # Simple product count fallback
            product_counts = df['Product'].value_counts().head(10)
            
            return {
                'product_counts': product_counts.to_dict(),
                'total_products': len(df['Product'].unique()),
                'fallback_used': True,
                'fallback_reason': 'Primary execution failed'
            }
            
        except Exception as e:
            raise Exception(f"Product performance fallback failed: {e}")
    
    def _execute_regional_sales(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Execute regional sales analytic."""
        try:
            # Group by region and calculate sales metrics
            if 'Sales' in df.columns:
                regional_sales = df.groupby('Region')['Sales'].agg(['sum', 'mean', 'count']).reset_index()
                regional_sales.columns = ['region', 'total_sales', 'average_sales', 'transaction_count']
            else:
                regional_sales = df.groupby('Region').size().reset_index()
                regional_sales.columns = ['region', 'transaction_count']
            
            # Sort by sales
            if 'total_sales' in regional_sales.columns:
                regional_sales = regional_sales.sort_values('total_sales', ascending=False)
            else:
                regional_sales = regional_sales.sort_values('transaction_count', ascending=False)
            
            return {
                'regional_sales': regional_sales.to_dict('records'),
                'top_regions': regional_sales.head(10).to_dict('records'),
                'total_regions': len(regional_sales)
            }
            
        except Exception as e:
            raise Exception(f"Regional sales execution failed: {e}")
    
    def _execute_regional_sales_fallback(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Execute regional sales fallback."""
        try:
            # Simple region count fallback
            region_counts = df['Region'].value_counts()
            
            return {
                'region_counts': region_counts.to_dict(),
                'total_regions': len(df['Region'].unique()),
                'fallback_used': True,
                'fallback_reason': 'Primary execution failed'
            }
            
        except Exception as e:
            raise Exception(f"Regional sales fallback failed: {e}")
    
    def _execute_sales_forecasting(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Execute sales forecasting analytic."""
        try:
            # Prepare time series data
            df_ts = df.copy()
            df_ts['Date'] = pd.to_datetime(df_ts['Date'])
            df_ts = df_ts.sort_values('Date')
            
            # Aggregate by date
            sales_col = 'Sales' if 'Sales' in df.columns else 'Amount'
            daily_sales = df_ts.groupby('Date')[sales_col].sum().reset_index()
            
            # Create time features
            daily_sales['day_of_year'] = daily_sales['Date'].dt.dayofyear
            daily_sales['month'] = daily_sales['Date'].dt.month
            daily_sales['quarter'] = daily_sales['Date'].dt.quarter
            
            # Simple linear regression forecast
            X = daily_sales[['day_of_year', 'month', 'quarter']].values
            y = daily_sales[sales_col].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Generate forecast
            last_date = daily_sales['Date'].max()
            forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=30, freq='D')
            
            forecast_data = []
            for date in forecast_dates:
                features = np.array([[date.dayofyear, date.month, date.quarter]])
                prediction = model.predict(features)[0]
                forecast_data.append({
                    'date': date.isoformat(),
                    'predicted_sales': float(prediction)
                })
            
            return {
                'forecast': forecast_data,
                'model_accuracy': float(model.score(X, y)),
                'forecast_period': 30,
                'last_actual_date': last_date.isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Sales forecasting execution failed: {e}")
    
    def _execute_sales_forecasting_fallback(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Execute sales forecasting fallback."""
        try:
            # Simple trend-based forecast
            sales_col = 'Sales' if 'Sales' in df.columns else 'Amount'
            sales_data = df[sales_col].dropna()
            
            # Calculate simple trend
            if len(sales_data) > 1:
                trend = (sales_data.iloc[-1] - sales_data.iloc[0]) / len(sales_data)
                last_value = sales_data.iloc[-1]
            else:
                trend = 0
                last_value = sales_data.iloc[0] if len(sales_data) > 0 else 0
            
            # Generate simple forecast
            forecast_data = []
            for i in range(30):
                prediction = last_value + (trend * (i + 1))
                forecast_data.append({
                    'date': (datetime.now() + timedelta(days=i+1)).isoformat(),
                    'predicted_sales': float(prediction)
                })
            
            return {
                'forecast': forecast_data,
                'forecast_period': 30,
                'fallback_used': True,
                'fallback_reason': 'Primary execution failed'
            }
            
        except Exception as e:
            raise Exception(f"Sales forecasting fallback failed: {e}")
    
    def _execute_demand_forecasting(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Execute demand forecasting analytic."""
        try:
            # Prepare time series data by product
            df_ts = df.copy()
            df_ts['Date'] = pd.to_datetime(df_ts['Date'])
            df_ts = df_ts.sort_values(['Product', 'Date'])
            
            # Aggregate by product and date
            daily_demand = df_ts.groupby(['Product', 'Date'])['Quantity'].sum().reset_index()
            
            # Get top products for forecasting
            product_totals = daily_demand.groupby('Product')['Quantity'].sum().sort_values(ascending=False)
            top_products = product_totals.head(5).index.tolist()
            
            forecasts = {}
            for product in top_products:
                product_data = daily_demand[daily_demand['Product'] == product]
                
                if len(product_data) >= 5:  # Minimum data points
                    # Simple linear trend
                    X = np.arange(len(product_data)).reshape(-1, 1)
                    y = product_data['Quantity'].values
                    
                    model = LinearRegression()
                    model.fit(X, y)
                    
                    # Generate forecast
                    future_X = np.arange(len(product_data), len(product_data) + 30).reshape(-1, 1)
                    future_demand = model.predict(future_X)
                    
                    forecasts[product] = {
                        'forecast': [float(x) for x in future_demand],
                        'trend': float(model.coef_[0]),
                        'data_points': len(product_data)
                    }
            
            return {
                'product_forecasts': forecasts,
                'forecast_period': 30,
                'products_forecasted': len(forecasts)
            }
            
        except Exception as e:
            raise Exception(f"Demand forecasting execution failed: {e}")
    
    def _execute_demand_forecasting_fallback(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Execute demand forecasting fallback."""
        try:
            # Simple average-based forecast
            product_avg = df.groupby('Product')['Quantity'].mean()
            top_products = product_avg.head(5)
            
            forecasts = {}
            for product, avg_demand in top_products.items():
                forecasts[product] = {
                    'forecast': [float(avg_demand)] * 30,
                    'average_demand': float(avg_demand),
                    'fallback_used': True
                }
            
            return {
                'product_forecasts': forecasts,
                'forecast_period': 30,
                'products_forecasted': len(forecasts),
                'fallback_used': True,
                'fallback_reason': 'Primary execution failed'
            }
            
        except Exception as e:
            raise Exception(f"Demand forecasting fallback failed: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            'analytics_ready_count': 0,
            'analytics_failed': 0,
            'analytics_fallback_rate': 0.0,
            'processing_time_ms': 0.0,
            'sales_summary_executed': 0,
            'product_performance_executed': 0,
            'regional_sales_executed': 0,
            'sales_forecasting_executed': 0,
            'demand_forecasting_executed': 0
        }
    
    def emit_metrics(self):
        """Emit metrics for observability."""
        try:
            metrics = {
                "analytics.ready_count": self.metrics['analytics_ready_count'],
                "analytics.failed": self.metrics['analytics_failed'],
                "analytics.fallback_rate": self.metrics['analytics_fallback_rate'],
                "analytics.processing_time_ms": self.metrics['processing_time_ms'],
                "analytics.sales_summary_executed": self.metrics['sales_summary_executed'],
                "analytics.product_performance_executed": self.metrics['product_performance_executed'],
                "analytics.regional_sales_executed": self.metrics['regional_sales_executed'],
                "analytics.sales_forecasting_executed": self.metrics['sales_forecasting_executed'],
                "analytics.demand_forecasting_executed": self.metrics['demand_forecasting_executed']
            }
            
            # In a real implementation, you would send these to your metrics system
            print(f"📊 Analytics executor metrics: {metrics}")
            return metrics
            
        except Exception as e:
            print(f"⚠️ Error emitting analytics executor metrics: {e}")
            return {"analytics.metrics_error": str(e)}

# Global executor instance
analytics_executor = AnalyticsExecutor()

def execute_analytics(df: pd.DataFrame, cleaning_results: Dict[str, Any]) -> AnalyticsExecutionResult:
    """
    Convenience function to execute analytics.
    
    Args:
        df: Cleaned DataFrame with canonical columns
        cleaning_results: Results from Phase 6 data cleaning
        
    Returns:
        AnalyticsExecutionResult with executed analytics
    """
    return analytics_executor.execute_analytics(df, cleaning_results)

if __name__ == "__main__":
    # Test the analytics executor
    print("🧪 Testing Analytics Executor")
    print("=" * 50)
    
    # Create test DataFrame
    test_df = pd.DataFrame({
        'Date': pd.date_range('2023-01-01', periods=100),
        'Sales': np.random.uniform(100, 1000, 100),
        'Product': np.random.choice(['A', 'B', 'C', 'D', 'E'], 100),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], 100),
        'Quantity': np.random.randint(1, 50, 100)
    })
    
    cleaning_results = {
        'Date': {'null_percentage': 0.0, 'quality_score': 100.0},
        'Sales': {'null_percentage': 0.0, 'quality_score': 100.0},
        'Product': {'null_percentage': 0.0, 'quality_score': 100.0},
        'Region': {'null_percentage': 0.0, 'quality_score': 100.0},
        'Quantity': {'null_percentage': 0.0, 'quality_score': 100.0}
    }
    
    result = execute_analytics(test_df, cleaning_results)
    
    if result.success:
        print(f"✅ Successfully executed {len(result.analytics_results)} analytics")
        print(f"⏱️ Processing time: {result.processing_time_seconds:.3f}s")
        
        for analytic_name, analytic_result in result.analytics_results.items():
            print(f"\n📊 {analytic_name}:")
            print(f"   Mode: {analytic_result.mode}")
            print(f"   Success: {analytic_result.success}")
            print(f"   Execution time: {analytic_result.execution_time_seconds:.3f}s")
            if analytic_result.fallback_used:
                print(f"   Fallback used: {analytic_result.fallback_used}")
    else:
        print(f"❌ Error: {result.error_message}")
