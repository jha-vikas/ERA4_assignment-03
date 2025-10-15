#!/usr/bin/env python3
"""
Test script to debug Gemini API connection
Run this on your EC2 instance to test the API
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_api():
    print("🔍 Testing Gemini API Configuration...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key exists
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
        print("   Make sure your .env file exists and contains:")
        print("   GEMINI_API_KEY=your_actual_api_key_here")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Check API key format
    if not api_key.startswith('AIza'):
        print("❌ ERROR: API key format is invalid")
        print("   Gemini API keys should start with 'AIza'")
        return False
    
    print("✅ API Key format is valid")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini model configured successfully")
        
        # Test a simple request
        print("🧪 Testing API call...")
        response = model.generate_content("Say 'Hello, this is a test'")
        
        if response and response.text:
            print(f"✅ API call successful!")
            print(f"   Response: {response.text.strip()}")
            return True
        else:
            print("❌ ERROR: API call returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: API call failed: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    if success:
        print("\n🎉 Gemini API is working correctly!")
        sys.exit(0)
    else:
        print("\n💥 Gemini API test failed!")
        sys.exit(1)
