"""
Main application window
Central hub for all billing operations and management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ..models.auth import auth


class MainWindow:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("தங்கமயில் சில்க்ஸ் - Billing Software")
        self.root.geometry("800x600")
        
        # Try to maximize window (cross-platform)
        try:
            self.root.state('zoomed')  # Windows/Linux
        except tk.TclError:
            try:
                self.root.wm_state('zoomed')  # Alternative method
            except tk.TclError:
                # Fallback: set to large size
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                self.root.geometry(f"{min(1200, screen_width-100)}x{min(800, screen_height-100)}")
        
        # Configure styles
        self.setup_styles()
        
        # Create main layout
        self.create_layout()
        
        # Update status
        self.update_status()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind keyboard shortcuts
        self.setup_shortcuts()
    
    def setup_styles(self):
        """Configure UI styles"""
        style = ttk.Style()
        
        # Modern color palette
        colors = {
            'primary': '#2C5282',      # Deep blue
            'secondary': '#B8860B',    # Gold
            'accent': '#38A169',       # Green
            'bg_main': '#F7FAFC',      # Light gray background
            'bg_card': '#FFFFFF',      # Card background
            'text_primary': '#2D3748', # Dark gray
            'text_secondary': "#0D408D", # Medium gray
            'border': '#E2E8F0'        # Light border
        }
        
        # Set main window background
        self.root.configure(bg=colors['bg_main'])
        
        # Modern button styles
        style.configure("MainMenu.TButton", 
                       font=("Segoe UI", 12, "bold"), 
                       padding=(25, 18),
                       focuscolor='none',
                       foreground=colors['text_primary'])
        
        style.map("MainMenu.TButton",
                 background=[('active', colors['primary']),
                           ('pressed', '#1A365D'),
                           ('!active', colors['bg_card'])],
                 foreground=[('active', 'white'),
                           ('pressed', 'white'),
                           ('!active', colors['text_primary'])])
        
        # Header styling
        style.configure("Header.TLabel", 
                       font=("Segoe UI", 22, "bold"),
                       foreground=colors['primary'],
                       background=colors['bg_main'])
        
        # Status bar styling
        style.configure("Status.TLabel", 
                       font=("Segoe UI", 10),
                       foreground=colors['text_secondary'],
                       background=colors['bg_card'])
        
        # Panel frame styling
        style.configure("Card.TLabelframe", 
                       borderwidth=1,
                       relief='solid',
                       background=colors['bg_card'])
        
        style.configure("Card.TLabelframe.Label", 
                       font=("Segoe UI", 12, "bold"),
                       foreground=colors['text_primary'],
                       background=colors['bg_card'])
    
    def create_layout(self):
        """Create main window layout"""
        # Modern header frame with background
        header_frame = tk.Frame(self.root, bg='white', height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Inner header content
        header_content = ttk.Frame(header_frame)
        header_content.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Title with icon
        title_label = ttk.Label(
            header_content, 
            text="🏪 தங்கமயில் சில்க்ஸ் - Billing Software",
            style="Header.TLabel"
        )
        title_label.pack(side=tk.LEFT)
        
        # Logout button with modern styling
        logout_btn = ttk.Button(
            header_content,
            text="🚪 Logout (Ctrl+Q)",
            command=self.logout
        )
        logout_btn.pack(side=tk.RIGHT)
        
        # Main content frame with modern spacing
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Configure grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left panel - Primary operations with card styling
        left_panel = ttk.LabelFrame(main_frame, text="💼 Primary Operations", 
                                  style="Card.TLabelframe", padding=25)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        
        # POS Billing button
        pos_btn = ttk.Button(
            left_panel,
            text="🛒 New Bill / POS (F1, Ctrl+N)",
            style="MainMenu.TButton",
            command=self.open_pos_billing
        )
        pos_btn.pack(fill=tk.X, pady=15)
        
        # Items Management button
        items_btn = ttk.Button(
            left_panel,
            text="📦 Items Master (F2, Ctrl+I)",
            style="MainMenu.TButton",
            command=self.open_items_management
        )
        items_btn.pack(fill=tk.X, pady=15)
        
        # Bill Management button
        bills_btn = ttk.Button(
            left_panel,
            text="📋 Bill Management (F3, Ctrl+M)",
            style="MainMenu.TButton",
            command=self.open_bill_management
        )
        bills_btn.pack(fill=tk.X, pady=15)
        
        # Reports button
        reports_btn = ttk.Button(
            left_panel,
            text="📊 Reports (F4, Ctrl+R)",
            style="MainMenu.TButton",
            command=self.open_reports
        )
        reports_btn.pack(fill=tk.X, pady=15)
        
        # Right panel - Management operations with card styling
        right_panel = ttk.LabelFrame(main_frame, text="⚙️ Management", 
                                   style="Card.TLabelframe", padding=25)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(15, 0))
        
        # Staff Management button
        staff_btn = ttk.Button(
            right_panel,
            text="👥 Staff Management (Ctrl+U)",
            style="MainMenu.TButton",
            command=self.open_staff_management
        )
        staff_btn.pack(fill=tk.X, pady=15)
        
        # Settings button
        settings_btn = ttk.Button(
            right_panel,
            text="⚙️ Settings (Ctrl+S)",
            style="MainMenu.TButton",
            command=self.open_settings
        )
        settings_btn.pack(fill=tk.X, pady=15)
        
        # Backup button
        backup_btn = ttk.Button(
            right_panel,
            text="💾 Database Backup (Ctrl+B)",
            style="MainMenu.TButton",
            command=self.create_backup
        )
        backup_btn.pack(fill=tk.X, pady=15)
        
        # Modern status bar
        status_frame = tk.Frame(self.root, bg='white', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = ttk.Label(
            status_frame,
            text="🟢 Ready",
            style="Status.TLabel"
        )
        self.status_label.pack(side=tk.LEFT, padx=15, pady=8)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts for primary operations"""
        # Primary operations shortcuts
        self.root.bind('<Control-n>', lambda e: self.open_pos_billing())  # Ctrl+N for New Bill
        self.root.bind('<Control-i>', lambda e: self.open_items_management())  # Ctrl+I for Items
        self.root.bind('<Control-m>', lambda e: self.open_bill_management())  # Ctrl+M for Bill Management
        self.root.bind('<Control-r>', lambda e: self.open_reports())  # Ctrl+R for Reports
        self.root.bind('<Control-u>', lambda e: self.open_staff_management())  # Ctrl+U for Users/Staff
        self.root.bind('<Control-s>', lambda e: self.open_settings())  # Ctrl+S for Settings
        self.root.bind('<Control-b>', lambda e: self.create_backup())  # Ctrl+B for Backup
        
        # Function keys
        self.root.bind('<F1>', lambda e: self.open_pos_billing())  # F1 for POS
        self.root.bind('<F2>', lambda e: self.open_items_management())  # F2 for Items
        self.root.bind('<F3>', lambda e: self.open_bill_management())  # F3 for Bill Management
        self.root.bind('<F4>', lambda e: self.open_reports())  # F4 for Reports
        
        # Logout shortcuts
        self.root.bind('<Control-q>', lambda e: self.logout())  # Ctrl+Q for Quit/Logout
        self.root.bind('<Alt-F4>', lambda e: self.on_closing())  # Alt+F4 for Exit
    
    def update_status(self):
        """Update status bar with current user info"""
        if auth.is_logged_in():
            staff_name = auth.get_current_staff_name()
            self.status_label.config(text=f"👤 {staff_name} | 🟢 Ready")
    
    def open_pos_billing(self):
        """Open POS billing window"""
        try:
            from .pos_billing import POSBillingWindow
            billing_window = POSBillingWindow()
            billing_window.show()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open POS billing: {str(e)}")
    
    def open_items_management(self):
        """Open items management window"""
        try:
            from .items_management import ItemsManagementWindow
            items_window = ItemsManagementWindow()
            items_window.show()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open items management: {str(e)}")
    
    def open_bill_management(self):
        """Open bill management window"""
        try:
            from .bill_management import BillManagementWindow
            bills_window = BillManagementWindow()
            bills_window.show()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open bill management: {str(e)}")
    
    def open_staff_management(self):
        """Open staff management window"""
        try:
            from .staff_management import StaffManagementWindow
            staff_window = StaffManagementWindow()
            staff_window.show()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open staff management: {str(e)}")
    
    def open_reports(self):
        """Open reports window"""
        try:
            from .reports import ReportsWindow
            reports_window = ReportsWindow()
            reports_window.show()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open reports: {str(e)}")
    
    def open_settings(self):
        """Open settings window"""
        messagebox.showinfo("Settings", "Settings window - Coming soon!")
    
    def create_backup(self):
        """Create database backup"""
        from ..database.connection import db
        from tkinter import filedialog
        import datetime
        
        try:
            # Generate default filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"thangamayil_backup_{timestamp}.db"
            
            # Ask user for save location
            backup_path = filedialog.asksaveasfilename(
                title="Save Database Backup",
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                initialvalue=default_filename
            )
            
            if backup_path:
                if db.backup_database(backup_path):
                    messagebox.showinfo("Success", f"Database backup created successfully at:\n{backup_path}")
                else:
                    messagebox.showerror("Error", "Failed to create database backup")
        
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def logout(self):
        """Logout current user"""
        try:
            result = messagebox.askyesno("Logout", "Are you sure you want to logout?")
            if result:
                auth.logout()
                self.root.quit()
        except Exception:
            auth.logout()
            self.root.quit()
    
    def on_closing(self):
        """Handle window close event"""
        try:
            result = messagebox.askyesno("Exit", "Are you sure you want to exit?")
            if result:
                auth.logout()
                self.root.quit()  # Use quit() for cleaner shutdown
        except Exception:
            # If messagebox fails, just quit
            auth.logout()
            self.root.quit()
    
    def run(self):
        """Run the main window"""
        self.root.mainloop()