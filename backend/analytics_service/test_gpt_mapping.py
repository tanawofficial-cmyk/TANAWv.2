"""
Test script for GPT-powered column mapping.
Tests the simplified mapper with sample retail datasets.
"""

import pandas as pd
import os
from simplified_mapper import SimplifiedMapper

def test_gpt_mapping():
    """Test GPT mapping with sample retail data."""
    
    # Check if OpenAI API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found. Please set your OpenAI API key.")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        return
    
    print("🧪 Testing GPT-Powered Column Mapping")
    print("=" * 50)
    
    # Create sample retail dataset
    sample_data = {
        'Product_ID': [101, 102, 103, 104, 105],
        'Sales_Date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
        'Sales_Amount': [1000, 1500, 1200, 1800, 2000],
        'Region': ['North', 'South', 'East', 'West', 'North'],
        'Quantity_Sold': [10, 15, 12, 18, 20],
        'Sales_Rep': ['John', 'Jane', 'Bob', 'Alice', 'John'],
        'Payment_Method': ['Credit', 'Cash', 'Debit', 'Credit', 'Cash']
    }
    
    df = pd.DataFrame(sample_data)
    print(f"📊 Sample Dataset:")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {list(df.columns)}")
    print()
    
    try:
        # Initialize mapper
        print("🚀 Initializing Simplified Mapper...")
        mapper = SimplifiedMapper(api_key)
        
        # Test mapping
        print("🔍 Testing column mapping...")
        results = mapper.map_columns(df, dataset_context="retail")
        
        if results['success']:
            print("✅ Mapping successful!")
            print()
            
            # Display results
            print("📋 Mapping Results:")
            print(f"   Total Cost: ${results['total_cost']:.4f}")
            print(f"   Cache Hits: {results['cache_hits']}")
            print(f"   Processing Time: {results['processing_time']:.2f}s")
            print()
            
            # Show mapped columns
            print("🗺️ Column Mappings:")
            for mapping in results['mapped_columns']:
                print(f"   {mapping['original_column']} → {mapping['mapped_column']} (confidence: {mapping['confidence']:.1f}%)")
                print(f"      Reasoning: {mapping['reasoning']}")
            
            if results['uncertain_columns']:
                print("\n⚠️ Uncertain Columns:")
                for uncertain in results['uncertain_columns']:
                    print(f"   {uncertain['original_column']} → {uncertain['mapped_column']} (confidence: {uncertain['confidence']:.1f}%)")
            
            if results['unmapped_columns']:
                print("\n❌ Unmapped Columns:")
                for unmapped in results['unmapped_columns']:
                    print(f"   {unmapped['original_column']} (reason: {unmapped['reason']})")
            
            # Show analytics readiness
            print("\n📊 Analytics Readiness:")
            analytics = results['analytics_readiness']
            print(f"   Ready Analytics: {analytics['ready_count']}/{analytics['total_count']}")
            
            for analytic in analytics['available_analytics']:
                print(f"   ✅ {analytic['name']} - Ready")
            
            for analytic in analytics['unavailable_analytics']:
                print(f"   ❌ {analytic['name']} - Missing: {', '.join(analytic['missing_columns'])}")
            
            # Show data quality
            print("\n🔍 Data Quality:")
            quality = results['data_quality']
            print(f"   Overall Score: {quality['overall_score']}/100")
            if quality['issues']:
                print("   Issues:")
                for issue in quality['issues']:
                    print(f"      - {issue}")
            
            # Show renamed dataframe
            print("\n📋 Renamed DataFrame:")
            renamed_df = results['renamed_dataframe']
            print(f"   Columns: {list(renamed_df.columns)}")
            print(f"   Shape: {renamed_df.shape}")
            
        else:
            print("❌ Mapping failed!")
            print(f"   Error: {results['error_message']}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_cache_functionality():
    """Test caching functionality."""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found.")
        return
    
    print("\n🧪 Testing Cache Functionality")
    print("=" * 50)
    
    try:
        mapper = SimplifiedMapper(api_key)
        
        # Test with same columns (should hit cache)
        sample_data = {
            'Product_ID': [1, 2, 3],
            'Sales_Date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'Amount': [100, 200, 300]
        }
        
        df = pd.DataFrame(sample_data)
        
        print("🔄 First mapping (should call GPT)...")
        results1 = mapper.map_columns(df)
        print(f"   Cost: ${results1['total_cost']:.4f}")
        print(f"   Cache Hits: {results1['cache_hits']}")
        
        print("\n🔄 Second mapping (should hit cache)...")
        results2 = mapper.map_columns(df)
        print(f"   Cost: ${results2['total_cost']:.4f}")
        print(f"   Cache Hits: {results2['cache_hits']}")
        
        # Show cache stats
        cache_stats = mapper.get_cache_stats()
        print(f"\n📊 Cache Statistics:")
        print(f"   Total Cached Mappings: {cache_stats['total_cached_mappings']}")
        print(f"   Total Usage Count: {cache_stats['total_usage_count']}")
        print(f"   Total Cost: ${cache_stats['total_cost']:.4f}")
        
    except Exception as e:
        print(f"❌ Cache test failed: {e}")

if __name__ == "__main__":
    print("🚀 TANAW GPT Mapping Test")
    print("=" * 50)
    
    # Test basic mapping
    test_gpt_mapping()
    
    # Test caching
    test_cache_functionality()
    
    print("\n✅ Test completed!")
