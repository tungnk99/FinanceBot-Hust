#!/usr/bin/env python3
"""
Simple API Test for FinanceBot
Test API cơ bản với các test cases đơn giản
"""
import requests
import json
import time

# API Configuration
API_URL = "http://0.0.0.0:8000/chat"

# Simple test cases
TEST_CASES = [
    {
        "name": "Test 1",
        "message": "lũ lụt ở huế",
        "context": {}
    }
]

def test_api(test_case):
    """Test a single API call"""
    payload = {
        "message": test_case["message"],
        "session_id": f"test_{int(time.time())}",
        "user_id": "test_user",
        "context": test_case["context"]
    }
    
    try:
        print(f"🧪 Testing: {test_case['name']}")
        print(f"💬 Message: {test_case['message']}")
        
        start_time = time.time()
        response = requests.post(API_URL, json=payload, timeout=300)
        execution_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS - Time: {execution_time:.2f}s")
            print(f"🤖 Agent: {result.get('selected_agent', {}).get('agent_name', 'Unknown')}")
            print(f"📥 Full Response:")
            print(f"{result.get('response', '')}")
            print(f"📊 Full Result:")
            print(f"{json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            print(f"📥 Error: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False

def run_all_tests():
    """Run all test cases"""
    print("🚀 FINANCEBOT SIMPLE API TEST")
    print("=" * 50)
    
    passed = 0
    total = len(TEST_CASES)
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{total}] {test_case['name']}")
        print("-" * 30)
        
        if test_api(test_case):
            passed += 1
        
        time.sleep(1)  # Delay between requests
    
    # Summary
    print(f"\n🎯 TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed!")

def test_single_case(message: str, deep_research: bool = False, attach_files: list = []):
    """Test a single case interactively"""
    print("🧪 SINGLE CASE TEST")
    print("=" * 30)
    
    test_case = {
        "name": "Custom Test",
        "message": message,
        "context": {"deep_research": deep_research, "attach_files": attach_files}
    }
    
    test_api(test_case)

def main():
    """Main function"""
    
    # run_all_tests()
    # message = "Hi"
    # message = "Giá VIC hôm nay là bao nhiêu?"
    # message = "Thị trường chứng khoán hôm nay thế nào?"
    # message = "Phân tích kỹ thuật cổ phiếu VIC"
    # message = "Phân tích cơ bản cổ phiếu VIC"
    # message = "Tìm kiếm cho tôi các thông tin về cổ phiếu VIC"
    # message = "Bạn có thể giúp gì cho tôi?"
    # message = "Tôi cần tư vấn về đầu tư"
    # message = "Giá AAPL hôm nay thế nào nhỉ?"
    # message = "Phân tích xu hướng VN-Index trong 6 tháng qua"
    # message = "Phân tích kỹ thuật cổ phiếu VIC"
    message = "Phân tích MACD cho HPG"
    # message = "Vẽ Bollinger Bands cho VIC"
    # message = "Phân tích cơ bản cổ phiếu VIC"
    # message = "Phân tích báo cáo tài chính quý 3 của VIC"
    # message = "Đánh giá rủi ro đầu tư vào VIC"
    # message = "Rủi ro thanh khoản của VCB"
    # message = "Vẽ biểu đồ giá VIC 6 tháng qua"
    # message = "Vẽ biểu đồ kỹ thuật với RSI và MACD cho VIC"

    test_single_case(message)


if __name__ == "__main__":
    main()
