#!/usr/bin/env python3
"""
Quick launcher for the console version of the billing application
"""

import subprocess
import sys
import os

def main():
    print("தங்கமயில் சில்க்ஸ் - Billing Software")
    print("Starting console application...")
    
    # Check if virtual environment exists
    venv_path = os.path.join(os.path.dirname(__file__), '.venv', 'bin', 'activate')
    
    if os.path.exists(venv_path):
        # Run with virtual environment
        subprocess.run([
            'bash', '-c', 
            f'source {venv_path} && python {os.path.join(os.path.dirname(__file__), "console_app.py")}'
        ])
    else:
        # Run directly
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'console_app.py')])

if __name__ == "__main__":
    main()