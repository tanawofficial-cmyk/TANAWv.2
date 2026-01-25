"""
TANAW Line Chart Generator
Phase 2: Line Charts for Time-Series Analysis
Handles: Sales Summary, Profit Trends, Cash Flow Analysis, Inventory Turnover
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime


class TANAWLineChartGenerator:
    """
    Dedicated Line Chart Generator for TANAW
    Phase 2: Build solid foundation for line charts across all domains
    """
    
    def __init__(self):
        """Initialize line chart generator with domain-agnostic configs"""
        
        # Initialize styling and fallback handler
        from chart_styling import TANAWChartStyling
        from fallback_handler import TANAWFallbackHandler
        self.styling = TANAWChartStyling()
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
                # CRITICAL FIX: Preserve original date values before conversion attempts
                original_dates = chart_df[date_col].copy()
                
                # First try without format (pandas auto-detection)
                chart_df[date_col] = pd.to_datetime(chart_df[date_col], errors='coerce')
                initial_valid = chart_df[date_col].notna().sum()
                initial_failed = len(chart_df) - initial_valid
                
                # If more than 30% fail OR if success rate is less than 70%, try DD-MM-YYYY format
                if initial_failed > len(chart_df) * 0.3 or initial_valid < len(chart_df) * 0.7:
                    print(f"⚠️ {initial_failed}/{len(chart_df)} dates failed to parse ({initial_failed/len(chart_df)*100:.1f}%), trying DD-MM-YYYY format")
                    # CRITICAL: Use original date values (not the already-converted ones)
                    chart_df[date_col] = pd.to_datetime(original_dates, format='%d-%m-%Y', errors='coerce')
                    # If that still fails, try dayfirst=True as fallback
                    still_failed = chart_df[date_col].isna().sum()
                    if still_failed > len(chart_df) * 0.3:
                        print(f"⚠️ DD-MM-YYYY format still failing ({still_failed} failed), trying dayfirst=True")
                        chart_df[date_col] = pd.to_datetime(original_dates, dayfirst=True, errors='coerce')
                
                chart_df = chart_df.dropna(subset=[date_col])
                
                if chart_df.empty:
                    print(f"❌ No valid dates found after conversion")
                    return None
                
                print(f"✅ Successfully parsed {len(chart_df)} rows with valid dates")
                print(f"   Date range: {chart_df[date_col].min()} to {chart_df[date_col].max()}")
                    
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
            
            # CRITICAL FIX: Ensure we have valid dates before checking length
            # Convert to datetime if not already (needed for proper date handling)
            if not pd.api.types.is_datetime64_any_dtype(grouped[date_col]):
                grouped[date_col] = pd.to_datetime(grouped[date_col], errors='coerce')
                grouped = grouped.dropna(subset=[date_col])
            
            # FALLBACK: Handle too many data points (simplify for frontend)
            # CRITICAL FIX: Only resample if significantly MORE than 1 year (e.g., > 500 days)
            # This ensures datasets with ~365-400 days stay as daily for accurate comparison with Power BI
            # Coffee.csv has 381 days - should stay daily, not weekly!
            if len(grouped) > 500:  # More than ~1.4 years of daily data
                print(f"⚠️ Too many data points ({len(grouped)}) - resampling to weekly for performance")
                # Resample to weekly
                grouped = grouped.set_index(date_col).resample('W')[value_col].sum().reset_index()
            elif len(grouped) >= 365:
                print(f"✅ {len(grouped)} days detected (1 year range) - using DAILY aggregation (no resampling)")
            else:
                print(f"✅ {len(grouped)} days detected - using DAILY aggregation")
            
            # CRITICAL FIX: Ensure dates are datetime before formatting
            if not pd.api.types.is_datetime64_any_dtype(grouped[date_col]):
                grouped[date_col] = pd.to_datetime(grouped[date_col], errors='coerce')
                grouped = grouped.dropna(subset=[date_col])
            
            # Convert dates to ISO format strings for JSON serialization
            grouped[date_col] = grouped[date_col].dt.strftime('%Y-%m-%d')
            
            # DEBUG: Log final data point count
            print(f"📊 Final chart data: {len(grouped)} data points")
            if len(grouped) > 0:
                print(f"   Date range: {grouped[date_col].iloc[0]} to {grouped[date_col].iloc[-1]}")
            
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
            
            # CRITICAL FIX: Find the date associated with max and min values
            max_date_row = grouped.loc[grouped[value_col].idxmax()]
            min_date_row = grouped.loc[grouped[value_col].idxmin()]
            max_date = max_date_row[date_col]
            min_date = min_date_row[date_col]
            
            # Ensure dates are in string format for JSON serialization
            if isinstance(max_date, pd.Timestamp):
                max_date = max_date.strftime('%Y-%m-%d')
            elif hasattr(max_date, 'strftime'):
                max_date = max_date.strftime('%Y-%m-%d')
            else:
                max_date = str(max_date)
                
            if isinstance(min_date, pd.Timestamp):
                min_date = min_date.strftime('%Y-%m-%d')
            elif hasattr(min_date, 'strftime'):
                min_date = min_date.strftime('%Y-%m-%d')
            else:
                min_date = str(min_date)
            
            print(f"📈 Peak sales date: {max_date} with value {max_value:,.2f}")
            print(f"📈 Lowest sales date: {min_date} with value {min_value:,.2f}")
            
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
                    "max_date": max_date,  # CRITICAL FIX: Date with highest sales
                    "min_date": min_date,  # CRITICAL FIX: Date with lowest sales
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
                date_col = None
                value_col = None
                
                # Check for Date column - 3-TIER PRIORITIZATION
                # PRIORITY 1: Use explicitly mapped "Date" column
                if self.column_mapping:
                    for original_col, canonical_type in self.column_mapping.items():
                        if canonical_type == "Date" and original_col in df.columns:
                            try:
                                pd.to_datetime(df[original_col], errors='coerce')
                                date_col = original_col
                                available_cols.append(date_col)
                                print(f"✅ Using mapped Date column: {original_col}")
                                break
                            except:
                                pass
                
                # PRIORITY 2: Check for canonical "Date" column
                if not date_col and "Date" in df.columns:
                    try:
                        pd.to_datetime(df["Date"], errors='coerce')
                        date_col = "Date"
                        available_cols.append(date_col)
                        print(f"✅ Using canonical Date column")
                    except:
                        pass
                
                # PRIORITY 3: Flexible search
                if not date_col:
                    print("🔍 No Date mapping found, attempting flexible search...")
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
                            date_col = col
                            available_cols.append(col)
                            print(f"✅ Found date column via flexible search: {col}")
                            break
                        except:
                            continue
                
                # Check for Value column - 3-TIER PRIORITIZATION
                # PRIORITY 1: Use explicitly mapped "Sales" column
                if self.column_mapping:
                    for original_col, canonical_type in self.column_mapping.items():
                        if canonical_type == "Sales" and original_col in df.columns:
                            try:
                                numeric_data = pd.to_numeric(df[original_col], errors='coerce')
                                if numeric_data.notna().sum() / len(df) >= 0.5:
                                    value_col = original_col
                                    available_cols.append(value_col)
                                    print(f"✅ Using mapped Sales column: {original_col}")
                                    break
                            except:
                                pass
                
                # PRIORITY 2: Check for canonical "Sales" column
                if not value_col and "Sales" in df.columns:
                    try:
                        numeric_data = pd.to_numeric(df["Sales"], errors='coerce')
                        if numeric_data.notna().sum() / len(df) >= 0.5:
                            value_col = "Sales"
                            available_cols.append(value_col)
                            print(f"✅ Using canonical Sales column")
                    except:
                        pass
                
                # PRIORITY 3: Flexible search
                if not value_col:
                    print("🔍 No Sales mapping found, attempting flexible search...")
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
                                value_col = col
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
                print(f"🔍 Attempting to generate Sales Summary (Sales Over Time) chart...")
                print(f"🔍 DataFrame columns: {df.columns.tolist()}")
                print(f"🔍 Column mapping: {self.column_mapping}")
                
                sales_summary_check = self.can_generate_chart(df, "sales_summary")
                print(f"🔍 Sales Summary readiness check: {sales_summary_check}")
                
                if sales_summary_check["ready"] and len(sales_summary_check["available_columns"]) >= 2:
                    # CRITICAL FIX: Explicitly find Date and Sales columns (not just first two)
                    available_cols = sales_summary_check["available_columns"]
                    
                    # Find Date column (prioritize canonical "Date", then look for date-like names)
                    date_col = None
                    if "Date" in available_cols:
                        date_col = "Date"
                    else:
                        # Look for date-like column names
                        for col in available_cols:
                            col_lower = str(col).lower()
                            if any(keyword in col_lower for keyword in ['date', 'datetime', 'time', 'timestamp']):
                                date_col = col
                                break
                    
                    # Find Sales/Value column (exclude date columns)
                    value_col = None
                    sales_keywords = ['sales', 'money', 'amount', 'revenue', 'value', 'total', 'price']
                    for col in available_cols:
                        if col == date_col:
                            continue  # Skip date column
                        col_lower = str(col).lower()
                        if any(keyword in col_lower for keyword in sales_keywords):
                            value_col = col
                            break
                    
                    # If still no value column, take first non-date column
                    if not value_col:
                        for col in available_cols:
                            if col != date_col:
                                value_col = col
                                break
                    
                    if not date_col or not value_col:
                        print(f"❌ Could not find distinct date and value columns")
                        print(f"   Date column: {date_col}, Value column: {value_col}")
                        print(f"   Available columns: {available_cols}")
                        raise ValueError("Need distinct Date and Sales columns for line chart")
                    
                    print(f"🔧 Selected columns: date_col={date_col}, value_col={value_col}")
                    
                    print(f"🎯 Generating Sales Summary chart with date_col={date_col}, value_col={value_col}")
                    
                    chart = self.generate_sales_summary(df, date_col, value_col)
                    if chart:
                        charts.append(chart)
                        print(f"✅ Generated Sales Summary (Sales Over Time) chart successfully!")
                    else:
                        print(f"❌ Sales Summary chart generation returned None")
                else:
                    print(f"⏭️ Sales Summary not available - Missing: {sales_summary_check.get('missing_columns', [])}")
                    print(f"   Ready status: {sales_summary_check.get('ready', False)}")
                    print(f"   Available columns: {sales_summary_check.get('available_columns', [])}")
            except Exception as e:
                print(f"❌ Error in Sales Summary generation: {e}")
                import traceback
                traceback.print_exc()
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

