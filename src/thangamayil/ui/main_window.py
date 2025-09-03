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
        self.root.state('zoomed')  # Maximize window on Windows/Linux
        
        # Configure styles
        self.setup_styles()
        
        # Create main layout
        self.create_layout()
        
        # Update status
        self.update_status()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Configure UI styles"""
        style = ttk.Style()
        
        # Configure button styles
        style.configure("MainMenu.TButton", 
                       font=("Arial", 12, "bold"), 
                       padding=(20, 15))
        
        style.configure("Header.TLabel", 
                       font=("Arial", 18, "bold"))
        
        style.configure("Status.TLabel", 
                       font=("Arial", 10))
    
    def create_layout(self):
        """Create main window layout"""
        # Header frame
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Title
        title_label = ttk.Label(
            header_frame, 
            text="தங்கமயில் சில்க்ஸ் - Billing Software",
            style="Header.TLabel"
        )
        title_label.pack(side=tk.LEFT)
        
        # Logout button
        logout_btn = ttk.Button(
            header_frame,
            text="Logout",
            command=self.logout
        )
        logout_btn.pack(side=tk.RIGHT)
        
        # Main content frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Configure grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left panel - Primary operations
        left_panel = ttk.LabelFrame(main_frame, text="Primary Operations", padding=20)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # POS Billing button
        pos_btn = ttk.Button(
            left_panel,
            text="🛒 New Bill / POS",
            style="MainMenu.TButton",
            command=self.open_pos_billing
        )
        pos_btn.pack(fill=tk.X, pady=10)
        
        # Items Management button
        items_btn = ttk.Button(
            left_panel,
            text="📦 Items Master",
            style="MainMenu.TButton",
            command=self.open_items_management
        )
        items_btn.pack(fill=tk.X, pady=10)
        
        # Reports button
        reports_btn = ttk.Button(
            left_panel,
            text="📊 Reports",
            style="MainMenu.TButton",
            command=self.open_reports
        )
        reports_btn.pack(fill=tk.X, pady=10)
        
        # Right panel - Management operations
        right_panel = ttk.LabelFrame(main_frame, text="Management", padding=20)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Staff Management button
        staff_btn = ttk.Button(
            right_panel,
            text="👥 Staff Management",
            style="MainMenu.TButton",
            command=self.open_staff_management
        )
        staff_btn.pack(fill=tk.X, pady=10)
        
        # Settings button
        settings_btn = ttk.Button(
            right_panel,
            text="⚙️ Settings",
            style="MainMenu.TButton",
            command=self.open_settings
        )
        settings_btn.pack(fill=tk.X, pady=10)
        
        # Backup button
        backup_btn = ttk.Button(
            right_panel,
            text="💾 Database Backup",
            style="MainMenu.TButton",
            command=self.create_backup
        )
        backup_btn.pack(fill=tk.X, pady=10)
        
        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            style="Status.TLabel",
            relief=tk.SUNKEN
        )
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
    
    def update_status(self):
        """Update status bar with current user info"""
        if auth.is_logged_in():
            staff_name = auth.get_current_staff_name()
            self.status_label.config(text=f"Logged in as: {staff_name} | Ready")
    
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