#!/usr/bin/env python3
"""
Test script to verify the application works correctly
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import gradio as gr
        print("✅ Gradio imported successfully")
        
        from research_manager import ProductAnalysisManager
        print("✅ ResearchManager imported successfully")
        
        from feature_agent import handle_feature_request
        print("✅ FeatureAgent imported successfully")
        
        from agents import Agent, Runner, function_tool
        print("✅ OpenAI Agents imported successfully")
        
        # Test optional dependencies
        try:
            import sendgrid
            print("✅ SendGrid imported successfully (optional)")
        except ImportError:
            print("⚠️  SendGrid not available (optional dependency)")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment_variables():
    """Test that required environment variables are set"""
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please set these in your Hugging Face Spaces secrets")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_gradio_interface():
    """Test that the Gradio interface can be created"""
    try:
        from app import create_interface
        ui = create_interface()
        print("✅ Gradio interface created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating Gradio interface: {e}")
        return False

async def test_async_functions():
    """Test that async functions work correctly"""
    try:
        from app import Assistant_conversation
        # Test with a simple message
        response = await Assistant_conversation("Hello, test message", [])
        print("✅ Async conversation function works")
        return True
    except Exception as e:
        print(f"❌ Error testing async functions: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Alex Product Manager Application...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Variables Test", test_environment_variables),
        ("Gradio Interface Test", test_gradio_interface),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    # Test async functions
    print(f"\n🔍 Running Async Functions Test...")
    try:
        asyncio.run(test_async_functions())
        passed += 1
    except Exception as e:
        print(f"❌ Async Functions Test failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total + 1} tests passed")
    
    if passed == total + 1:
        print("🎉 All tests passed! The application is ready for Hugging Face Spaces.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
