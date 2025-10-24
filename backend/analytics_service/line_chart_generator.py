"""
TANAW Line Chart Generator
Phase 2: Line Charts for Time-Series Analysis
Handles: Sales Summary, Profit Trends, Cash Flow Analysis, Inventory Turnover
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
from chart_styling import TANAWChartStyling
from fallback_handler import TANAWFallbackHandler


class TANAWLineChartGenerator:
    """
    Dedicated Line Chart Generator for TANAW
    Phase 2: Build solid foundation for line charts across all domains
    """
    
    def __init__(self):
        """Initialize line chart generator with domain-agnostic configs"""
        # Initialize chart styling
        self.styling = TANAWChartStyling()
        
        # Initialize fallback handler
        self.fallback_handler = TANAWFallbackHandler()
        
        self.chart_configs = {
            "time_series_summary": {
                "title": "Time Series Summary",
                "description": "Trend over time",
                "icon": "📈",
                "aggregate": "sum"  # Default aggregation
            }
        }
    
    def _generate_smart_labels(self, col_name: str) -> Dict[str, str]:
        """
        Generate domain-aware labels based on column name
        Works across Sales, Finance, Inventory, Customer domains
        
        Args:
            col_name: Column name to analyze
            
        Returns:
            Dictionary with suggested label and unit
        """
        col_lower = col_name.lower().replace("_", " ").replace("-", " ")
        
        # Detect domain and generate appropriate labels
        label_map = {
            # Sales/Revenue (removed currency symbol for generalization)
            ("sales", "revenue", "amount"): (col_name, ""),
            # Financial (removed currency symbol for generalization)
            ("profit", "margin", "income", "expense", "cost"): (col_name, ""),
            ("balance", "transaction"): (col_name, ""),
            # Quantity/Count
            ("quantity", "count", "total", "sum"): (col_name, "units"),
            ("stock", "inventory", "supply"): (col_name, "units"),
            # Rate/Percentage
            ("turnover", "rate", "ratio"): (col_name, "rate"),
            ("percentage", "percent"): (col_name, "%"),
            # Cash Flow (removed currency symbol for generalization)
            ("cash", "flow", "cashflow"): (col_name, ""),
            # Time-based
            ("hours", "duration", "time"): (col_name, "hours"),
            ("days", "weeks", "months"): (col_name, col_lower.split()[0]),
            # General numeric
            ("value", "measure", "metric"): (col_name, "units"),
        }
        
        # Check for matches
        for keywords, (label, unit) in label_map.items():
            if any(keyword in col_lower for keyword in keywords):
                return {"label": label, "unit": unit}
        
        # Default: use column name as-is
        return {"label": col_name, "unit": ""}
    
    def generate_sales_summary(self, df: pd.DataFrame, date_col: str, value_col: str) -> Optional[Dict[str, Any]]:
        """
        Generate Sales Summary line chart (domain-agnostic time series)
        Works for: Sales over time, Revenue over time, Expenses over time, etc.
        
        Args:
            df: DataFrame to analyze
            date_col: Column name for dates
            value_col: Column name for values (sales, revenue, expenses, etc.)
            
        Returns:
            Chart data dictionary or None if invalid
        """
        try:
            print(f"📈 Generating Time Series Summary chart")
            print(f"📈 Date column: {date_col}")
            print(f"📈 Value column: {value_col}")
            print(f"📈 DataFrame shape: {df.shape}")
            
            # FALLBACK: Handle None or empty DataFrame
            if df is None or df.empty:
                print("❌ DataFrame is None or empty")
                return None
            
            # Handle duplicate columns
            df_clean = df.copy()
            if df_clean.columns.duplicated().any():
                print(f"⚠️ Found duplicate columns, removing duplicates")
                df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]
            
            # Validate required columns
            if date_col not in df_clean.columns or value_col not in df_clean.columns:
                print(f"❌ Missing required columns: {date_col}, {value_col}")
                print(f"📈 Available columns: {list(df_clean.columns)}")
                return None
            
            # Clean and prepare data
            chart_df = df_clean[[date_col, value_col]].copy()
            
            # FALLBACK: Handle all NaN data
            if chart_df.isnull().all().all():
                print(f"❌ All data is NaN - no valid data found")
                return None
            
            chart_df = chart_df.dropna()
            
            if chart_df.empty:
                print(f"❌ No valid data after cleaning")
                return None
            
            # FALLBACK: Handle insufficient data
            if len(chart_df) < 2:
                print(f"❌ Insufficient data for line chart ({len(chart_df)} points)")
                return None
            
            # Convert date column to datetime
            try:
                chart_df[date_col] = pd.to_datetime(chart_df[date_col], errors='coerce')
                chart_df = chart_df.dropna(subset=[date_col])
                
                if chart_df.empty:
                    print(f"❌ No valid dates found after conversion")
                    return None
                    
            except Exception as e:
                print(f"❌ Error converting dates: {e}")
                return None
            
            # Convert value to numeric
            try:
                chart_df[value_col] = pd.to_numeric(chart_df[value_col], errors='coerce')
                chart_df = chart_df.dropna()
                
                if chart_df.empty:
                    print(f"❌ No numeric value data found")
                    return None
                
                # FALLBACK: Check for all zero or constant values
                if chart_df[value_col].nunique() <= 1:
                    print(f"⚠️ Value data has no variation (all values are the same)")
                    
            except Exception as e:
                print(f"❌ Error converting values to numeric: {e}")
                return None
            
            # Sort by date
            chart_df = chart_df.sort_values(date_col)
            
            # Group by date and aggregate (in case of duplicate dates)
            grouped = chart_df.groupby(date_col)[value_col].sum().reset_index()
            
            # FALLBACK: Handle too many data points (simplify for frontend)
            if len(grouped) > 365:  # More than 1 year of daily data
                print(f"⚠️ Too many data points ({len(grouped)}) - sampling for performance")
                # Resample to weekly or monthly
                grouped[date_col] = pd.to_datetime(grouped[date_col])
                grouped = grouped.set_index(date_col).resample('W')[value_col].sum().reset_index()
            
            # Convert dates to ISO format strings for JSON serialization
            grouped[date_col] = grouped[date_col].dt.strftime('%Y-%m-%d')
            
            # Generate dynamic labels
            date_label = self._generate_smart_labels(date_col)
            value_label = self._generate_smart_labels(value_col)
            
            # Create dynamic title
            title = f"{value_label['label']} Over Time"
            description = f"Trend of {value_label['label'].lower()} over time"
            
            # Create chart data
            chart_data = {
                "x": grouped[date_col].tolist(),
                "y": grouped[value_col].tolist(),
                "x_label": "Date",
                "y_label": f"{value_label['label']}" + (f" ({value_label['unit']})" if value_label['unit'] else "")
            }
            
            # Calculate trend metrics
            total_value = float(grouped[value_col].sum())
            avg_value = float(grouped[value_col].mean())
            min_value = float(grouped[value_col].min())
            max_value = float(grouped[value_col].max())
            
            # Calculate trend direction (simple linear trend)
            if len(grouped) >= 2:
                first_half_avg = grouped[value_col].iloc[:len(grouped)//2].mean()
                second_half_avg = grouped[value_col].iloc[len(grouped)//2:].mean()
                trend = "increasing" if second_half_avg > first_half_avg else "decreasing"
                trend_percentage = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
            else:
                trend = "stable"
                trend_percentage = 0
            
            print(f"📈 Generated time series data: {len(grouped)} data points")
            print(f"📈 Date range: {grouped[date_col].iloc[0]} to {grouped[date_col].iloc[-1]}")
            print(f"📈 Trend: {trend} ({trend_percentage:+.1f}%)")
            
            # Brief description for user understanding
            brief_description = f"Shows {value_label['label'].lower()} trends over time to identify patterns, growth, and seasonal variations. Data is aggregated by summing all {value_label['label'].lower()} per day and displayed chronologically. Use this to track performance trends, identify peak periods, forecast future patterns, and make data-driven decisions about timing and resource allocation."
            
            return {
                "id": f"{value_col.lower()}_time_series",
                "title": title,
                "type": "line",
                "description": description,
                "brief_description": brief_description,
                "icon": "📈",
                "status": "success",
                "data": chart_data,
                "config": self.styling.get_line_chart_config(
                    chart_type="sales",
                    x_label=chart_data.get("x_label", "Date"),
                    y_label=chart_data.get("y_label", "Sales")
                ),
                "meta": {
                    "data_points": len(grouped),
                    "date_range": {
                        "start": grouped[date_col].iloc[0],
                        "end": grouped[date_col].iloc[-1]
                    },
                    "total_value": total_value,
                    "average_value": avg_value,
                    "min_value": min_value,
                    "max_value": max_value,
                    "trend": trend,
                    "trend_percentage": float(trend_percentage),
                    "date_column": date_col,
                    "value_column": value_col
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating Time Series chart: {e}")
            import traceback
            traceback.print_exc()
            # Try fallback methods
            return self.fallback_handler.handle_line_chart_fallback(
                df, "time_series", self.generate_sales_summary,
                date_col=date_col, value_col=value_col
            )
    
    # REMOVED: generate_revenue_over_time method (redundant with Sales Over Time)
    
    def generate_profit_trend(self, df: pd.DataFrame, date_col: str, profit_col: str) -> Optional[Dict[str, Any]]:
        """
        Generate Profit Trend line chart for Finance domain
        
        Args:
            df: DataFrame to analyze
            date_col: Column name for dates
            profit_col: Column name for profit values
            
        Returns:
            Chart data dictionary or None if invalid
        """
        try:
            print(f"📈 Generating Profit Trend chart")
            print(f"📈 Date column: {date_col}")
            print(f"📈 Profit column: {profit_col}")
            
            # Use the same logic as generate_sales_summary but with Finance-specific labels
            chart = self.generate_sales_summary(df, date_col, profit_col)
            if chart:
                # Override with Finance-specific labels
                chart["title"] = "Profit Trend"
                chart["description"] = "Profit trend analysis over time"
                chart["y_label"] = "Profit"
                chart["insights"] = f"Profit trend analysis shows {chart.get('insights', '')}"
            
            return chart
        except Exception as e:
            print(f"❌ Error generating Profit Trend chart: {e}")
            return None
    
    def generate_cash_flow_analysis(self, df: pd.DataFrame, date_col: str, cashflow_col: str) -> Optional[Dict[str, Any]]:
        """
        Generate Cash Flow Analysis line chart for Finance domain
        
        Args:
            df: DataFrame to analyze
            date_col: Column name for dates
            cashflow_col: Column name for cash flow values
            
        Returns:
            Chart data dictionary or None if invalid
        """
        try:
            print(f"💸 Generating Cash Flow Analysis chart")
            print(f"💸 Date column: {date_col}")
            print(f"💸 Cash Flow column: {cashflow_col}")
            
            # Use the same logic as generate_sales_summary but with Finance-specific labels
            chart = self.generate_sales_summary(df, date_col, cashflow_col)
            if chart:
                # Override with Finance-specific labels
                chart["title"] = "Cash Flow Analysis"
                chart["description"] = "Cash flow trends over time"
                chart["y_label"] = "Cash Flow"
                chart["insights"] = f"Cash flow analysis shows {chart.get('insights', '')}"
            
            return chart
        except Exception as e:
            print(f"❌ Error generating Cash Flow Analysis chart: {e}")
            return None
    
    def generate_inventory_turnover(self, df: pd.DataFrame, date_col: str, turnover_col: str) -> Optional[Dict[str, Any]]:
        """
        Generate Inventory Turnover line chart for Inventory domain
        
        Uses LAST value aggregation (not SUM) because turnover rate is a ratio,
        not an additive metric. We want the most recent turnover rate per day.
        
        Args:
            df: DataFrame to analyze
            date_col: Column name for dates
            turnover_col: Column name for turnover rate
            
        Returns:
            Chart data dictionary or None if invalid
        """
        try:
            print(f"📦 Generating Inventory Turnover chart")
            print(f"📦 Date column: {date_col}")
            print(f"📦 Turnover column: {turnover_col}")
            
            # CUSTOM LOGIC for Inventory Turnover (different from sales)
            # Handle None or empty DataFrame
            if df is None or df.empty:
                print("❌ DataFrame is None or empty")
                return None
            
            # Handle duplicate columns
            df_clean = df.copy()
            if df_clean.columns.duplicated().any():
                print(f"⚠️ Found duplicate columns, removing duplicates")
                df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]
            
            # Validate required columns
            if date_col not in df_clean.columns or turnover_col not in df_clean.columns:
                print(f"❌ Missing required columns: {date_col}, {turnover_col}")
                return None
            
            # Clean and prepare data
            chart_df = df_clean[[date_col, turnover_col]].copy()
            chart_df = chart_df.dropna()
            
            if chart_df.empty:
                print(f"❌ No valid data after cleaning")
                return None
            
            # Convert date column to datetime
            try:
                chart_df[date_col] = pd.to_datetime(chart_df[date_col], errors='coerce')
                chart_df = chart_df.dropna(subset=[date_col])
                if chart_df.empty:
                    print(f"❌ No valid dates found")
                    return None
            except Exception as e:
                print(f"❌ Error converting dates: {e}")
                return None
            
            # Convert turnover to numeric
            try:
                chart_df[turnover_col] = pd.to_numeric(chart_df[turnover_col], errors='coerce')
                chart_df = chart_df.dropna()
                if chart_df.empty:
                    print(f"❌ No numeric turnover data found")
                    return None
            except Exception as e:
                print(f"❌ Error converting turnover to numeric: {e}")
                return None
            
            # Sort by date
            chart_df = chart_df.sort_values(date_col)
            
            # CRITICAL FIX: Use LAST (not SUM) for turnover rate
            # Turnover rate is a ratio, not an additive metric
            # We want the most recent turnover rate per day
            grouped = chart_df.groupby(date_col)[turnover_col].last().reset_index()
            
            print(f"📦 Using LAST aggregation for turnover rate (ratio, not sum)")
            print(f"📦 Generated {len(grouped)} data points")
            
            # Convert dates to ISO format strings
            grouped[date_col] = grouped[date_col].dt.strftime('%Y-%m-%d')
            
            # Create chart data
            chart_data = {
                "x": grouped[date_col].tolist(),
                "y": grouped[turnover_col].tolist(),
                "x_label": "Date",
                "y_label": "Turnover Rate"
            }
            
            # Calculate metrics
            avg_turnover = float(grouped[turnover_col].mean())
            min_turnover = float(grouped[turnover_col].min())
            max_turnover = float(grouped[turnover_col].max())
            
            # Calculate trend
            if len(grouped) >= 2:
                first_half_avg = grouped[turnover_col].iloc[:len(grouped)//2].mean()
                second_half_avg = grouped[turnover_col].iloc[len(grouped)//2:].mean()
                trend = "increasing" if second_half_avg > first_half_avg else "decreasing"
                trend_percentage = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
            else:
                trend = "stable"
                trend_percentage = 0
            
            print(f"📦 Avg turnover: {avg_turnover:.2f}, Range: {min_turnover:.2f}-{max_turnover:.2f}")
            print(f"📦 Trend: {trend} ({trend_percentage:+.1f}%)")
            
            # Brief description for user understanding
            brief_description = "Shows how quickly inventory moves over time. Turnover rate indicates how many times inventory is sold and replaced in a period. Higher values mean faster-moving stock and better cash flow. Uses the most recent turnover rate per day (not summed). Use this to identify fast vs slow-moving items, optimize cash flow, detect dead stock, and improve supplier relationships."
            
            return {
                "id": "inventory_turnover_analysis",
                "title": "Inventory Turnover",
                "type": "line",
                "description": "Measure stock movement speed over time (higher = faster inventory movement)",
                "brief_description": brief_description,
                "icon": "🔄",
                "status": "success",
                "data": chart_data,
                "config": self.styling.get_line_chart_config(
                    chart_type="inventory",
                    x_label=chart_data.get("x_label", "Date"),
                    y_label=chart_data.get("y_label", "Turnover Rate")
                ),
                "meta": {
                    "data_points": len(grouped),
                    "date_range": {
                        "start": grouped[date_col].iloc[0],
                        "end": grouped[date_col].iloc[-1]
                    },
                    "average_turnover": avg_turnover,
                    "min_turnover": min_turnover,
                    "max_turnover": max_turnover,
                    "trend": trend,
                    "trend_percentage": float(trend_percentage),
                    "date_column": date_col,
                    "turnover_column": turnover_col,
                    "aggregation_method": "last"  # Important: not sum!
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating Inventory Turnover chart: {e}")
            import traceback
            traceback.print_exc()
            # Try fallback methods
            return self.fallback_handler.handle_line_chart_fallback(
                df, "inventory_turnover", self.generate_inventory_turnover,
                date_col=date_col, turnover_col=turnover_col
            )
    
    def can_generate_chart(self, df: pd.DataFrame, chart_type: str) -> Dict[str, Any]:
        """
        Check if line chart can be generated with available data
        
        Args:
            df: DataFrame to analyze
            chart_type: Type of chart to check
            
        Returns:
            Dictionary with readiness status and missing columns
        """
        try:
            if chart_type == "sales_summary":
                available_cols = []
                
                # Check for Date column
                date_candidates = [
                    "Date", "DateTime", "Date_Time", "Timestamp", "Time",
                    "Sale_Date", "SaleDate", "Transaction_Date", "TransactionDate",
                    "Order_Date", "OrderDate", "Created_At", "CreatedAt",
                    "Period", "Day", "Month", "Year", "Fecha", "Fch"
                ]
                
                for col in df.columns:
                    col_str = str(col)
                    col_lower = col_str.lower().replace(" ", "_").replace("-", "_")
                    
                    # Check for date patterns
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in date_candidates):
                        # Validate it's actually a date column
                        try:
                            pd.to_datetime(df[col], errors='coerce')
                            available_cols.append(col)
                            break
                        except:
                            continue
                
                # Check for Value column (Sales, Amount, etc.) - EXCLUDE Revenue/Profit/Cash_Flow to avoid duplicates
                value_candidates = [
                    "Sales", "Amount", "Value", "Total", "Sum",
                    "Sales_Amount", "SalesAmount", "Total_Sales", "TotalSales",
                    "Expense", "Expense_Amount", "ExpenseAmount",
                    "Balance", "GL_Balance", "Account_Balance",
                    "Income", "Cost",
                    "Vnts", "Ventas"  # Spanish variations
                ]
                
                for col in df.columns:
                    col_str = str(col)
                    col_lower = col_str.lower().replace(" ", "_").replace("-", "_")
                    
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in value_candidates):
                        # Validate numeric
                        try:
                            numeric_data = pd.to_numeric(df[col], errors='coerce')
                            non_null_count = numeric_data.notna().sum()
                            total_count = len(df)
                            
                            # Only accept if at least 50% of values are numeric
                            if non_null_count / total_count >= 0.5:
                                available_cols.append(col)
                                print(f"✅ Found valid value column: {col} ({non_null_count}/{total_count} numeric values)")
                                break
                            else:
                                print(f"⚠️ Skipping {col} - not enough numeric data ({non_null_count}/{total_count})")
                        except Exception as e:
                            print(f"⚠️ Skipping {col} - validation failed: {e}")
                            continue
                
                ready = len(available_cols) >= 2
                missing_cols = [] if ready else ["Date column", "Value column"]
                
                return {
                    "ready": ready,
                    "available_columns": available_cols,
                    "missing_columns": missing_cols,
                    "chart_type": "line",
                    "description": "Time series summary"
                }
            
            # REMOVED: revenue_over_time case (redundant with sales_summary)
            
            elif chart_type == "profit_trend":
                available_cols = []
                
                # Check for Date column
                date_candidates = [
                    "Date", "DateTime", "Date_Time", "Timestamp", "Time",
                    "Sale_Date", "SaleDate", "Transaction_Date", "TransactionDate",
                    "Order_Date", "OrderDate", "Created_At", "CreatedAt",
                    "Period", "Day", "Month", "Year", "Fecha", "Fch"
                ]
                
                for col in df.columns:
                    col_str = str(col)
                    col_lower = col_str.lower().replace(" ", "_").replace("-", "_")
                    
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in date_candidates):
                        try:
                            pd.to_datetime(df[col], errors='coerce')
                            available_cols.append(col)
                            break
                        except:
                            continue
                
                # Check for Profit column
                profit_candidates = [
                    "Profit", "Net_Profit", "NetProfit", "Gross_Profit",
                    "Operating_Profit", "EBIT", "EBITDA", "Earnings", 
                    "Net_Income", "Profit_Loss", "PL"
                ]
                
                for col in df.columns:
                    col_str = str(col)
                    col_lower = col_str.lower().replace(" ", "_").replace("-", "_")
                    
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in profit_candidates):
                        try:
                            numeric_data = pd.to_numeric(df[col], errors='coerce')
                            non_null_count = numeric_data.notna().sum()
                            total_count = len(df)
                            
                            if non_null_count / total_count >= 0.5:
                                available_cols.append(col)
                                print(f"✅ Found valid profit column: {col} ({non_null_count}/{total_count} numeric values)")
                                break
                        except Exception as e:
                            print(f"⚠️ Skipping {col} - validation failed: {e}")
                            continue
                
                ready = len(available_cols) >= 2
                missing_cols = [] if ready else ["Date column", "Profit column"]
                
                return {
                    "ready": ready,
                    "available_columns": available_cols,
                    "missing_columns": missing_cols,
                    "chart_type": "line",
                    "description": "Profit trend"
                }
            
            elif chart_type == "cash_flow_analysis":
                available_cols = []
                
                # Check for Date column
                date_candidates = [
                    "Date", "DateTime", "Date_Time", "Timestamp", "Time",
                    "Sale_Date", "SaleDate", "Transaction_Date", "TransactionDate",
                    "Order_Date", "OrderDate", "Created_At", "CreatedAt",
                    "Period", "Day", "Month", "Year", "Fecha", "Fch"
                ]
                
                for col in df.columns:
                    col_str = str(col)
                    col_lower = col_str.lower().replace(" ", "_").replace("-", "_")
                    
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in date_candidates):
                        try:
                            pd.to_datetime(df[col], errors='coerce')
                            available_cols.append(col)
                            break
                        except:
                            continue
                
                # Check for Cash Flow column
                cashflow_candidates = [
                    "Cash_Flow", "CashFlow", "Net_Cash_Flow", "NetCashFlow",
                    "Operating_Cash_Flow", "Cash", "Cash_Balance",
                    "Free_Cash_Flow", "FreeCashFlow", "CF", "OCF"
                ]
                
                for col in df.columns:
                    col_str = str(col)
                    col_lower = col_str.lower().replace(" ", "_").replace("-", "_")
                    
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in cashflow_candidates):
                        try:
                            numeric_data = pd.to_numeric(df[col], errors='coerce')
                            non_null_count = numeric_data.notna().sum()
                            total_count = len(df)
                            
                            if non_null_count / total_count >= 0.5:
                                available_cols.append(col)
                                print(f"✅ Found valid cash flow column: {col} ({non_null_count}/{total_count} numeric values)")
                                break
                        except Exception as e:
                            print(f"⚠️ Skipping {col} - validation failed: {e}")
                            continue
                
                ready = len(available_cols) >= 2
                missing_cols = [] if ready else ["Date column", "Cash Flow column"]
                
                return {
                    "ready": ready,
                    "available_columns": available_cols,
                    "missing_columns": missing_cols,
                    "chart_type": "line",
                    "description": "Cash flow analysis"
                }
            
            elif chart_type == "inventory_turnover":
                available_cols = []
                
                # Check for Date column
                date_candidates = [
                    "Date", "DateTime", "Date_Time", "Timestamp", "Time",
                    "Sale_Date", "SaleDate", "Transaction_Date", "TransactionDate",
                    "Order_Date", "OrderDate", "Created_At", "CreatedAt",
                    "Period", "Day", "Month", "Year", "Fecha", "Fch"
                ]
                
                for col in df.columns:
                    col_str = str(col)
                    col_lower = col_str.lower().replace(" ", "_").replace("-", "_")
                    
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in date_candidates):
                        try:
                            pd.to_datetime(df[col], errors='coerce')
                            available_cols.append(col)
                            break
                        except:
                            continue
                
                # Check for Inventory Turnover column (EXCLUSIVE - no overlap with Stock/Quantity)
                turnover_candidates = [
                    "Turnover_Rate", "TurnoverRate", "Inventory_Turnover",
                    "InventoryTurnover", "Stock_Turnover", "StockTurnover",
                    "Turnover_Ratio", "TurnoverRatio", "ITR", "ITO",
                    "Inventory_Turn", "InventoryTurn", "Turn_Rate", "TurnRate",
                    "Rotation", "Rotation_Rate", "RotationRate"
                ]
                
                for col in df.columns:
                    col_str = str(col)
                    col_lower = col_str.lower().replace(" ", "_").replace("-", "_")
                    
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in turnover_candidates):
                        try:
                            numeric_data = pd.to_numeric(df[col], errors='coerce')
                            non_null_count = numeric_data.notna().sum()
                            total_count = len(df)
                            
                            if non_null_count / total_count >= 0.5:
                                available_cols.append(col)
                                print(f"✅ Found valid turnover column: {col} ({non_null_count}/{total_count} numeric values)")
                                break
                        except Exception as e:
                            print(f"⚠️ Skipping {col} - validation failed: {e}")
                            continue
                
                ready = len(available_cols) >= 2
                missing_cols = [] if ready else ["Date column", "Turnover Rate column"]
                
                return {
                    "ready": ready,
                    "available_columns": available_cols,
                    "missing_columns": missing_cols,
                    "chart_type": "line",
                    "description": "Inventory turnover"
                }
            
            return {
                "ready": False,
                "available_columns": [],
                "missing_columns": ["Unknown chart type"],
                "chart_type": "line",
                "description": "Unknown chart type"
            }
            
        except Exception as e:
            print(f"❌ Error checking chart readiness: {e}")
            return {
                "ready": False,
                "available_columns": [],
                "missing_columns": [f"Error: {str(e)}"],
                "chart_type": "line",
                "description": "Error checking readiness"
            }
    
    def generate_all_line_charts(self, df: pd.DataFrame, column_mapping: Dict[str, str] = None, context: str = "UNKNOWN") -> List[Dict[str, Any]]:
        """
        Generate all possible line charts for the given dataset with comprehensive fallbacks
        
        Args:
            df: DataFrame to analyze
            column_mapping: Optional mapping from original column names to canonical names
            context: Business context - "SALES", "INVENTORY", "MIXED", or "UNKNOWN"
            
        Returns:
            List of chart dictionaries
        """
        charts = []
        
        # Store column mapping and context for detection
        self.column_mapping = column_mapping or {}
        self.context = context
        
        print(f"📈 Line Chart Generator - Context: {context}")
        
        # FALLBACK 1: Handle empty or invalid datasets
        if df is None or df.empty:
            print("⚠️ Dataset is empty or None - no charts can be generated")
            return []
        
        # FALLBACK 2: Handle datasets with no column names or numeric column names
        if (df.columns.tolist() == [None] * len(df.columns) or 
            all(col is None for col in df.columns) or
            all(isinstance(col, (int, float)) for col in df.columns)):
            print("⚠️ Dataset has no proper column names - generating default names")
            df.columns = [f"Column_{i+1}" for i in range(len(df.columns))]
        
        # FALLBACK 3: Handle datasets with all NaN columns
        if df.isnull().all().all():
            print("⚠️ Dataset contains only NaN values - no charts can be generated")
            return []
        
        # FALLBACK 4: Handle datasets with too few rows for time series
        if len(df) < 2:
            print("⚠️ Dataset has less than 2 rows - insufficient data for time series")
            return []
        
        print(f"🔍 Dataset validation passed: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"🎯 Generating line charts based on context: {context}")
        
        # Try Sales Summary (Time Series) with safe wrapper (SALES charts)
        if context in ["SALES", "MIXED", "UNKNOWN"]:
            try:
                sales_summary_check = self.can_generate_chart(df, "sales_summary")
                print(f"🔍 Sales Summary check: {sales_summary_check}")
                if sales_summary_check["ready"] and len(sales_summary_check["available_columns"]) >= 2:
                    date_col = sales_summary_check["available_columns"][0]  # First available date column
                    value_col = sales_summary_check["available_columns"][1]   # First available value column
                    
                    chart = self.generate_sales_summary(df, date_col, value_col)
                    if chart:
                        charts.append(chart)
                        print(f"✅ Generated Sales Summary chart")
                    else:
                        print(f"❌ Sales Summary chart generation failed")
                else:
                    print(f"⏭️ Sales Summary not available: {sales_summary_check.get('missing_columns', [])}")
            except Exception as e:
                print(f"❌ Error checking Sales Summary readiness: {e}")
        else:
            print(f"⏭️ Skipping Sales Summary (context={context}, sales chart)")
        
        # FINANCE CHARTS TEMPORARILY DISABLED
        # Focusing on Sales & Inventory domains only for semantic detection implementation
        # TODO: Re-enable Finance charts (Profit Trend, Cash Flow) after smart context detection
        
        # Try Inventory Turnover (Inventory Domain) (INVENTORY charts)
        # SPECIAL HANDLING: Check original column names before GPT mapping
        if context in ["INVENTORY", "MIXED", "UNKNOWN"]:
            try:
                print(f"🔍 Checking for Inventory Turnover with original column names...")
                print(f"🔍 Column mapping: {self.column_mapping}")
                
                # Check if original column names contain turnover-related keywords
                turnover_original_col = None
                date_original_col = None
                
                turnover_keywords = [
                    "turnover", "turn_rate", "turnrate", "rotation", "itr", "ito",
                    "inventory_turn", "inventoryturn", "stock_turn", "stockturn"
                ]
                
                for orig_col, mapped_col in self.column_mapping.items():
                    orig_lower = str(orig_col).lower().replace(" ", "_").replace("-", "_")
                    
                    # Check for turnover column
                    if any(keyword in orig_lower for keyword in turnover_keywords):
                        turnover_original_col = mapped_col  # Use the mapped (canonical) column name
                        print(f"✅ Found turnover column: {orig_col} -> {mapped_col}")
                    
                    # Check for date column
                    if mapped_col == "Date":
                        date_original_col = mapped_col
                        print(f"✅ Found date column: {orig_col} -> {mapped_col}")
                
                # If we found both in original column names, generate the chart
                if turnover_original_col and date_original_col:
                    print(f"🎯 Generating Inventory Turnover from original columns")
                    print(f"🎯 Date column (canonical): {date_original_col}")
                    print(f"🎯 Turnover column (canonical): {turnover_original_col}")
                    
                    chart = self.generate_inventory_turnover(df, date_original_col, turnover_original_col)
                    if chart:
                        charts.append(chart)
                        print(f"✅ Generated Inventory Turnover chart from original column names")
                    else:
                        print(f"❌ Inventory Turnover chart generation failed")
                else:
                    print(f"⏭️ Inventory Turnover not available in original column names")
                    print(f"   - Turnover column found: {turnover_original_col is not None}")
                    print(f"   - Date column found: {date_original_col is not None}")
                    
            except Exception as e:
                print(f"❌ Error checking Inventory Turnover with original columns: {e}")
        else:
            print(f"⏭️ Skipping Inventory Turnover (context={context}, inventory chart)")
        
        print(f"📈 Generated {len(charts)} line charts total")
        return charts
    
    def _safe_generate_chart(self, chart_type: str, df: pd.DataFrame, col1: str, col2: str) -> Optional[Dict[str, Any]]:
        """
        Safely generate a chart with comprehensive error handling
        
        Args:
            chart_type: Type of chart to generate
            df: DataFrame to analyze
            col1: First column name (usually date)
            col2: Second column name (usually value)
            
        Returns:
            Chart dictionary or None if failed
        """
        try:
            if chart_type == "sales_summary":
                return self.generate_sales_summary(df, col1, col2)
            else:
                print(f"❌ Unknown chart type: {chart_type}")
                return None
        except MemoryError:
            print(f"❌ Memory error generating {chart_type} chart - dataset too large")
            return None
        except Exception as e:
            print(f"❌ Unexpected error generating {chart_type} chart: {e}")
            import traceback
            traceback.print_exc()
            return None

