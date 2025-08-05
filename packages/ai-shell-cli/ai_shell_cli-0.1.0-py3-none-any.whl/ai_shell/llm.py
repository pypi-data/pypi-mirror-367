"""
LLM client for Google Gemini API integration.
Handles command generation and explanation.
"""

import os
import json
import requests
from typing import Optional

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
        self.max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "500"))
        self.timeout = int(os.getenv("GEMINI_TIMEOUT", "30"))
        
    def _make_request(self, messages: list) -> Optional[str]:
        """Make a request to Gemini API."""
        headers = {
            "Content-Type": "application/json"
        }
        
        # Convert messages to Gemini format
        # For command generation, we'll send the system prompt + user query as a single message
        if len(messages) >= 2:
            system_msg = messages[0]["content"]
            user_msg = messages[1]["content"]
            combined_prompt = f"{system_msg}\n\nUser request: {user_msg}"
        else:
            combined_prompt = messages[0]["content"]
        
        data = {
            "contents": [
                {
                    "parts": [{"text": combined_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Unexpected API response format: {e}")
    
    def generate_command(self, query: str) -> str:
        """Generate a shell command from natural language query."""
        system_prompt = """You are a shell command generator. Your ONLY job is to convert natural language requests into safe shell commands.

CRITICAL RULES:
1. Generate ONLY the shell command - no explanations, no text, no markdown
2. Return ONLY the command that can be executed directly
3. Use safe, standard Unix/Linux commands
4. Avoid dangerous commands like rm -rf, sudo, or commands that could damage the system
5. If the request is unclear or potentially dangerous, return "SAFETY_CHECK_FAILED"
6. Keep commands simple and readable
7. Use proper quoting for file paths with spaces

EXAMPLES:
- "find all PDF files" → find . -name "*.pdf"
- "list files modified today" → find . -type f -mtime -1
- "show disk usage" → du -sh *
- "search for text in files" → grep -r "text" .
- "list all files" → ls -la
- "find large files" → find . -type f -size +100M
- "list python files" → find . -name "*.py"
- "show memory usage" → free -h
- "check disk space" → df -h
- "delete all files" → SAFETY_CHECK_FAILED

IMPORTANT: Return ONLY the command, nothing else.

Query: {query}"""

        messages = [
            {"role": "system", "content": system_prompt.format(query=query)},
            {"role": "user", "content": query}
        ]
        
        result = self._make_request(messages)
        
        if result and result != "SAFETY_CHECK_FAILED":
            # Clean up the response - remove any markdown formatting
            result = result.strip()
            if result.startswith("```"):
                result = result.split("\n", 1)[1]
            if result.endswith("```"):
                result = result.rsplit("\n", 1)[0]
            return result.strip()
        
        raise Exception("Command generation failed safety check")
    
    def explain_command(self, command: str, original_query: str) -> str:
        """Explain what a shell command does."""
        system_prompt = """You are a helpful assistant that explains shell commands in simple terms.

Explain what the command does, what each part means, and what the user can expect to see as output.
Keep explanations clear and beginner-friendly.

Command: {command}
Original request: {original_query}"""

        messages = [
            {"role": "system", "content": system_prompt.format(command=command, original_query=original_query)},
            {"role": "user", "content": f"Please explain this command: {command}"}
        ]
        
        result = self._make_request(messages)
        return result or "Unable to generate explanation." 