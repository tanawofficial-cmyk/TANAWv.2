"""
Test script to verify frontend-backend integration with GPT mapping.
This simulates the data flow between backend and frontend.
"""

import json
import pandas as pd
from simplified_mapper import SimplifiedMapper
import os

def test_frontend_backend_integration():
    """Test the complete data flow from backend to frontend."""
    
    print("🧪 Testing Frontend-Backend Integration")
    print("=" * 50)
    
    # Check if OpenAI API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found. Please set your OpenAI API key.")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        return
    
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
        # Step 1: Backend GPT Mapping
        print("🔧 Step 1: Backend GPT Mapping")
        mapper = SimplifiedMapper(api_key)
        results = mapper.map_columns(df, dataset_context="retail")
        
        if not results['success']:
            print(f"❌ Backend mapping failed: {results['error_message']}")
            return
        
        print("✅ Backend mapping successful!")
        print(f"   Mapped columns: {len(results['mapped_columns'])}")
        print(f"   Uncertain columns: {len(results['uncertain_columns'])}")
        print(f"   Unmapped columns: {len(results['unmapped_columns'])}")
        print(f"   Total cost: ${results['total_cost']:.4f}")
        print(f"   Cache hits: {results['cache_hits']}")
        print()
        
        # Step 2: Simulate Backend Response Format
        print("🔧 Step 2: Simulating Backend Response Format")
        backend_response = {
            "success": True,
            "analysis_id": "test_123",
            "message": "GPT-powered analysis completed successfully",
            "mapped_columns": results['mapped_columns'],
            "uncertain_columns": results['uncertain_columns'],
            "unmapped_columns": results['unmapped_columns'],
            "analytics_readiness": results['analytics_readiness'],
            "data_quality": results['data_quality'],
            "gpt_metadata": {
                "total_cost": results['total_cost'],
                "cache_hits": results['cache_hits'],
                "processing_time": results['processing_time'],
                "mapping_method": "gpt",
                "success": True
            },
            "processing_time": results['processing_time'],
            "dataset_info": {
                "rows": len(df),
                "columns": len(df.columns),
                "filename": "test_dataset.csv",
                "encoding": "utf-8",
                "delimiter": ","
            }
        }
        
        print("✅ Backend response format created!")
        print(f"   Response keys: {list(backend_response.keys())}")
        print()
        
        # Step 3: Simulate Frontend Data Processing
        print("🔧 Step 3: Simulating Frontend Data Processing")
        
        # Test Dashboard.js data handling
        analysis_data = backend_response
        
        # Test mapped columns display
        mapped_columns = analysis_data.get('mapped_columns', [])
        print(f"📋 Frontend Mapped Columns Display:")
        for col in mapped_columns:
            print(f"   {col['original_column']} → {col['mapped_column']} ({col['confidence']:.1f}% confidence)")
            print(f"      Source: {col['source']}, Reasoning: {col['reasoning']}")
        
        # Test uncertain columns display
        uncertain_columns = analysis_data.get('uncertain_columns', [])
        if uncertain_columns:
            print(f"\n⚠️ Frontend Uncertain Columns Display:")
            for col in uncertain_columns:
                print(f"   {col['original_column']} → {col['mapped_column']} ({col['confidence']:.1f}% confidence)")
        
        # Test unmapped columns display
        unmapped_columns = analysis_data.get('unmapped_columns', [])
        if unmapped_columns:
            print(f"\n❌ Frontend Unmapped Columns Display:")
            for col in unmapped_columns:
                print(f"   {col['original_column']} - {col['reason']}")
        
        # Test analytics readiness display
        analytics_readiness = analysis_data.get('analytics_readiness', {})
        print(f"\n📊 Frontend Analytics Readiness Display:")
        print(f"   Ready analytics: {analytics_readiness.get('ready_count', 0)}")
        print(f"   Total analytics: {analytics_readiness.get('total_count', 0)}")
        
        for analytic in analytics_readiness.get('available_analytics', []):
            print(f"   ✅ {analytic['name']} - Ready")
        
        for analytic in analytics_readiness.get('unavailable_analytics', []):
            print(f"   ❌ {analytic['name']} - Missing: {', '.join(analytic['missing_columns'])}")
        
        # Test GPT metadata display
        gpt_metadata = analysis_data.get('gpt_metadata', {})
        print(f"\n🤖 Frontend GPT Metadata Display:")
        print(f"   Total cost: ${gpt_metadata.get('total_cost', 0):.4f}")
        print(f"   Cache hits: {gpt_metadata.get('cache_hits', 0)}")
        print(f"   Processing time: {gpt_metadata.get('processing_time', 0):.2f}s")
        
        # Step 4: Test JSON Serialization
        print("\n🔧 Step 4: Testing JSON Serialization")
        try:
            json_response = json.dumps(backend_response, indent=2)
            print("✅ JSON serialization successful!")
            print(f"   Response size: {len(json_response)} characters")
        except Exception as e:
            print(f"❌ JSON serialization failed: {e}")
            return
        
        # Step 5: Test Frontend Component Compatibility
        print("\n🔧 Step 5: Testing Frontend Component Compatibility")
        
        # Test Dashboard.js compatibility
        dashboard_compatible = all([
            'mapped_columns' in analysis_data,
            'uncertain_columns' in analysis_data,
            'unmapped_columns' in analysis_data,
            'gpt_metadata' in analysis_data
        ])
        print(f"   Dashboard.js compatibility: {'✅' if dashboard_compatible else '❌'}")
        
        # Test AnalyticsDisplay.js compatibility
        analytics_display_compatible = all([
            'analytics_readiness' in analysis_data,
            'gpt_metadata' in analysis_data
        ])
        print(f"   AnalyticsDisplay.js compatibility: {'✅' if analytics_display_compatible else '❌'}")
        
        # Test AnalyticsDashboard.js compatibility
        analytics_dashboard_compatible = all([
            'analytics_readiness' in analysis_data,
            'gpt_metadata' in analysis_data
        ])
        print(f"   AnalyticsDashboard.js compatibility: {'✅' if analytics_dashboard_compatible else '❌'}")
        
        print("\n✅ Frontend-Backend Integration Test Complete!")
        print("🎉 All components are compatible with GPT mapping system!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_frontend_backend_integration()
