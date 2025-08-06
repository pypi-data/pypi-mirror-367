#!/usr/bin/env python3
"""
Simple test to verify Agent Zero Lite imports work correctly
"""

def test_core_imports():
    print("Testing core imports...")
    
    try:
        import models
        print("✓ models.py imported successfully")
    except Exception as e:
        print(f"✗ models.py import failed: {e}")
        return False
    
    try:
        from agent import Agent, AgentContext, AgentConfig
        print("✓ agent.py core classes imported successfully")
    except Exception as e:
        print(f"✗ agent.py import failed: {e}")
        return False
    
    try:
        import initialize
        print("✓ initialize.py imported successfully")
    except Exception as e:
        print(f"✗ initialize.py import failed: {e}")
        return False
    
    return True

def test_tool_imports():
    print("\nTesting tool imports...")
    
    try:
        from agent_zero_lite.python.tools.response import ResponseTool
        print("✓ response tool imported successfully")
    except Exception as e:
        print(f"✗ response tool import failed: {e}")
        return False
    
    try:
        from agent_zero_lite.python.tools.code_execution_tool import CodeExecution
        print("✓ code execution tool imported successfully")
    except Exception as e:
        print(f"✗ code execution tool import failed: {e}")
        return False
    
    try:
        from agent_zero_lite.python.tools.memory_save import MemorySave
        print("✓ memory save tool imported successfully")
    except Exception as e:
        print(f"✗ memory save tool import failed: {e}")
        return False
    
    return True

def test_helper_imports():
    print("\nTesting helper imports...")
    
    try:
        from agent_zero_lite.python.helpers.tool import Tool, Response
        print("✓ tool helper imported successfully")
    except Exception as e:
        print(f"✗ tool helper import failed: {e}")
        return False
    
    try:
        from agent_zero_lite.python.helpers.print_style import PrintStyle
        print("✓ print style helper imported successfully")
    except Exception as e:
        print(f"✗ print style helper import failed: {e}")
        return False
    
    try:
        from agent_zero_lite.python.helpers.settings import get_settings
        print("✓ settings helper imported successfully")
    except Exception as e:
        print(f"✗ settings helper import failed: {e}")
        return False
    
    return True

def test_litellm():
    print("\nTesting LiteLLM integration...")
    
    try:
        import litellm
        print("✓ LiteLLM imported successfully")
    except Exception as e:
        print(f"✗ LiteLLM import failed: {e}")
        return False
    
    try:
        from agent_zero_lite.models import ModelConfig, ModelType
        print("✓ Model configuration classes imported successfully")
    except Exception as e:
        print(f"✗ Model config import failed: {e}")
        return False
    
    return True

def main():
    print("=" * 50)
    print("AGENT ZERO LITE - IMPORT TEST")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_core_imports()
    all_passed &= test_tool_imports()
    all_passed &= test_helper_imports() 
    all_passed &= test_litellm()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Agent Zero Lite is ready!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your API keys to .env")
        print("3. Run: python run_ui.py")
        print("4. Open: http://localhost:50001")
    else:
        print("❌ SOME TESTS FAILED - Check the errors above")
        print("\nYou may need to:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Fix import issues")
    print("=" * 50)
    
    return all_passed

if __name__ == "__main__":
    main()