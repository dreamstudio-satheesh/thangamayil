#!/usr/bin/env python3
"""
Safe GUI launcher with better error handling for தங்கமयில் சில்க்ஸ் Billing Software
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Safe GUI application entry point"""
    # Create root window early to handle any tkinter issues
    root = tk.Tk()
    root.withdraw()  # Hide root window initially
    
    try:
        from thangamayil.database.connection import db
        from thangamayil.models.auth import auth
        from thangamayil import APP_NAME, APP_VERSION
        
        print(f"Starting {APP_NAME} GUI v{APP_VERSION}")
        
        # Initialize database
        db.connect()
        print("✓ Database connected")
        
        # Import and show login
        from thangamayil.ui.login import LoginWindow
        login_window = LoginWindow()
        login_success = login_window.run()
        
        if login_success:
            print("✓ Login successful")
            
            # Import and start main application
            from thangamayil.ui.main_window import MainWindow
            
            # Destroy the hidden root window
            root.destroy()
            
            # Create and run main application
            main_app = MainWindow()
            main_app.run()
        else:
            print("Login cancelled or failed")
            root.destroy()
    
    except ImportError as e:
        messagebox.showerror(
            "Import Error", 
            f"Failed to import required modules:\n{e}\n\nPlease run: pip install -e ."
        )
        print(f"Import error: {e}")
        root.destroy()
    
    except Exception as e:
        try:
            messagebox.showerror("Error", f"Application error:\n{str(e)}")
        except:
            pass  # GUI might be destroyed
        print(f"Error: {e}")
        try:
            root.destroy()
        except:
            pass
    
    finally:
        try:
            db.disconnect()
        except:
            pass
        print("Application closed")

if __name__ == "__main__":
    main()