#!/usr/bin/env python3
"""
Simple GUI test - just shows a basic tkinter window to verify GUI works
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_gui():
    """Test basic GUI functionality"""
    root = tk.Tk()
    root.title("தங்கமயில் சில்க்ஸ் - GUI Test")
    root.geometry("400x300")
    
    # Main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    ttk.Label(main_frame, text="GUI Test Successful!", 
             font=("Arial", 16, "bold")).pack(pady=(0, 20))
    
    # Test basic functionality
    try:
        from thangamayil.database.connection import db
        db.connect()
        ttk.Label(main_frame, text="✓ Database connection works", 
                 foreground="green").pack(pady=5)
        
        from thangamayil.models.auth import auth
        ttk.Label(main_frame, text="✓ Authentication module works", 
                 foreground="green").pack(pady=5)
        
        from thangamayil.models.items import ItemsManager
        items = ItemsManager.get_all_categories()
        ttk.Label(main_frame, text=f"✓ Found {len(items)} categories", 
                 foreground="green").pack(pady=5)
        
        ttk.Label(main_frame, text="All core modules working!", 
                 font=("Arial", 12, "bold"), foreground="blue").pack(pady=20)
        
    except Exception as e:
        ttk.Label(main_frame, text=f"✗ Error: {str(e)}", 
                 foreground="red").pack(pady=5)
    
    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=20)
    
    def test_login():
        try:
            from thangamayil.ui.login import show_login
            if show_login():
                messagebox.showinfo("Success", "Login test successful!")
            else:
                messagebox.showinfo("Info", "Login cancelled")
        except Exception as e:
            messagebox.showerror("Error", f"Login test failed: {e}")
    
    ttk.Button(button_frame, text="Test Login", command=test_login).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Close", command=root.destroy).pack(side=tk.LEFT, padx=5)
    
    # Show instructions
    ttk.Label(main_frame, text="Default login: admin / admin123", 
             font=("Arial", 10), foreground="gray").pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    print("Testing GUI functionality...")
    test_basic_gui()