"""
TANAW Customer Analytics Module
Provides customer-specific analytics and visualizations.
Updated: Now uses flexible column detection to work with various customer data formats.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class CustomerChart:
    id: str
    title: str
    type: str
    description: str
    icon: str
    domain: str  # NEW: Domain identifier ('customer')
    data: Dict
    config: Dict

class TANAWCustomerAnalytics:
    """
    Customer analytics engine for TANAW.
    Provides customer segmentation, purchase frequency, and lifetime value analysis.
    Updated: Uses flexible column detection for better compatibility.
    """
    
    def __init__(self):
        # Customer-specific column patterns
        self.customer_patterns = {
            'customer': ['customer', 'customer_id', 'customer_name', 'client', 'buyer', 'purchaser'],
            'customer_type': ['customer_type', 'customer_segment', 'segment', 'type', 'category'],
            'revenue': ['revenue', 'sales', 'income', 'amount', 'total'],
            'transaction': ['transaction', 'transaction_id', 'order', 'order_id', 'purchase']
        }
        
        self.analytics_config = {
            'customer_segmentation': {
                'name': 'Customer Segmentation Analysis',
                'description': 'Groups customers by behavior and value',
                'icon': '👥',
                'type': 'pie'
            },
            'lifetime_value': {
                'name': 'Customer Lifetime Value',
                'description': 'Analyzes customer value over time',
                'icon': '💎',
                'type': 'bar'
            },
            'churn_analysis': {
                'name': 'Churn Analysis',
                'description': 'Identifies customers at risk of churning',
                'icon': '⚠️',
                'type': 'bar'
            },
            'satisfaction_trends': {
                'name': 'Customer Satisfaction Trends',
                'description': 'Tracks satisfaction over time',
                'icon': '😊',
                'type': 'line'
            },
            'acquisition_analysis': {
                'name': 'Customer Acquisition Analysis',
                'description': 'Analyzes new customer acquisition',
                'icon': '🆕',
                'type': 'line'
            }
        }
    
    def generate_analytics(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> List[CustomerChart]:
        """
        Generate customer analytics charts.
        Now focuses on 3 key customer charts with flexible column detection.
        
        Args:
            df: Cleaned dataset
            column_mapping: Column mapping dictionary
            
        Returns:
            List of customer analytics charts
        """
        print(f"👥 TANAW Customer Analytics: Generating analytics for {df.shape[0]} records")
        print(f"📋 Available columns: {list(df.columns)}")
        print(f"🗺️ Column mapping: {column_mapping}")
        
        charts = []
        
        # Chart 1: Customer Segmentation (Pie Chart)
        print("\n👥 Chart 1: Generating Customer Segmentation...")
        segmentation_chart = self._generate_customer_segmentation(df, column_mapping)
        if segmentation_chart:
            charts.append(segmentation_chart)
            print(f"✅ Successfully generated Customer Segmentation")
        else:
            print(f"⚠️ Skipped Customer Segmentation (missing required columns)")
        
        # Chart 2: Purchase Frequency (Bar Chart)
        print("\n👥 Chart 2: Generating Purchase Frequency...")
        frequency_chart = self._generate_purchase_frequency(df, column_mapping)
        if frequency_chart:
            charts.append(frequency_chart)
            print(f"✅ Successfully generated Purchase Frequency")
        else:
            print(f"⚠️ Skipped Purchase Frequency (missing required columns)")
        
        # Chart 3: Lifetime Value (Bar Chart)
        print("\n👥 Chart 3: Generating Customer Lifetime Value...")
        clv_chart = self._generate_customer_lifetime_value(df, column_mapping)
        if clv_chart:
            charts.append(clv_chart)
            print(f"✅ Successfully generated Customer Lifetime Value")
        else:
            print(f"⚠️ Skipped Customer Lifetime Value (missing required columns)")
        
        print(f"\n✅ Generated {len(charts)} customer analytics charts")
        return charts
    
    # ==================== HELPER METHODS ====================
    
    def _find_column(self, df: pd.DataFrame, column_mapping: Dict[str, str], 
                    patterns: List[str], canonical: List[str] = None) -> Optional[str]:
        """
        Flexible column detection using patterns and canonical mappings.
        Same approach as Finance analytics for consistency.
        """
        # First, check if canonical column exists directly in dataframe
        if canonical:
            for canon_name in canonical:
                if canon_name in df.columns:
                    print(f"   ✓ Found column '{canon_name}' directly in DataFrame")
                    return canon_name
        
        # Second, check actual column names with pattern matching
        for col in df.columns:
            col_lower = str(col).lower().replace('_', ' ').replace('-', ' ')
            for pattern in patterns:
                if pattern.lower() in col_lower:
                    print(f"   ✓ Found column '{col}' matching pattern '{pattern}'")
                    return col
        
        # Third, check canonical mappings
        if canonical:
            for orig_col, canon_col in column_mapping.items():
                if canon_col in canonical and orig_col in df.columns:
                    print(f"   ✓ Found column '{orig_col}' via canonical mapping '{canon_col}'")
                    return orig_col
        
        print(f"   ✗ No column found for patterns: {patterns} or canonical: {canonical}")
        return None
    
    def _find_date_column(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[str]:
        """Find date column using patterns."""
        date_patterns = ['date', 'datetime', 'time', 'timestamp', 'fecha', 'day', 'period', 'transaction_date']
        return self._find_column(df, column_mapping,
            patterns=date_patterns,
            canonical=['Date'])
    
    # ==================== NEW CUSTOMER CHARTS ====================
    
    def _generate_customer_segmentation(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[CustomerChart]:
        """
        Chart 1: Customer Segmentation Analysis
        Type: Pie Chart
        Shows: Customer base composition (New, Returning, VIP)
        """
        try:
            print("   🔍 Looking for required columns...")
            
            # Try to find customer type/segment column
            customer_type_col = self._find_column(df, column_mapping,
                patterns=self.customer_patterns['customer_type'],
                canonical=['Customer'])
            
            # If no segment column, try to create segmentation from purchase behavior
            if not customer_type_col:
                print("   ⚠️ No customer_type column - creating segmentation from purchase data...")
                
                # Find customer ID column
                customer_col = self._find_column(df, column_mapping,
                    patterns=self.customer_patterns['customer'],
                    canonical=['Customer'])
                
                if not customer_col:
                    print("   ❌ No customer column found")
                    return None
                
                # Create basic segmentation based on purchase frequency
                purchase_counts = df[customer_col].value_counts()
                
                df_work = df.copy()
                df_work['Customer_Type'] = df_work[customer_col].map(
                    lambda x: 'VIP' if purchase_counts.get(x, 0) >= 5 else
                             'Returning' if purchase_counts.get(x, 0) >= 2 else
                             'New'
                )
                customer_type_col = 'Customer_Type'
            
            print(f"   📊 Using: Customer Type='{customer_type_col}'")
            
            # Count by segment
            df_work = df.copy() if customer_type_col not in df.columns else df
            segment_counts = df_work[customer_type_col].value_counts().reset_index()
            segment_counts.columns = ['segment', 'count']
            
            print(f"   ✅ Generated segmentation with {len(segment_counts)} segments")
            
            return CustomerChart(
                id='customer_segmentation',
                title='Customer Segmentation Analysis',
                type='pie',
                description='Customer base composition',
                icon='👥',
                domain='customer',
                data={
                    'labels': segment_counts['segment'].tolist(),
                    'values': segment_counts['count'].tolist()
                },
                config={'maintainAspectRatio': False, 'responsive': True}
            )
            
        except Exception as e:
            print(f"   ❌ Error generating customer segmentation: {e}")
            import traceback
            print(f"   📋 Traceback: {traceback.format_exc()}")
            return None
    
    def _generate_purchase_frequency(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[CustomerChart]:
        """
        Chart 2: Customer Purchase Frequency
        Type: Bar Chart
        Shows: Number of purchases per customer
        """
        try:
            print("   🔍 Looking for required columns...")
            
            # Find customer column
            customer_col = self._find_column(df, column_mapping,
                patterns=self.customer_patterns['customer'],
                canonical=['Customer'])
            
            if not customer_col:
                print("   ❌ No customer column found")
                return None
            
            print(f"   📊 Using: Customer='{customer_col}'")
            
            # Count purchases per customer
            purchase_freq = df.groupby(customer_col).size().reset_index(name='Purchase_Count')
            purchase_freq = purchase_freq.sort_values('Purchase_Count', ascending=False).head(20)
            
            print(f"   ✅ Generated purchase frequency for {len(purchase_freq)} customers")
            print(f"   📊 Frequency range: {purchase_freq['Purchase_Count'].min()} to {purchase_freq['Purchase_Count'].max()} purchases")
            
            return CustomerChart(
                id='purchase_frequency',
                title='Customer Purchase Frequency',
                type='bar',
                description='Number of purchases per customer',
                icon='🛒',
                domain='customer',
                data={
                    'x': purchase_freq[customer_col].tolist(),
                    'y': purchase_freq['Purchase_Count'].tolist(),
                    'x_label': 'Customer',
                    'y_label': 'Number of Purchases'
                },
                config={'maintainAspectRatio': False, 'responsive': True}
            )
            
        except Exception as e:
            print(f"   ❌ Error generating purchase frequency: {e}")
            import traceback
            print(f"   📋 Traceback: {traceback.format_exc()}")
            return None
    
    def _generate_customer_lifetime_value(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[CustomerChart]:
        """
        Chart 3: Customer Lifetime Value (CLV)
        Type: Bar Chart
        Shows: Total revenue contribution per customer
        """
        try:
            print("   🔍 Looking for required columns...")
            
            # Find customer column
            customer_col = self._find_column(df, column_mapping,
                patterns=self.customer_patterns['customer'],
                canonical=['Customer'])
            
            # Find revenue column
            revenue_col = self._find_column(df, column_mapping,
                patterns=self.customer_patterns['revenue'],
                canonical=['Sales', 'Amount'])
            
            if not customer_col or not revenue_col:
                print(f"   ❌ Missing required columns (customer: {customer_col}, revenue: {revenue_col})")
                return None
            
            print(f"   📊 Using: Customer='{customer_col}', Revenue='{revenue_col}'")
            
            # Calculate CLV (total revenue per customer)
            clv = df.groupby(customer_col)[revenue_col].sum().reset_index(name='CLV')
            clv = clv.sort_values('CLV', ascending=False).head(20)
            
            print(f"   ✅ Generated CLV for {len(clv)} customers")
            print(f"   📊 CLV range: ₱{clv['CLV'].min():,.0f} to ₱{clv['CLV'].max():,.0f}")
            
            return CustomerChart(
                id='customer_lifetime_value',
                title='Customer Lifetime Value (Top 20)',
                type='bar',
                description='Total revenue contribution per customer',
                icon='💎',
                domain='customer',
                data={
                    'x': clv[customer_col].tolist(),
                    'y': clv['CLV'].tolist(),
                    'x_label': 'Customer',
                    'y_label': 'Total Revenue (₱)'
                },
                config={'maintainAspectRatio': False, 'responsive': True}
            )
            
        except Exception as e:
            print(f"   ❌ Error generating CLV: {e}")
            import traceback
            print(f"   📋 Traceback: {traceback.format_exc()}")
            return None
    
    # ==================== OLD METHODS (KEEP FOR COMPATIBILITY) ====================
    
    def _generate_segmentation_analysis(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[CustomerChart]:
        """Generate customer segmentation analysis."""
        try:
            # Look for customer and sales columns
            customer_col = None
            amount_col = None
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == 'Sales' and orig_col in df.columns:
                    amount_col = orig_col
                elif canonical_col == 'Product' and orig_col in df.columns:
                    customer_col = orig_col
            
            if not amount_col or not customer_col:
                print("⚠️ Missing required columns for segmentation analysis")
                return None
            
            # Calculate customer value
            customer_value = df.groupby(customer_col)[amount_col].sum().reset_index()
            customer_value = customer_value.sort_values(amount_col, ascending=False)
            
            # Create segments based on value
            total_value = customer_value[amount_col].sum()
            customer_value['cumulative_pct'] = customer_value[amount_col].cumsum() / total_value * 100
            
            # Define segments
            def assign_segment(cum_pct):
                if cum_pct <= 20:
                    return 'High Value (20%)'
                elif cum_pct <= 50:
                    return 'Medium Value (30%)'
                else:
                    return 'Low Value (50%)'
            
            customer_value['segment'] = customer_value['cumulative_pct'].apply(assign_segment)
            segment_data = customer_value.groupby('segment')[amount_col].sum().reset_index()
            
            return CustomerChart(
                id='customer_segmentation',
                title='Customer Segmentation Analysis',
                type='pie',
                description='Customer distribution by value segments',
                icon='👥',
                data={
                    'x': segment_data['segment'].tolist(),
                    'y': segment_data[amount_col].tolist()
                },
                config={'maintainAspectRatio': False, 'responsive': True}
            )
            
        except Exception as e:
            print(f"❌ Error generating segmentation analysis: {e}")
            return None
    
    def _generate_ltv_analysis(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[CustomerChart]:
        """Generate customer lifetime value analysis."""
        try:
            customer_col = None
            amount_col = None
            date_col = None
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == 'Sales' and orig_col in df.columns:
                    amount_col = orig_col
                elif canonical_col == 'Product' and orig_col in df.columns:
                    customer_col = orig_col
                elif canonical_col == 'Date' and orig_col in df.columns:
                    date_col = orig_col
            
            if not all([customer_col, amount_col, date_col]):
                print("⚠️ Missing required columns for LTV analysis")
                return None
            
            # Convert date
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Calculate customer LTV
            customer_ltv = df.groupby(customer_col)[amount_col].sum().reset_index()
            customer_ltv = customer_ltv.sort_values(amount_col, ascending=False)
            
            # Take top 15 customers
            customer_ltv = customer_ltv.head(15)
            
            return CustomerChart(
                id='lifetime_value',
                title='Customer Lifetime Value',
                type='bar',
                description='Top customers by lifetime value',
                icon='💎',
                data={
                    'x': customer_ltv[customer_col].tolist(),
                    'y': customer_ltv[amount_col].tolist()
                },
                config={'maintainAspectRatio': False, 'responsive': True}
            )
            
        except Exception as e:
            print(f"❌ Error generating LTV analysis: {e}")
            return None
    
    def _generate_churn_analysis(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[CustomerChart]:
        """Generate churn analysis."""
        try:
            customer_col = None
            date_col = None
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == 'Product' and orig_col in df.columns:
                    customer_col = orig_col
                elif canonical_col == 'Date' and orig_col in df.columns:
                    date_col = orig_col
            
            if not customer_col or not date_col:
                print("⚠️ Missing required columns for churn analysis")
                return None
            
            # Convert date
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Calculate last activity date for each customer
            customer_activity = df.groupby(customer_col)[date_col].max().reset_index()
            
            # Define churn risk based on recency
            max_date = df[date_col].max()
            customer_activity['days_since_last_activity'] = (max_date - customer_activity[date_col]).dt.days
            
            # Categorize churn risk
            def categorize_churn_risk(days):
                if days <= 30:
                    return 'Low Risk'
                elif days <= 90:
                    return 'Medium Risk'
                else:
                    return 'High Risk'
            
            customer_activity['churn_risk'] = customer_activity['days_since_last_activity'].apply(categorize_churn_risk)
            churn_data = customer_activity['churn_risk'].value_counts().reset_index()
            
            return CustomerChart(
                id='churn_analysis',
                title='Churn Analysis',
                type='bar',
                description='Customer churn risk distribution',
                icon='⚠️',
                data={
                    'x': churn_data['churn_risk'].tolist(),
                    'y': churn_data['count'].tolist()
                },
                config={'maintainAspectRatio': False, 'responsive': True}
            )
            
        except Exception as e:
            print(f"❌ Error generating churn analysis: {e}")
            return None
    
    def _generate_satisfaction_analysis(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[CustomerChart]:
        """Generate satisfaction trends analysis."""
        try:
            date_col = None
            amount_col = None
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == 'Date' and orig_col in df.columns:
                    date_col = orig_col
                elif canonical_col == 'Sales' and orig_col in df.columns:
                    amount_col = orig_col
            
            if not date_col or not amount_col:
                print("⚠️ Missing required columns for satisfaction analysis")
                return None
            
            # Convert date
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Simulate satisfaction scores based on transaction amounts
            # Higher amounts = higher satisfaction
            df['satisfaction_score'] = np.clip(df[amount_col] / df[amount_col].mean() * 5, 1, 5)
            
            # Group by month and calculate average satisfaction
            monthly_satisfaction = df.groupby(df[date_col].dt.to_period('M'))['satisfaction_score'].mean().reset_index()
            monthly_satisfaction[date_col] = monthly_satisfaction[date_col].astype(str)
            
            return CustomerChart(
                id='satisfaction_trends',
                title='Customer Satisfaction Trends',
                type='line',
                description='Average satisfaction score over time',
                icon='😊',
                data={
                    'x': monthly_satisfaction[date_col].tolist(),
                    'y': monthly_satisfaction['satisfaction_score'].tolist()
                },
                config={'maintainAspectRatio': False, 'responsive': True}
            )
            
        except Exception as e:
            print(f"❌ Error generating satisfaction analysis: {e}")
            return None
    
    def _generate_acquisition_analysis(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[CustomerChart]:
        """Generate customer acquisition analysis."""
        try:
            customer_col = None
            date_col = None
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == 'Product' and orig_col in df.columns:
                    customer_col = orig_col
                elif canonical_col == 'Date' and orig_col in df.columns:
                    date_col = orig_col
            
            if not customer_col or not date_col:
                print("⚠️ Missing required columns for acquisition analysis")
                return None
            
            # Convert date
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Find first activity date for each customer
            customer_first_activity = df.groupby(customer_col)[date_col].min().reset_index()
            
            # Group by month to get new customer acquisition
            customer_first_activity['acquisition_month'] = customer_first_activity[date_col].dt.to_period('M')
            acquisition_data = customer_first_activity.groupby('acquisition_month').size().reset_index()
            acquisition_data.columns = [date_col, 'new_customers']
            acquisition_data[date_col] = acquisition_data[date_col].astype(str)
            
            return CustomerChart(
                id='acquisition_analysis',
                title='Customer Acquisition Analysis',
                type='line',
                description='New customer acquisition over time',
                icon='🆕',
                data={
                    'x': acquisition_data[date_col].tolist(),
                    'y': acquisition_data['new_customers'].tolist()
                },
                config={'maintainAspectRatio': False, 'responsive': True}
            )
            
        except Exception as e:
            print(f"❌ Error generating acquisition analysis: {e}")
            return None
