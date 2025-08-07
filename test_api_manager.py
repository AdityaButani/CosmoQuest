#!/usr/bin/env python3
"""
Test script for the Groq API Manager

This script tests the robust fallback mechanism and key rotation.
"""

import sys
import os
import json
import time
from datetime import datetime

# Add the current directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from groq_api_manager import get_groq_manager
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_basic_functionality():
    """Test basic API manager functionality"""
    print("=" * 60)
    print("Testing Basic Functionality")
    print("=" * 60)
    
    manager = get_groq_manager()
    
    # Test simple request
    prompt = """You are an educational content creator. Create a short lesson about photosynthesis.

Respond with valid JSON in this format:
{
    "title": "Introduction to Photosynthesis",
    "content": "Brief educational content about photosynthesis (100 words)",
    "key_points": ["Point 1", "Point 2", "Point 3"]
}"""
    
    print("Making test request...")
    result = manager.make_request(prompt, quest_num=1)
    
    if result:
        print("✅ Request successful!")
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Content length: {len(result.get('content', ''))}")
    else:
        print("❌ Request failed!")
    
    return result is not None

def test_key_rotation():
    """Test key rotation under load"""
    print("\n" + "=" * 60)
    print("Testing Key Rotation")
    print("=" * 60)
    
    manager = get_groq_manager()
    
    # Make multiple requests to test rotation
    success_count = 0
    total_requests = 5
    
    for i in range(total_requests):
        prompt = f"""Create educational content about topic {i+1}.
        
Respond with valid JSON:
{{"title": "Topic {i+1}", "content": "Educational content about topic {i+1}"}}"""
        
        print(f"Request {i+1}/{total_requests}...")
        result = manager.make_request(prompt, quest_num=(i % 5) + 1)
        
        if result:
            success_count += 1
            print(f"  ✅ Success")
        else:
            print(f"  ❌ Failed")
        
        # Small delay between requests
        time.sleep(0.5)
    
    print(f"\nRotation test results: {success_count}/{total_requests} successful")
    return success_count > 0

def test_error_handling():
    """Test error handling with invalid prompts"""
    print("\n" + "=" * 60)
    print("Testing Error Handling")
    print("=" * 60)
    
    manager = get_groq_manager()
    
    # Test with a prompt that might cause issues
    invalid_prompt = "Generate invalid JSON that will break parsing: {{{"
    
    print("Testing with invalid prompt...")
    result = manager.make_request(invalid_prompt)
    
    if result is None:
        print("✅ Error handling working - correctly returned None for invalid prompt")
        return True
    else:
        print("⚠️ Unexpected success with invalid prompt")
        return False

def display_status():
    """Display current API manager status"""
    print("\n" + "=" * 60)
    print("API Manager Status")
    print("=" * 60)
    
    manager = get_groq_manager()
    status = manager.get_status()
    
    print(f"Timestamp: {status['timestamp']}")
    print(f"Total Requests: {status['stats']['total_requests']}")
    print(f"Successful Requests: {status['stats']['successful_requests']}")
    print(f"Failed Requests: {status['stats']['failed_requests']}")
    print(f"Key Switches: {status['stats']['key_switches']}")
    print(f"Rate Limit Hits: {status['stats']['rate_limit_hits']}")
    
    print("\nKey Status:")
    for key in status['keys']:
        availability = "✅" if key['available'] else "❌"
        print(f"  {availability} {key['name']}: {key['status']} (Success Rate: {key['success_rate']:.1%})")
        if key['last_error']:
            print(f"     Last Error: {key['last_error'][:100]}...")

def test_quest_specific_configs():
    """Test quest-specific configurations"""
    print("\n" + "=" * 60)
    print("Testing Quest-Specific Configurations")
    print("=" * 60)
    
    manager = get_groq_manager()
    
    # Test each quest type
    for quest_num in [1, 2, 3, 4, 5]:
        prompt = f"""Create educational content for Quest {quest_num}.
        
Respond with valid JSON:
{{"title": "Quest {quest_num} Content", "content": "Educational content for quest {quest_num}"}}"""
        
        print(f"Testing Quest {quest_num}...")
        result = manager.make_request(prompt, quest_num=quest_num)
        
        if result:
            print(f"  ✅ Quest {quest_num} successful")
        else:
            print(f"  ❌ Quest {quest_num} failed")

def main():
    """Run all tests"""
    print("CosmosQuest - Groq API Manager Test Suite")
    print(f"Started at: {datetime.now()}")
    
    try:
        # Run tests
        basic_success = test_basic_functionality()
        rotation_success = test_key_rotation()
        error_handling_success = test_error_handling()
        
        # Test quest-specific features
        test_quest_specific_configs()
        
        # Display final status
        display_status()
        
        # Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        tests = [
            ("Basic Functionality", basic_success),
            ("Key Rotation", rotation_success),
            ("Error Handling", error_handling_success),
        ]
        
        passed = sum(1 for _, success in tests if success)
        total = len(tests)
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! API manager is working correctly.")
            return 0
        else:
            print("⚠️ Some tests failed. Check the logs above.")
            return 1
            
    except Exception as e:
        print(f"❌ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
