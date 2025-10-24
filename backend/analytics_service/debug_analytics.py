#!/usr/bin/env python3
"""
Debug script to test analytics generation directly
"""

import pandas as pd
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_clean import TANAWDataProcessor

def debug_analytics():
    """Debug analytics generation"""
    
    # Load the test data
    df = pd.read_csv("../../TEST FILES/sales_data.csv")
    print(f"📊 Loaded DataFrame: {df.shape}")
    print(f"📊 Columns: {list(df.columns)}")
    
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
    
    # Initialize processor
    processor = TANAWDataProcessor()
    
    # Test the old analytics generation
    print("🔍 Testing OLD analytics generation...")
    result = processor.generate_analytics_and_charts(df, column_mapping)
    print(f"🔍 Result: {result}")
    
    if result.get('charts'):
        print(f"✅ Generated {len(result['charts'])} charts")
        for i, chart in enumerate(result['charts']):
            print(f"   Chart {i+1}: {chart.get('title', 'Unknown')} - {chart.get('type', 'Unknown')}")
    else:
        print("❌ No charts generated!")
        print(f"🔍 Readiness: {result.get('readiness', {})}")

if __name__ == "__main__":
    debug_analytics()
