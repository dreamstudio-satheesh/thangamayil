#!/usr/bin/env python3
"""
Simple launcher for தங்கமயில் சில்க்ஸ் Billing Software
Direct launch without splash screen
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Simple application entry point"""
    try:
        from thangamayil.database.connection import db
        from thangamayil.ui.login import show_login
        from thangamayil.ui.main_window import MainWindow
        from thangamayil import APP_NAME, APP_VERSION
        
        print(f"Starting {APP_NAME} v{APP_VERSION}")
        
        # Initialize database
        db.connect()
        print("✓ Database connected")
        
        # Show login
        print("Showing login window...")
        if show_login():
            print("✓ Login successful")
            
            # Start main application
            print("Starting main application...")
            main_app = MainWindow()
            main_app.run()
        else:
            print("Login cancelled")
    
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            db.disconnect()
        except:
            pass
        print("Application closed")

if __name__ == "__main__":
    main()