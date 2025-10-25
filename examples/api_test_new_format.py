#!/usr/bin/env python3
"""
Test script for the updated API format with new context parameters
"""
import requests
import json

# API endpoint
API_URL = "http://0.0.0.0:8000/chat"

# Test data with new context format
test_data = {
    "message": "string",
    "session_id": "string",
    "user_id": "string",
    "context": {
        "deep_research": False,
        "attach_files": []
    }
}

def test_api_call():
    """Test the API with new context format"""
    try:
        print("🚀 Testing API with new context format...")
        print(f"📤 Request data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            API_URL,
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json=test_data,
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"📥 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ API call failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_curl_command():
    """Generate the equivalent curl command"""
    curl_command = f"""curl -X 'POST' \\
  '{API_URL}' \\
  -H 'accept: application/json' \\
  -H 'Content-Type: application/json' \\
  -d '{json.dumps(test_data, ensure_ascii=False)}'"""
    
    print("\n🔧 Equivalent curl command:")
    print(curl_command)

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Testing FinanceBot API with new context format")
    print("=" * 60)
    
    test_curl_command()
    print("\n" + "=" * 60)
    test_api_call()
