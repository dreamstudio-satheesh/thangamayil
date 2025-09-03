#!/usr/bin/env python3
"""
Main entry point for தங்கமயில் சில்க்ஸ் Billing Software
Handles application startup, login, and main window initialization
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from thangamayil.ui.login import show_login
    from thangamayil.ui.main_window import MainWindow
    from thangamayil.database.connection import db
    from thangamayil import APP_NAME, APP_VERSION
except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure all required dependencies are installed.")
    print("Run: uv pip install -e .")
    sys.exit(1)


class BillingApplication:
    """Main application class"""
    
    def __init__(self):
        self.main_window = None
    
    def initialize_database(self):
        """Initialize database connection and schema"""
        try:
            # Test database connection
            db.connect()
            print("Database connected successfully")
            return True
        except Exception as e:
            messagebox.showerror(
                "Database Error",
                f"Failed to initialize database:\n{str(e)}\n\nPlease check database configuration."
            )
            return False
    
    def show_splash_screen(self):
        """Show application splash screen"""
        splash = tk.Tk()
        splash.title(APP_NAME)
        splash.geometry("500x300")
        splash.resizable(False, False)
        
        # Center splash screen (same as login window)
        splash.update_idletasks()
        width = splash.winfo_width()
        height = splash.winfo_height()
        x = (splash.winfo_screenwidth() // 2) - (width // 2)
        y = (splash.winfo_screenheight() // 2) - (height // 2)
        splash.geometry(f"{width}x{height}+{x}+{y}")
        
        # Splash content
        tk.Label(splash, text=APP_NAME, font=("Arial", 16, "bold")).pack(pady=20)
        tk.Label(splash, text=f"Version {APP_VERSION}", font=("Arial", 10)).pack()
        tk.Label(splash, text="Loading...", font=("Arial", 10)).pack(pady=20)
        
        # Progress bar
        progress_frame = tk.Frame(splash)
        progress_frame.pack(pady=10)
        
        progress_bar = tk.Canvas(progress_frame, width=200, height=10, bg="white", highlightthickness=1)
        progress_bar.pack()
        
        # Animate progress
        for i in range(0, 201, 10):
            progress_bar.delete("all")
            progress_bar.create_rectangle(0, 0, i, 10, fill="blue", outline="")
            splash.update()
            splash.after(50)  # Small delay for animation
        
        splash.destroy()
    
    def run(self):
        """Main application entry point"""
        print(f"Starting {APP_NAME} v{APP_VERSION}")
        
        # Show splash screen
        self.show_splash_screen()
        
        # Initialize database
        if not self.initialize_database():
            return
        
        # Show login window
        print("Showing login window...")
        if not show_login():
            print("Login cancelled or failed")
            return
        
        print("Login successful, starting main application...")
        
        # Create and run main window
        try:
            self.main_window = MainWindow()
            self.main_window.run()
        except Exception as e:
            try:
                messagebox.showerror("Application Error", f"An error occurred:\n{str(e)}")
            except:
                pass  # GUI might be destroyed
            print(f"Application error: {e}")
        finally:
            # Cleanup
            try:
                db.disconnect()
            except:
                pass
            print("Application closed")


def main():
    """Entry point function"""
    try:
        app = BillingApplication()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        messagebox.showerror("Fatal Error", f"A fatal error occurred:\n{str(e)}")
    finally:
        # Ensure all Tkinter windows are destroyed
        try:
            root = tk._default_root
            if root:
                root.quit()
        except:
            pass


if __name__ == "__main__":
    main()