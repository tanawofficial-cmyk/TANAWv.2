"""
TANAW Bar Chart Generator
Phase 1: Focused Bar Chart Development
Handles: Product Performance, Location-based Sales, Category Analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
from chart_styling import TANAWChartStyling
from fallback_handler import TANAWFallbackHandler


class TANAWBarChartGenerator:
    """
    Dedicated Bar Chart Generator for TANAW
    Phase 1: Build solid foundation for bar charts only
    """
    
    def __init__(self):
        """Initialize bar chart generator with domain-agnostic configs"""
        # Initialize chart styling
        self.styling = TANAWChartStyling()
        
        # Initialize fallback handler
        self.fallback_handler = TANAWFallbackHandler()
        
        # Domain-agnostic base configs (will be customized per chart)
        self.chart_configs = {
            "item_performance": {
                "title": "Item Performance Analysis",
                "description": "Compares performance across different items",
                "icon": "📊",
                "sort_by": "value",
                "top_n": 10
            },
            "location_distribution": {
                "title": "Location Distribution Analysis", 
                "description": "Shows distribution and performance by location",
                "icon": "🗺️",
                "sort_by": "value",
                "top_n": 15
            },
            "category_analysis": {
                "title": "Category Analysis",
                "description": "Analyzes performance by category",
                "icon": "📦",
                "sort_by": "value",
                "top_n": 20
            }
        }
    
    def _generate_smart_labels(self, col_name: str) -> Dict[str, str]:
        """
        Generate domain-aware labels based on column name
        Works across Sales, Healthcare, Finance, Education, Inventory, etc.
        
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
            # Healthcare
            ("patient", "admission", "discharge"): (col_name, "count"),
            ("treatment", "procedure", "consultation"): (col_name, "count"),
            ("dosage", "medication"): (col_name, "mg"),
            # Education
            ("student", "enrollment", "attendance"): (col_name, "count"),
            ("grade", "score", "mark"): (col_name, "points"),
            ("course", "subject", "class"): (col_name, "count"),
            # Time-based
            ("hours", "duration", "time"): (col_name, "hours"),
            ("days", "weeks", "months"): (col_name, col_lower.split()[0]),
            # Percentage
            ("rate", "percentage", "ratio"): (col_name, "%"),
            # General numeric
            ("value", "measure", "metric"): (col_name, "units"),
        }
        
        # Check for matches
        for keywords, (label, unit) in label_map.items():
            if any(keyword in col_lower for keyword in keywords):
                return {"label": label, "unit": unit}
        
        # Default: use column name as-is
        return {"label": col_name, "unit": ""}
    
    def generate_product_performance(self, df: pd.DataFrame, product_col: str, sales_col: str) -> Optional[Dict[str, Any]]:
        """
        Generate Product Performance bar chart
        
        Args:
            df: DataFrame with product and sales data
            product_col: Column name for products
            sales_col: Column name for sales amounts
            
        Returns:
            Chart data dictionary or None if invalid
        """
        try:
            print(f"📊 Generating Product Performance chart")
            print(f"📊 Product column: {product_col}")
            print(f"📊 Sales column: {sales_col}")
            print(f"📊 DataFrame shape: {df.shape}")
            
            # FALLBACK: Handle None or empty DataFrame
            if df is None or df.empty:
                print("❌ DataFrame is None or empty")
                return None
            
            # Handle duplicate columns by creating a clean copy
            df_clean = df.copy()
            if df_clean.columns.duplicated().any():
                print(f"⚠️ Found duplicate columns, removing duplicates")
                df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]
                print(f"📊 Cleaned DataFrame shape: {df_clean.shape}")
            
            # FALLBACK: Handle missing columns gracefully
            if product_col not in df_clean.columns or sales_col not in df_clean.columns:
                print(f"❌ Missing required columns: {product_col}, {sales_col}")
                print(f"📊 Available columns: {list(df_clean.columns)}")
                return None
            
            # Clean and prepare data
            chart_df = df_clean[[product_col, sales_col]].copy()
            
            # FALLBACK: Handle all NaN data
            if chart_df.isnull().all().all():
                print(f"❌ All data is NaN - no valid data found")
                return None
            
            # FALLBACK: Handle data with too many NaN values
            nan_ratio = chart_df.isnull().sum().sum() / (len(chart_df) * len(chart_df.columns))
            if nan_ratio > 0.8:  # More than 80% NaN
                print(f"⚠️ High NaN ratio ({nan_ratio:.2%}) - attempting to clean data")
            
            chart_df = chart_df.dropna()
            
            if chart_df.empty:
                print(f"❌ No valid data after cleaning")
                return None
            
            # FALLBACK: Handle insufficient data after cleaning
            if len(chart_df) < 2:
                print(f"❌ Insufficient data after cleaning ({len(chart_df)} rows)")
                return None
            
            # Convert sales to numeric with error handling
            try:
                chart_df[sales_col] = pd.to_numeric(chart_df[sales_col], errors='coerce')
                chart_df = chart_df.dropna()
                
                if chart_df.empty:
                    print(f"❌ No numeric sales data found after conversion")
                    return None
                
                # FALLBACK: Check for all zero or constant values
                if chart_df[sales_col].nunique() <= 1:
                    print(f"⚠️ Sales data has no variation (all values are the same)")
                    # Still generate chart but with warning
                
            except Exception as e:
                print(f"❌ Error converting sales to numeric: {e}")
                return None
            
            # FALLBACK: Handle grouping errors
            try:
                # Group by product and sum sales
                grouped = chart_df.groupby(product_col)[sales_col].sum().reset_index()
                
                if grouped.empty:
                    print(f"❌ Grouping resulted in empty data")
                    return None
                
                # Sort by sales value (descending)
                grouped = grouped.sort_values(sales_col, ascending=False)
                
                # FALLBACK: Handle extreme values
                if grouped[sales_col].max() > 1e12:  # Very large numbers
                    print(f"⚠️ Detected very large sales values - applying scaling")
                    grouped[sales_col] = grouped[sales_col] / 1e6  # Scale down by millions
                
                # SMART FILTERING: Handle large datasets intelligently
                config = self.chart_configs["item_performance"]
                top_n = config["top_n"]
                
                # If dataset is large, implement smart filtering
                if len(grouped) > top_n:
                    print(f"📊 Large dataset detected: {len(grouped)} items, applying smart filtering")
                    
                    # Strategy 1: Take top performers (most important for business)
                    top_performers = grouped.head(top_n)
                    
                    # Strategy 2: If there are many low performers, show some for comparison
                    if len(grouped) > top_n * 2:
                        # Show top performers + some bottom performers for context
                        bottom_performers = grouped.tail(3)  # Show 3 worst performers
                        grouped = pd.concat([top_performers, bottom_performers]).drop_duplicates()
                        print(f"📊 Smart filtering: Showing top {len(top_performers)} + bottom 3 performers")
                    else:
                        grouped = top_performers
                        print(f"📊 Standard filtering: Showing top {top_n} performers")
                else:
                    print(f"📊 Dataset size manageable: {len(grouped)} items")
                
                print(f"📊 Generated data for {len(grouped)} products")
                if len(grouped) > 0:
                    print(f"📊 Top product: {grouped.iloc[0][product_col]} with {grouped.iloc[0][sales_col]:,.2f}")
                
            except Exception as e:
                print(f"❌ Error during grouping: {e}")
                return None
            
            # Generate dynamic labels based on column names (DOMAIN-AGNOSTIC)
            item_label = self._generate_smart_labels(product_col)
            value_label = self._generate_smart_labels(sales_col)
            
            # Create dynamic title based on columns (works for any domain)
            title = f"{item_label['label']} Comparison by {value_label['label']}"
            description = f"Compares {value_label['label'].lower()} across different {item_label['label'].lower()}s"
            
            # Create chart data
            chart_data = {
                "x": grouped[product_col].tolist(),
                "y": grouped[sales_col].tolist(),
                "x_label": "Product",
                "y_label": f"{value_label['label']}" + (f" ({value_label['unit']})" if value_label['unit'] else "")
            }
            
            # Brief description for user understanding
            brief_description = f"Compares total {value_label['label'].lower()} across all {item_label['label'].lower()}s to identify top and bottom performers. Data is aggregated by summing {value_label['label'].lower()} per {item_label['label'].lower()} and sorted from highest to lowest. Use this to optimize inventory allocation, marketing focus, and resource distribution."
            
            return {
                "id": f"{product_col.lower()}_comparison_analysis",
                "title": title,
                "type": "bar",
                "description": description,
                "brief_description": brief_description,
                "icon": "📊",
                "status": "success",
                "data": chart_data,
                "config": self.styling.get_bar_chart_config(
                    chart_type="sales",
                    x_label=chart_data.get("x_label", "Product"),
                    y_label=chart_data.get("y_label", "Sales")
                ),
                "meta": {
                    "total_items": len(grouped),
                    "top_item": grouped.iloc[0][product_col] if len(grouped) > 0 else None,
                    "top_value": float(grouped.iloc[0][sales_col]) if len(grouped) > 0 else 0,
                    "total_value": float(grouped[sales_col].sum()),
                    "item_column": product_col,
                    "value_column": sales_col
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating Product Performance chart: {e}")
            # Try fallback methods
            return self.fallback_handler.handle_bar_chart_fallback(
                df, "product_performance", self.generate_product_performance,
                product_col=product_col, sales_col=sales_col
            )
    
    def generate_regional_sales(self, df: pd.DataFrame, region_col: str, sales_col: str) -> Optional[Dict[str, Any]]:
        """
        Generate Location-based Sales bar chart
        
        Args:
            df: DataFrame with location and sales data
            region_col: Column name for locations
            sales_col: Column name for sales amounts
            
        Returns:
            Chart data dictionary or None if invalid
        """
        try:
            print(f"📊 Generating Location-based Sales chart")
            print(f"📊 Location column: {region_col}")
            print(f"📊 Sales column: {sales_col}")
            
            # FALLBACK: Handle None or empty DataFrame
            if df is None or df.empty:
                print("❌ DataFrame is None or empty")
                return None
            
            # Handle duplicate columns by creating a clean copy
            df_clean = df.copy()
            if df_clean.columns.duplicated().any():
                print(f"⚠️ Found duplicate columns, removing duplicates")
                df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]
                print(f"📊 Cleaned DataFrame shape: {df_clean.shape}")
            
            # FALLBACK: Handle missing columns gracefully
            if region_col not in df_clean.columns or sales_col not in df_clean.columns:
                print(f"❌ Missing required columns: {region_col}, {sales_col}")
                print(f"📊 Available columns: {list(df_clean.columns)}")
                return None
            
            # Clean and prepare data
            chart_df = df_clean[[region_col, sales_col]].copy()
            chart_df = chart_df.dropna()
            
            if chart_df.empty:
                print(f"❌ No valid data after cleaning")
                return None
            
            # Convert sales to numeric
            chart_df[sales_col] = pd.to_numeric(chart_df[sales_col], errors='coerce')
            chart_df = chart_df.dropna()
            
            if chart_df.empty:
                print(f"❌ No numeric sales data found")
                return None
            
            # Group by region and sum sales
            grouped = chart_df.groupby(region_col)[sales_col].sum().reset_index()
            
            # Sort by sales value (descending)
            grouped = grouped.sort_values(sales_col, ascending=False)
            
            # SMART FILTERING: Handle large location datasets
            config = self.chart_configs["location_distribution"]
            top_n = config["top_n"]
            
            # If dataset is large, implement smart filtering
            if len(grouped) > top_n:
                print(f"🗺️ Large location dataset detected: {len(grouped)} locations, applying smart filtering")
                
                # Strategy 1: Take top performing locations (most important for business)
                top_locations = grouped.head(top_n)
                
                # Strategy 2: If there are many low performing locations, show some for comparison
                if len(grouped) > top_n * 2:
                    # Show top locations + some bottom locations for context
                    bottom_locations = grouped.tail(3)  # Show 3 worst performing locations
                    grouped = pd.concat([top_locations, bottom_locations]).drop_duplicates()
                    print(f"🗺️ Smart filtering: Showing top {len(top_locations)} + bottom 3 locations")
                else:
                    grouped = top_locations
                    print(f"🗺️ Standard filtering: Showing top {top_n} locations")
            else:
                print(f"🗺️ Location dataset size manageable: {len(grouped)} locations")
            
            print(f"📊 Generated data for {len(grouped)} locations")
            
            # Generate dynamic labels based on column names (DOMAIN-AGNOSTIC)
            location_label = self._generate_smart_labels(region_col)
            value_label = self._generate_smart_labels(sales_col)
            
            # Create dynamic title based on columns (works for any domain)
            title = f"{location_label['label']} Distribution by {value_label['label']}"
            description = f"Shows distribution of {value_label['label'].lower()} across different {location_label['label'].lower()}s"
            
            # Create chart data
            chart_data = {
                "x": grouped[region_col].tolist(),
                "y": grouped[sales_col].tolist(),
                "x_label": "Location",
                "y_label": f"{value_label['label']}" + (f" ({value_label['unit']})" if value_label['unit'] else "")
            }
            
            # Brief description for user understanding
            brief_description = f"Shows {value_label['label'].lower()} distribution across different locations (branches, regions, cities, etc.). Data is aggregated by summing all {value_label['label'].lower()} per location and sorted by performance. Use this to identify top-performing markets, plan geographic expansion, and optimize resource allocation across locations."
            
            return {
                "id": f"{region_col.lower()}_distribution_analysis",
                "title": title,
                "type": "bar",
                "description": description,
                "brief_description": brief_description,
                "icon": "🗺️",
                "status": "success",
                "data": chart_data,
                "config": self.styling.get_bar_chart_config(
                    chart_type="sales",
                    x_label=chart_data.get("x_label", "Location"),
                    y_label=chart_data.get("y_label", "Sales")
                ),
                "meta": {
                    "total_locations": len(grouped),
                    "top_location": grouped.iloc[0][region_col] if len(grouped) > 0 else None,
                    "top_value": float(grouped.iloc[0][sales_col]) if len(grouped) > 0 else 0,
                    "total_value": float(grouped[sales_col].sum()),
                    "location_column": region_col,
                    "value_column": sales_col
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating Location-based Sales chart: {e}")
            # Try fallback methods
            return self.fallback_handler.handle_bar_chart_fallback(
                df, "regional_sales", self.generate_regional_sales,
                region_col=region_col, sales_col=sales_col
            )
    
    def can_generate_chart(self, df: pd.DataFrame, chart_type: str) -> Dict[str, Any]:
        """
        Check if bar chart can be generated with available data
        
        Args:
            df: DataFrame to analyze
            chart_type: Type of chart to check ('product_performance', 'regional_sales')
            
        Returns:
            Dictionary with readiness status and missing columns
        """
        try:
            if chart_type == "product_performance":
                required_cols = ["Product", "Sales"]
                available_cols = []
                
                # Check for Product column - PRIORITIZE ACTUAL PRODUCT NAMES over categories
                # Priority 1: Actual product name columns (highest priority)
                product_name_candidates = [
                    "Product", "Product_Name", "ProductName", "Product Name", "product_name",
                    "Item", "Item_Name", "ItemName", "Item Name", "item_name",
                    "SKU", "Product_Code", "ProductCode", "Code", "product_code",
                    "Name", "Product_Description", "ProductDescription", "Description"
                ]
                
                # Priority 2: Brand columns (medium priority)
                brand_candidates = [
                    "Brand", "Brand_Name", "BrandName", "Brand Name", "brand_name"
                ]
                
                # Priority 3: Category columns (lowest priority - only if no better option)
                category_candidates = [
                    "Category", "Category_Name", "CategoryName", "Category Name", "category_name"
                ]
                
                # Try to find the BEST product column - PRIORITY system
                product_col = None
                
                # PRIORITY 1: Use explicitly mapped "Product" column
                if self.column_mapping:
                    for original_col, canonical_type in self.column_mapping.items():
                        if canonical_type == "Product" and original_col in df.columns:
                            product_col = original_col
                            print(f"✅ Using mapped Product column: {original_col}")
                            break
                
                # PRIORITY 2: Check for canonical "Product" column (after mapping)
                if not product_col and "Product" in df.columns:
                    product_col = "Product"
                    print(f"✅ Using canonical Product column")
                
                # PRIORITY 3: Flexible search (only if no explicit mapping)
                if not product_col:
                    print("🔍 No Product mapping found, attempting flexible search...")
                    # First, try actual product name columns
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in product_name_candidates):
                        product_col = col
                        print(f"✅ Found product name column: {col}")
                        break
                
                # If no product name found, try brand columns
                if not product_col:
                    for col in df.columns:
                        col_lower = col.lower().replace(" ", "_").replace("-", "_")
                        if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                               for candidate in brand_candidates):
                            product_col = col
                            print(f"⚠️ Using brand column as product: {col}")
                            break
                
                # Last resort: use category columns (but warn user)
                if not product_col:
                    for col in df.columns:
                        col_lower = col.lower().replace(" ", "_").replace("-", "_")
                        if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                               for candidate in category_candidates):
                            product_col = col
                            print(f"⚠️ WARNING: Using category column as product (may show categories instead of specific products): {col}")
                            break
                
                if product_col:
                    available_cols.append(product_col)
                    print(f"✅ Selected product column: {product_col}")
                else:
                    print("❌ No suitable product column found")
                
                # Check for Sales column - 3-TIER PRIORITIZATION
                sales_col = None
                
                # PRIORITY 1: Use explicitly mapped "Sales" column
                if self.column_mapping:
                    for original_col, canonical_type in self.column_mapping.items():
                        if canonical_type == "Sales" and original_col in df.columns:
                            # Validate numeric
                            try:
                                numeric_data = pd.to_numeric(df[original_col], errors='coerce')
                                if numeric_data.notna().sum() / len(df) >= 0.5:
                                    sales_col = original_col
                                    available_cols.append(sales_col)
                                    print(f"✅ Using mapped Sales column: {original_col}")
                                    break
                            except:
                                pass
                
                # PRIORITY 2: Check for canonical "Sales" column (after mapping)
                if not sales_col and "Sales" in df.columns:
                    try:
                        numeric_data = pd.to_numeric(df["Sales"], errors='coerce')
                        if numeric_data.notna().sum() / len(df) >= 0.5:
                            sales_col = "Sales"
                            available_cols.append(sales_col)
                            print(f"✅ Using canonical Sales column")
                    except:
                        pass
                
                # PRIORITY 3: Flexible search (only if no mapping exists)
                if not sales_col:
                    print("🔍 No Sales mapping found, attempting flexible search...")
                sales_candidates = [
                    # Mapped names (highest priority)
                    "Sales", "Amount", "Revenue", "Value", "Total", "Sum",
                    # Common variations
                    "Sales_Amount", "SalesAmount", "Sales Amount", "sales_amount",
                    "Amount", "Total_Amount", "TotalAmount", "Total Amount", "amount",
                    "Revenue", "Total_Revenue", "TotalRevenue", "Total Revenue", "revenue",
                    "Value", "Total_Value", "TotalValue", "Total Value", "value",
                    # Price variations
                    "Price", "Unit_Price", "UnitPrice", "Unit Price", "unit_price",
                    "List_Price", "ListPrice", "List Price", "list_price",
                    # Cost variations
                    "Cost", "Total_Cost", "TotalCost", "Total Cost", "total_cost",
                    # Profit variations
                    "Profit", "Total_Profit", "TotalProfit", "Total Profit", "profit",
                    "Margin", "Total_Margin", "TotalMargin", "Total Margin", "margin"
                ]
                
                # Flexible matching - check for partial matches too AND validate numeric data
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in sales_candidates):
                        # Validate that this column contains numeric data
                        try:
                            # Check if column can be converted to numeric
                            numeric_data = pd.to_numeric(df[col], errors='coerce')
                            non_null_count = numeric_data.notna().sum()
                            total_count = len(df)
                            
                            # Only accept if at least 50% of values are numeric
                            if non_null_count / total_count >= 0.5:
                                sales_col = col
                                available_cols.append(col)
                                print(f"✅ Found valid sales column: {col} ({non_null_count}/{total_count} numeric values)")
                                break
                            else:
                                print(f"⚠️ Skipping {col} - not enough numeric data ({non_null_count}/{total_count})")
                        except Exception as e:
                            print(f"⚠️ Skipping {col} - validation failed: {e}")
                            continue
                
                # We're ready if we found both a product column and a sales column
                ready = len(available_cols) >= 2
                missing_cols = [] if ready else ["Product column", "Sales column"]
                
                return {
                    "ready": ready,
                    "available_columns": available_cols,
                    "missing_columns": missing_cols,
                    "chart_type": "bar",
                    "description": "Product performance comparison"
                }
                
            elif chart_type == "regional_sales":
                available_cols = []
                
                # PRIORITY 1: Check if "Region" was explicitly mapped
                location_col = None
                
                if self.column_mapping:
                    # Look for columns mapped to "Region" in the mapping
                    for original_col, canonical_type in self.column_mapping.items():
                        if canonical_type == "Region" and original_col in df.columns:
                            location_col = original_col
                            print(f"✅ Using mapped Region column: {original_col}")
                            break
                
                # PRIORITY 2: Check for canonical "Region" column (after mapping)
                if not location_col and "Region" in df.columns:
                    location_col = "Region"
                    print(f"✅ Using canonical Region column")
                
                # PRIORITY 3: Flexible search (only if no mapping exists)
                if not location_col:
                    print("🔍 No Region mapping found, attempting flexible location search...")
                region_candidates = [
                        "Location", "Branch", "Area", "City", "State", "Country",
                        "Territory", "Zone", "District", "Warehouse", "Store", "Outlet"
                    ]
                    
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    
                        # Skip product-related columns
                    if any(product_indicator in col_lower for product_indicator in [
                        "product", "item", "name", "sku", "brand", "category"
                    ]):
                        print(f"⚠️ Skipping {col} - appears to be product name, not location")
                        continue
                    
                        # Skip numeric-only columns (like "Count", "Number", etc.)
                        if col_lower in ["count", "number", "id", "qty", "quantity", "units"]:
                            print(f"⚠️ Skipping {col} - numeric identifier, not location")
                            continue
                        
                        if any(candidate.lower() in col_lower or col_lower in candidate.lower() 
                           for candidate in region_candidates):
                        location_col = col
                            print(f"✅ Found location column via flexible search: {col}")
                        break
                
                if location_col:
                    available_cols.append(location_col)
                else:
                    print("❌ No suitable location column found - skipping regional sales chart")
                    return {
                        "ready": False,
                        "available_columns": [],
                        "missing_columns": ["Location column"],
                        "chart_type": "bar",
                        "description": "Regional sales requires actual location data"
                    }
                
                # Check for Sales column - 3-TIER PRIORITIZATION
                sales_col = None
                
                # PRIORITY 1: Use explicitly mapped "Sales" column
                if self.column_mapping:
                    for original_col, canonical_type in self.column_mapping.items():
                        if canonical_type == "Sales" and original_col in df.columns:
                            # Validate numeric
                            try:
                                numeric_data = pd.to_numeric(df[original_col], errors='coerce')
                                if numeric_data.notna().sum() / len(df) >= 0.5:
                                    sales_col = original_col
                                    available_cols.append(sales_col)
                                    print(f"✅ Using mapped Sales column: {original_col}")
                                    break
                            except:
                                pass
                
                # PRIORITY 2: Check for canonical "Sales" column (after mapping)
                if not sales_col and "Sales" in df.columns:
                    try:
                        numeric_data = pd.to_numeric(df["Sales"], errors='coerce')
                        if numeric_data.notna().sum() / len(df) >= 0.5:
                            sales_col = "Sales"
                            available_cols.append(sales_col)
                            print(f"✅ Using canonical Sales column")
                    except:
                        pass
                
                # PRIORITY 3: Flexible search (only if no mapping exists)
                if not sales_col:
                    print("🔍 No Sales mapping found, attempting flexible search...")
                sales_candidates = [
                    # Mapped names (highest priority)
                    "Sales", "Amount", "Revenue", "Value", "Total", "Sum",
                    # Common variations
                    "Sales_Amount", "SalesAmount", "Sales Amount", "sales_amount",
                    "Amount", "Total_Amount", "TotalAmount", "Total Amount", "amount",
                    "Revenue", "Total_Revenue", "TotalRevenue", "Total Revenue", "revenue",
                    "Value", "Total_Value", "TotalValue", "Total Value", "value",
                    # Price variations
                    "Price", "Unit_Price", "UnitPrice", "Unit Price", "unit_price",
                    "List_Price", "ListPrice", "List Price", "list_price",
                    # Cost variations
                    "Cost", "Total_Cost", "TotalCost", "Total Cost", "total_cost",
                    # Profit variations
                    "Profit", "Total_Profit", "TotalProfit", "Total Profit", "profit",
                    "Margin", "Total_Margin", "TotalMargin", "Total Margin", "margin"
                ]
                
                # Flexible matching - check for partial matches too AND validate numeric data
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in sales_candidates):
                        # Validate that this column contains numeric data
                        try:
                            # Check if column can be converted to numeric
                            numeric_data = pd.to_numeric(df[col], errors='coerce')
                            non_null_count = numeric_data.notna().sum()
                            total_count = len(df)
                            
                            # Only accept if at least 50% of values are numeric
                            if non_null_count / total_count >= 0.5:
                                sales_col = col
                                available_cols.append(col)
                                print(f"✅ Found valid sales column: {col} ({non_null_count}/{total_count} numeric values)")
                                break
                            else:
                                print(f"⚠️ Skipping {col} - not enough numeric data ({non_null_count}/{total_count})")
                        except Exception as e:
                            print(f"⚠️ Skipping {col} - validation failed: {e}")
                            continue
                
                # We're ready if we found both a location column and a sales column
                ready = len(available_cols) >= 2
                missing_cols = [] if ready else ["Location column", "Sales column"]
                
                return {
                    "ready": ready,
                    "available_columns": available_cols,
                    "missing_columns": missing_cols,
                    "chart_type": "bar",
                    "description": "Location-based sales comparison"
                }
            
            elif chart_type == "expense_distribution":
                available_cols = []
                
                # Check for Category/Department column
                category_candidates = [
                    "Category", "Department", "Expense_Category", "ExpenseCategory",
                    "Type", "Expense_Type", "ExpenseType", "Classification",
                    "Account", "Account_Name", "AccountName"
                ]
                
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    # Check main column
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in category_candidates):
                        available_cols.append(col)
                        break
                    # Check additional columns (preserved from mapping)
                    elif col.endswith("_additional") and any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in category_candidates):
                        available_cols.append(col)
                        break
                
                # Check for Expense column
                expense_candidates = [
                    "Expense", "Expense_Amount", "ExpenseAmount", "Amount",
                    "Cost", "Total_Cost", "TotalCost", "Spending",
                    "Debit", "Payment", "Payout"
                ]
                
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    # Check main column
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in expense_candidates):
                        # Validate numeric
                        try:
                            numeric_data = pd.to_numeric(df[col], errors='coerce')
                            if numeric_data.notna().sum() / len(df) >= 0.5:
                                available_cols.append(col)
                                break
                        except:
                            continue
                    # Check additional columns (preserved from mapping)
                    elif col.endswith("_additional") and any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in expense_candidates):
                        # Validate numeric
                        try:
                            numeric_data = pd.to_numeric(df[col], errors='coerce')
                            if numeric_data.notna().sum() / len(df) >= 0.5:
                                available_cols.append(col)
                                break
                        except:
                            continue
                
                ready = len(available_cols) >= 2
                missing_cols = [] if ready else ["Category column", "Expense column"]
                
                return {
                    "ready": ready,
                    "available_columns": available_cols,
                    "missing_columns": missing_cols,
                    "chart_type": "bar",
                    "description": "Expense distribution by category"
                }
            
            elif chart_type == "profit_margin":
                available_cols = []
                
                # Check for Item column (Product, Location, Account, etc.)
                item_candidates = [
                    "Product", "Item", "Account", "Location", "Category",
                    "Product_Name", "ProductName", "Item_Name", "ItemName",
                    "Account_Name", "AccountName"
                ]
                
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in item_candidates):
                        available_cols.append(col)
                        break
                
                # Check for Margin column (LEVEL 1: Direct margin column)
                margin_candidates = [
                    "Margin", "Profit_Margin", "ProfitMargin", "Margin_%",
                    "Profit_Percentage", "ProfitPercentage", "ROI", "Return"
                ]
                
                margin_col_found = None
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in margin_candidates):
                        try:
                            numeric_data = pd.to_numeric(df[col], errors='coerce')
                            if numeric_data.notna().sum() / len(df) >= 0.5:
                                margin_col_found = col
                                available_cols.append(col)
                                break
                        except:
                            continue
                
                # If margin column found, we're ready
                if margin_col_found:
                    ready = True
                    missing_cols = []
                else:
                    # LEVEL 2: Check for Profit and Revenue columns for calculation
                    profit_col_found = None
                    revenue_col_found = None
                    
                    profit_candidates = ["Profit", "Net_Profit", "NetProfit", "Gross_Profit"]
                    revenue_candidates = ["Revenue", "Sales", "Income", "Total_Revenue"]
                    
                    for col in df.columns:
                        col_lower = col.lower().replace(" ", "_").replace("-", "_")
                        # Check for Profit
                        if not profit_col_found and any(candidate.lower().replace(" ", "_") in col_lower 
                                                        for candidate in profit_candidates):
                            try:
                                numeric_data = pd.to_numeric(df[col], errors='coerce')
                                if numeric_data.notna().sum() / len(df) >= 0.5:
                                    profit_col_found = col
                                    available_cols.append(col)
                            except:
                                continue
                        
                        # Check for Revenue
                        if not revenue_col_found and any(candidate.lower().replace(" ", "_") in col_lower 
                                                         for candidate in revenue_candidates):
                            try:
                                numeric_data = pd.to_numeric(df[col], errors='coerce')
                                if numeric_data.notna().sum() / len(df) >= 0.5:
                                    revenue_col_found = col
                                    available_cols.append(col)
                            except:
                                continue
                    
                    # Ready if we have Item + (Margin OR (Profit + Revenue))
                    # Need at least: Item column + either margin OR both profit+revenue
                    has_item = len(available_cols) >= 1
                    has_margin = margin_col_found is not None
                    has_components = profit_col_found is not None and revenue_col_found is not None
                    
                    ready = has_item and (has_margin or has_components)
                    
                    missing_cols = []
                    if not ready:
                        if not has_item:
                            missing_cols.append("Item/Product column")
                        if not has_margin and not has_components:
                            missing_cols.append("Margin% column OR (Profit + Revenue columns)")
                
                return {
                    "ready": ready,
                    "available_columns": available_cols,
                    "missing_columns": missing_cols,
                    "chart_type": "bar",
                    "description": "Profit margin comparison"
                }
            
            elif chart_type == "stock_level_overview":
                available_cols = []
                
                # PRIORITY 1: Use explicitly mapped "Product" column
                item_col = None
                
                if self.column_mapping:
                    for original_col, canonical_type in self.column_mapping.items():
                        if canonical_type == "Product" and original_col in df.columns:
                            item_col = original_col
                            print(f"✅ Using mapped Product column for stock: {original_col}")
                            break
                
                # PRIORITY 2: Check for canonical "Product" column
                if not item_col and "Product" in df.columns:
                    item_col = "Product"
                    print(f"✅ Using canonical Product column for stock")
                
                # PRIORITY 3: Flexible search (only if no mapping)
                if not item_col:
                    print("🔍 No Product mapping, attempting flexible item search...")
                item_candidates = [
                        "Item", "Product", "SKU", "Item_Code", "Product_Name", "Item_Name"
                ]
                
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    # Skip customer-related columns
                    if any(customer_kw in col_lower for customer_kw in ["customer", "client", "buyer", "person"]):
                        print(f"⚠️ Skipping {col} - appears to be customer name, not product")
                        continue
                    
                    if any(candidate.lower() in col_lower or col_lower in candidate.lower() 
                           for candidate in item_candidates):
                        item_col = col
                        print(f"✅ Found item column via flexible search: {col}")
                        break
                
                if item_col:
                    available_cols.append(item_col)
                else:
                    print("❌ No suitable item column found")
                
                # Check for Stock/Quantity column
                stock_candidates = [
                    "Stock", "Stock_Level", "StockLevel", "Quantity", "Qty",
                    "Units", "On_Hand", "OnHand", "Available", "Inventory",
                    "Current_Stock", "CurrentStock", "In_Stock", "InStock"
                ]
                
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in stock_candidates):
                        # Validate numeric
                        try:
                            numeric_data = pd.to_numeric(df[col], errors='coerce')
                            if numeric_data.notna().sum() / len(df) >= 0.5:
                                available_cols.append(col)
                                break
                        except:
                            continue
                
                ready = len(available_cols) >= 2
                missing_cols = [] if ready else ["Item column", "Stock column"]
                
                return {
                    "ready": ready,
                    "available_columns": available_cols,
                    "missing_columns": missing_cols,
                    "chart_type": "bar",
                    "description": "Stock level overview"
                }
            
            elif chart_type == "reorder_status":
                available_cols = []
                
                # PRIORITY 1: Use explicitly mapped "Product" column
                item_col = None
                
                if self.column_mapping:
                    for original_col, canonical_type in self.column_mapping.items():
                        if canonical_type == "Product" and original_col in df.columns:
                            item_col = original_col
                            print(f"✅ Using mapped Product column for reorder: {original_col}")
                            break
                
                # PRIORITY 2: Check for canonical "Product" column
                if not item_col and "Product" in df.columns:
                    item_col = "Product"
                    print(f"✅ Using canonical Product column for reorder")
                
                # PRIORITY 3: Flexible search (only if no mapping)
                if not item_col:
                    print("🔍 No Product mapping, attempting flexible item search...")
                item_candidates = [
                        "Item", "Product", "SKU", "Item_Code", "Product_Name", "Item_Name"
                ]
                
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    # Skip customer-related columns
                    if any(customer_kw in col_lower for customer_kw in ["customer", "client", "buyer", "person"]):
                        print(f"⚠️ Skipping {col} - appears to be customer name, not product")
                        continue
                    
                    if any(candidate.lower() in col_lower or col_lower in candidate.lower() 
                           for candidate in item_candidates):
                        item_col = col
                        print(f"✅ Found item column via flexible search: {col}")
                        break
                
                if item_col:
                    available_cols.append(item_col)
                else:
                    print("❌ No suitable item column found")
                
                # Check for Stock column
                stock_candidates = [
                    "Stock", "Stock_Level", "StockLevel", "Quantity", "Qty",
                    "Current_Stock", "CurrentStock", "On_Hand", "OnHand"
                ]
                
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in stock_candidates):
                        try:
                            numeric_data = pd.to_numeric(df[col], errors='coerce')
                            if numeric_data.notna().sum() / len(df) >= 0.5:
                                available_cols.append(col)
                                break
                        except:
                            continue
                
                # Optional: Check for Reorder Point column
                reorder_candidates = [
                    "Reorder", "Reorder_Point", "ReorderPoint", "Reorder_Level",
                    "Minimum", "Min_Stock", "MinStock", "Threshold", "Safety_Stock"
                ]
                
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    if any(candidate.lower().replace(" ", "_") in col_lower or col_lower in candidate.lower().replace(" ", "_") 
                           for candidate in reorder_candidates):
                        try:
                            numeric_data = pd.to_numeric(df[col], errors='coerce')
                            if numeric_data.notna().sum() / len(df) >= 0.5:
                                available_cols.append(col)
                                break
                        except:
                            continue
                
                ready = len(available_cols) >= 2  # At minimum need item + stock
                missing_cols = [] if ready else ["Item column", "Stock column"]
                
                return {
                    "ready": ready,
                    "available_columns": available_cols,
                    "missing_columns": missing_cols,
                    "chart_type": "bar",
                    "description": "Reorder status analysis"
                }
            
            return {
                "ready": False,
                "available_columns": [],
                "missing_columns": ["Unknown chart type"],
                "chart_type": "bar",
                "description": "Unknown chart type"
            }
            
        except Exception as e:
            print(f"❌ Error checking chart readiness: {e}")
            return {
                "ready": False,
                "available_columns": [],
                "missing_columns": [f"Error: {str(e)}"],
                "chart_type": "bar",
                "description": "Error checking readiness"
            }
    
    def generate_all_bar_charts(self, df: pd.DataFrame, column_mapping: Dict[str, str] = None, context: str = "UNKNOWN") -> List[Dict[str, Any]]:
        """
        Generate all possible bar charts for the given dataset with comprehensive fallbacks
        
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
        
        print(f"📊 Bar Chart Generator - Context: {context}")
        
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
        
        # FALLBACK 4: Handle datasets with too few rows
        if len(df) < 2:
            print("⚠️ Dataset has less than 2 rows - insufficient data for charts")
            return []
        
        # FALLBACK 5: Handle datasets with too many columns (potential memory issues)
        if len(df.columns) > 1000:
            print("⚠️ Dataset has too many columns - sampling for performance")
            df = df.iloc[:, :100]  # Keep first 100 columns
        
        print(f"🔍 Dataset validation passed: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"🎯 Generating bar charts based on context: {context}")
        
        # CONTEXT-AWARE CHART GENERATION
        # Filter charts based on detected business context to avoid misleading analytics
        # SALES context: Generate product/regional sales charts
        # INVENTORY context: Generate stock level/reorder charts
        # MIXED/UNKNOWN: Generate all charts
        
        # Try Product Performance with safe wrapper (SALES charts)
        if context in ["SALES", "MIXED", "UNKNOWN"]:
            try:
                product_check = self.can_generate_chart(df, "product_performance")
                print(f"🔍 Product Performance check: {product_check}")
                if product_check["ready"] and len(product_check["available_columns"]) >= 2:
                    product_col = product_check["available_columns"][0]  # First available product column
                    sales_col = product_check["available_columns"][1]   # First available sales column
                    chart = self._safe_generate_chart("product_performance", df, product_col, sales_col)
                    if chart:
                        charts.append(chart)
                        print(f"✅ Generated Product Performance chart")
                    else:
                        print(f"❌ Product Performance chart generation failed")
                else:
                    print(f"⏭️ Product Performance not available: {product_check.get('missing_columns', [])}")
            except Exception as e:
                print(f"❌ Error checking Product Performance readiness: {e}")
        else:
            print(f"⏭️ Skipping Product Performance (context={context}, sales chart)")
        
        # Try Location-based Sales with safe wrapper (SALES charts)
        if context in ["SALES", "MIXED", "UNKNOWN"]:
            try:
                regional_check = self.can_generate_chart(df, "regional_sales")
                print(f"🔍 Location-based Sales check: {regional_check}")
                if regional_check["ready"] and len(regional_check["available_columns"]) >= 2:
                    region_col = regional_check["available_columns"][0]  # First available location column
                    sales_col = regional_check["available_columns"][1]   # First available sales column
                    chart = self._safe_generate_chart("regional_sales", df, region_col, sales_col)
                    if chart:
                        charts.append(chart)
                        print(f"✅ Generated Location-based Sales chart")
                    else:
                        print(f"❌ Location-based Sales chart generation failed")
                else:
                    print(f"⏭️ Location-based Sales not available: {regional_check.get('missing_columns', [])}")
            except Exception as e:
                print(f"❌ Error checking Location-based Sales readiness: {e}")
        else:
            print(f"⏭️ Skipping Location-based Sales (context={context}, sales chart)")
        
        # FINANCE CHARTS TEMPORARILY DISABLED
        # Focusing on Sales & Inventory domains only for semantic detection implementation
        # TODO: Re-enable Finance charts after implementing smart context detection
        
        # Try Stock Level Overview (Inventory Domain) with safe wrapper (INVENTORY charts)
        if context in ["INVENTORY", "MIXED", "UNKNOWN"]:
            try:
                stock_check = self.can_generate_chart(df, "stock_level_overview")
                print(f"🔍 Stock Level Overview check: {stock_check}")
                if stock_check["ready"] and len(stock_check["available_columns"]) >= 2:
                    item_col = stock_check["available_columns"][0]  # First available item column
                    stock_col = stock_check["available_columns"][1]   # First available stock column
                    chart = self._safe_generate_chart("stock_level_overview", df, item_col, stock_col)
                    if chart:
                        charts.append(chart)
                        print(f"✅ Generated Stock Level Overview chart")
                    else:
                        print(f"❌ Stock Level Overview chart generation failed")
                else:
                    print(f"⏭️ Stock Level Overview not available: {stock_check.get('missing_columns', [])}")
            except Exception as e:
                print(f"❌ Error checking Stock Level Overview readiness: {e}")
        else:
            print(f"⏭️ Skipping Stock Level Overview (context={context}, inventory chart)")
        
        # Try Reorder Status (Inventory Domain) with safe wrapper (INVENTORY charts)
        if context in ["INVENTORY", "MIXED", "UNKNOWN"]:
            try:
                reorder_check = self.can_generate_chart(df, "reorder_status")
                print(f"🔍 Reorder Status check: {reorder_check}")
                if reorder_check["ready"] and len(reorder_check["available_columns"]) >= 2:
                    item_col = reorder_check["available_columns"][0]  # First available item column
                    stock_col = reorder_check["available_columns"][1]   # First available stock column
                    reorder_col = reorder_check["available_columns"][2] if len(reorder_check["available_columns"]) >= 3 else None
                    chart = self._safe_generate_chart("reorder_status", df, item_col, stock_col, reorder_col)
                    if chart:
                        charts.append(chart)
                        print(f"✅ Generated Reorder Status chart")
                    else:
                        print(f"❌ Reorder Status chart generation failed")
                else:
                    print(f"⏭️ Reorder Status not available: {reorder_check.get('missing_columns', [])}")
            except Exception as e:
                print(f"❌ Error checking Reorder Status readiness: {e}")
        else:
            print(f"⏭️ Skipping Reorder Status (context={context}, inventory chart)")
        
        print(f"📊 Generated {len(charts)} bar charts total")
        return charts
        
    def generate_expense_distribution(self, df: pd.DataFrame, category_col: str, expense_col: str) -> Optional[Dict[str, Any]]:
        """
        Generate Expense Distribution bar chart for Finance domain
        
        Args:
            df: DataFrame to analyze
            category_col: Column name for expense categories
            expense_col: Column name for expense amounts
            
        Returns:
            Chart data dictionary or None if invalid
        """
        try:
            print(f"💰 Generating Expense Distribution chart")
            print(f"💰 Category column: {category_col}")
            print(f"💰 Expense column: {expense_col}")
            
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
            if category_col not in df_clean.columns or expense_col not in df_clean.columns:
                print(f"❌ Missing required columns: {category_col}, {expense_col}")
                return None
            
            # Clean and prepare data
            chart_df = df_clean[[category_col, expense_col]].copy()
            chart_df = chart_df.dropna()
            
            if chart_df.empty:
                print(f"❌ No valid data after cleaning")
                return None
            
            # Convert expense to numeric
            chart_df[expense_col] = pd.to_numeric(chart_df[expense_col], errors='coerce')
            chart_df = chart_df.dropna()
            
            if chart_df.empty:
                print(f"❌ No numeric expense data found")
                return None
            
            # Group by category and sum expenses
            grouped = chart_df.groupby(category_col)[expense_col].sum().reset_index()
            grouped = grouped.sort_values(expense_col, ascending=False)
            
            # Generate dynamic labels
            category_label = self._generate_smart_labels(category_col)
            expense_label = self._generate_smart_labels(expense_col)
            
            title = f"Expense Distribution by {category_label['label']}"
            description = f"Breakdown of {expense_label['label'].lower()} across different {category_label['label'].lower()}s"
            
            # Create chart data
            chart_data = {
                "x": grouped[category_col].tolist(),
                "y": grouped[expense_col].tolist(),
                "x_label": "Category",
                "y_label": f"{expense_label['label']}" + (f" ({expense_label['unit']})" if expense_label['unit'] else "")
            }
            
            print(f"💰 Generated expense data for {len(grouped)} categories")
            print(f"💰 Top expense: {grouped.iloc[0][category_col]} with {grouped.iloc[0][expense_col]:,.2f}")
            
            return {
                "id": f"{category_col.lower()}_expense_distribution",
                "title": title,
                "type": "bar",
                "description": description,
                "icon": "💰",
                "status": "success",
                "data": chart_data,
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                },
                "meta": {
                    "total_categories": len(grouped),
                    "top_category": grouped.iloc[0][category_col] if len(grouped) > 0 else None,
                    "top_expense": float(grouped.iloc[0][expense_col]) if len(grouped) > 0 else 0,
                    "total_expense": float(grouped[expense_col].sum()),
                    "category_column": category_col,
                    "expense_column": expense_col
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating Expense Distribution chart: {e}")
            return None
    
    def generate_profit_margin(self, df: pd.DataFrame, item_col: str, margin_col: str = None, profit_col: str = None, revenue_col: str = None) -> Optional[Dict[str, Any]]:
        """
        Generate Profit Margin Ratio bar chart for Finance domain
        
        Formula: Profit_Margin(%) = (Profit / Revenue) * 100
        
        Args:
            df: DataFrame to analyze
            item_col: Column name for items (Product, Location, Account, etc.)
            margin_col: Column name for profit margin percentages (if exists)
            profit_col: Column name for profit values (for calculation)
            revenue_col: Column name for revenue values (for calculation)
            
        Returns:
            Chart data dictionary or None if invalid
        """
        try:
            print(f"💰 Generating Profit Margin chart")
            print(f"💰 Item column: {item_col}")
            print(f"💰 Margin column: {margin_col}")
            print(f"💰 Profit column: {profit_col}")
            print(f"💰 Revenue column: {revenue_col}")
            
            # FALLBACK: Handle None or empty DataFrame
            if df is None or df.empty:
                print("❌ DataFrame is None or empty")
                return None
            
            # Handle duplicate columns
            df_clean = df.copy()
            if df_clean.columns.duplicated().any():
                print(f"⚠️ Found duplicate columns, removing duplicates")
                df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]
            
            # LEVEL 1: Use existing margin column if available
            if margin_col and margin_col in df_clean.columns:
                print(f"✅ Using existing margin column: {margin_col}")
                
                # Clean and prepare data
                chart_df = df_clean[[item_col, margin_col]].copy()
                chart_df = chart_df.dropna()
                
                if chart_df.empty:
                    print(f"❌ No valid data after cleaning")
                    return None
                
                # Convert margin to numeric
                chart_df[margin_col] = pd.to_numeric(chart_df[margin_col], errors='coerce')
                chart_df = chart_df.dropna()
                
                if chart_df.empty:
                    print(f"❌ No numeric margin data found")
                    return None
                
                # Group by item and take last (most recent) margin
                grouped = chart_df.groupby(item_col)[margin_col].last().reset_index()
                grouped = grouped.sort_values(margin_col, ascending=False)
                
                margin_column_name = margin_col
            
            # LEVEL 2: Calculate from Profit and Revenue if available
            elif profit_col and revenue_col and profit_col in df_clean.columns and revenue_col in df_clean.columns:
                print(f"🧮 Calculating margin from Profit and Revenue")
                print(f"   Formula: (Profit / Revenue) * 100")
                
                # Clean and prepare data
                chart_df = df_clean[[item_col, profit_col, revenue_col]].copy()
                chart_df = chart_df.dropna()
                
                if chart_df.empty:
                    print(f"❌ No valid data after cleaning")
                    return None
                
                # Convert to numeric
                chart_df[profit_col] = pd.to_numeric(chart_df[profit_col], errors='coerce')
                chart_df[revenue_col] = pd.to_numeric(chart_df[revenue_col], errors='coerce')
                chart_df = chart_df.dropna()
                
                if chart_df.empty:
                    print(f"❌ No numeric profit/revenue data found")
                    return None
                
                # Group by item and take last (most recent) values
                grouped = chart_df.groupby(item_col).agg({
                    profit_col: 'last',
                    revenue_col: 'last'
                }).reset_index()
                
                # Calculate Profit Margin: (Profit / Revenue) * 100
                # Handle division by zero
                grouped['Calculated_Margin'] = 0.0
                mask = grouped[revenue_col] != 0
                grouped.loc[mask, 'Calculated_Margin'] = (grouped.loc[mask, profit_col] / grouped.loc[mask, revenue_col]) * 100
                
                # Sort by margin
                grouped = grouped.sort_values('Calculated_Margin', ascending=False)
                
                # Use calculated margin column
                margin_column_name = 'Calculated_Margin'
                
                print(f"✅ Calculated profit margin for {len(grouped)} items")
                
            # LEVEL 3: Cannot generate chart
            else:
                print(f"❌ Cannot generate Profit Margin chart - missing data")
                print(f"   Need either: Margin% column OR (Profit + Revenue columns)")
                return None
            
            # Continue with chart generation (same for both levels)
            
            # Generate dynamic labels
            item_label = self._generate_smart_labels(item_col)
            
            title = f"Profit Margin by {item_label['label']}"
            description = f"Compare profitability across different {item_label['label'].lower()}s"
            
            # Create chart data
            chart_data = {
                "x": grouped[item_col].tolist(),
                "y": grouped[margin_column_name].tolist(),
                "x_label": "Product",
                "y_label": "Profit Margin (%)"
            }
            
            print(f"💰 Generated margin data for {len(grouped)} items")
            print(f"💰 Highest margin: {grouped.iloc[0][item_col]} with {grouped.iloc[0][margin_column_name]:.2f}%")
            
            return {
                "id": f"{item_col.lower()}_profit_margin",
                "title": title,
                "type": "bar",
                "description": description,
                "icon": "💰",
                "status": "success",
                "data": chart_data,
                "config": {
                    "maintainAspectRatio": False,
                    "responsive": True
                },
                "meta": {
                    "total_items": len(grouped),
                    "top_item": grouped.iloc[0][item_col] if len(grouped) > 0 else None,
                    "top_margin": float(grouped.iloc[0][margin_column_name]) if len(grouped) > 0 else 0,
                    "average_margin": float(grouped[margin_column_name].mean()),
                    "item_column": item_col,
                    "margin_column": margin_column_name,
                    "calculated": margin_column_name == 'Calculated_Margin'
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating Profit Margin chart: {e}")
            return None
    
    def generate_stock_level_overview(self, df: pd.DataFrame, item_col: str, stock_col: str) -> Optional[Dict[str, Any]]:
        """
        Generate Stock Level Overview bar chart for Inventory domain
        
        Args:
            df: DataFrame to analyze
            item_col: Column name for items (Product, SKU, Item_Code, etc.)
            stock_col: Column name for stock levels (Stock, Quantity, Units, etc.)
            
        Returns:
            Chart data dictionary or None if invalid
        """
        try:
            print(f"📦 Generating Stock Level Overview chart")
            print(f"📦 Item column: {item_col}")
            print(f"📦 Stock column: {stock_col}")
            
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
            if item_col not in df_clean.columns or stock_col not in df_clean.columns:
                print(f"❌ Missing required columns: {item_col}, {stock_col}")
                return None
            
            # Clean and prepare data
            chart_df = df_clean[[item_col, stock_col]].copy()
            chart_df = chart_df.dropna()
            
            if chart_df.empty:
                print(f"❌ No valid data after cleaning")
                return None
            
            # Convert stock to numeric
            chart_df[stock_col] = pd.to_numeric(chart_df[stock_col], errors='coerce')
            chart_df = chart_df.dropna()
            
            if chart_df.empty:
                print(f"❌ No numeric stock data found")
                return None
            
            # Group by item and sum all stock quantities
            # Formula: SUM(Stock_Level) per Product (shows total inventory on hand)
            grouped = chart_df.groupby(item_col)[stock_col].sum().reset_index()
            grouped = grouped.sort_values(stock_col, ascending=False)
            
            # Generate dynamic labels
            item_label = self._generate_smart_labels(item_col)
            stock_label = self._generate_smart_labels(stock_col)
            
            title = f"Stock Level Overview by {item_label['label']}"
            description = f"View inventory levels per {item_label['label'].lower()}"
            
            # Create chart data
            chart_data = {
                "x": grouped[item_col].tolist(),
                "y": grouped[stock_col].tolist(),
                "x_label": "Product",
                "y_label": f"Stock Level" + (f" ({stock_label['unit']})" if stock_label['unit'] else "")
            }
            
            print(f"📦 Generated stock data for {len(grouped)} items")
            print(f"📦 Highest stock: {grouped.iloc[0][item_col]} with {grouped.iloc[0][stock_col]:,.0f} units")
            
            # Brief description for user understanding
            brief_description = f"Displays current inventory levels for each {item_label['label'].lower()}. Shows the most recent stock count per {item_label['label'].lower()}, sorted from highest to lowest. Use this to identify overstocked items (potential dead stock) and understocked items (potential stockouts). Helps optimize inventory investment and storage space."
            
            return {
                "id": f"{item_col.lower()}_stock_level_overview",
                "title": title,
                "type": "bar",
                "description": description,
                "brief_description": brief_description,
                "icon": "📦",
                "status": "success",
                "data": chart_data,
                "config": self.styling.get_bar_chart_config(
                    chart_type="inventory",
                    x_label=chart_data.get("x_label", "Product"),
                    y_label=chart_data.get("y_label", "Stock Level")
                ),
                "meta": {
                    "total_items": len(grouped),
                    "highest_stock_item": grouped.iloc[0][item_col] if len(grouped) > 0 else None,
                    "highest_stock_level": float(grouped.iloc[0][stock_col]) if len(grouped) > 0 else 0,
                    "total_stock": float(grouped[stock_col].sum()),
                    "average_stock": float(grouped[stock_col].mean()),
                    "item_column": item_col,
                    "stock_column": stock_col
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating Stock Level Overview chart: {e}")
            # Try fallback methods
            return self.fallback_handler.handle_bar_chart_fallback(
                df, "stock_level_overview", self.generate_stock_level_overview,
                item_col=item_col, stock_col=stock_col
            )
    
    def generate_reorder_status(self, df: pd.DataFrame, item_col: str, stock_col: str, reorder_col: str = None) -> Optional[Dict[str, Any]]:
        """
        Generate Reorder Point Status bar chart for Inventory domain
        Shows items that need reordering (stock below reorder point)
        
        Args:
            df: DataFrame to analyze
            item_col: Column name for items
            stock_col: Column name for current stock levels
            reorder_col: Column name for reorder points (optional)
            
        Returns:
            Chart data dictionary or None if invalid
        """
        try:
            print(f"📦 Generating Reorder Status chart")
            print(f"📦 Item column: {item_col}")
            print(f"📦 Stock column: {stock_col}")
            print(f"📦 Reorder column: {reorder_col}")
            
            # FALLBACK: Handle None or empty DataFrame
            if df is None or df.empty:
                print("❌ DataFrame is None or empty")
                return None
            
            # Handle duplicate columns
            df_clean = df.copy()
            if df_clean.columns.duplicated().any():
                print(f"⚠️ Found duplicate columns, removing duplicates")
                df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]
            
            # Determine columns to use
            if reorder_col and reorder_col in df_clean.columns:
                required_cols = [item_col, stock_col, reorder_col]
            else:
                required_cols = [item_col, stock_col]
            
            # Validate required columns
            if not all(col in df_clean.columns for col in required_cols):
                print(f"❌ Missing required columns: {required_cols}")
                return None
            
            # Clean and prepare data
            chart_df = df_clean[required_cols].copy()
            chart_df = chart_df.dropna()
            
            if chart_df.empty:
                print(f"❌ No valid data after cleaning")
                return None
            
            # Convert numeric columns
            chart_df[stock_col] = pd.to_numeric(chart_df[stock_col], errors='coerce')
            if reorder_col and reorder_col in chart_df.columns:
                chart_df[reorder_col] = pd.to_numeric(chart_df[reorder_col], errors='coerce')
            
            chart_df = chart_df.dropna()
            
            if chart_df.empty:
                print(f"❌ No numeric data found")
                return None
            
            # Group by item and aggregate stock and reorder data
            if reorder_col and reorder_col in chart_df.columns:
                grouped = chart_df.groupby(item_col).agg({
                    stock_col: 'sum',  # Sum all stock quantities
                    reorder_col: 'last'  # Use last (most recent) reorder point
                }).reset_index()
                
                # Calculate gap (negative means needs reordering)
                grouped['gap'] = grouped[stock_col] - grouped[reorder_col]
                
                # Sort by gap (most urgent first - most negative)
                grouped = grouped.sort_values('gap', ascending=True)
                
                # Show all items or top 15 that need reordering
                if len(grouped) > 15:
                    grouped = grouped.head(15)
            else:
                # If no reorder column, just show stock levels
                # Sum all stock quantities per item
                grouped = chart_df.groupby(item_col)[stock_col].sum().reset_index()
                grouped = grouped.sort_values(stock_col, ascending=True)  # Lowest stock first
                if len(grouped) > 15:
                    grouped = grouped.head(15)
            
            # Generate dynamic labels
            item_label = self._generate_smart_labels(item_col)
            stock_label = self._generate_smart_labels(stock_col)
            
            if reorder_col and reorder_col in grouped.columns:
                title = f"Reorder Status - Items Needing Attention"
                description = f"Items with stock below or near reorder point"
                y_data = grouped['gap'].tolist()
                y_label = f"Stock Gap" + (f" ({stock_label['unit']})" if stock_label['unit'] else "")
            else:
                title = f"Low Stock Items by {item_label['label']}"
                description = f"Items with lowest stock levels"
                y_data = grouped[stock_col].tolist()
                y_label = f"Stock Level" + (f" ({stock_label['unit']})" if stock_label['unit'] else "")
            
            # Create chart data
            chart_data = {
                "x": grouped[item_col].tolist(),
                "y": y_data,
                "x_label": "Product",
                "y_label": y_label
            }
            
            print(f"📦 Generated reorder data for {len(grouped)} items")
            
            # Brief description for user understanding
            if reorder_col and reorder_col in grouped.columns:
                brief_description = f"Identifies items requiring immediate reorder attention. Shows the gap between current stock and reorder point (negative values = below reorder point). Items are sorted by urgency, with the most critical items first. Use this to prevent stockouts, optimize procurement timing, and maintain healthy inventory levels."
            else:
                brief_description = f"Shows items with the lowest stock levels. Without reorder point data, displays current stock sorted from lowest to highest. Use this to identify potential stockout risks and prioritize procurement decisions."
            
            return {
                "id": f"{item_col.lower()}_reorder_status",
                "title": title,
                "type": "bar",
                "description": description,
                "brief_description": brief_description,
                "icon": "📦",
                "status": "success",
                "data": chart_data,
                "config": self.styling.get_bar_chart_config(
                    chart_type="inventory",
                    x_label=chart_data.get("x_label", "Product"),
                    y_label=chart_data.get("y_label", "Stock Level")
                ),
                "meta": {
                    "total_items": len(grouped),
                    "items_analyzed": len(grouped),
                    "has_reorder_point": reorder_col is not None and reorder_col in df_clean.columns,
                    "item_column": item_col,
                    "stock_column": stock_col,
                    "reorder_column": reorder_col
                }
            }
            
        except Exception as e:
            print(f"❌ Error generating Reorder Status chart: {e}")
            # Try fallback methods
            return self.fallback_handler.handle_bar_chart_fallback(
                df, "reorder_status", self.generate_reorder_status,
                item_col=item_col, stock_col=stock_col, reorder_col=reorder_col
            )
    
    def _safe_generate_chart(self, chart_type: str, df: pd.DataFrame, col1: str, col2: str, col3: str = None) -> Optional[Dict[str, Any]]:
        """
        Safely generate a chart with comprehensive error handling
        
        Args:
            chart_type: Type of chart to generate
            df: DataFrame to analyze
            col1: First column name
            col2: Second column name
            
        Returns:
            Chart dictionary or None if failed
        """
        try:
            if chart_type == "product_performance":
                return self.generate_product_performance(df, col1, col2)
            elif chart_type == "regional_sales":
                return self.generate_regional_sales(df, col1, col2)
            elif chart_type == "expense_distribution":
                return self.generate_expense_distribution(df, col1, col2)
            elif chart_type == "profit_margin":
                return self.generate_profit_margin(df, col1, col2)
            elif chart_type == "stock_level_overview":
                return self.generate_stock_level_overview(df, col1, col2)
            elif chart_type == "reorder_status":
                return self.generate_reorder_status(df, col1, col2, col3)
            else:
                print(f"❌ Unknown chart type: {chart_type}")
                return None
        except MemoryError:
            print(f"❌ Memory error generating {chart_type} chart - dataset too large")
            return None
        except Exception as e:
            print(f"❌ Unexpected error generating {chart_type} chart: {e}")
            return None
