"""
TANAW Finance Analytics Module
Provides finance-specific analytics and visualizations.
Updated: Now uses flexible column detection to avoid duplicates with sales charts.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class FinanceChart:
    id: str
    title: str
    type: str
    description: str
    icon: str
    domain: str  # NEW: Domain identifier ('finance')
    data: Dict
    config: Dict

class TANAWFinanceAnalytics:
    """
    Finance analytics engine for TANAW.
    Provides expense analysis, cash flow, budget tracking, and profit margins.
    Updated: Uses flexible column detection to avoid sales chart duplicates.
    """
    
    def __init__(self):
        # Finance-specific column patterns
        self.finance_patterns = {
            'revenue': ['revenue', 'income', 'sales', 'sales_amount', 'total_sales'],
            'expense': ['expense', 'expenses', 'cost', 'costs', 'spending', 'expenditure'],
            'profit': ['profit', 'net_income', 'earnings'],
            'budget': ['budget', 'budgeted', 'planned', 'allocated'],
            'category': ['category', 'account', 'department', 'type']
        }
        
        self.analytics_config = {
            'expense_breakdown': {
                'name': 'Expense Breakdown Analysis',
                'description': 'Categorizes and analyzes expenses',
                'icon': '💰',
                'type': 'pie'
            },
            'cash_flow_analysis': {
                'name': 'Cash Flow Analysis',
                'description': 'Tracks cash flow over time',
                'icon': '💸',
                'type': 'line'
            },
            'budget_vs_actual': {
                'name': 'Budget vs Actual Report',
                'description': 'Compares budgeted vs actual expenses',
                'icon': '📊',
                'type': 'bar'
            },
            'profit_margin': {
                'name': 'Profit Margin Analysis',
                'description': 'Analyzes profit margins by category',
                'icon': '📈',
                'type': 'bar'
            },
            'financial_forecast': {
                'name': 'Financial Forecasting',
                'description': 'Predicts future financial trends',
                'icon': '🔮',
                'type': 'line'
            }
        }
    
    def generate_analytics(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> List[FinanceChart]:
        """
        Generate finance analytics charts.
        Now focuses on 3 key finance charts with flexible column detection.
        
        Args:
            df: Cleaned dataset
            column_mapping: Column mapping dictionary
            
        Returns:
            List of finance analytics charts
        """
        print(f"💰 TANAW Finance Analytics: Generating analytics for {df.shape[0]} records")
        print(f"📋 Available columns: {list(df.columns)}")
        print(f"🗺️ Column mapping: {column_mapping}")
        
        charts = []
        
        # Chart 1: Revenue and Expense Trend (Line Chart)
        print("\n📊 Chart 1: Generating Revenue and Expense Trend...")
        revenue_expense_chart = self._generate_revenue_expense_trend(df, column_mapping)
        if revenue_expense_chart:
            charts.append(revenue_expense_chart)
            print(f"✅ Successfully generated Revenue and Expense Trend")
        else:
            print(f"⚠️ Skipped Revenue and Expense Trend (missing required columns)")
        
        # Chart 2: Profit Margin Analysis (Bar Chart)
        print("\n📊 Chart 2: Generating Profit Margin Analysis...")
        profit_chart = self._generate_profit_margin_analysis(df, column_mapping)
        if profit_chart:
            charts.append(profit_chart)
            print(f"✅ Successfully generated Profit Margin Analysis")
        else:
            print(f"⚠️ Skipped Profit Margin Analysis (missing required columns)")
        
        # Chart 3: Cash Flow Forecast (Line Chart)
        print("\n📊 Chart 3: Generating Cash Flow Forecast...")
        forecast_chart = self._generate_cash_flow_forecast(df, column_mapping)
        if forecast_chart:
            charts.append(forecast_chart)
            print(f"✅ Successfully generated Cash Flow Forecast")
        else:
            print(f"⚠️ Skipped Cash Flow Forecast (missing required columns)")
        
        print(f"\n✅ Generated {len(charts)} finance analytics charts")
        return charts
    
    # ==================== HELPER METHODS ====================
    
    def _find_column(self, df: pd.DataFrame, column_mapping: Dict[str, str], 
                    patterns: List[str], canonical: List[str] = None) -> Optional[str]:
        """
        Flexible column detection using patterns and canonical mappings.
        
        Args:
            df: DataFrame
            column_mapping: Column mapping dictionary
            patterns: List of pattern keywords to match
            canonical: List of canonical column types to check
            
        Returns:
            Column name if found, None otherwise
        """
        # First, check if canonical column exists directly in dataframe (after mapping)
        if canonical:
            for canon_name in canonical:
                if canon_name in df.columns:
                    print(f"   ✓ Found column '{canon_name}' directly in DataFrame")
                    return canon_name
        
        # Second, check actual column names in dataframe (case-insensitive pattern matching)
        for col in df.columns:
            col_lower = str(col).lower().replace('_', ' ').replace('-', ' ')
            for pattern in patterns:
                if pattern.lower() in col_lower:
                    print(f"   ✓ Found column '{col}' matching pattern '{pattern}'")
                    return col
        
        # Third, check canonical mappings (for original column names)
        if canonical:
            for orig_col, canon_col in column_mapping.items():
                if canon_col in canonical and orig_col in df.columns:
                    print(f"   ✓ Found column '{orig_col}' via canonical mapping '{canon_col}'")
                    return orig_col
        
        print(f"   ✗ No column found for patterns: {patterns} or canonical: {canonical}")
        return None
    
    def _find_date_column(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[str]:
        """Find date column using patterns."""
        date_patterns = ['date', 'datetime', 'time', 'timestamp', 'fecha', 'day', 'period']
        return self._find_column(df, column_mapping,
            patterns=date_patterns,
            canonical=['Date'])
    
    # ==================== NEW FINANCE CHARTS ====================
    
    def _generate_revenue_expense_trend(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[FinanceChart]:
        """
        Chart 1: Revenue and Expense Trend
        Type: Multi-Series Line Chart
        Shows: Revenue vs Expenses over time
        """
        try:
            print("   🔍 Looking for required columns...")
            
            # Find date column
            date_col = self._find_date_column(df, column_mapping)
            if not date_col:
                print("   ❌ No date column found")
                return None
            
            # Find revenue column
            revenue_col = self._find_column(df, column_mapping,
                patterns=self.finance_patterns['revenue'],
                canonical=['Revenue', 'Sales', 'Amount'])  # Check Revenue first, then Sales
            
            # If no revenue column, try to calculate it from Unit_Price × Sales_Volume
            calculated_revenue = False
            if not revenue_col:
                print("   ⚙️ No direct revenue column - attempting to calculate from Unit_Price × Sales_Volume")
                price_col = self._find_column(df, column_mapping,
                    patterns=['price', 'unit_price', 'cost', 'rate'],
                    canonical=['Price', 'Amount'])
                volume_col = self._find_column(df, column_mapping,
                    patterns=['sales_volume', 'quantity', 'volume', 'qty', 'units'],
                    canonical=['Sales', 'Quantity'])
                
                if price_col and volume_col:
                    df_work = df.copy()
                    # Clean price column (remove currency symbols and convert to float)
                    df_work[price_col] = df_work[price_col].astype(str).str.replace('$', '').str.replace(',', '')
                    df_work[price_col] = pd.to_numeric(df_work[price_col], errors='coerce')
                    df_work[volume_col] = pd.to_numeric(df_work[volume_col], errors='coerce')
                    
                    # Calculate revenue
                    df_work['Calculated_Revenue'] = df_work[price_col] * df_work[volume_col]
                    revenue_col = 'Calculated_Revenue'
                    calculated_revenue = True
                    print(f"   ✓ Calculated revenue from '{price_col}' × '{volume_col}'")
                    # Use calculated dataframe
                    df = df_work
                else:
                    print(f"   ⚠️ Cannot calculate revenue - missing price or volume columns")
            
            # Find expense column
            expense_col = self._find_column(df, column_mapping,
                patterns=self.finance_patterns['expense'],
                canonical=['Expense', 'Finance', 'Cost'])  # Check Expense first, then Finance
            
            # Need at least one of revenue or expense
            if not revenue_col and not expense_col:
                print("   ❌ No revenue or expense columns found")
                return None
            
            print(f"   📊 Using: Date='{date_col}', Revenue='{revenue_col}' {'(calculated)' if calculated_revenue else ''}, Expense='{expense_col}'")
            
            # Convert date column to datetime (use existing df if revenue was calculated)
            if not calculated_revenue:
                df_work = df.copy()
            # df_work already exists if calculated_revenue is True
            df_work[date_col] = pd.to_datetime(df_work[date_col], errors='coerce')
            df_work = df_work.dropna(subset=[date_col])
            
            if len(df_work) == 0:
                print("   ❌ No valid dates after conversion")
                return None
            
            # Prepare aggregation dictionary
            agg_dict = {}
            if revenue_col:
                agg_dict[revenue_col] = 'sum'
            if expense_col:
                agg_dict[expense_col] = 'sum'
            
            # Group by date and sum
            df_grouped = df_work.groupby(date_col, as_index=False).agg(agg_dict)
            df_grouped = df_grouped.sort_values(date_col)
            
            # Format dates for display
            date_values = df_grouped[date_col].dt.strftime('%Y-%m-%d').tolist()
            
            # Build series data
            series_data = []
            if revenue_col:
                series_data.append({
                    'name': 'Revenue',
                    'y': df_grouped[revenue_col].fillna(0).tolist(),
                    'color': '#10b981'  # Green
                })
            if expense_col:
                series_data.append({
                    'name': 'Expenses',
                    'y': df_grouped[expense_col].fillna(0).tolist(),
                    'color': '#ef4444'  # Red
                })
            
            print(f"   ✅ Generated trend with {len(df_grouped)} data points")
            
            return FinanceChart(
                id='revenue_expense_trend',
                title='Revenue and Expense Trend',
                type='line',
                description='Total revenue vs expenses over time',
                icon='💰',
                domain='finance',
                data={
                    'x': date_values,
                    'series': series_data,
                    'x_label': 'Date',
                    'y_label': 'Amount (₱)',
                    'chart_subtype': 'multi_series'  # Identifies multi-line chart
                },
                config={
                    'maintainAspectRatio': False,
                    'responsive': True
                }
            )
            
        except Exception as e:
            print(f"   ❌ Error generating revenue/expense trend: {e}")
            import traceback
            print(f"   📋 Traceback: {traceback.format_exc()}")
            return None
    
    def _generate_profit_margin_analysis(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[FinanceChart]:
        """
        Chart 2: Profit Margin Analysis
        Type: Bar Chart
        Shows: Profit margin % by product/category
        """
        try:
            print("   🔍 Looking for required columns...")
            
            # Find product/category column
            product_col = self._find_column(df, column_mapping,
                patterns=['product', 'category', 'item', 'account', 'department'],
                canonical=['Product', 'Category'])
            
            if not product_col:
                print("   ❌ No product/category column found")
                return None
            
            # Find revenue column
            revenue_col = self._find_column(df, column_mapping,
                patterns=self.finance_patterns['revenue'],
                canonical=['Revenue', 'Sales', 'Amount'])  # Check Revenue first
            
            # If no revenue column, try to calculate it from Unit_Price × Sales_Volume
            calculated_revenue = False
            df_work = df.copy()
            if not revenue_col:
                print("   ⚙️ No direct revenue column - attempting to calculate from Unit_Price × Sales_Volume")
                price_col = self._find_column(df, column_mapping,
                    patterns=['price', 'unit_price', 'cost', 'rate'],
                    canonical=['Price', 'Amount'])
                volume_col = self._find_column(df, column_mapping,
                    patterns=['sales_volume', 'quantity', 'volume', 'qty', 'units'],
                    canonical=['Sales', 'Quantity'])
                
                if price_col and volume_col:
                    # Clean price column (remove currency symbols and convert to float)
                    df_work[price_col] = df_work[price_col].astype(str).str.replace('$', '').str.replace(',', '')
                    df_work[price_col] = pd.to_numeric(df_work[price_col], errors='coerce')
                    df_work[volume_col] = pd.to_numeric(df_work[volume_col], errors='coerce')
                    
                    # Calculate revenue
                    df_work['Calculated_Revenue'] = df_work[price_col] * df_work[volume_col]
                    revenue_col = 'Calculated_Revenue'
                    calculated_revenue = True
                    print(f"   ✓ Calculated revenue from '{price_col}' × '{volume_col}'")
                else:
                    print(f"   ⚠️ Cannot calculate revenue - missing price or volume columns")
            
            if not revenue_col:
                print("   ❌ No revenue column found and cannot calculate")
                return None
            
            # Find expense/cost column (optional)
            expense_col = self._find_column(df, column_mapping,
                patterns=self.finance_patterns['expense'],
                canonical=['Expense', 'Finance', 'Cost'])  # Check Expense first
            
            print(f"   📊 Using: Product='{product_col}', Revenue='{revenue_col}' {'(calculated)' if calculated_revenue else ''}, Expense='{expense_col}'")
            
            # Calculate profit and margin (already have df_work)
            
            if expense_col:
                # Calculate actual profit and margin
                # FIXED: Prevent division by zero when revenue is 0
                revenue_numeric = pd.to_numeric(df_work[revenue_col], errors='coerce')
                expense_numeric = pd.to_numeric(df_work[expense_col], errors='coerce')
                df_work['Profit'] = revenue_numeric - expense_numeric
                # Use np.where to handle division by zero
                df_work['Profit_Margin_%'] = np.where(
                    revenue_numeric != 0,
                    (df_work['Profit'] / revenue_numeric) * 100,
                    0  # Set margin to 0 when revenue is 0
                )
            else:
                # Estimate margin without expense data (assume 20% average margin)
                print("   ⚠️ No expense column - estimating 20% default margin")
                df_work['Profit_Margin_%'] = 20.0
            
            # Group by product/category
            if expense_col:
                df_grouped = df_work.groupby(product_col, as_index=False).agg({
                    'Profit_Margin_%': 'mean',
                    revenue_col: 'sum'
                })
            else:
                df_grouped = df_work.groupby(product_col, as_index=False).agg({
                    revenue_col: 'sum'
                })
                df_grouped['Profit_Margin_%'] = 20.0
            
            # Sort by margin
            df_grouped = df_grouped.sort_values('Profit_Margin_%', ascending=False).head(15)
            
            # Handle NaN values
            df_grouped['Profit_Margin_%'] = df_grouped['Profit_Margin_%'].fillna(0)
            
            print(f"   ✅ Generated profit margin data for {len(df_grouped)} products/categories")
            print(f"   📊 Margin range: {df_grouped['Profit_Margin_%'].min():.1f}% to {df_grouped['Profit_Margin_%'].max():.1f}%")
            
            return FinanceChart(
                id='profit_margin_analysis',
                title='Profit Margin Analysis',
                type='bar',
                description='Profit margin % by product/category',
                icon='📊',
                domain='finance',
                data={
                    'x': df_grouped[product_col].tolist(),
                    'y': df_grouped['Profit_Margin_%'].tolist(),
                    'x_label': product_col,
                    'y_label': 'Profit Margin (%)'
                },
                config={
                    'maintainAspectRatio': False,
                    'responsive': True,
                    'color_scheme': 'profit_margin'  # Frontend can use green for high, red for low
                }
            )
            
        except Exception as e:
            print(f"   ❌ Error generating profit margin analysis: {e}")
            import traceback
            print(f"   📋 Traceback: {traceback.format_exc()}")
            return None
    
    def _generate_cash_flow_forecast(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[FinanceChart]:
        """
        Chart 3: Cash Flow Forecast
        Type: Line Forecast Chart
        Shows: Predicted net cash flow for next 30 days
        """
        try:
            print("   🔍 Looking for required columns...")
            
            # Find date column
            date_col = self._find_date_column(df, column_mapping)
            if not date_col:
                print("   ❌ No date column found")
                return None
            
            # Find revenue column
            revenue_col = self._find_column(df, column_mapping,
                patterns=self.finance_patterns['revenue'],
                canonical=['Revenue', 'Sales', 'Amount'])  # Check Revenue first
            
            # If no revenue column, try to calculate it from Unit_Price × Sales_Volume
            calculated_revenue = False
            df_work = df.copy()
            if not revenue_col:
                print("   ⚙️ No direct revenue column - attempting to calculate from Unit_Price × Sales_Volume")
                price_col = self._find_column(df, column_mapping,
                    patterns=['price', 'unit_price', 'cost', 'rate'],
                    canonical=['Price', 'Amount'])
                volume_col = self._find_column(df, column_mapping,
                    patterns=['sales_volume', 'quantity', 'volume', 'qty', 'units'],
                    canonical=['Sales', 'Quantity'])
                
                if price_col and volume_col:
                    # Clean price column (remove currency symbols and convert to float)
                    df_work[price_col] = df_work[price_col].astype(str).str.replace('$', '').str.replace(',', '')
                    df_work[price_col] = pd.to_numeric(df_work[price_col], errors='coerce')
                    df_work[volume_col] = pd.to_numeric(df_work[volume_col], errors='coerce')
                    
                    # Calculate revenue
                    df_work['Calculated_Revenue'] = df_work[price_col] * df_work[volume_col]
                    revenue_col = 'Calculated_Revenue'
                    calculated_revenue = True
                    print(f"   ✓ Calculated revenue from '{price_col}' × '{volume_col}'")
                else:
                    print(f"   ⚠️ Cannot calculate revenue - missing price or volume columns")
            
            # Find expense column
            expense_col = self._find_column(df, column_mapping,
                patterns=self.finance_patterns['expense'],
                canonical=['Expense', 'Finance', 'Cost'])  # Check Expense first
            
            if not revenue_col:
                print("   ❌ No revenue column found for cash flow")
                return None
            
            print(f"   📊 Using: Date='{date_col}', Revenue='{revenue_col}' {'(calculated)' if calculated_revenue else ''}, Expense='{expense_col}'")
            
            # Calculate net cash flow (already have df_work)
            df_work[date_col] = pd.to_datetime(df_work[date_col], errors='coerce')
            df_work = df_work.dropna(subset=[date_col])
            
            if len(df_work) == 0:
                print("   ❌ No valid dates")
                return None
            
            # Calculate net cash flow
            df_work['Net_Cash_Flow'] = pd.to_numeric(df_work[revenue_col], errors='coerce')
            if expense_col:
                df_work['Net_Cash_Flow'] -= pd.to_numeric(df_work[expense_col], errors='coerce')
            
            # Group by date and sum
            df_grouped = df_work.groupby(date_col, as_index=False)['Net_Cash_Flow'].sum()
            df_grouped = df_grouped.sort_values(date_col)
            
            # Simple linear forecast for next 30 days
            if len(df_grouped) >= 7:
                # Use last 7 days average for forecast
                recent_values = df_grouped['Net_Cash_Flow'].tail(7).values
                forecast_value = np.mean(recent_values)
                
                # Calculate trend
                x_values = np.arange(len(recent_values))
                trend_coef = np.polyfit(x_values, recent_values, 1)[0]
                
                # Generate forecast
                last_date = df_grouped[date_col].iloc[-1]
                forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30, freq='D')
                
                # Forecast with trend
                forecast_values = [forecast_value + (trend_coef * i) for i in range(1, 31)]
                
                # Combine historical and forecast
                historical_dates = df_grouped[date_col].dt.strftime('%Y-%m-%d').tolist()
                historical_values = df_grouped['Net_Cash_Flow'].tolist()
                
                forecast_dates_str = forecast_dates.strftime('%Y-%m-%d').tolist()
                
                all_dates = historical_dates + forecast_dates_str
                all_values = historical_values + forecast_values
                
                # Mark where forecast starts
                forecast_start_index = len(historical_dates)
                
                print(f"   ✅ Generated cash flow forecast: {len(historical_dates)} historical + 30 forecast days")
                print(f"   📊 Average net cash flow: ₱{forecast_value:,.0f}/day")
                
                return FinanceChart(
                    id='cash_flow_forecast',
                    title='Cash Flow Forecast (Next 30 Days)',
                    type='line',
                    description='Predicted net cash flow for planning',
                    icon='🔮',
                    domain='finance',
                    data={
                        'x': all_dates,
                        'y': all_values,
                        'forecast_start_index': forecast_start_index,
                        'x_label': 'Date',
                        'y_label': 'Net Cash Flow (₱)',
                        'chart_subtype': 'forecast'
                    },
                    config={
                        'maintainAspectRatio': False,
                        'responsive': True
                    }
                )
            else:
                print("   ⚠️ Insufficient data for forecasting (need at least 7 days)")
                return None
            
        except Exception as e:
            print(f"   ❌ Error generating cash flow forecast: {e}")
            import traceback
            print(f"   📋 Traceback: {traceback.format_exc()}")
            return None
    
    # ==================== OLD METHODS (KEEP FOR NOW) ====================
    
    def _generate_expense_breakdown(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[FinanceChart]:
        """Generate expense breakdown analysis."""
        try:
            # Look for expense/amount columns
            amount_col = None
            category_col = None
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == 'Sales' and orig_col in df.columns:
                    amount_col = orig_col
                elif canonical_col == 'Product' and orig_col in df.columns:
                    category_col = orig_col
            
            if not amount_col or not category_col:
                print("⚠️ Missing required columns for expense breakdown")
                return None
            
            # Group by category and sum amounts
            expense_data = df.groupby(category_col)[amount_col].sum().reset_index()
            expense_data = expense_data.sort_values(amount_col, ascending=False)
            
            # Take top 8 categories for pie chart
            expense_data = expense_data.head(8)
            
            return FinanceChart(
                id='expense_breakdown',
                title='Expense Breakdown Analysis',
                type='pie',
                description='Expense distribution by category',
                icon='💰',
                data={
                    'x': expense_data[category_col].tolist(),
                    'y': expense_data[amount_col].tolist()
                },
                config={'maintainAspectRatio': False, 'responsive': True}
            )
            
        except Exception as e:
            print(f"❌ Error generating expense breakdown: {e}")
            return None
    
    def _generate_cashflow_analysis(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[FinanceChart]:
        """Generate cash flow analysis."""
        try:
            amount_col = None
            date_col = None
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == 'Sales' and orig_col in df.columns:
                    amount_col = orig_col
                elif canonical_col == 'Date' and orig_col in df.columns:
                    date_col = orig_col
            
            if not amount_col or not date_col:
                print("⚠️ Missing required columns for cash flow analysis")
                return None
            
            # Convert date and group by month
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            monthly_cashflow = df.groupby(df[date_col].dt.to_period('M'))[amount_col].sum().reset_index()
            monthly_cashflow[date_col] = monthly_cashflow[date_col].astype(str)
            
            return FinanceChart(
                id='cash_flow_analysis',
                title='Cash Flow Analysis',
                type='line',
                description='Monthly cash flow trends',
                icon='💸',
                data={
                    'x': monthly_cashflow[date_col].tolist(),
                    'y': monthly_cashflow[amount_col].tolist()
                },
                config={'maintainAspectRatio': False, 'responsive': True}
            )
            
        except Exception as e:
            print(f"❌ Error generating cash flow analysis: {e}")
            return None
    
    def _generate_budget_analysis(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[FinanceChart]:
        """Generate budget vs actual analysis."""
        try:
            amount_col = None
            category_col = None
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == 'Sales' and orig_col in df.columns:
                    amount_col = orig_col
                elif canonical_col == 'Product' and orig_col in df.columns:
                    category_col = orig_col
            
            if not amount_col or not category_col:
                print("⚠️ Missing required columns for budget analysis")
                return None
            
            # Calculate actual expenses by category
            actual_data = df.groupby(category_col)[amount_col].sum().reset_index()
            
            # Simulate budget data (in real scenario, this would come from budget system)
            # Use deterministic calculation based on category hash for consistency
            def get_deterministic_budget_multiplier(category_name: str) -> float:
                """Generate consistent budget multiplier based on category name hash"""
                import hashlib
                hash_val = int(hashlib.md5(str(category_name).encode()).hexdigest()[:8], 16)
                # Map hash to range [0.8, 1.2] deterministically
                normalized = (hash_val % 1000) / 1000.0  # 0.0 to 0.999
                return 0.8 + (normalized * 0.4)  # 0.8 to 1.2
            
            actual_data['budget'] = actual_data.apply(
                lambda row: row[amount_col] * get_deterministic_budget_multiplier(row[category_col]),
                axis=1
            )
            
            # Calculate variance
            actual_data['variance'] = actual_data[amount_col] - actual_data['budget']
            actual_data = actual_data.sort_values('variance', ascending=True)
            
            return FinanceChart(
                id='budget_vs_actual',
                title='Budget vs Actual Report',
                type='bar',
                description='Budget variance by category',
                icon='📊',
                data={
                    'x': actual_data[category_col].tolist(),
                    'y': actual_data['variance'].tolist()
                },
                config={'maintainAspectRatio': False, 'responsive': True}
            )
            
        except Exception as e:
            print(f"❌ Error generating budget analysis: {e}")
            return None
    
    def _generate_profit_analysis(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[FinanceChart]:
        """Generate profit margin analysis."""
        try:
            amount_col = None
            category_col = None
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == 'Sales' and orig_col in df.columns:
                    amount_col = orig_col
                elif canonical_col == 'Product' and orig_col in df.columns:
                    category_col = orig_col
            
            if not amount_col or not category_col:
                print("⚠️ Missing required columns for profit analysis")
                return None
            
            # Calculate profit margins by category
            profit_data = df.groupby(category_col)[amount_col].sum().reset_index()
            
            # Simulate cost data and calculate margins (deterministic based on category)
            def get_deterministic_cost_multiplier(category_name: str) -> float:
                """Generate consistent cost multiplier based on category name hash"""
                import hashlib
                hash_val = int(hashlib.md5(str(category_name).encode()).hexdigest()[:8], 16)
                # Map hash to range [0.6, 0.8] deterministically
                normalized = (hash_val % 1000) / 1000.0  # 0.0 to 0.999
                return 0.6 + (normalized * 0.2)  # 0.6 to 0.8
            
            profit_data['cost'] = profit_data.apply(
                lambda row: row[amount_col] * get_deterministic_cost_multiplier(row[category_col]),
                axis=1
            )
            profit_data['profit'] = profit_data[amount_col] - profit_data['cost']
            # FIXED: Prevent division by zero when amount is 0
            profit_data['margin'] = np.where(
                profit_data[amount_col] != 0,
                (profit_data['profit'] / profit_data[amount_col]) * 100,
                0  # Set margin to 0 when amount is 0
            )
            
            profit_data = profit_data.sort_values('margin', ascending=False)
            
            return FinanceChart(
                id='profit_margin',
                title='Profit Margin Analysis',
                type='bar',
                description='Profit margins by category',
                icon='📈',
                data={
                    'x': profit_data[category_col].tolist(),
                    'y': profit_data['margin'].tolist()
                },
                config={'maintainAspectRatio': False, 'responsive': True}
            )
            
        except Exception as e:
            print(f"❌ Error generating profit analysis: {e}")
            return None
    
    def _generate_financial_forecast(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[FinanceChart]:
        """Generate financial forecasting."""
        try:
            amount_col = None
            date_col = None
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == 'Sales' and orig_col in df.columns:
                    amount_col = orig_col
                elif canonical_col == 'Date' and orig_col in df.columns:
                    date_col = orig_col
            
            if not amount_col or not date_col:
                print("⚠️ Missing required columns for financial forecast")
                return None
            
            # Convert date and group by month
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            monthly_data = df.groupby(df[date_col].dt.to_period('M'))[amount_col].sum().reset_index()
            monthly_data[date_col] = monthly_data[date_col].astype(str)
            
            # Simple trend-based forecast
            if len(monthly_data) >= 3:
                # Calculate trend
                values = monthly_data[amount_col].values
                trend = np.polyfit(range(len(values)), values, 1)[0]
                
                # Generate forecast for next 3 months
                last_value = values[-1]
                forecast_dates = []
                forecast_values = []
                
                for i in range(1, 4):
                    forecast_date = pd.to_datetime(monthly_data[date_col].iloc[-1]) + pd.DateOffset(months=i)
                    forecast_dates.append(forecast_date.strftime('%Y-%m'))
                    forecast_values.append(last_value + (trend * i))
                
                # Combine historical and forecast data
                all_dates = monthly_data[date_col].tolist() + forecast_dates
                all_values = monthly_data[amount_col].tolist() + forecast_values
                
                return FinanceChart(
                    id='financial_forecast',
                    title='Financial Forecasting',
                    type='line',
                    description='Financial trends with 3-month forecast',
                    icon='🔮',
                    data={
                        'x': all_dates,
                        'y': all_values
                    },
                    config={'maintainAspectRatio': False, 'responsive': True}
                )
            
        except Exception as e:
            print(f"❌ Error generating financial forecast: {e}")
            return None
