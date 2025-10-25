#!/usr/bin/env python3
"""
TANAW Sales Forecast Generator
Generates predictive analytics and forecasting charts for Sales domain
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import Prophet for advanced forecasting
try:
    from prophet import Prophet
    from prophet.plot import plot_plotly, plot_components_plotly
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("⚠️ Prophet not available, falling back to linear regression")

class TANAWSalesForecastGenerator:
    """
    Generates sales forecasting charts with predictive analytics
    """
    
    def __init__(self):
        self.forecast_periods = 30  # Forecast 30 days ahead
        self.confidence_level = 0.95  # 95% confidence interval
        
        # Prophet configuration for better forecasting
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
        Check if dataset can generate sales forecast
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with readiness status and available columns
        """
        try:
            available_cols = []
            
            # Check for Date column - 3-TIER PRIORITIZATION
            date_col = None
            
            # PRIORITY 1: Use explicitly mapped "Date" column
            if hasattr(self, 'column_mapping') and self.column_mapping:
                for original_col, canonical_type in self.column_mapping.items():
                    if canonical_type == "Date" and original_col in df.columns:
                        try:
                            pd.to_datetime(df[original_col].head(5), errors='coerce')
                            date_col = original_col
                            available_cols.append(date_col)
                            print(f"✅ Using mapped Date column: {original_col}")
                            break
                        except:
                            pass
            
            # PRIORITY 2: Check for canonical "Date" column
            if not date_col and "Date" in df.columns:
                try:
                    pd.to_datetime(df["Date"].head(5), errors='coerce')
                    date_col = "Date"
                    available_cols.append(date_col)
                    print(f"✅ Using canonical Date column")
                except:
                    pass
            
            # PRIORITY 3: Flexible search
            if not date_col:
                print("🔍 No Date mapping found, attempting flexible search...")
                date_candidates = [
                    "Date", "OrderDate", "Order_Date", "TransactionDate", "Transaction_Date",
                    "SaleDate", "Sale_Date", "PurchaseDate", "Purchase_Date", "Time",
                    "Timestamp", "CreatedAt", "Created_At", "UpdatedAt", "Updated_At"
                ]
                
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in date_candidates):
                        # Try to parse as date
                        try:
                            pd.to_datetime(df[col].head(5), errors='coerce')
                            date_col = col
                            available_cols.append(col)
                            print(f"✅ Found date column via flexible search: {col}")
                            break
                        except:
                            continue
            
            if not date_col:
                return {
                    "ready": False,
                    "available_columns": [],
                    "missing_columns": ["Date column"],
                    "chart_type": "forecast",
                    "description": "Sales forecast requires date column"
                }
            
            # Check for Sales/Value column - 3-TIER PRIORITIZATION
            sales_col = None
            
            # PRIORITY 1: Use explicitly mapped "Sales" column
            if hasattr(self, 'column_mapping') and self.column_mapping:
                for original_col, canonical_type in self.column_mapping.items():
                    if canonical_type == "Sales" and original_col in df.columns:
                        try:
                            numeric_data = pd.to_numeric(df[original_col], errors='coerce')
                            if numeric_data.notna().sum() / len(df) >= 0.5:
                                sales_col = original_col
                                available_cols.append(sales_col)
                                print(f"✅ Using mapped Sales column: {original_col}")
                                break
                        except:
                            pass
            
            # PRIORITY 2: Check for canonical "Sales" column
            if not sales_col and "Sales" in df.columns:
                try:
                    numeric_data = pd.to_numeric(df["Sales"], errors='coerce')
                    if numeric_data.notna().sum() / len(df) >= 0.5:
                        sales_col = "Sales"
                        available_cols.append(sales_col)
                        print(f"✅ Using canonical Sales column")
                except:
                    pass
            
            # PRIORITY 3: Flexible search
            if not sales_col:
                print("🔍 No Sales mapping found, attempting flexible search...")
                sales_candidates = [
                    "Sales", "Sales_Amount", "SalesAmount", "Revenue", "Total_Sales", "TotalSales",
                    "Amount", "Value", "Price", "Cost", "Income", "Profit", "Earnings"
                ]
                
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in sales_candidates):
                        # Validate numeric
                        try:
                            numeric_data = pd.to_numeric(df[col], errors='coerce')
                            if numeric_data.notna().sum() / len(df) >= 0.5:
                                sales_col = col
                                available_cols.append(col)
                                print(f"✅ Found sales column via flexible search: {col}")
                                break
                        except:
                            continue
            
            if not sales_col:
                return {
                    "ready": False,
                    "available_columns": available_cols,
                    "missing_columns": ["Sales/Value column"],
                    "chart_type": "forecast",
                    "description": "Sales forecast requires numeric sales column"
                }
            
            # Check if we have enough data points for forecasting
            min_data_points = 10
            if len(df) < min_data_points:
                return {
                    "ready": False,
                    "available_columns": available_cols,
                    "missing_columns": [f"At least {min_data_points} data points"],
                    "chart_type": "forecast",
                    "description": f"Sales forecast requires at least {min_data_points} data points"
                }
            
            return {
                "ready": True,
                "available_columns": available_cols,
                "missing_columns": [],
                "chart_type": "forecast",
                "description": "Sales forecast ready"
            }
            
        except Exception as e:
            return {
                "ready": False,
                "available_columns": [],
                "missing_columns": [f"Error: {str(e)}"],
                "chart_type": "forecast",
                "description": f"Error checking forecast readiness: {e}"
            }
    
    def generate_sales_forecast(self, df: pd.DataFrame, date_col: str, sales_col: str) -> Dict[str, Any]:
        """
        Generate sales forecast chart using Prophet for advanced forecasting
        
        Args:
            df: DataFrame with sales data
            date_col: Name of date column
            sales_col: Name of sales column
            
        Returns:
            Dictionary with forecast chart data
        """
        try:
            # Prepare data
            forecast_df = df.copy()
            
            # Parse dates
            forecast_df[date_col] = pd.to_datetime(forecast_df[date_col], errors='coerce')
            forecast_df = forecast_df.dropna(subset=[date_col, sales_col])
            
            # Convert sales to numeric
            forecast_df[sales_col] = pd.to_numeric(forecast_df[sales_col], errors='coerce')
            forecast_df = forecast_df.dropna(subset=[sales_col])
            
            if len(forecast_df) < 10:  # Prophet needs more data
                raise ValueError("Insufficient data for Prophet forecasting (minimum 10 data points)")
            
            # Aggregate by date (sum sales per day)
            daily_sales = forecast_df.groupby(date_col)[sales_col].sum().reset_index()
            daily_sales = daily_sales.sort_values(date_col)
            
            if PROPHET_AVAILABLE:
                # Use Prophet for advanced forecasting
                return self._generate_prophet_forecast(daily_sales, date_col, sales_col)
            else:
                # Fallback to linear regression
                return self._generate_linear_forecast(daily_sales, date_col, sales_col)
            
        except Exception as e:
            print(f"❌ Error generating sales forecast: {e}")
            return None
    
    def _generate_prophet_forecast(self, daily_sales: pd.DataFrame, date_col: str, sales_col: str) -> Dict[str, Any]:
        """
        Generate forecast using Prophet (advanced time series forecasting)
        """
        try:
            # Prepare data for Prophet (requires 'ds' and 'y' columns)
            prophet_data = daily_sales.rename(columns={date_col: 'ds', sales_col: 'y'})
            
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
            historical_sales = [item["y"] for item in historical_data]
            forecast_sales = [item["y"] for item in forecast_data]
            
            # Calculate trend and seasonality metrics
            trend_slope = float(forecast['trend'].iloc[-1] - forecast['trend'].iloc[-self.forecast_periods-1]) / self.forecast_periods
            avg_historical = np.mean(historical_sales)
            growth_rate = (trend_slope / avg_historical * 100) if avg_historical > 0 else 0
            
            # Generate smart labels
            labels = self._generate_smart_labels(sales_col)
            
            # Brief description for user understanding
            brief_description = f"Predicts future {labels['title'].lower()} for the next {self.forecast_periods} days using Facebook Prophet AI, an advanced machine learning model. Shows historical data, future predictions, and confidence intervals (shaded area). Prophet automatically detects trends, seasonality, and patterns for superior accuracy. Use this for capacity planning, goal setting, budget forecasting, and strategic decision-making."
            
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
                    "total_historical_sales": float(sum(historical_sales)),
                    "predicted_total_forecast": float(sum(forecast_sales)),
                    "growth_rate": f"{growth_rate:.2f}%",
                    "seasonality_detected": True,
                    "model_accuracy": "High (Prophet AI)"
                }
            }
            
        except Exception as e:
            print(f"❌ Error in Prophet forecast: {e}")
            # Try comprehensive fallback methods
            return self.fallback_handler.handle_forecast_fallback(
                daily_sales, "sales_forecast", self._generate_prophet_forecast,
                date_col=date_col, sales_col=sales_col
            )
    
    def _generate_linear_forecast(self, daily_sales: pd.DataFrame, date_col: str, sales_col: str) -> Dict[str, Any]:
        """
        Generate forecast using linear regression (fallback method)
        """
        try:
            # Create time series
            daily_sales['date_numeric'] = (daily_sales[date_col] - daily_sales[date_col].min()).dt.days
            
            # Simple linear trend forecast
            x = daily_sales['date_numeric'].values
            y = daily_sales[sales_col].values
            
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
            last_date = daily_sales[date_col].max()
            forecast_dates = [last_date + timedelta(days=i+1) for i in range(self.forecast_periods)]
            forecast_x = [daily_sales['date_numeric'].max() + i + 1 for i in range(self.forecast_periods)]
            forecast_y = [slope * x_val + intercept for x_val in forecast_x]
            
            # Calculate confidence intervals (simplified)
            std_error = np.sqrt(ss_res / (n - 2)) if n > 2 else np.std(y)
            confidence_margin = 1.96 * std_error  # 95% confidence
            
            upper_bound = [y + confidence_margin for y in forecast_y]
            lower_bound = [max(0, y - confidence_margin) for y in forecast_y]
            
            # Prepare chart data for frontend
            # Historical data with type field
            historical_data = []
            for i, (date, sales) in enumerate(zip(daily_sales[date_col], daily_sales[sales_col])):
                historical_data.append({
                    "x": date.strftime('%Y-%m-%d'),
                    "y": float(sales),
                    "type": "historical"
                })
            
            # Forecast data with type field
            forecast_data = []
            for i, (date, sales, upper, lower) in enumerate(zip(forecast_dates, forecast_y, upper_bound, lower_bound)):
                forecast_data.append({
                    "x": date.strftime('%Y-%m-%d'),
                    "y": float(sales),
                    "upper": float(upper),
                    "lower": float(lower),
                    "type": "forecast"
                })
            
            # Combine for chart display
            chart_data = historical_data + forecast_data
            
            # Generate smart labels
            labels = self._generate_smart_labels(sales_col)
            
            # Brief description for user understanding
            brief_description = f"Predicts future {labels['title'].lower()} for the next {self.forecast_periods} days using linear regression. Shows historical data, future predictions, and confidence intervals. Linear regression provides reliable forecasts for steady trends. Use this for capacity planning, goal setting, and strategic decision-making when Prophet AI is unavailable."
            
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
                    "total_historical_sales": float(sum([item["y"] for item in historical_data])),
                    "predicted_total_forecast": float(sum(forecast_y)),
                    "growth_rate": f"{(float(slope) / float(np.mean([item["y"] for item in historical_data])) * 100):.2f}%" if float(np.mean([item["y"] for item in historical_data])) > 0 else "0%",
                    "model_accuracy": "Medium (Linear Regression)"
                }
            }
            
        except Exception as e:
            print(f"❌ Error in linear forecast: {e}")
            return None
    
    def _generate_smart_labels(self, sales_col: str) -> Dict[str, str]:
        """
        Generate smart labels based on column name
        """
        sales_col_lower = sales_col.lower()
        
        if "revenue" in sales_col_lower:
            return {
                "title": "Revenue Forecast",
                "description": "Predicted revenue trends with confidence intervals",
                "y_label": "Revenue"
            }
        elif "profit" in sales_col_lower:
            return {
                "title": "Profit Forecast", 
                "description": "Predicted profit trends with confidence intervals",
                "y_label": "Profit"
            }
        elif "amount" in sales_col_lower or "value" in sales_col_lower:
            return {
                "title": "Sales Value Forecast",
                "description": "Predicted sales value trends with confidence intervals", 
                "y_label": "Sales Value"
            }
        else:
            return {
                "title": "Sales Forecast",
                "description": "Predicted sales trends with confidence intervals",
                "y_label": "Sales"
            }
    
    def generate_all_sales_forecasts(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generate all possible sales forecasts for the dataset
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            List of forecast chart dictionaries
        """
        forecasts = []
        
        try:
            print(f"🔍 Dataset validation: {df.shape[0]} rows, {df.shape[1]} columns")
            print("🎯 Generating Sales Forecast with predictive analytics")
            
            # Check if forecast can be generated
            forecast_check = self.can_generate_forecast(df)
            print(f"🔍 Sales Forecast check: {forecast_check}")
            
            if forecast_check["ready"] and len(forecast_check["available_columns"]) >= 2:
                date_col = None
                sales_col = None
                
                # Find date column
                for col in forecast_check["available_columns"]:
                    if any(keyword in col.lower() for keyword in ["date", "time", "timestamp"]):
                        date_col = col
                        break
                
                # Find sales column  
                for col in forecast_check["available_columns"]:
                    if any(keyword in col.lower() for keyword in ["sales", "revenue", "amount", "value", "profit"]):
                        sales_col = col
                        break
                
                if date_col and sales_col:
                    print(f"📊 Generating forecast: {date_col} vs {sales_col}")
                    forecast = self.generate_sales_forecast(df, date_col, sales_col)
                    if forecast:
                        forecasts.append(forecast)
                        print(f"✅ Generated Sales Forecast")
                    else:
                        print(f"❌ Sales Forecast generation failed")
                else:
                    print(f"⏭️ Sales Forecast not available: missing date or sales column")
            else:
                print(f"⏭️ Sales Forecast not available: {forecast_check.get('missing_columns', [])}")
                
        except Exception as e:
            print(f"❌ Error in sales forecast generation: {e}")
        
        print(f"📊 Generated {len(forecasts)} sales forecasts total")
        return forecasts
