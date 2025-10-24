"""
TANAW Predictive Analytics Engine
Implements forecasting and predictive analytics using Prophet and other ML models
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

try:
    from prophet import Prophet
    from prophet.plot import plot_plotly, plot_components_plotly
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

logger = logging.getLogger(__name__)

class TANAWPredictiveAnalytics:
    """
    Predictive analytics engine for TANAW
    Handles forecasting, trend analysis, and predictive insights
    """
    
    def __init__(self):
        """Initialize predictive analytics engine"""
        self.prophet_config = {
            'yearly_seasonality': True,
            'weekly_seasonality': True,
            'daily_seasonality': False,
            'seasonality_mode': 'multiplicative',
            'changepoint_prior_scale': 0.05,
            'seasonality_prior_scale': 10.0
        }
        
    def generate_sales_forecast(self, df: pd.DataFrame, forecast_periods: int = 30) -> Dict[str, Any]:
        """
        Generate sales forecast using Prophet
        
        Args:
            df: DataFrame with Date and Sales columns
            forecast_periods: Number of periods to forecast ahead
            
        Returns:
            Dict containing forecast results and charts
        """
        try:
            # Prepare data for Prophet
            prophet_data = self._prepare_prophet_data(df, 'Sales')
            
            if prophet_data is None or len(prophet_data) < 10:
                return self._get_insufficient_data_response()
            
            # Initialize and fit Prophet model
            model = Prophet(**self.prophet_config)
            model.fit(prophet_data)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=forecast_periods)
            
            # Generate forecast
            forecast = model.predict(future)
            
            # Extract forecast components
            forecast_data = self._extract_forecast_data(forecast, forecast_periods)
            
            # Generate forecast chart
            forecast_chart = self._create_forecast_chart(prophet_data, forecast, forecast_periods)
            
            # Generate components chart
            components_chart = self._create_components_chart(model, forecast)
            
            # Calculate forecast metrics
            metrics = self._calculate_forecast_metrics(prophet_data, forecast, forecast_periods)
            
            return {
                "success": True,
                "forecast_data": forecast_data,
                "charts": [forecast_chart, components_chart],
                "metrics": metrics,
                "model_info": {
                    "model_type": "Prophet",
                    "forecast_periods": forecast_periods,
                    "data_points": len(prophet_data),
                    "seasonality_detected": self._detect_seasonality(forecast)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating sales forecast: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "forecast_data": None,
                "charts": [],
                "metrics": {}
            }
    
    def generate_demand_forecast(self, df: pd.DataFrame, product_col: str = 'Product', 
                                quantity_col: str = 'Quantity', forecast_periods: int = 30) -> Dict[str, Any]:
        """
        Generate demand forecast for products
        
        Args:
            df: DataFrame with Date, Product, and Quantity columns
            product_col: Name of product column
            quantity_col: Name of quantity column
            forecast_periods: Number of periods to forecast ahead
            
        Returns:
            Dict containing demand forecast results
        """
        try:
            # Get top products by total quantity
            top_products = df.groupby(product_col)[quantity_col].sum().nlargest(5).index.tolist()
            
            forecasts = []
            charts = []
            
            # Create multi-line chart data
            multi_line_data = {
                "historical": {},
                "forecast": {}
            }
            
            for product in top_products:
                # Filter data for this product
                product_data = df[df[product_col] == product].copy()
                
                if len(product_data) < 10:
                            continue
                        
                # Prepare data for Prophet
                prophet_data = self._prepare_prophet_data(product_data, quantity_col)
                        
                if prophet_data is None:
                            continue
                        
                # Generate forecast for this product
                model = Prophet(**self.prophet_config)
                model.fit(prophet_data)
                
                future = model.make_future_dataframe(periods=forecast_periods)
                forecast = model.predict(future)
                
                # Extract forecast data
                forecast_data = self._extract_forecast_data(forecast, forecast_periods)
                forecast_data['product'] = product
                
                forecasts.append(forecast_data)
                
                # Add to multi-line data
                dates = forecast['ds'].dt.strftime('%Y-%m-%d').tolist()
                values = forecast['yhat'].tolist()
                
                # Split into historical and forecast
                historical_dates = dates[:-forecast_periods]
                historical_values = values[:-forecast_periods]
                forecast_dates = dates[-forecast_periods:]
                forecast_values = values[-forecast_periods:]
                
                multi_line_data["historical"][product] = {
                    "dates": historical_dates,
                    "values": historical_values
                }
                multi_line_data["forecast"][product] = {
                    "dates": forecast_dates,
                    "values": forecast_values
                }
            
            # Create multi-line chart
            if multi_line_data["historical"]:
                multi_line_chart = self._create_multi_line_demand_chart(multi_line_data, top_products)
                charts.append(multi_line_chart)
            
            return {
                "success": True,
                "forecasts": forecasts,
                "charts": charts,
                "top_products": top_products,
                "model_info": {
                    "model_type": "Prophet",
                    "forecast_periods": forecast_periods,
                    "products_forecasted": len(forecasts)
                }
            }
        
        except Exception as e:
            logger.error(f"Error generating demand forecast: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "forecasts": [],
                "charts": []
            }
    
    def generate_inventory_forecast(self, df: pd.DataFrame, stock_col: str = 'Stock', 
                                   forecast_periods: int = 30) -> Dict[str, Any]:
        """
        Generate inventory forecast and reorder recommendations
        
        Args:
            df: DataFrame with Date and Stock columns
            forecast_periods: Number of periods to forecast ahead
            
        Returns:
            Dict containing inventory forecast results
        """
        try:
            # Prepare data for Prophet
            prophet_data = self._prepare_prophet_data(df, stock_col)
            
            if prophet_data is None or len(prophet_data) < 10:
                return self._get_insufficient_data_response()
            
            # Generate forecast
            model = Prophet(**self.prophet_config)
            model.fit(prophet_data)
            
            future = model.make_future_dataframe(periods=forecast_periods)
            forecast = model.predict(future)
            
            # Extract forecast data
            forecast_data = self._extract_forecast_data(forecast, forecast_periods)
            
            # Calculate reorder points
            reorder_analysis = self._calculate_reorder_points(forecast_data)
            
            # Create inventory chart
            inventory_chart = self._create_inventory_forecast_chart(prophet_data, forecast, forecast_periods)
            
            return {
                "success": True,
                "forecast_data": forecast_data,
                "reorder_analysis": reorder_analysis,
                "charts": [inventory_chart],
                "model_info": {
                    "model_type": "Prophet",
                    "forecast_periods": forecast_periods
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating inventory forecast: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "forecast_data": None,
                "charts": []
            }
    
    def generate_cash_flow_forecast(self, df: pd.DataFrame, revenue_col: str = 'Revenue', 
                                   expense_col: str = 'Expense', forecast_periods: int = 30) -> Dict[str, Any]:
        """
        Generate cash flow forecast
        
        Args:
            df: DataFrame with Date, Revenue, and Expense columns
            forecast_periods: Number of periods to forecast ahead
            
        Returns:
            Dict containing cash flow forecast results
        """
        try:
            # Calculate net cash flow
            df['net_cash_flow'] = df[revenue_col] - df[expense_col]
            
            # Prepare data for Prophet
            prophet_data = self._prepare_prophet_data(df, 'net_cash_flow')
            
            if prophet_data is None or len(prophet_data) < 10:
                return self._get_insufficient_data_response()
            
            # Generate forecast
            model = Prophet(**self.prophet_config)
            model.fit(prophet_data)
            
            future = model.make_future_dataframe(periods=forecast_periods)
            forecast = model.predict(future)
            
            # Extract forecast data
            forecast_data = self._extract_forecast_data(forecast, forecast_periods)
            
            # Calculate cash flow metrics
            cash_flow_metrics = self._calculate_cash_flow_metrics(forecast_data)
            
            # Create cash flow chart
            cash_flow_chart = self._create_cash_flow_chart(prophet_data, forecast, forecast_periods)
            
            return {
                "success": True,
                "forecast_data": forecast_data,
                "cash_flow_metrics": cash_flow_metrics,
                "charts": [cash_flow_chart],
                "model_info": {
                    "model_type": "Prophet",
                    "forecast_periods": forecast_periods
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating cash flow forecast: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "forecast_data": None,
                "charts": []
            }
    
    def _prepare_prophet_data(self, df: pd.DataFrame, value_col: str) -> Optional[pd.DataFrame]:
        """Prepare data for Prophet model"""
        try:
            # Ensure we have Date and value columns
            if 'Date' not in df.columns or value_col not in df.columns:
                return None
            
            # Convert date column
            df_copy = df.copy()
            df_copy['Date'] = pd.to_datetime(df_copy['Date'], errors='coerce')
            
            # Remove rows with invalid dates
            df_copy = df_copy.dropna(subset=['Date'])
            
            # Convert value column to numeric
            df_copy[value_col] = pd.to_numeric(df_copy[value_col], errors='coerce')
            df_copy = df_copy.dropna(subset=[value_col])
            
            if len(df_copy) < 10:
                return None
            
            # Group by date and sum values (in case of multiple entries per date)
            prophet_data = df_copy.groupby('Date')[value_col].sum().reset_index()
            
            # Rename columns for Prophet
            prophet_data.columns = ['ds', 'y']
            
            # Sort by date
            prophet_data = prophet_data.sort_values('ds')
            
            return prophet_data
            
        except Exception as e:
            logger.error(f"Error preparing Prophet data: {str(e)}")
            return None
    
    def _extract_forecast_data(self, forecast: pd.DataFrame, forecast_periods: int) -> Dict[str, Any]:
        """Extract forecast data for frontend"""
        try:
            # Get historical and forecast data
            historical = forecast[:-forecast_periods]
            future_forecast = forecast[-forecast_periods:]
            
            # Extract dates and values
            historical_dates = historical['ds'].dt.strftime('%Y-%m-%d').tolist()
            # Use actual historical values (y) instead of model predictions (yhat) for historical data
            historical_values = historical['y'].tolist() if 'y' in historical.columns else historical['yhat'].tolist()
            
            forecast_dates = future_forecast['ds'].dt.strftime('%Y-%m-%d').tolist()
            forecast_values = future_forecast['yhat'].tolist()
            forecast_lower = future_forecast['yhat_lower'].tolist()
            forecast_upper = future_forecast['yhat_upper'].tolist()
            
            return {
                "historical": {
                    "dates": historical_dates,
                    "values": historical_values
                },
                "forecast": {
                    "dates": forecast_dates,
                    "values": forecast_values,
                    "lower_bound": forecast_lower,
                    "upper_bound": forecast_upper
                },
                "last_historical_value": historical_values[-1] if historical_values else 0,
                "first_forecast_value": forecast_values[0] if forecast_values else 0,
                "forecast_trend": self._calculate_trend(historical_values, forecast_values)
            }
            
        except Exception as e:
            logger.error(f"Error extracting forecast data: {str(e)}")
            return {}
    
    def _create_forecast_chart(self, historical_data: pd.DataFrame, forecast: pd.DataFrame, 
                              forecast_periods: int) -> Dict[str, Any]:
        """Create forecast chart for frontend"""
        try:
            # Combine historical and forecast data
            historical = forecast[:-forecast_periods]
            future_forecast = forecast[-forecast_periods:]
            
            # Prepare chart data
            chart_data = {
                "historical": {
                    "x": historical['ds'].dt.strftime('%Y-%m-%d').tolist(),
                    "y": historical['y'].tolist() if 'y' in historical.columns else historical['yhat'].tolist()
                },
                "forecast": {
                    "x": future_forecast['ds'].dt.strftime('%Y-%m-%d').tolist(),
                    "y": future_forecast['yhat'].tolist(),
                    "lower_bound": future_forecast['yhat_lower'].tolist(),
                    "upper_bound": future_forecast['yhat_upper'].tolist()
                }
            }
            
            return {
                "id": "sales_forecast",
                "title": "Sales Forecast with Predictions",
                "type": "line_forecast",
                "description": "Historical sales data with 30-day future predictions",
                "icon": "📈",
                "status": "success",
                "data": chart_data,
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating forecast chart: {str(e)}")
            return None
    
    def _create_components_chart(self, model: Prophet, forecast: pd.DataFrame) -> Dict[str, Any]:
        """Create components chart showing trend and seasonality"""
        try:
            # Extract components data directly from forecast DataFrame
            dates = forecast['ds'].dt.strftime('%Y-%m-%d').tolist()
            trend = forecast['trend'].tolist()
            
            # Get seasonality components
            seasonal_data = []
            seasonal_name = "Seasonality"
            
            if 'yearly' in forecast.columns:
                seasonal_data = forecast['yearly'].tolist()
                seasonal_name = "Yearly Seasonality"
            elif 'weekly' in forecast.columns:
                seasonal_data = forecast['weekly'].tolist()
                seasonal_name = "Weekly Seasonality"
            elif 'daily' in forecast.columns:
                seasonal_data = forecast['daily'].tolist()
                seasonal_name = "Daily Seasonality"
            
            # Create chart data in the format expected by frontend
            chart_data = []
            for i, date in enumerate(dates):
                chart_data.append({
                    "x": date,
                    "y": trend[i],
                    "seasonal": seasonal_data[i] if seasonal_data else 0,
                    "date": date
                })
            
            return {
                "id": "forecast_components",
                "title": "Forecast Components",
                "type": "components",
                "description": "Trend and seasonality analysis",
                "icon": "🔍",
                "status": "success",
                "data": chart_data,
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating components chart: {str(e)}")
            return None
    
    def _create_multi_line_demand_chart(self, multi_line_data: Dict[str, Any], products: List[str]) -> Dict[str, Any]:
        """Create multi-line demand forecast chart for multiple products"""
        try:
            # Create simplified chart data structure
            chart_data = {
                "x": [],  # dates
                "y": []   # values array for each product
            }
            
            # Get all unique dates
            all_dates = set()
            for product in products:
                if product in multi_line_data["historical"]:
                    all_dates.update(multi_line_data["historical"][product]["dates"])
                if product in multi_line_data["forecast"]:
                    all_dates.update(multi_line_data["forecast"][product]["dates"])
            
            all_dates = sorted(list(all_dates))
            
            # Create simplified data structure (revert to single line)
            chart_data = {
                "x": [],  # dates
                "y": []   # values array for each product
            }
            
            # Get all unique dates
            all_dates = set()
            for product in products:
                if product in multi_line_data["historical"]:
                    all_dates.update(multi_line_data["historical"][product]["dates"])
                if product in multi_line_data["forecast"]:
                    all_dates.update(multi_line_data["forecast"][product]["dates"])
            
            all_dates = sorted(list(all_dates))
            
            # Create simplified data structure
            for date in all_dates:
                chart_data["x"].append(date)
                
                # Create a simple value for this date (sum of all products)
                total_value = 0
                valid_products = 0
                
                for product in products:
                    # Check historical data
                    if product in multi_line_data["historical"]:
                        dates = multi_line_data["historical"][product]["dates"]
                        values = multi_line_data["historical"][product]["values"]
                        if date in dates:
                            total_value += values[dates.index(date)]
                            valid_products += 1
                    
                    # Check forecast data
                    if product in multi_line_data["forecast"]:
                        dates = multi_line_data["forecast"][product]["dates"]
                        values = multi_line_data["forecast"][product]["values"]
                        if date in dates:
                            total_value += values[dates.index(date)]
                            valid_products += 1
                
                # Use average if multiple products, or total if single product
                if valid_products > 0:
                    chart_data["y"].append(total_value / max(valid_products, 1))
                else:
                    chart_data["y"].append(0)
            
            return {
                "id": "multi_product_demand_forecast",
                "title": "Product Demand Forecast",
                "type": "line",  # Keep as simple line for now
                "description": f"Demand forecast for top {len(products)} products",
                "icon": "📦",
                "status": "success",
                "data": chart_data,
                "products": products,
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating multi-line demand chart: {str(e)}")
            return None
    
    def _create_demand_forecast_chart(self, product: str, historical_data: pd.DataFrame, 
                                    forecast: pd.DataFrame, forecast_periods: int) -> Dict[str, Any]:
        """Create demand forecast chart for a specific product"""
        try:
            historical = forecast[:-forecast_periods]
            future_forecast = forecast[-forecast_periods:]
            
            chart_data = {
                "historical": {
                    "x": historical['ds'].dt.strftime('%Y-%m-%d').tolist(),
                    "y": historical['yhat'].tolist()
                },
                "forecast": {
                    "x": future_forecast['ds'].dt.strftime('%Y-%m-%d').tolist(),
                    "y": future_forecast['yhat'].tolist()
                }
            }
            
            return {
                "id": f"demand_forecast_{product}",
                "title": f"Demand Forecast - {product}",
                "type": "line_forecast",
                "description": f"Demand forecast for {product}",
                "icon": "📦",
                "status": "success",
                "data": chart_data,
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating demand forecast chart: {str(e)}")
            return None
    
    def _create_inventory_forecast_chart(self, historical_data: pd.DataFrame, 
                                       forecast: pd.DataFrame, forecast_periods: int) -> Dict[str, Any]:
        """Create inventory forecast chart"""
        try:
            historical = forecast[:-forecast_periods]
            future_forecast = forecast[-forecast_periods:]
            
            chart_data = {
                "historical": {
                    "x": historical['ds'].dt.strftime('%Y-%m-%d').tolist(),
                    "y": historical['yhat'].tolist()
                },
                "forecast": {
                    "x": future_forecast['ds'].dt.strftime('%Y-%m-%d').tolist(),
                    "y": future_forecast['yhat'].tolist()
                }
            }
            
            return {
                "id": "inventory_forecast",
                "title": "Inventory Forecast",
                "type": "line_forecast",
                "description": "Predicted inventory levels",
                "icon": "📦",
                "status": "success",
                "data": chart_data,
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating inventory forecast chart: {str(e)}")
            return None
    
    def _create_cash_flow_chart(self, historical_data: pd.DataFrame, 
                               forecast: pd.DataFrame, forecast_periods: int) -> Dict[str, Any]:
        """Create cash flow forecast chart"""
        try:
            historical = forecast[:-forecast_periods]
            future_forecast = forecast[-forecast_periods:]
            
            chart_data = {
                "historical": {
                    "x": historical['ds'].dt.strftime('%Y-%m-%d').tolist(),
                    "y": historical['yhat'].tolist()
                },
                "forecast": {
                    "x": future_forecast['ds'].dt.strftime('%Y-%m-%d').tolist(),
                    "y": future_forecast['yhat'].tolist()
                }
            }
            
            return {
                "id": "cash_flow_forecast",
                "title": "Cash Flow Forecast",
                "type": "line_forecast",
                "description": "Predicted cash flow",
                "icon": "💰",
                "status": "success",
                "data": chart_data,
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                }
            }
                
        except Exception as e:
            logger.error(f"Error creating cash flow chart: {str(e)}")
            return None
    
    def _calculate_forecast_metrics(self, historical_data: pd.DataFrame, 
                                  forecast: pd.DataFrame, forecast_periods: int) -> Dict[str, Any]:
        """Calculate forecast accuracy and trend metrics"""
        try:
            # Calculate MAPE (Mean Absolute Percentage Error) for historical data
            historical_actual = historical_data['y'].values
            historical_predicted = forecast[:-forecast_periods]['yhat'].values
            
            mape = np.mean(np.abs((historical_actual - historical_predicted) / historical_actual)) * 100
            
            # Calculate trend
            historical_values = historical_data['y'].tolist()
            forecast_values = forecast[-forecast_periods:]['yhat'].tolist()
            
            trend = self._calculate_trend(historical_values, forecast_values)
            
            # Calculate growth rate
            if len(historical_values) > 0 and len(forecast_values) > 0 and historical_values[-1] != 0:
                growth_rate = ((forecast_values[-1] - historical_values[-1]) / abs(historical_values[-1])) * 100
                # Cap growth rate to reasonable range
                growth_rate = max(-1000, min(1000, growth_rate))
            else:
                growth_rate = 0
            
            return {
                "mape": round(mape, 2),
                "trend": trend,
                "growth_rate": round(growth_rate, 2),
                "forecast_accuracy": "High" if mape < 10 else "Medium" if mape < 20 else "Low"
            }
            
        except Exception as e:
            logger.error(f"Error calculating forecast metrics: {str(e)}")
            return {}
    
    def _calculate_trend(self, historical_values: List[float], forecast_values: List[float]) -> str:
        """Calculate trend direction"""
        try:
            if len(historical_values) < 2 or len(forecast_values) < 2:
                return "Unknown"
            
            # Calculate historical trend
            historical_trend = (historical_values[-1] - historical_values[0]) / len(historical_values)
            
            # Calculate forecast trend
            forecast_trend = (forecast_values[-1] - forecast_values[0]) / len(forecast_values)
            
            # Determine overall trend
            if forecast_trend > historical_trend * 1.1:
                return "Increasing"
            elif forecast_trend < historical_trend * 0.9:
                return "Decreasing"
            else:
                return "Stable"
                
        except Exception as e:
            logger.error(f"Error calculating trend: {str(e)}")
            return "Unknown"
    
    def _detect_seasonality(self, forecast: pd.DataFrame) -> Dict[str, bool]:
        """Detect seasonality patterns"""
        try:
            seasonality = {
                "yearly": 'yearly' in forecast.columns,
                "weekly": 'weekly' in forecast.columns,
                "daily": 'daily' in forecast.columns
            }
            return seasonality
        except Exception as e:
            logger.error(f"Error detecting seasonality: {str(e)}")
            return {"yearly": False, "weekly": False, "daily": False}
    
    def _calculate_reorder_points(self, forecast_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate reorder points for inventory"""
        try:
            forecast_values = forecast_data.get('forecast', {}).get('values', [])
            
            if not forecast_values:
                return {}
            
            # Calculate average daily demand
            avg_daily_demand = np.mean(forecast_values)
            
            # Calculate safety stock (assuming 7 days lead time)
            lead_time = 7
            safety_stock = avg_daily_demand * lead_time * 1.5  # 50% safety margin
            
            # Calculate reorder point
            reorder_point = avg_daily_demand * lead_time + safety_stock
            
            return {
                "average_daily_demand": round(avg_daily_demand, 2),
                "safety_stock": round(safety_stock, 2),
                "reorder_point": round(reorder_point, 2),
                "lead_time_days": lead_time
            }
            
        except Exception as e:
            logger.error(f"Error calculating reorder points: {str(e)}")
            return {}
    
    def _calculate_cash_flow_metrics(self, forecast_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cash flow metrics"""
        try:
            forecast_values = forecast_data.get('forecast', {}).get('values', [])
            
            if not forecast_values:
                return {}
            
            # Calculate cash flow metrics
            total_forecast = sum(forecast_values)
            avg_monthly = np.mean(forecast_values)
            min_cash_flow = min(forecast_values)
            max_cash_flow = max(forecast_values)
            
            # Determine cash flow health
            if min_cash_flow < 0:
                cash_flow_health = "Critical"
            elif avg_monthly < 1000:
                cash_flow_health = "Low"
            elif avg_monthly < 5000:
                cash_flow_health = "Moderate"
            else:
                cash_flow_health = "Healthy"
            
            return {
                "total_forecast": round(total_forecast, 2),
                "average_monthly": round(avg_monthly, 2),
                "minimum_cash_flow": round(min_cash_flow, 2),
                "maximum_cash_flow": round(max_cash_flow, 2),
                "cash_flow_health": cash_flow_health
            }
            
        except Exception as e:
            logger.error(f"Error calculating cash flow metrics: {str(e)}")
            return {}
    
    def _get_insufficient_data_response(self) -> Dict[str, Any]:
        """Return response for insufficient data"""
        return {
            "success": False,
            "error": "Insufficient data for forecasting. Need at least 10 data points.",
            "forecast_data": None,
            "charts": [],
            "metrics": {}
        }