#!/usr/bin/env python3
"""
Debug script to test the full analytics pipeline
"""

import pandas as pd
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_clean import TANAWDataProcessor

def test_full_pipeline():
    """Test the full analytics pipeline with comprehensive dataset"""
    
    # Create test data with our comprehensive columns
    data = {
        'ProductName': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones'],
        'SalesDate': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        'AmountSold': [45000, 12500, 28000, 89000, 35000],
        'Territory': ['North', 'South', 'East', 'West', 'North'],
        'QtySold': [25, 100, 60, 18, 75],
        'ExpenseCategory': ['Marketing', 'Operations', 'Technology', 'Marketing', 'Operations'],
        'ExpenseAmount': [5000, 3000, 4000, 6000, 2500],
        'ProfitMargin': [15.5, 12.8, 18.2, 22.1, 16.7],
        'StockLevel': [150, 200, 120, 80, 180],
        'ReorderPoint': [50, 75, 40, 30, 60]
    }
    
    df = pd.DataFrame(data)
    
    # Create column mapping
    column_mapping = {
        'ProductName': 'Product',
        'SalesDate': 'Date', 
        'AmountSold': 'Sales',
        'Territory': 'Region',
        'QtySold': 'Quantity',
        'ExpenseCategory': 'Category',
        'ExpenseAmount': 'Expense',
        'ProfitMargin': 'Margin',
        'StockLevel': 'Stock',
        'ReorderPoint': 'Reorder'
    }
    
    print("🧪 Testing Full Analytics Pipeline")
    print(f"📊 Dataset shape: {df.shape}")
    print(f"📊 Columns: {list(df.columns)}")
    print(f"📊 Column mapping: {column_mapping}")
    print()
    
    # Initialize analytics engine
    engine = TANAWDataProcessor()
    
    # Generate analytics
    result = engine.generate_analytics_and_charts(df, column_mapping)
    
    print("🔍 FULL PIPELINE RESULTS:")
    print(f"📊 Total charts generated: {len(result.get('charts', []))}")
    print()
    
    # List each chart
    charts = result.get('charts', [])
    for i, chart in enumerate(charts, 1):
        print(f"Chart {i}:")
        print(f"  - ID: {chart.get('id', 'N/A')}")
        print(f"  - Title: {chart.get('title', 'N/A')}")
        print(f"  - Type: {chart.get('type', 'N/A')}")
        print(f"  - Status: {chart.get('status', 'N/A')}")
        print()
    
    # Check validation report
    validation_report = result.get('validation_report', {})
    print(f"🛡️ Validation Report:")
    print(f"  - Checked: {validation_report.get('summary', {}).get('checked', 'N/A')}")
    print(f"  - Duplicates: {validation_report.get('summary', {}).get('duplicates', 'N/A')}")
    print(f"  - Issues: {validation_report.get('summary', {}).get('issues', 'N/A')}")
    print()
    
    # Check readiness
    readiness = result.get('readiness', {})
    print(f"📊 Analytics Readiness:")
    print(f"  - Available: {len(readiness.get('available_analytics', []))}")
    print(f"  - Unavailable: {len(readiness.get('unavailable_analytics', []))}")
    print(f"  - Ready count: {readiness.get('ready_count', 'N/A')}")
    print(f"  - Total count: {readiness.get('total_count', 'N/A')}")
    
    return result

if __name__ == "__main__":
    result = test_full_pipeline()
    print("✅ Full pipeline test completed!")
