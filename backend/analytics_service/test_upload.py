#!/usr/bin/env python3
"""
Test script to simulate file upload and see what happens
"""

import requests
import json
import os

def test_upload():
    """Test file upload to the server"""
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5002/api/health", timeout=5)
        print("✅ Server is running")
    except:
        print("❌ Server is not running")
        return
    
    # Test file upload
    file_path = "../../TEST FILES/sales_data.csv"
    
    if not os.path.exists(file_path):
        print(f"❌ Test file not found: {file_path}")
        return
    
    print(f"📁 Uploading file: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                "http://localhost:5002/api/files/upload-clean",
                files=files,
                timeout=30
            )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful!")
            print(f"📊 Charts generated: {len(data.get('analysis', {}).get('charts', []))}")
            print(f"📊 Analytics readiness: {data.get('analytics_readiness', {})}")
            
            if data.get('analysis', {}).get('charts'):
                for i, chart in enumerate(data['analysis']['charts']):
                    print(f"   Chart {i+1}: {chart.get('title', 'Unknown')} - {chart.get('type', 'Unknown')}")
            else:
                print("   ❌ No charts generated!")
        else:
            print(f"❌ Upload failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during upload: {e}")

if __name__ == "__main__":
    test_upload()
