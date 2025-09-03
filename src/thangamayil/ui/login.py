"""
Login window for staff authentication
Handles user login and session initialization
"""

import tkinter as tk
from tkinter import ttk
from ..models.auth import auth


class LoginWindow:
    """Login window for staff authentication"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("தங்கமயில் சில்க்ஸ் - Staff Login")
        self.root.geometry("700x700")
        self.root.resizable(True, True)
        
        # Center the window
        self.center_window()
        
        # Configure styles
        self.setup_styles()
        
        # Create UI elements
        self.create_widgets()
        
        # Set focus to username entry - multiple methods for reliability
        self.username_entry.focus_set()
        self.username_entry.focus_force()
        self.root.after(10, lambda: self.username_entry.focus_set())
        self.root.after(100, lambda: self.username_entry.focus_force())
        
        # Bind keyboard shortcuts
        self.root.bind('<Return>', lambda event: self.login())
        self.root.bind('<Escape>', lambda event: self.root.quit())
        self.root.bind('<Alt-F4>', lambda event: self.root.quit())
        
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
        
        # Modern color palette
        colors = {
            'primary': '#2C5282',      # Deep blue
            'secondary': '#B8860B',    # Gold
            'accent': '#38A169',       # Green
            'bg_light': '#F7FAFC',     # Light gray
            'bg_card': '#FFFFFF',      # White
            'text_primary': '#2D3748', # Dark gray
            'text_secondary': '#718096' # Medium gray
        }
        
        # Configure modern styles
        style.configure("Title.TLabel", 
                       font=("Segoe UI", 20, "bold"), 
                       foreground=colors['primary'])
        
        style.configure("Subtitle.TLabel", 
                       font=("Segoe UI", 11), 
                       foreground=colors['text_secondary'])
        
        style.configure("Modern.TLabel", 
                       font=("Segoe UI", 10), 
                       foreground=colors['text_primary'])
        
        style.configure("Login.TButton", 
                       font=("Segoe UI", 11, "bold"), 
                       padding=(20, 12),
                       focuscolor='none')
        
        style.map("Login.TButton",
                 background=[('active', colors['primary']),
                           ('pressed', '#1A365D')],
                 foreground=[('active', 'white'),
                           ('pressed', 'white'),
                           ('!active', colors['text_primary'])])
        
        style.configure("Modern.TEntry", 
                       font=("Segoe UI", 11),
                       fieldbackground=colors['bg_card'],
                       padding=10)
        
        # Set window background
        self.root.configure(bg=colors['bg_light'])
    
    def create_widgets(self):
        """Create and layout UI widgets"""
        # Main card frame with modern styling
        card_frame = tk.Frame(self.root, bg='white', relief='solid', bd=1)
        card_frame.pack(expand=True, fill='both', padx=50, pady=50)
        
        # Inner content frame - use tk.Frame instead of ttk.Frame
        main_frame = tk.Frame(card_frame, bg='white')
        main_frame.pack(expand=True, fill='both', padx=50, pady=50)
        
        # Title with modern styling
        title_label = tk.Label(
            main_frame, 
            text="🏪 தங்கமயில் சில்க்ஸ்", 
            font=("Segoe UI", 20, "bold"),
            fg="#2C5282",
            bg="white"
        )
        title_label.pack(pady=(0, 8))
        
        subtitle_label = tk.Label(
            main_frame, 
            text="Billing Software - Staff Login", 
            font=("Segoe UI", 11),
            fg="#718096",
            bg="white"
        )
        subtitle_label.pack(pady=(0, 40))
        
        # Input fields container
        fields_frame = tk.Frame(main_frame, bg='white')
        fields_frame.pack(fill='x', pady=(0, 30))
        
        # Username field
        tk.Label(fields_frame, text="👤 Staff Name", 
                font=("Segoe UI", 10), fg="#2D3748", bg="white").pack(anchor='w', pady=(0, 8))
        self.username_entry = tk.Entry(fields_frame, 
                                     font=("Segoe UI", 11), 
                                     relief='solid', bd=1,
                                     highlightthickness=2,
                                     highlightcolor="#2C5282")
        self.username_entry.pack(fill='x', pady=(0, 20), ipady=8)
        
        # Password field
        tk.Label(fields_frame, text="🔐 Password", 
                font=("Segoe UI", 10), fg="#2D3748", bg="white").pack(anchor='w', pady=(0, 8))
        self.password_entry = tk.Entry(fields_frame, show="*", 
                                     font=("Segoe UI", 11), 
                                     relief='solid', bd=1,
                                     highlightthickness=2,
                                     highlightcolor="#2C5282")
        self.password_entry.pack(fill='x', ipady=8)
        
        # Login button with proper centering
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=(30, 20))
        
        self.login_button = ttk.Button(
            button_frame, 
            text="🚀 Login", 
            command=self.login, 
            style="Login.TButton"
        )
        self.login_button.pack(expand=True)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="", fg="#E53E3E", bg="white", font=("Segoe UI", 10))
        self.status_label.pack(pady=(0, 20))
        
    
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