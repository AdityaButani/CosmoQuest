#!/usr/bin/env python3
"""
Integration test for the complete CosmosQuest API management system
"""

import requests
import json
import time

def test_api_status():
    """Test the API status endpoint"""
    try:
        response = requests.get("http://127.0.0.1:5000/api/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Status endpoint working!")
            print(f"   Total keys: {len(data['data']['keys'])}")
            print(f"   Available keys: {sum(1 for k in data['data']['keys'] if k['available'])}")
            print(f"   Total requests so far: {data['data']['stats']['total_requests']}")
            return True
        else:
            print(f"❌ API Status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Status error: {str(e)}")
        return False

def test_quest_generation():
    """Test quest generation through the web interface"""
    try:
        # Start a session
        session = requests.Session()
        
        # Get the main page first
        response = session.get("http://127.0.0.1:5000/", timeout=10)
        if response.status_code != 200:
            print(f"❌ Main page failed: {response.status_code}")
            return False
        
        # Generate a quest
        print("🧪 Testing quest generation...")
        quest_data = {"topic": "Artificial Intelligence"}
        response = session.post("http://127.0.0.1:5000/generate-quest", data=quest_data, timeout=30)
        
        if response.status_code == 302:  # Redirect expected
            print("✅ Quest generation successful!")
            print("   Redirected to quest page")
            return True
        else:
            print(f"❌ Quest generation failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Quest generation error: {str(e)}")
        return False

def test_dashboard():
    """Test the admin dashboard"""
    try:
        response = requests.get("http://127.0.0.1:5000/admin/api-dashboard", timeout=10)
        if response.status_code == 200 and "CosmosQuest - API Key Dashboard" in response.text:
            print("✅ Admin dashboard working!")
            return True
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard error: {str(e)}")
        return False

def main():
    print("CosmosQuest Integration Test")
    print("=" * 40)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    tests = [
        ("API Status", test_api_status),
        ("Admin Dashboard", test_dashboard),
        ("Quest Generation", test_quest_generation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n{'='*40}")
    print(f"Integration Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        print("\n✨ Your CosmosQuest API management system is working correctly!")
        print("📊 Visit http://127.0.0.1:5000/admin/api-dashboard to monitor your API keys")
        print("🚀 Visit http://127.0.0.1:5000/ to start generating quests")
    else:
        print("⚠️ Some tests failed. Check the server logs.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
