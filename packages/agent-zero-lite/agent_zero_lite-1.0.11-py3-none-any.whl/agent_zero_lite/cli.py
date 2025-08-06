#!/usr/bin/env python3
"""
CLI entry point for Agent Zero Lite
"""

import sys
import os

def main():
    """Main CLI entry point"""
    try:
        # Import and run the UI using absolute import
        from agent_zero_lite import run_ui
        run_ui.main()
    except ImportError as e:
        print(f"Error importing Agent Zero Lite modules: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()