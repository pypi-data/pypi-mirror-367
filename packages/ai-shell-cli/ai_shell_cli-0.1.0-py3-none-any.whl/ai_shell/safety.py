"""
Safety checker for shell commands.
Detects potentially dangerous commands and patterns.
"""

import re
from typing import List, Tuple


class SafetyChecker:
    def __init__(self):
        # Dangerous command patterns
        self.dangerous_patterns = [
            # File deletion commands
            r'\brm\s+.*-rf?\b',
            r'\brm\s+.*--force\b',
            r'\brmdir\s+.*-rf?\b',
            
            # System modification commands
            r'\bsudo\b',
            r'\bsu\b',
            r'\bchmod\s+.*777\b',
            r'\bchown\s+.*root\b',
            
            # Network and system commands
            r'\bdd\b',
            r'\bformat\b',
            r'\binit\s+\d',
            r'\bshutdown\b',
            r'\breboot\b',
            r'\bhalt\b',
            
            # Shell injection patterns
            r'`.*`',
            r'\$\(.*\)',
            r'&&.*&&',
            r'\|\|.*\|\|',
            
            # Fork bomb patterns
            r':\(\)\s*\{\s*:\|\s*:\s*&\s*\};',
            r':\(\)\s*\{\s*:\|\s*:\s*&\s*\};:',
            
            # Dangerous redirects
            r'>\s*/dev/',
            r'>>\s*/dev/',
            r'>\s*/proc/',
            r'>>\s*/proc/',
            
            # Overwrite system files
            r'>\s*/etc/',
            r'>>\s*/etc/',
            r'>\s*/boot/',
            r'>>\s*/boot/',
            r'>\s*/usr/',
            r'>>\s*/usr/',
            
            # Dangerous file operations
            r'\bcat\s+.*>\s*.*\b',
            r'\becho\s+.*>\s*.*\b',
            r'\bprintf\s+.*>\s*.*\b',
            
            # Process management
            r'\bkillall\b',
            r'\bpkill\s+.*-9\b',
            r'\bkill\s+.*-9\b',
            
            # Network commands
            r'\bwget\s+.*\|\s*bash\b',
            r'\bcurl\s+.*\|\s*bash\b',
            r'\bwget\s+.*\|\s*sh\b',
            r'\bcurl\s+.*\|\s*sh\b',
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns]
        
        # Whitelist of safe commands (even if they match dangerous patterns)
        self.safe_commands = [
            'rm --help',
            'sudo --help',
            'chmod --help',
            'chown --help',
            'dd --help',
            'kill --help',
            'killall --help',
        ]
    
    def is_safe(self, command: str) -> bool:
        """
        Check if a command is safe to execute.
        Returns True if safe, False if potentially dangerous.
        """
        if not command or not command.strip():
            return False
        
        # Check if it's a help command
        if any(safe in command.lower() for safe in self.safe_commands):
            return True
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(command):
                return False
        
        # Additional safety checks
        if self._has_dangerous_combinations(command):
            return False
        
        return True
    
    def _has_dangerous_combinations(self, command: str) -> bool:
        """Check for dangerous command combinations."""
        command_lower = command.lower()
        
        # Check for rm with wildcards
        if 'rm' in command_lower and any(char in command for char in ['*', '?', '[']):
            return True
        
        # Check for commands that could affect the entire system
        if any(cmd in command_lower for cmd in ['rm -rf /', 'rm -rf /*', 'rm -rf /home']):
            return True
        
        # Check for commands that could delete user data
        if 'rm -rf' in command_lower and any(path in command_lower for path in ['~', '$HOME', '/home']):
            return True
        
        return False
    
    def get_safety_report(self, command: str) -> Tuple[bool, List[str]]:
        """
        Get a detailed safety report for a command.
        Returns (is_safe, list_of_warnings)
        """
        warnings = []
        
        if not command or not command.strip():
            warnings.append("Empty or invalid command")
            return False, warnings
        
        # Check for dangerous patterns
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(command):
                warnings.append(f"Matches dangerous pattern: {self.dangerous_patterns[i]}")
        
        # Check for dangerous combinations
        if self._has_dangerous_combinations(command):
            warnings.append("Contains dangerous command combinations")
        
        is_safe = len(warnings) == 0
        return is_safe, warnings
    
    def get_safe_alternatives(self, command: str) -> List[str]:
        """
        Suggest safer alternatives for dangerous commands.
        """
        command_lower = command.lower()
        alternatives = []
        
        if 'rm -rf' in command_lower:
            alternatives.append("Use 'rm -i' for interactive deletion")
            alternatives.append("Use 'trash' command for safe deletion")
            alternatives.append("Use 'mv' to move files to a temporary directory")
        
        if 'sudo' in command_lower:
            alternatives.append("Consider if you really need sudo")
            alternatives.append("Use 'sudo -l' to see what you can run")
        
        if 'chmod 777' in command_lower:
            alternatives.append("Use more restrictive permissions like 644 or 755")
            alternatives.append("Use 'chmod +x' for executable files")
        
        if 'dd' in command_lower:
            alternatives.append("Consider using 'cp' or 'rsync' instead")
            alternatives.append("Use 'dd' with 'conv=noerror' for safer operation")
        
        return alternatives 