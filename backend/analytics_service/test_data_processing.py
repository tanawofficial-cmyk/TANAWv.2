#!/usr/bin/env python3
"""
Test script to debug the data processing pipeline
"""

import pandas as pd
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import TANAWDataProcessorCore

def test_data_processing():
    """Test the data processing pipeline with sample data"""
    
    # Create sample data similar to sales_data.csv
    data = {
        'Product_ID': [1052, 1093, 1015, 1072, 1061],
        'Sale_Date': ['2023-02-03', '2023-04-21', '2023-09-21', '2023-08-24', '2023-03-24'],
        'Sales_Rep': ['Bob', 'Bob', 'David', 'Bob', 'Charlie'],
        'Region': ['North', 'West', 'South', 'South', 'East'],
        'Sales_Amount': [5053.97, 4384.02, 4631.23, 2167.94, 3750.2],
        'Quantity_Sold': [18, 17, 30, 39, 13],
        'Product_Category': ['Furniture', 'Furniture', 'Food', 'Clothing', 'Electronics']
    }
    
    df = pd.DataFrame(data)
    print(f"📊 Sample DataFrame shape: {df.shape}")
    print(f"📊 Sample DataFrame columns: {list(df.columns)}")
    
    # Create column mapping (what GPT would return)
    column_mapping = {
        'Product_ID': 'Product',
        'Sale_Date': 'Date', 
        'Sales_Rep': 'Sales_Rep',
        'Region': 'Region',
        'Sales_Amount': 'Sales',
        'Quantity_Sold': 'Quantity',
        'Product_Category': 'Category'
    }
    
    print(f"📋 Column mapping: {column_mapping}")
    
    # Initialize data processor
    processor = TANAWDataProcessorCore()
    
    # Test analytics
    analytics_requested = ["sales_summary", "product_performance", "regional_sales"]
    
    print(f"🔍 Testing analytics: {analytics_requested}")
    
    # Process dataset
    result = processor.process_dataset(df, column_mapping, analytics_requested)
    
    print(f"📊 Processing result:")
    print(f"   Success: {result['success']}")
    print(f"   Charts generated: {len(result['charts'])}")
    print(f"   Processing metadata: {result.get('processing_metadata', {})}")
    
    if result['charts']:
        for i, chart in enumerate(result['charts']):
            print(f"   Chart {i+1}: {chart.get('title', 'Unknown')} - {chart.get('type', 'Unknown')}")
    else:
        print("   ❌ No charts generated!")
    
    return result

if __name__ == "__main__":
    test_data_processing()
