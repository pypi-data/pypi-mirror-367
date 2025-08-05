#!/usr/bin/env python3
"""
Test script to verify command generation works correctly.
"""

import os
from dotenv import load_dotenv
from llm import LLMClient

# Load environment variables
load_dotenv()

def test_command_generation():
    """Test command generation with various queries."""
    try:
        llm = LLMClient()
        
        test_queries = [
            "list all files",
            "find PDF files",
            "show disk usage",
            "check memory usage"
        ]
        
        print("🧪 Testing command generation...")
        
        for query in test_queries:
            print(f"\n📝 Query: {query}")
            try:
                command = llm.generate_command(query)
                print(f"💡 Generated: {command}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to initialize LLM client: {e}")

if __name__ == "__main__":
    test_command_generation() 