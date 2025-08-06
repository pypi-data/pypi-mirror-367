#!/usr/bin/env python3
"""
CLI entry point for Agent Zero Lite
"""

import sys
import os

def main():
    """Main CLI entry point"""
    # Add the current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Import and run the UI
    from . import run_ui
    run_ui.main() if hasattr(run_ui, 'main') else exec(open(os.path.join(current_dir, 'run_ui.py')).read())

if __name__ == '__main__':
    main()