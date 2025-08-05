#!/usr/bin/env python3
"""
AI-shell - AI-Powered Interactive Shell
Accepts natural language input and returns executable commands.
"""

import os
import sys
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text

from .llm import LLMClient
from .executor import CommandExecutor
from .safety import SafetyChecker


class AIShell:
    def __init__(self):
        self.console = Console()
        self.llm = LLMClient()
        self.executor = CommandExecutor()
        self.safety = SafetyChecker()
        self.running = True
        
    def print_banner(self):
        """Display the shell banner."""
        banner = Text("🧠 AI-shell - AI-Powered Interactive Shell", style="bold blue")
        subtitle = Text("Type natural language to get shell commands", style="dim")
        
        self.console.print(Panel(
            banner + "\n" + subtitle,
            border_style="blue",
            padding=(1, 2)
        ))
        self.console.print()
        
    def get_prompt(self) -> str:
        """Get user input with the AI-shell prompt."""
        return Prompt.ask("AI-shell> ", console=self.console)
        
    def process_natural_language(self, user_input: str) -> Optional[str]:
        """Process natural language input and return shell command."""
        try:
            self.console.print("🤖 Generating command...", style="dim")
            command = self.llm.generate_command(user_input)
            return command
        except Exception as e:
            self.console.print(f"❌ Error generating command: {e}", style="red")
            return None
            
    def explain_command(self, command: str, original_query: str) -> str:
        """Get explanation for the generated command."""
        try:
            explanation = self.llm.explain_command(command, original_query)
            return explanation
        except Exception as e:
            return f"Unable to generate explanation: {e}"
            
    def check_safety(self, command: str) -> tuple[bool, list[str]]:
        """Check if command is safe and return warnings."""
        is_safe = self.safety.is_safe(command)
        warnings = []
        
        if not is_safe:
            _, warnings = self.safety.get_safety_report(command)
            
        return is_safe, warnings
        
    def confirm_execution(self, command: str, warnings: list[str]) -> bool:
        """Ask user for confirmation to execute command."""
        self.console.print(f"💡 Suggested: {command}", style="yellow")
        
        if warnings:
            self.console.print("⚠️  Warnings:", style="red")
            for warning in warnings:
                self.console.print(f"  • {warning}", style="red")
            self.console.print()
            
        response = Prompt.ask(
            "Run this command?",
            choices=["y", "n", "Y", "N"],
            default="n",
            console=self.console
        )
        
        return response.lower() == "y"
        
    def execute_command(self, command: str, original_query: str):
        """Execute the command and display results."""
        self.console.print("📤 Executing...", style="green")
        
        result = self.executor.execute(command, original_query)
        
        if result.success:
            self.console.print("✅ Command executed successfully!", style="green")
            if result.output.strip():
                self.console.print("\n📄 Output:")
                self.console.print(result.output)
        else:
            self.console.print(f"❌ Command failed (exit code: {result.exit_code})", style="red")
            if result.error:
                self.console.print(f"Error: {result.error}", style="red")
                
    def handle_special_commands(self, user_input: str) -> bool:
        """Handle special shell commands like :quit, :explain, etc."""
        input_lower = user_input.lower().strip()
        
        if input_lower in [":quit", ":exit", "quit", "exit"]:
            self.console.print("👋 Goodbye!", style="blue")
            self.running = False
            return True
            
        if input_lower == ":help":
            self.show_help()
            return True
            
        if input_lower == ":history":
            self.show_history()
            return True
            
        if input_lower == ":clear":
            os.system("clear")
            return True
            
        return False
        
    def show_help(self):
        """Display help information."""
        help_text = """
🔧 Available Commands:
  • Natural language queries (e.g., "find all PDF files")
  • :quit, :exit - Exit the shell
  • :help - Show this help
  • :history - Show command history
  • :clear - Clear screen
  • :explain - Explain the last generated command
  • :dryrun - Preview command without executing

💡 Examples:
  • "delete all .zip files in Downloads"
  • "list all python files modified in the last 24 hours"
  • "show disk usage for current directory"
  • "find all files larger than 100MB"
        """
        self.console.print(Panel(help_text, title="Help", border_style="green"))
        
    def show_history(self):
        """Display command history."""
        history = self.executor.get_history(limit=10)
        
        if not history:
            self.console.print("📜 No command history found.", style="dim")
            return
            
        self.console.print("📜 Recent Commands:", style="bold")
        for entry in history:
            timestamp = entry.get('timestamp', 'Unknown')
            query = entry.get('original_query', 'Unknown')
            command = entry.get('generated_command', 'Unknown')
            
            self.console.print(f"  {timestamp}: {query} → {command}")
            
    def run(self):
        """Main shell loop."""
        self.print_banner()
        
        while self.running:
            try:
                user_input = self.get_prompt()
                
                if not user_input.strip():
                    continue
                    
                # Handle special commands
                if self.handle_special_commands(user_input):
                    continue
                    
                # Process natural language
                command = self.process_natural_language(user_input)
                
                if not command:
                    self.console.print("❌ Failed to generate command. Please try again.", style="red")
                    continue
                    
                # Check safety
                is_safe, warnings = self.check_safety(command)
                
                # Ask for confirmation
                if self.confirm_execution(command, warnings):
                    self.execute_command(command, user_input)
                else:
                    self.console.print("❌ Cancelled", style="red")
                    
                self.console.print()  # Add spacing
                
            except KeyboardInterrupt:
                self.console.print("\n👋 Goodbye!", style="blue")
                break
            except EOFError:
                self.console.print("\n👋 Goodbye!", style="blue")
                break
            except Exception as e:
                self.console.print(f"❌ Unexpected error: {e}", style="red")


def main():
    """Main entry point."""
    try:
        shell = AIShell()
        shell.run()
    except Exception as e:
        console = Console()
        console.print(f"❌ Failed to start shell: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main() 