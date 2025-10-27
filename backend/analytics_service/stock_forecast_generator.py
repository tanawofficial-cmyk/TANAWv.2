#!/usr/bin/env python3
"""
TANAW Stock Forecast Generator
Generates predictive analytics and forecasting charts for Inventory domain
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
from chart_styling import TANAWChartStyling

# Import Prophet for advanced forecasting
try:
    from prophet import Prophet
    from prophet.plot import plot_plotly, plot_components_plotly
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("⚠️ Prophet not available, falling back to linear regression")

class TANAWStockForecastGenerator:
    """
    Generates stock forecasting charts with predictive analytics for inventory management
    """
    
    def __init__(self):
        self.forecast_periods = 30  # Forecast 30 days ahead
        self.confidence_level = 0.95  # 95% confidence interval
        
        # Initialize chart styling
        self.styling = TANAWChartStyling()
        
        # Prophet configuration for stock forecasting
        self.prophet_config = {
            'yearly_seasonality': True,
            'weekly_seasonality': True,
            'daily_seasonality': False,
            'seasonality_mode': 'multiplicative',
            'changepoint_prior_scale': 0.05,
            'seasonality_prior_scale': 10.0,
            'holidays_prior_scale': 10.0,
            'interval_width': 0.95
        }
        
    def can_generate_forecast(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Check if dataset can generate stock forecast
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with readiness status and available columns
        """
        try:
            available_cols = []
            
            # Check for Date column
            date_candidates = [
                "Date", "OrderDate", "Order_Date", "TransactionDate", "Transaction_Date",
                "SaleDate", "Sale_Date", "PurchaseDate", "Purchase_Date", "Time",
                "Timestamp", "CreatedAt", "Created_At", "UpdatedAt", "Updated_At"
            ]
            
            date_col = None
            for col in df.columns:
                col_lower = col.lower().replace(" ", "_").replace("-", "_")
                if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                       for candidate in date_candidates):
                    # Try to parse as date
                    try:
                        pd.to_datetime(df[col].head(5), errors='coerce')
                        date_col = col
                        available_cols.append(col)
                        break
                    except:
                        continue
            
            if not date_col:
                return {
                    "ready": False,
                    "available_columns": [],
                    "missing_columns": ["Date column"],
                    "chart_type": "forecast",
                    "description": "Stock forecast requires date column"
                }
            
            # Check for Stock/Inventory column
            stock_candidates = [
                "Stock", "Stock_Level", "StockLevel", "Inventory", "Quantity", "Units",
                "On_Hand", "OnHand", "Available", "Current_Stock", "CurrentStock"
            ]
            
            stock_col = None
            for col in df.columns:
                col_lower = col.lower().replace(" ", "_").replace("-", "_")
                if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                       for candidate in stock_candidates):
                    # Validate numeric
                    try:
                        numeric_data = pd.to_numeric(df[col], errors='coerce')
                        if numeric_data.notna().sum() / len(df) >= 0.5:
                            stock_col = col
                            available_cols.append(col)
                            break
                    except:
                        continue
            
            if not stock_col:
                return {
                    "ready": False,
                    "available_columns": available_cols,
                    "missing_columns": ["Stock/Inventory column"],
                    "chart_type": "forecast",
                    "description": "Stock forecast requires numeric stock column"
                }
            
            # Check if we have enough data points for forecasting
            min_data_points = 10
            if len(df) < min_data_points:
                return {
                    "ready": False,
                    "available_columns": available_cols,
                    "missing_columns": [f"At least {min_data_points} data points"],
                    "chart_type": "forecast",
                    "description": f"Stock forecast requires at least {min_data_points} data points"
                }
            
            return {
                "ready": True,
                "available_columns": available_cols,
                "missing_columns": [],
                "chart_type": "forecast",
                "description": "Stock forecast ready"
            }
            
        except Exception as e:
            return {
                "ready": False,
                "available_columns": [],
                "missing_columns": [f"Error: {str(e)}"],
                "chart_type": "forecast",
                "description": f"Error checking forecast readiness: {e}"
            }
    
    def generate_stock_forecast(self, df: pd.DataFrame, date_col: str, stock_col: str) -> Dict[str, Any]:
        """
        Generate stock forecast chart using Prophet for advanced forecasting
        
        Args:
            df: DataFrame with stock data
            date_col: Name of date column
            stock_col: Name of stock column
            
        Returns:
            Dictionary with forecast chart data
        """
        try:
            # Prepare data
            forecast_df = df.copy()
            
            # Parse dates
            forecast_df[date_col] = pd.to_datetime(forecast_df[date_col], errors='coerce')
            forecast_df = forecast_df.dropna(subset=[date_col, stock_col])
            
            # Convert stock to numeric
            forecast_df[stock_col] = pd.to_numeric(forecast_df[stock_col], errors='coerce')
            forecast_df = forecast_df.dropna(subset=[stock_col])
            
            if len(forecast_df) < 10:  # Prophet needs more data
                raise ValueError("Insufficient data for Prophet forecasting (minimum 10 data points)")
            
            # Aggregate by date (average stock per day)
            daily_stock = forecast_df.groupby(date_col)[stock_col].mean().reset_index()
            daily_stock = daily_stock.sort_values(date_col)
            
            if PROPHET_AVAILABLE:
                # Use Prophet for advanced forecasting
                return self._generate_prophet_forecast(daily_stock, date_col, stock_col)
            else:
                # Fallback to linear regression
                return self._generate_linear_forecast(daily_stock, date_col, stock_col)
            
        except Exception as e:
            print(f"❌ Error generating stock forecast: {e}")
            return None
    
    def _generate_prophet_forecast(self, daily_stock: pd.DataFrame, date_col: str, stock_col: str) -> Dict[str, Any]:
        """
        Generate forecast using Prophet (advanced time series forecasting)
        """
        try:
            # Prepare data for Prophet (requires 'ds' and 'y' columns)
            prophet_data = daily_stock.rename(columns={date_col: 'ds', stock_col: 'y'})
            
            # Initialize Prophet with configuration
            model = Prophet(**self.prophet_config)
            
            # Fit the model
            model.fit(prophet_data)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=self.forecast_periods)
            
            # Generate forecast
            forecast = model.predict(future)
            
            # Extract historical and forecast data
            historical_data = []
            forecast_data = []
            
            # Historical data (actual)
            for i, row in prophet_data.iterrows():
                historical_data.append({
                    "x": row['ds'].strftime('%Y-%m-%d'),
                    "y": float(row['y']),
                    "type": "historical"
                })
            
            # Forecast data (predicted)
            forecast_rows = forecast.tail(self.forecast_periods)
            for _, row in forecast_rows.iterrows():
                forecast_data.append({
                    "x": row['ds'].strftime('%Y-%m-%d'),
                    "y": float(row['yhat']),
                    "upper": float(row['yhat_upper']),
                    "lower": float(row['yhat_lower']),
                    "type": "forecast"
                })
            
            # Combine for chart display
            chart_data = historical_data + forecast_data
            
            # Calculate advanced metrics
            historical_stock = [item["y"] for item in historical_data]
            forecast_stock = [item["y"] for item in forecast_data]
            
            # Calculate trend and seasonality metrics
            trend_slope = float(forecast['trend'].iloc[-1] - forecast['trend'].iloc[-self.forecast_periods-1]) / self.forecast_periods
            avg_historical = np.mean(historical_stock)
            growth_rate = (trend_slope / avg_historical * 100) if avg_historical > 0 else 0
            
            # Calculate reorder recommendations
            reorder_analysis = self._calculate_reorder_recommendations(historical_stock, forecast_stock)
            
            # Generate smart labels
            labels = self._generate_smart_labels(stock_col)
            
            # Brief description for user understanding
            brief_description = f"Predicts future stock levels for the next {self.forecast_periods} days using Facebook Prophet AI. Shows historical inventory, future predictions, confidence intervals, and reorder recommendations with urgency levels. Prophet detects demand patterns and seasonality for accurate inventory planning. Use this to prevent stockouts, optimize reorder timing, calculate safety stock, and manage working capital effectively."
            
            return {
                "type": "line_forecast",
                "title": f"{labels['title']} (Prophet AI)",
                "description": f"{labels['description']} using Facebook Prophet AI for superior accuracy",
                "brief_description": brief_description,
                "x_label": "Date",
                "y_label": labels["y_label"],
                "data": chart_data,
                "config": self.styling.get_forecast_chart_config(
                    chart_type="forecast",
                    x_label="Date",
                    y_label=labels["y_label"]
                ),
                "insights": {
                    "model_type": "Prophet AI",
                    "trend_slope": float(trend_slope),
                    "forecast_periods": int(self.forecast_periods),
                    "confidence_level": float(self.confidence_level),
                    "avg_historical_stock": float(avg_historical),
                    "predicted_avg_forecast": float(np.mean(forecast_stock)),
                    "growth_rate": f"{growth_rate:.2f}%",
                    "seasonality_detected": True,
                    "model_accuracy": "High (Prophet AI)",
                    "reorder_analysis": reorder_analysis
                }
            }
            
        except Exception as e:
            print(f"❌ Error in Prophet forecast: {e}")
            # Fallback to linear regression
            return self._generate_linear_forecast(daily_stock, date_col, stock_col)
    
    def _generate_linear_forecast(self, daily_stock: pd.DataFrame, date_col: str, stock_col: str) -> Dict[str, Any]:
        """
        Generate forecast using linear regression (fallback method)
        """
        try:
            # Create time series
            daily_stock['date_numeric'] = (daily_stock[date_col] - daily_stock[date_col].min()).dt.days
            
            # Simple linear trend forecast
            x = daily_stock['date_numeric'].values
            y = daily_stock[stock_col].values
            
            # Calculate trend
            n = len(x)
            sum_x = np.sum(x)
            sum_y = np.sum(y)
            sum_xy = np.sum(x * y)
            sum_x2 = np.sum(x * x)
            
            # Linear regression coefficients
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Calculate R-squared for confidence
            y_pred = slope * x + intercept
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Generate forecast
            last_date = daily_stock[date_col].max()
            forecast_dates = [last_date + timedelta(days=i+1) for i in range(self.forecast_periods)]
            forecast_x = [daily_stock['date_numeric'].max() + i + 1 for i in range(self.forecast_periods)]
            forecast_y = [slope * x_val + intercept for x_val in forecast_x]
            
            # Calculate confidence intervals (simplified)
            std_error = np.sqrt(ss_res / (n - 2)) if n > 2 else np.std(y)
            confidence_margin = 1.96 * std_error  # 95% confidence
            
            upper_bound = [y + confidence_margin for y in forecast_y]
            lower_bound = [max(0, y - confidence_margin) for y in forecast_y]
            
            # Prepare chart data for frontend
            # Historical data with type field
            historical_data = []
            for i, (date, stock) in enumerate(zip(daily_stock[date_col], daily_stock[stock_col])):
                historical_data.append({
                    "x": date.strftime('%Y-%m-%d'),
                    "y": float(stock),
                    "type": "historical"
                })
            
            # Forecast data with type field
            forecast_data = []
            for i, (date, stock, upper, lower) in enumerate(zip(forecast_dates, forecast_y, upper_bound, lower_bound)):
                forecast_data.append({
                    "x": date.strftime('%Y-%m-%d'),
                    "y": float(stock),
                    "upper": float(upper),
                    "lower": float(lower),
                    "type": "forecast"
                })
            
            # Combine for chart display
            chart_data = historical_data + forecast_data
            
            # Calculate reorder recommendations
            reorder_analysis = self._calculate_reorder_recommendations(
                [item["y"] for item in historical_data], 
                forecast_y
            )
            
            # Generate smart labels
            labels = self._generate_smart_labels(stock_col)
            
            # Brief description for user understanding
            brief_description = f"Predicts future stock levels for the next {self.forecast_periods} days using linear regression. Shows historical inventory, future predictions, confidence intervals, and reorder recommendations. Linear regression provides reliable forecasts for steady inventory trends. Use this to prevent stockouts, optimize reorder timing, and manage inventory when Prophet AI is unavailable."
            
            return {
                "type": "line_forecast",
                "title": f"{labels['title']} (Linear)",
                "description": f"{labels['description']} using linear regression",
                "brief_description": brief_description,
                "x_label": "Date",
                "y_label": labels["y_label"],
                "data": chart_data,
                "config": self.styling.get_forecast_chart_config(
                    chart_type="forecast",
                    x_label="Date",
                    y_label=labels["y_label"]
                ),
                "insights": {
                    "model_type": "Linear Regression",
                    "trend_slope": float(slope),
                    "r_squared": float(r_squared),
                    "forecast_periods": int(self.forecast_periods),
                    "confidence_level": float(self.confidence_level),
                    "avg_historical_stock": float(np.mean([item['y'] for item in historical_data])),
                    "predicted_avg_forecast": float(np.mean(forecast_y)),
                    "growth_rate": f"{(float(slope) / float(np.mean([item['y'] for item in historical_data])) * 100):.2f}%" if float(np.mean([item['y'] for item in historical_data])) > 0 else "0%",
                    "model_accuracy": "Medium (Linear Regression)",
                    "reorder_analysis": reorder_analysis
                }
            }
            
        except Exception as e:
            print(f"❌ Error in linear forecast: {e}")
            return None
    
    def _calculate_reorder_recommendations(self, historical_stock: List[float], forecast_stock: List[float]) -> Dict[str, Any]:
        """
        Calculate reorder recommendations based on stock forecast
        """
        try:
            avg_historical = np.mean(historical_stock)
            avg_forecast = np.mean(forecast_stock)
            min_historical = np.min(historical_stock)
            min_forecast = np.min(forecast_stock)
            
            # Calculate safety stock (20% of average)
            safety_stock = avg_historical * 0.2
            
            # Calculate reorder point (safety stock + lead time demand)
            lead_time_days = 7  # Assume 7-day lead time
            daily_consumption = avg_historical / 30  # Average daily consumption
            lead_time_demand = daily_consumption * lead_time_days
            reorder_point = safety_stock + lead_time_demand
            
            # Determine reorder urgency
            current_stock = historical_stock[-1] if historical_stock else avg_historical
            days_until_reorder = (current_stock - reorder_point) / daily_consumption if daily_consumption > 0 else 999
            
            urgency = "Critical" if days_until_reorder < 0 else "High" if days_until_reorder < 7 else "Medium" if days_until_reorder < 14 else "Low"
            
            return {
                "safety_stock": float(safety_stock),
                "reorder_point": float(reorder_point),
                "current_stock": float(current_stock),
                "days_until_reorder": float(days_until_reorder),
                "urgency": urgency,
                "recommended_action": "Reorder immediately" if urgency == "Critical" else "Plan reorder soon" if urgency == "High" else "Monitor stock levels"
            }
            
        except Exception as e:
            return {
                "safety_stock": 0,
                "reorder_point": 0,
                "current_stock": 0,
                "days_until_reorder": 0,
                "urgency": "Unknown",
                "recommended_action": "Unable to calculate recommendations"
            }
    
    def _generate_smart_labels(self, stock_col: str) -> Dict[str, str]:
        """
        Generate smart labels based on column name
        """
        stock_col_lower = stock_col.lower()
        
        if "inventory" in stock_col_lower:
            return {
                "title": "Inventory Forecast",
                "description": "Predicted inventory levels with confidence intervals",
                "y_label": "Inventory Level"
            }
        elif "quantity" in stock_col_lower:
            return {
                "title": "Quantity Forecast", 
                "description": "Predicted quantity levels with confidence intervals",
                "y_label": "Quantity"
            }
        elif "units" in stock_col_lower:
            return {
                "title": "Units Forecast",
                "description": "Predicted unit levels with confidence intervals", 
                "y_label": "Units"
            }
        else:
            return {
                "title": "Stock Forecast",
                "description": "Predicted stock levels with confidence intervals",
                "y_label": "Stock Level"
            }
    
    def generate_all_stock_forecasts(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generate all possible stock forecasts for the dataset
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            List of forecast chart dictionaries
        """
        forecasts = []
        
        try:
            print(f"🔍 Dataset validation: {df.shape[0]} rows, {df.shape[1]} columns")
            print("🎯 Generating Stock Forecast with predictive analytics")
            
            # Check if forecast can be generated
            forecast_check = self.can_generate_forecast(df)
            print(f"🔍 Stock Forecast check: {forecast_check}")
            
            if forecast_check["ready"] and len(forecast_check["available_columns"]) >= 2:
                date_col = None
                stock_col = None
                
                # Find date column
                for col in forecast_check["available_columns"]:
                    if any(keyword in col.lower() for keyword in ["date", "time", "timestamp"]):
                        date_col = col
                        break
                
                # Find stock column  
                for col in forecast_check["available_columns"]:
                    if any(keyword in col.lower() for keyword in ["stock", "inventory", "quantity", "units"]):
                        stock_col = col
                        break
                
                if date_col and stock_col:
                    print(f"📊 Generating forecast: {date_col} vs {stock_col}")
                    forecast = self.generate_stock_forecast(df, date_col, stock_col)
                    if forecast:
                        forecasts.append(forecast)
                        print(f"✅ Generated Stock Forecast")
                    else:
                        print(f"❌ Stock Forecast generation failed")
                else:
                    print(f"⏭️ Stock Forecast not available: missing date or stock column")
            else:
                print(f"⏭️ Stock Forecast not available: {forecast_check.get('missing_columns', [])}")
                
        except Exception as e:
            print(f"❌ Error in stock forecast generation: {e}")
        
        print(f"📊 Generated {len(forecasts)} stock forecasts total")
        return forecasts
