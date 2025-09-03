"""
Staff Management Window
Interface for managing staff accounts, passwords, and permissions
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ..models.auth import StaffManager


class StaffManagementWindow:
    """Staff management interface"""
    
    def __init__(self):
        self.window = None
        self.staff_listbox = None
        self.staff_data = []
    
    def show(self):
        """Display the staff management window"""
        self.window = tk.Toplevel()
        self.window.title("Staff Management - தங்கமயில் சில்க்ஸ்")
        self.window.geometry("800x600")
        self.window.transient()
        self.window.grab_set()
        
        self.create_widgets()
        self.load_staff_data()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Create the UI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Staff Management", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left panel - Staff list
        left_frame = ttk.LabelFrame(main_frame, text="Staff List", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Staff listbox with scrollbar
        listbox_frame = ttk.Frame(left_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.staff_listbox = tk.Listbox(listbox_frame, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.staff_listbox.yview)
        self.staff_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.staff_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.staff_listbox.bind('<<ListboxSelect>>', self.on_staff_select)
        
        # Right panel - Staff details and actions
        right_frame = ttk.LabelFrame(main_frame, text="Staff Details", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Staff details form
        details_frame = ttk.Frame(right_frame)
        details_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(details_frame, text="Staff Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(details_frame, width=30, font=("Arial", 10))
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(details_frame, text="Status:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value="Active")
        status_combo = ttk.Combobox(details_frame, textvariable=self.status_var, 
                                   values=["Active", "Inactive"], state="readonly", width=27)
        status_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(details_frame, text="Created:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.created_label = ttk.Label(details_frame, text="", font=("Arial", 10))
        self.created_label.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        details_frame.columnconfigure(1, weight=1)
        
        # Action buttons
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Add New Staff", command=self.add_staff).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Update Staff", command=self.update_staff).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Change Password", command=self.change_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Refresh", command=self.load_staff_data).pack(side=tk.LEFT, padx=5)
        
        # Bottom buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(bottom_frame, text="Close", command=self.window.destroy).pack()
    
    def load_staff_data(self):
        """Load staff data from database"""
        try:
            self.staff_data = StaffManager.get_all_staff()
            
            # Clear listbox
            self.staff_listbox.delete(0, tk.END)
            
            # Populate listbox
            for staff in self.staff_data:
                status = "Active" if staff['is_active'] else "Inactive"
                display_text = f"{staff['staff_name']} ({status})"
                self.staff_listbox.insert(tk.END, display_text)
            
            # Clear form
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load staff data: {e}")
    
    def on_staff_select(self, event):
        """Handle staff selection from list"""
        selection = self.staff_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index >= len(self.staff_data):
            return
        
        staff = self.staff_data[index]
        
        # Populate form
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, staff['staff_name'])
        
        self.status_var.set("Active" if staff['is_active'] else "Inactive")
        
        created_date = staff.get('created_at', 'N/A')
        if created_date and len(created_date) > 10:
            created_date = created_date[:10]  # Show only date part
        self.created_label.config(text=created_date)
    
    def clear_form(self):
        """Clear the form fields"""
        self.name_entry.delete(0, tk.END)
        self.status_var.set("Active")
        self.created_label.config(text="")
    
    def add_staff(self):
        """Add new staff member"""
        dialog = AddStaffDialog(self.window)
        if dialog.result:
            self.load_staff_data()
    
    def update_staff(self):
        """Update selected staff member"""
        selection = self.staff_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a staff member to update")
            return
        
        index = selection[0]
        staff = self.staff_data[index]
        
        new_name = self.name_entry.get().strip()
        if not new_name:
            messagebox.showerror("Invalid Input", "Staff name cannot be empty")
            return
        
        is_active = self.status_var.get() == "Active"
        
        try:
            success = StaffManager.update_staff(staff['staff_id'], new_name, is_active)
            if success:
                messagebox.showinfo("Success", "Staff updated successfully!")
                self.load_staff_data()
            else:
                messagebox.showerror("Error", "Failed to update staff")
        
        except Exception as e:
            messagebox.showerror("Error", f"Update failed: {e}")
    
    def change_password(self):
        """Change password for selected staff member"""
        selection = self.staff_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a staff member")
            return
        
        index = selection[0]
        staff = self.staff_data[index]
        
        dialog = ChangePasswordDialog(self.window, staff['staff_name'])
        if dialog.result:
            try:
                success = StaffManager.change_password(staff['staff_id'], dialog.result)
                if success:
                    messagebox.showinfo("Success", "Password changed successfully!")
                else:
                    messagebox.showerror("Error", "Failed to change password")
            except Exception as e:
                messagebox.showerror("Error", f"Password change failed: {e}")


class AddStaffDialog:
    """Dialog for adding new staff member"""
    
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Staff")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Add New Staff Member", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Form fields
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(fields_frame, text="Staff Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(fields_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.name_entry.focus()
        
        ttk.Label(fields_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(fields_frame, show="*", width=30)
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(fields_frame, text="Confirm Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.confirm_entry = ttk.Entry(fields_frame, show="*", width=30)
        self.confirm_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        fields_frame.columnconfigure(1, weight=1)
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Add Staff", command=self.add_staff).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.add_staff())
    
    def add_staff(self):
        """Add the staff member"""
        name = self.name_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not name:
            messagebox.showerror("Error", "Staff name is required")
            self.name_entry.focus()
            return
        
        if not password:
            messagebox.showerror("Error", "Password is required")
            self.password_entry.focus()
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            self.confirm_entry.focus()
            return
        
        if len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters")
            self.password_entry.focus()
            return
        
        # Check if staff name exists
        if StaffManager.staff_exists(name):
            messagebox.showerror("Error", "Staff name already exists")
            self.name_entry.focus()
            return
        
        try:
            success = StaffManager.add_staff(name, password)
            if success:
                self.result = True
                messagebox.showinfo("Success", f"Staff '{name}' added successfully!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add staff")
        
        except Exception as e:
            messagebox.showerror("Error", f"Add staff failed: {e}")


class ChangePasswordDialog:
    """Dialog for changing staff password"""
    
    def __init__(self, parent, staff_name):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Change Password - {staff_name}")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets(staff_name)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_widgets(self, staff_name):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=f"Change Password for: {staff_name}", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Form fields
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(fields_frame, text="New Password:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(fields_frame, show="*", width=30)
        self.password_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.password_entry.focus()
        
        ttk.Label(fields_frame, text="Confirm Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.confirm_entry = ttk.Entry(fields_frame, show="*", width=30)
        self.confirm_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        fields_frame.columnconfigure(1, weight=1)
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Change Password", command=self.change_password).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.change_password())
    
    def change_password(self):
        """Change the password"""
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not password:
            messagebox.showerror("Error", "Password is required")
            self.password_entry.focus()
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            self.confirm_entry.focus()
            return
        
        if len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters")
            self.password_entry.focus()
            return
        
        self.result = password
        self.dialog.destroy()