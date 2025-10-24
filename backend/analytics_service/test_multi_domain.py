#!/usr/bin/env python3
"""
Test TANAW's multi-domain capabilities
Tests: Sales, Finance, Inventory, and Customer domains
"""

import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_clean import TANAWDataProcessor
from gpt_column_mapper import GPTColumnMapper
from config_manager import get_config

def create_sales_dataset():
    """Create a typical sales domain dataset"""
    print("\n" + "="*80)
    print("📊 CREATING SALES DOMAIN DATASET")
    print("="*80)
    
    data = {
        'Product_Name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones', 'Webcam', 'Speaker', 'Microphone'],
        'Sales_Amount': [1200.50, 25.99, 89.99, 450.00, 129.99, 75.50, 199.99, 85.00],
        'Region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West'],
        'Sale_Date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19', '2024-01-20', '2024-01-21', '2024-01-22'],
        'Quantity_Sold': [5, 100, 50, 10, 30, 45, 15, 25]
    }
    
    df = pd.DataFrame(data)
    print(f"✅ Created Sales dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"   Columns: {list(df.columns)}")
    return df

def create_finance_dataset():
    """Create a typical finance domain dataset"""
    print("\n" + "="*80)
    print("💰 CREATING FINANCE DOMAIN DATASET")
    print("="*80)
    
    data = {
        'Account_Name': ['Marketing', 'Operations', 'R&D', 'Sales', 'HR', 'IT', 'Legal', 'Admin'],
        'Balance': [50000.00, 125000.00, 75000.00, 200000.00, 45000.00, 80000.00, 30000.00, 25000.00],
        'Department': ['Marketing', 'Operations', 'Technology', 'Sales', 'People', 'Technology', 'Legal', 'Admin'],
        'Transaction_Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05', '2024-01-06', '2024-01-07', '2024-01-08'],
        'Expense': [10000, 25000, 15000, 30000, 8000, 12000, 5000, 4000]
    }
    
    df = pd.DataFrame(data)
    print(f"✅ Created Finance dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"   Columns: {list(df.columns)}")
    return df

def create_inventory_dataset():
    """Create a typical inventory domain dataset"""
    print("\n" + "="*80)
    print("📦 CREATING INVENTORY DOMAIN DATASET")
    print("="*80)
    
    data = {
        'Item_Code': ['ITM001', 'ITM002', 'ITM003', 'ITM004', 'ITM005', 'ITM006', 'ITM007', 'ITM008'],
        'Stock_Level': [150, 500, 75, 200, 300, 50, 400, 125],
        'Warehouse_Location': ['Warehouse_A', 'Warehouse_B', 'Warehouse_C', 'Warehouse_A', 'Warehouse_B', 'Warehouse_C', 'Warehouse_A', 'Warehouse_B'],
        'Reorder_Date': ['2024-02-01', '2024-02-05', '2024-02-10', '2024-02-15', '2024-02-20', '2024-02-25', '2024-03-01', '2024-03-05'],
        'Quantity': [150, 500, 75, 200, 300, 50, 400, 125]
    }
    
    df = pd.DataFrame(data)
    print(f"✅ Created Inventory dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"   Columns: {list(df.columns)}")
    return df

def create_customer_dataset():
    """Create a typical customer domain dataset"""
    print("\n" + "="*80)
    print("👥 CREATING CUSTOMER DOMAIN DATASET")
    print("="*80)
    
    data = {
        'Customer_ID': ['CUST001', 'CUST002', 'CUST003', 'CUST004', 'CUST005', 'CUST006', 'CUST007', 'CUST008'],
        'Lifetime_Value': [5000.00, 12500.00, 3200.00, 8900.00, 15000.00, 2500.00, 9800.00, 6700.00],
        'Segment': ['Premium', 'Premium', 'Standard', 'Premium', 'VIP', 'Standard', 'Premium', 'Standard'],
        'Signup_Date': ['2023-06-15', '2023-08-20', '2023-09-10', '2023-10-05', '2023-07-12', '2023-11-08', '2023-08-25', '2023-09-30'],
        'Engagement_Score': [85, 92, 65, 78, 95, 55, 88, 70]
    }
    
    df = pd.DataFrame(data)
    print(f"✅ Created Customer dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"   Columns: {list(df.columns)}")
    return df

def test_domain(domain_name, df):
    """Test a specific domain dataset"""
    print("\n" + "="*80)
    print(f"🧪 TESTING {domain_name.upper()} DOMAIN")
    print("="*80)
    
    try:
        # Step 1: Initialize components
        config = get_config()
        api_key = config.openai.api_key if config.openai and config.openai.is_configured() else None
        
        if not api_key:
            print("⚠️ No OpenAI API key found - using fallback mapper")
            # Create simple fallback mapping
            column_mapping = {col: col for col in df.columns}
        else:
            # Step 2: Map columns using GPT
            print("\n📋 Step 1: Mapping columns with GPT...")
            gpt_mapper = GPTColumnMapper(api_key)
            mapping_result = gpt_mapper.map_columns(df.columns.tolist(), dataset_context=domain_name)
            
            if not mapping_result.success:
                print(f"❌ Mapping failed: {mapping_result.error_message}")
                return False
            
            # Create column mapping dict
            column_mapping = {}
            for mapping in mapping_result.mappings:
                if mapping.mapped_to != "Ignore":
                    column_mapping[mapping.original_column] = mapping.mapped_to
                    print(f"   {mapping.original_column:30} → {mapping.mapped_to:15} (confidence: {mapping.confidence}%)")
        
        # Step 3: Initialize TANAW processor
        print("\n🔧 Step 2: Initializing TANAW processor...")
        processor = TANAWDataProcessor()
        
        # Step 4: Detect domain
        print("\n🎯 Step 3: Detecting domain...")
        domain_classification = processor.domain_detector.detect_domain(df, column_mapping)
        print(f"   Detected: {domain_classification.domain.upper()}")
        print(f"   Confidence: {domain_classification.confidence:.2%}")
        print(f"   Indicators: {domain_classification.indicators[:3]}")  # Show first 3
        
        # Step 5: Clean and transform data
        print("\n🧹 Step 4: Cleaning and transforming data...")
        cleaned_df = processor.clean_and_transform_data(df, column_mapping)
        print(f"   Shape: {cleaned_df.shape}")
        print(f"   Columns after mapping: {list(cleaned_df.columns)}")
        
        # Step 6: Generate analytics
        print("\n📊 Step 5: Generating analytics and charts...")
        analytics_result = processor.generate_analytics_and_charts(cleaned_df, column_mapping)
        
        if analytics_result.get('success'):
            charts = analytics_result.get('charts', [])
            print(f"   ✅ Generated {len(charts)} charts")
            
            # Show chart details
            for i, chart in enumerate(charts, 1):
                print(f"\n   Chart {i}:")
                print(f"      Title: {chart.get('title')}")
                print(f"      Type: {chart.get('type')}")
                print(f"      Description: {chart.get('description')}")
                if 'data' in chart:
                    data = chart['data']
                    print(f"      X-axis: {data.get('x_label')} ({len(data.get('x', []))} items)")
                    print(f"      Y-axis: {data.get('y_label')}")
                    if data.get('x') and data.get('y'):
                        print(f"      Sample data: {data['x'][0]} → {data['y'][0]}")
            
            return True
        else:
            print(f"   ❌ Analytics generation failed: {analytics_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error testing {domain_name} domain: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run multi-domain tests"""
    print("\n" + "="*80)
    print("🚀 TANAW MULTI-DOMAIN TEST SUITE")
    print("="*80)
    print("Testing domain detection and analytics across 4 business domains")
    print("="*80)
    
    # Create datasets
    datasets = {
        'Sales': create_sales_dataset(),
        'Finance': create_finance_dataset(),
        'Inventory': create_inventory_dataset(),
        'Customer': create_customer_dataset()
    }
    
    # Test each domain
    results = {}
    for domain_name, df in datasets.items():
        success = test_domain(domain_name, df)
        results[domain_name] = success
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    for domain_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {domain_name:15} {status}")
    
    total_passed = sum(1 for s in results.values() if s)
    total_tests = len(results)
    
    print(f"\n   Total: {total_passed}/{total_tests} domains passed")
    print("="*80)
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

