#!/usr/bin/env python3
"""
Basic test script for AI-shell interactive shell.
Tests core functionality without requiring API key.
"""

import sys
import os
from ai_shell.safety import SafetyChecker
from ai_shell.executor import CommandExecutor

def test_safety_checker():
    """Test the safety checker functionality."""
    print("🧪 Testing Safety Checker...")
    
    safety = SafetyChecker()
    
    # Test safe commands
    safe_commands = [
        "ls -la",
        "find . -name '*.txt'",
        "grep -r 'hello' .",
        "du -sh *",
        "cat file.txt",
        "echo 'hello world'",
        "find . -type f -size +100M",
        "free -h",
        "df -h"
    ]
    
    for cmd in safe_commands:
        is_safe = safety.is_safe(cmd)
        print(f"  ✅ {cmd}: {'SAFE' if is_safe else 'UNSAFE'}")
        assert is_safe, f"Command should be safe: {cmd}"
    
    # Test dangerous commands
    dangerous_commands = [
        "rm -rf /",
        "sudo rm -rf /",
        "chmod 777 /etc/passwd",
        ":(){ :|:& };:",
        "dd if=/dev/zero of=/dev/sda",
        "killall -9 process",
        "rm -rf ~/*",
        "sudo shutdown -h now"
    ]
    
    for cmd in dangerous_commands:
        is_safe = safety.is_safe(cmd)
        print(f"  ⚠️  {cmd}: {'SAFE' if is_safe else 'UNSAFE'}")
        assert not is_safe, f"Command should be unsafe: {cmd}"
    
    print("✅ Safety checker tests passed!")

def test_executor():
    """Test the command executor functionality."""
    print("\n🧪 Testing Command Executor...")
    
    executor = CommandExecutor()
    
    # Test history file creation
    history_file = executor.history_file
    print(f"  📁 History file: {history_file}")
    assert history_file.exists(), "History file should be created"
    
    # Test safe command execution
    result = executor.execute("echo 'test'", "test query")
    print(f"  ✅ Command execution: {'SUCCESS' if result.success else 'FAILED'}")
    assert result.success, "Simple echo command should succeed"
    assert "test" in result.output, "Output should contain 'test'"
    
    print("✅ Command executor tests passed!")

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing Imports...")
    
    try:
        from ai_shell.llm import LLMClient
        print("  ✅ LLMClient imported successfully")
    except Exception as e:
        print(f"  ⚠️  LLMClient import failed (expected without API key): {e}")
    
    try:
        from ai_shell.safety import SafetyChecker
        print("  ✅ SafetyChecker imported successfully")
    except Exception as e:
        print(f"  ❌ SafetyChecker import failed: {e}")
        return False
    
    try:
        from ai_shell.executor import CommandExecutor
        print("  ✅ CommandExecutor imported successfully")
    except Exception as e:
        print(f"  ❌ CommandExecutor import failed: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting AI-shell interactive shell tests...\n")
    
    # Test imports
    if not test_imports():
        print("❌ Import tests failed!")
        sys.exit(1)
    
    # Test safety checker
    try:
        test_safety_checker()
    except Exception as e:
        print(f"❌ Safety checker test failed: {e}")
        sys.exit(1)
    
    # Test executor
    try:
        test_executor()
    except Exception as e:
        print(f"❌ Executor test failed: {e}")
        sys.exit(1)
    
    print("\n🎉 All tests passed! The AI-shell interactive shell is ready to use.")
    print("\n📝 Next steps:")
    print("1. Set your OPENAI_API_KEY environment variable")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Start the shell: python main.py")
    print("4. Try: 'find all PDF files' or 'show disk usage'")

if __name__ == "__main__":
    main() 