"""
Command executor for safely running shell commands and logging interactions.
"""

import os
import subprocess
import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    exit_code: int
    output: str
    error: str
    command: str
    original_query: str
    timestamp: datetime.datetime


class CommandExecutor:
    def __init__(self):
        # Allow custom history file path from environment
        history_path = os.getenv("AISH_HISTORY_FILE", "~/.ai_shell_history.log")
        self.history_file = Path(history_path).expanduser()
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """Ensure the history file exists."""
        if not self.history_file.exists():
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            self.history_file.touch()
    
    def execute(self, command: str, original_query: str) -> CommandResult:
        """
        Execute a shell command and return the result.
        Also logs the command to history.
        """
        timestamp = datetime.datetime.now()
        
        # Log the command
        self._log_command(command, original_query, timestamp)
        
        try:
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return CommandResult(
                success=result.returncode == 0,
                exit_code=result.returncode,
                output=result.stdout,
                error=result.stderr,
                command=command,
                original_query=original_query,
                timestamp=timestamp
            )
            
        except subprocess.TimeoutExpired:
            return CommandResult(
                success=False,
                exit_code=-1,
                output="",
                error="Command timed out after 5 minutes",
                command=command,
                original_query=original_query,
                timestamp=timestamp
            )
        except Exception as e:
            return CommandResult(
                success=False,
                exit_code=-1,
                output="",
                error=str(e),
                command=command,
                original_query=original_query,
                timestamp=timestamp
            )
    
    def _log_command(self, command: str, original_query: str, timestamp: datetime.datetime):
        """Log the command to the history file."""
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                log_entry = {
                    'timestamp': timestamp.isoformat(),
                    'original_query': original_query,
                    'generated_command': command,
                    'working_directory': os.getcwd(),
                    'user': os.getenv('USER', 'unknown')
                }
                
                # Write as JSON for easy parsing
                f.write(f"{json.dumps(log_entry)}\n")
                
        except Exception as e:
            # Don't fail the main execution if logging fails
            print(f"Warning: Failed to log command: {e}")
    
    def get_history(self, limit: int = 50) -> list:
        """Get recent command history."""
        history = []
        
        try:
            if not self.history_file.exists():
                return history
            
            with open(self.history_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Parse the last N entries
            for line in lines[-limit:]:
                try:
                    entry = json.loads(line.strip())
                    history.append(entry)
                except json.JSONDecodeError:
                    continue  # Skip malformed entries
                    
        except Exception as e:
            print(f"Warning: Failed to read history: {e}")
        
        return history
    
    def clear_history(self):
        """Clear the command history."""
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            self._ensure_history_file()
        except Exception as e:
            print(f"Warning: Failed to clear history: {e}")


# Import json at the top level for the logging functionality
import json 