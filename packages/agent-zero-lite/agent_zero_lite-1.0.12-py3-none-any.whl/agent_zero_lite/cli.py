#!/usr/bin/env python3
"""
CLI entry point for Agent Zero Lite
"""

import sys
import os
import argparse
from pathlib import Path

def init_project():
    """Initialize Agent Zero Lite project with .env file"""
    print("🚀 Initializing Agent Zero Lite project...")
    
    # Create .env file
    env_file = Path(".env")
    if env_file.exists():
        print("📝 .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("Skipping .env file creation")
        else:
            create_env_file(env_file)
    else:
        create_env_file(env_file)
    
    print("\n✅ Project initialized successfully!")
    print("\nNext steps:")
    print("1. Edit the .env file and add your API keys")
    print("2. Run: agent-zero-lite start")
    print("3. Open: http://127.0.0.1:50001")

def create_env_file(env_file):
    """Create .env file with template"""
    env_content = """# Agent Zero Lite Configuration
# Add your API keys below (uncomment and fill in the ones you need)

# OpenAI API Key (for OpenAI models)
# OPENAI_API_KEY=your_openai_api_key_here

# OpenRouter API Key (for accessing multiple models via OpenRouter)
# OPENROUTER_API_KEY=your_openrouter_api_key_here

# Anthropic API Key (for Claude models)
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google API Key (for Gemini models)
# GOOGLE_API_KEY=your_google_api_key_here

# Optional: Custom port (default is 50001)
# PORT=50001

# Optional: Custom memory subdirectory
# AGENT_MEMORY_SUBDIR=default

# Optional: Flask secret key (auto-generated if not provided)
# FLASK_SECRET_KEY=your_secret_key_here
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    print(f"📄 Created {env_file} with configuration template")

def start_server():
    """Start the Agent Zero Lite server"""
    try:
        # Import and run the UI using absolute import
        from agent_zero_lite import run_ui
        run_ui.main()
    except ImportError as e:
        print(f"Error importing Agent Zero Lite modules: {e}")
        sys.exit(1)

def show_help():
    """Show help information"""
    print("""Agent Zero Lite - Lightweight AI Agent Framework

Commands:
  init     Initialize a new Agent Zero Lite project (.env file)
  start    Start the Agent Zero Lite server (default)
  help     Show this help message

Examples:
  agent-zero-lite init      # Initialize project with .env template  
  agent-zero-lite start     # Start the server
  agent-zero-lite           # Same as 'start'

For more information, visit: https://pypi.org/project/agent-zero-lite/
""")

def main():
    """Main CLI entry point"""
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command in ['init', 'initialize']:
            init_project()
        elif command in ['start', 'serve', 'run']:
            start_server()
        elif command in ['help', '--help', '-h']:
            show_help()
        else:
            print(f"Unknown command: {command}")
            print("Run 'agent-zero-lite help' for available commands")
            sys.exit(1)
    else:
        # Default to start if no command provided
        start_server()

if __name__ == '__main__':
    main()