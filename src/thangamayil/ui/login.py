"""
Login window for staff authentication
Handles user login and session initialization
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ..models.auth import auth


class LoginWindow:
    """Login window for staff authentication"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("தங்கமயில் சில்க்ஸ் - Staff Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Configure styles
        self.setup_styles()
        
        # Create UI elements
        self.create_widgets()
        
        # Set focus to username entry
        self.username_entry.focus()
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login())
        
        # Store login result
        self.login_successful = False
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_styles(self):
        """Configure UI styles"""
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Login.TButton", font=("Arial", 10, "bold"), padding=10)
    
    def create_widgets(self):
        """Create and layout UI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="தங்கமயில் சில்க்ஸ்", 
            style="Title.TLabel"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        subtitle_label = ttk.Label(
            main_frame, 
            text="Billing Software - Staff Login", 
            font=("Arial", 10)
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Username field
        ttk.Label(main_frame, text="Staff Name:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(main_frame, width=25, font=("Arial", 10))
        self.username_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Password field
        ttk.Label(main_frame, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(main_frame, show="*", width=25, font=("Arial", 10))
        self.password_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Login button
        self.login_button = ttk.Button(
            main_frame, 
            text="Login", 
            command=self.login, 
            style="Login.TButton"
        )
        self.login_button.grid(row=4, column=0, columnspan=2, pady=30)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.grid(row=5, column=0, columnspan=2)
        
        # Default credentials info
        info_frame = ttk.LabelFrame(main_frame, text="Default Credentials", padding="10")
        info_frame.grid(row=6, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))
        
        ttk.Label(info_frame, text="Username: admin").pack(anchor=tk.W)
        ttk.Label(info_frame, text="Password: admin123").pack(anchor=tk.W)
    
    def login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.show_error("Please enter both username and password")
            return
        
        # Clear previous error
        self.status_label.config(text="")
        
        # Disable login button during authentication
        try:
            self.login_button.config(state="disabled", text="Logging in...")
            self.root.update()
        except tk.TclError:
            # Widget may have been destroyed
            return
        
        # Attempt authentication
        try:
            if auth.login(username, password):
                self.login_successful = True
                messagebox.showinfo("Success", f"Welcome, {username}!")
                self.root.quit()  # Use quit() instead of destroy()
                return
            else:
                self.show_error("Invalid username or password")
        except Exception as e:
            self.show_error(f"Login error: {str(e)}")
        
        # Re-enable login button if still exists
        try:
            self.login_button.config(state="normal", text="Login")
        except tk.TclError:
            # Widget destroyed, ignore
            pass
    
    def show_error(self, message):
        """Display error message"""
        self.status_label.config(text=message)
        # Clear password field on error
        self.password_entry.delete(0, tk.END)
        self.password_entry.focus()
    
    def run(self):
        """Run the login window"""
        self.root.mainloop()
        success = self.login_successful
        self.root.destroy()  # Clean up after mainloop
        return success


def show_login():
    """Show login window and return success status"""
    login_window = LoginWindow()
    return login_window.run()