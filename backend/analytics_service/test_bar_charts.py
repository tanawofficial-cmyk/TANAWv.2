"""
Test Script for TANAW Bar Chart Generator
Phase 1: Test bar chart generation with sample data
"""

import pandas as pd
import numpy as np
from bar_chart_generator import TANAWBarChartGenerator
from datetime import datetime, timedelta

def create_sample_sales_data():
    """Create sample sales data for testing"""
    np.random.seed(42)  # For reproducible results
    
    # Sample products
    products = ['Cold coffee', 'Sugarcane juice', 'Panipuri', 'Frankie', 'Sandwich', 
               'Aalopuri', 'Vadapav', 'Tea', 'Coffee', 'Samosa']
    
    # Sample regions
    regions = ['North', 'South', 'East', 'West', 'Central']
    
    # Generate sample data
    data = []
    for i in range(100):  # 100 records
        product = np.random.choice(products)
        region = np.random.choice(regions)
        sales = np.random.normal(500, 200)  # Average sales around 500
        sales = max(0, sales)  # No negative sales
        
        data.append({
            'Product': product,
            'Region': region,
            'Sales': sales,
            'Date': datetime.now() - timedelta(days=np.random.randint(0, 365))
        })
    
    return pd.DataFrame(data)

def test_bar_chart_generator():
    """Test the bar chart generator"""
    print("🧪 Testing TANAW Bar Chart Generator")
    print("=" * 50)
    
    # Create sample data
    df = create_sample_sales_data()
    print(f"📊 Created sample dataset: {df.shape}")
    print(f"📊 Columns: {list(df.columns)}")
    print(f"📊 Sample data:")
    print(df.head())
    print()
    
    # Initialize generator
    generator = TANAWBarChartGenerator()
    
    # Test Product Performance chart
    print("🔍 Testing Product Performance chart...")
    product_check = generator.can_generate_chart(df, "product_performance")
    print(f"📊 Product Performance readiness: {product_check}")
    
    if product_check["ready"]:
        product_chart = generator.generate_product_performance(df, "Product", "Sales")
        if product_chart:
            print(f"✅ Product Performance chart generated successfully")
            print(f"📊 Chart title: {product_chart['title']}")
            print(f"📊 Chart type: {product_chart['type']}")
            print(f"📊 Data points: {len(product_chart['data']['x'])}")
            print(f"📊 Top 3 products: {product_chart['data']['x'][:3]}")
            print(f"📊 Top 3 sales: {product_chart['data']['y'][:3]}")
        else:
            print(f"❌ Failed to generate Product Performance chart")
    else:
        print(f"❌ Product Performance chart not ready: {product_check['missing_columns']}")
    
    print()
    
    # Test Regional Sales chart
    print("🔍 Testing Regional Sales chart...")
    regional_check = generator.can_generate_chart(df, "regional_sales")
    print(f"📊 Regional Sales readiness: {regional_check}")
    
    if regional_check["ready"]:
        regional_chart = generator.generate_regional_sales(df, "Region", "Sales")
        if regional_chart:
            print(f"✅ Regional Sales chart generated successfully")
            print(f"📊 Chart title: {regional_chart['title']}")
            print(f"📊 Chart type: {regional_chart['type']}")
            print(f"📊 Data points: {len(regional_chart['data']['x'])}")
            print(f"📊 Top 3 regions: {regional_chart['data']['x'][:3]}")
            print(f"📊 Top 3 sales: {regional_chart['data']['y'][:3]}")
        else:
            print(f"❌ Failed to generate Regional Sales chart")
    else:
        print(f"❌ Regional Sales chart not ready: {regional_check['missing_columns']}")
    
    print()
    
    # Test generate all bar charts
    print("🔍 Testing generate_all_bar_charts...")
    all_charts = generator.generate_all_bar_charts(df)
    print(f"📊 Generated {len(all_charts)} bar charts")
    
    for i, chart in enumerate(all_charts):
        print(f"📊 Chart {i+1}: {chart['title']} ({chart['type']})")
        print(f"   - Data points: {len(chart['data']['x'])}")
        print(f"   - Status: {chart['status']}")
    
    print()
    print("🎉 Bar Chart Generator test completed!")

if __name__ == "__main__":
    test_bar_chart_generator()
