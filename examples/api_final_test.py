#!/usr/bin/env python3
"""
Final test script for the updated API format with new context parameters
"""
import requests
import json

# API endpoint
API_URL = "http://0.0.0.0:8000/chat"

def test_default_format():
    """Test with default format as requested"""
    test_data = {
        "message": "string",
        "session_id": "string", 
        "user_id": "string",
        "context": {
            "deep_research": False,
            "attach_files": []
        }
    }
    
    print("🧪 Testing API with DEFAULT format:")
    print(f"📤 Request: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(API_URL, json=test_data, timeout=30)
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"📥 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_real_query():
    """Test with real query"""
    test_data = {
        "message": "giá VIC hôm nay là bao nhiêu",
        "session_id": "test_session_123",
        "user_id": "test_user_456", 
        "context": {
            "deep_research": True,
            "attach_files": []
        }
    }
    
    print("\n🧪 Testing API with REAL QUERY:")
    print(f"📤 Request: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(API_URL, json=test_data, timeout=30)
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"📥 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def show_curl_examples():
    """Show equivalent curl commands"""
    print("\n🔧 Equivalent curl commands:")
    
    print("\n1. Default format:")
    default_curl = """curl -X 'POST' \\
  'http://0.0.0.0:8000/chat' \\
  -H 'accept: application/json' \\
  -H 'Content-Type: application/json' \\
  -d '{
  "message": "string",
  "session_id": "string",
  "user_id": "string",
  "context": {
    "deep_research": false,
    "attach_files": []
  }
}'"""
    print(default_curl)
    
    print("\n2. Real query format:")
    real_curl = """curl -X 'POST' \\
  'http://0.0.0.0:8000/chat' \\
  -H 'accept: application/json' \\
  -H 'Content-Type: application/json' \\
  -d '{
  "message": "giá VIC hôm nay là bao nhiêu",
  "session_id": "string",
  "user_id": "string",
  "context": {
    "deep_research": true,
    "attach_files": []
  }
}'"""
    print(real_curl)

if __name__ == "__main__":
    print("=" * 80)
    print("🎯 FinanceBot API - Final Test with New Context Format")
    print("=" * 80)
    
    show_curl_examples()
    
    print("\n" + "=" * 80)
    test_default_format()
    
    print("\n" + "=" * 80)
    test_real_query()
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
