"""
TANAW Inventory Analytics Module
Provides inventory-specific analytics and visualizations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from chart_styling import TANAWChartStyling
from fallback_handler import TANAWFallbackHandler

@dataclass
class InventoryChart:
    id: str
    title: str
    type: str
    description: str
    brief_description: str
    icon: str
    data: Dict
    config: Dict

class TANAWInventoryAnalytics:
    """
    Inventory analytics engine for TANAW.
    Provides stock analysis, turnover rates, reorder points, and location insights.
    """
    
    def __init__(self):
        # Initialize chart styling
        self.styling = TANAWChartStyling()
        
        # Initialize fallback handler
        self.fallback_handler = TANAWFallbackHandler()
        
        self.analytics_config = {
            'stock_level_analysis': {
                'name': 'Stock Level Analysis',
                'description': 'Shows current stock levels across products',
                'icon': '📦',
                'type': 'bar'
            },
            'inventory_turnover': {
                'name': 'Inventory Turnover Report',
                'description': 'Analyzes how quickly inventory moves',
                'icon': '🔄',
                'type': 'bar'
            },
            'reorder_analysis': {
                'name': 'Reorder Point Analysis',
                'description': 'Identifies products needing reorder',
                'icon': '⚠️',
                'type': 'bar'
            },
            'location_analysis': {
                'name': 'Location-based Inventory',
                'description': 'Stock distribution across locations',
                'icon': '📍',
                'type': 'bar'
            },
            'supplier_performance': {
                'name': 'Supplier Performance Analysis',
                'description': 'Evaluates supplier delivery and quality',
                'icon': '🚚',
                'type': 'bar'
            }
        }
    
    def generate_analytics(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> List[InventoryChart]:
        """
        Generate inventory analytics charts.
        
        Args:
            df: Cleaned dataset
            column_mapping: Column mapping dictionary
            
        Returns:
            List of inventory analytics charts
        """
        print(f"📦 TANAW Inventory Analytics: Generating analytics for {df.shape[0]} records")
        
        charts = []
        
        # 1. Stock Level Analysis
        stock_chart = self._generate_stock_level_analysis(df, column_mapping)
        if stock_chart:
            charts.append(stock_chart)
        
        # 2. Inventory Turnover Analysis
        turnover_chart = self._generate_turnover_analysis(df, column_mapping)
        if turnover_chart:
            charts.append(turnover_chart)
        
        # 3. Reorder Point Analysis
        reorder_chart = self._generate_reorder_analysis(df, column_mapping)
        if reorder_chart:
            charts.append(reorder_chart)
        
        # 4. Location-based Analysis
        location_chart = self._generate_location_analysis(df, column_mapping)
        if location_chart:
            charts.append(location_chart)
        
        # 5. Supplier Performance Analysis
        supplier_chart = self._generate_supplier_analysis(df, column_mapping)
        if supplier_chart:
            charts.append(supplier_chart)
        
        print(f"✅ Generated {len(charts)} inventory analytics charts")
        return charts
    
    def _generate_stock_level_analysis(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[InventoryChart]:
        """Generate stock level analysis chart."""
        try:
            # Look for quantity/stock columns
            quantity_col = None
            product_col = None
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == 'Quantity' and orig_col in df.columns:
                    quantity_col = orig_col
                elif canonical_col == 'Product' and orig_col in df.columns:
                    product_col = orig_col
            
            if not quantity_col or not product_col:
                print("⚠️ Missing required columns for stock level analysis")
                return None
            
            # Group by product and sum quantities
            stock_data = df.groupby(product_col)[quantity_col].sum().reset_index()
            stock_data = stock_data.sort_values(quantity_col, ascending=True)
            
            # Take top 20 products to avoid overcrowding
            stock_data = stock_data.head(20)
            
            brief_description = "Displays current inventory levels for each product, sorted from lowest to highest stock. Shows the actual quantity on hand for each product. Use this to identify overstocked items (potential dead stock) and understocked items (potential stockouts). Helps optimize inventory investment and storage space allocation."
            
            return InventoryChart(
                id='stock_level_analysis',
                title='Stock Level Analysis',
                type='bar',
                description='Current stock levels across products',
                brief_description=brief_description,
                icon='📦',
                data={
                    'x': stock_data[product_col].tolist(),
                    'y': stock_data[quantity_col].tolist(),
                    'x_label': 'Product',
                    'y_label': 'Stock Level (units)'
                },
                config=self.styling.get_bar_chart_config(
                    chart_type="inventory",
                    x_label="Product",
                    y_label="Stock Level (units)"
                )
            )
            
        except Exception as e:
            print(f"❌ Error generating stock level analysis: {e}")
            # Try fallback methods
            return self.fallback_handler.handle_inventory_fallback(
                df, "stock_level_analysis", self._generate_stock_level_analysis,
                column_mapping=column_mapping
            )
    
    def _generate_turnover_analysis(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[InventoryChart]:
        """Generate inventory turnover analysis."""
        try:
            # Look for quantity and date columns
            quantity_col = None
            date_col = None
            product_col = None
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == 'Quantity' and orig_col in df.columns:
                    quantity_col = orig_col
                elif canonical_col == 'Date' and orig_col in df.columns:
                    date_col = orig_col
                elif canonical_col == 'Product' and orig_col in df.columns:
                    product_col = orig_col
            
            if not all([quantity_col, date_col, product_col]):
                print("⚠️ Missing required columns for turnover analysis")
                return None
            
            # Convert date column
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Calculate monthly turnover by product
            monthly_turnover = df.groupby([product_col, df[date_col].dt.to_period('M')])[quantity_col].sum().reset_index()
            turnover_by_product = monthly_turnover.groupby(product_col)[quantity_col].mean().reset_index()
            turnover_by_product = turnover_by_product.sort_values(quantity_col, ascending=False)
            
            # Take top 15 products
            turnover_by_product = turnover_by_product.head(15)
            
            brief_description = "Calculates the average monthly inventory movement for each product. Data is grouped by product and month, then averaged to show typical monthly turnover. Higher values indicate faster-moving inventory. Use this to optimize stock levels, identify slow-moving items, and improve cash flow management."
            
            return InventoryChart(
                id='inventory_turnover',
                title='Inventory Turnover Report',
                type='bar',
                description='Average monthly inventory turnover by product',
                brief_description=brief_description,
                icon='🔄',
                data={
                    'x': turnover_by_product[product_col].tolist(),
                    'y': turnover_by_product[quantity_col].tolist(),
                    'x_label': 'Product',
                    'y_label': 'Avg Monthly Volume (units)'
                },
                config=self.styling.get_bar_chart_config(
                    chart_type="inventory",
                    x_label="Product",
                    y_label="Avg Monthly Volume (units)"
                )
            )
            
        except Exception as e:
            print(f"❌ Error generating turnover analysis: {e}")
            return None
    
    def _generate_reorder_analysis(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[InventoryChart]:
        """Generate reorder point analysis."""
        try:
            quantity_col = None
            product_col = None
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == 'Quantity' and orig_col in df.columns:
                    quantity_col = orig_col
                elif canonical_col == 'Product' and orig_col in df.columns:
                    product_col = orig_col
            
            if not quantity_col or not product_col:
                print("⚠️ Missing required columns for reorder analysis")
                return None
            
            # Calculate current stock levels
            current_stock = df.groupby(product_col)[quantity_col].sum().reset_index()
            
            # Simple reorder logic: flag products with stock < 10% of average
            avg_stock = current_stock[quantity_col].mean()
            reorder_threshold = avg_stock * 0.1
            
            current_stock['needs_reorder'] = current_stock[quantity_col] < reorder_threshold
            reorder_products = current_stock[current_stock['needs_reorder']].sort_values(quantity_col)
            
            if len(reorder_products) == 0:
                # If no products need reorder, show lowest stock products
                reorder_products = current_stock.nsmallest(10, quantity_col)
            
            brief_description = "Identifies products that have fallen below the reorder threshold (10% of average stock level). Products are sorted by current stock level from lowest to highest. Use this to prioritize procurement decisions, prevent stockouts, and maintain optimal inventory levels for customer demand."
            
            return InventoryChart(
                id='reorder_analysis',
                title='Reorder Point Analysis',
                type='bar',
                description='Products that may need reordering',
                brief_description=brief_description,
                icon='⚠️',
                data={
                    'x': reorder_products[product_col].tolist(),
                    'y': reorder_products[quantity_col].tolist(),
                    'x_label': 'Product',
                    'y_label': 'Current Stock (units)'
                },
                config=self.styling.get_bar_chart_config(
                    chart_type="inventory",
                    x_label="Product",
                    y_label="Current Stock (units)"
                )
            )
            
        except Exception as e:
            print(f"❌ Error generating reorder analysis: {e}")
            return None
    
    def _generate_location_analysis(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[InventoryChart]:
        """Generate location-based inventory analysis."""
        try:
            quantity_col = None
            location_col = None
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == 'Quantity' and orig_col in df.columns:
                    quantity_col = orig_col
                elif canonical_col == 'Location' and orig_col in df.columns:
                    location_col = orig_col
            
            if not quantity_col or not location_col:
                print("⚠️ Missing required columns for location analysis")
                return None
            
            # Group by location
            location_data = df.groupby(location_col)[quantity_col].sum().reset_index()
            location_data = location_data.sort_values(quantity_col, ascending=False)
            
            brief_description = "Shows the total inventory quantity at each location, sorted from highest to lowest. Data is aggregated by summing all product quantities per location. Use this to identify locations with excess inventory (potential redistribution opportunities) and locations with insufficient stock (potential shortage risks). Helps optimize inventory distribution across your supply chain network."
            
            return InventoryChart(
                id='location_analysis',
                title='Location-based Inventory',
                type='bar',
                description='Stock distribution across locations',
                brief_description=brief_description,
                icon='📍',
                data={
                    'x': location_data[location_col].tolist(),
                    'y': location_data[quantity_col].tolist(),
                    'x_label': 'Location',
                    'y_label': 'Total Inventory (units)'
                },
                config=self.styling.get_bar_chart_config(
                    chart_type="inventory",
                    x_label="Location",
                    y_label="Total Inventory (units)"
                )
            )
            
        except Exception as e:
            print(f"❌ Error generating location analysis: {e}")
            return None
    
    def _generate_supplier_analysis(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Optional[InventoryChart]:
        """Generate supplier performance analysis."""
        try:
            # Look for supplier-related columns
            supplier_col = None
            quantity_col = None
            
            # Check for supplier columns
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['supplier', 'vendor', 'provider']):
                    supplier_col = col
                    break
            
            for orig_col, canonical_col in column_mapping.items():
                if canonical_col == 'Quantity' and orig_col in df.columns:
                    quantity_col = orig_col
            
            if not supplier_col or not quantity_col:
                print("⚠️ Missing supplier or quantity columns")
                return None
            
            # Group by supplier
            supplier_data = df.groupby(supplier_col)[quantity_col].sum().reset_index()
            supplier_data = supplier_data.sort_values(quantity_col, ascending=False)
            
            brief_description = "Analyzes the total volume supplied by each supplier, sorted from highest to lowest contribution. Data is aggregated by summing all quantities per supplier. Use this to evaluate supplier relationships, identify key suppliers, assess supply chain concentration risk, and inform supplier negotiation strategies. Helps optimize procurement decisions and supplier portfolio management."
            
            return InventoryChart(
                id='supplier_performance',
                title='Supplier Performance Analysis',
                type='bar',
                description='Volume by supplier',
                brief_description=brief_description,
                icon='🚚',
                data={
                    'x': supplier_data[supplier_col].tolist(),
                    'y': supplier_data[quantity_col].tolist(),
                    'x_label': 'Supplier',
                    'y_label': 'Supply Volume (units)'
                },
                config=self.styling.get_bar_chart_config(
                    chart_type="inventory",
                    x_label="Supplier",
                    y_label="Supply Volume (units)"
                )
            )
            
        except Exception as e:
            print(f"❌ Error generating supplier analysis: {e}")
            return None