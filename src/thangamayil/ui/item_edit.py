"""
Item Edit Dialog
Dialog for editing bill item quantity and discount
"""

import tkinter as tk
from tkinter import ttk, messagebox


class EditBillItemDialog:
    """Dialog for editing bill item quantity and discount"""
    
    def __init__(self, parent, bill_item):
        self.result = None
        self.original_item = bill_item
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Edit Item - {bill_item['item_name']}")
        self.dialog.geometry("400x200")
        try:
            self.dialog.transient(parent)
            self.dialog.grab_set()
        except tk.TclError:
            pass
        
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
        
        ttk.Label(main_frame, text=f"Edit: {self.original_item['item_name']}", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Form fields
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.X, pady=(0, 20))
        fields_frame.columnconfigure(1, weight=1)
        
        ttk.Label(fields_frame, text="Quantity:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.quantity_entry = ttk.Entry(fields_frame, width=20)
        self.quantity_entry.grid(row=0, column=1, sticky="we", pady=5, padx=(10, 0))
        self.quantity_entry.insert(0, str(self.original_item['quantity']))
        self.quantity_entry.focus()
        self.quantity_entry.select_range(0, tk.END)
        
        ttk.Label(fields_frame, text="Discount %:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.discount_entry = ttk.Entry(fields_frame, width=20)
        self.discount_entry.grid(row=1, column=1, sticky="we", pady=5, padx=(10, 0))
        self.discount_entry.insert(0, str(self.original_item['discount_percentage']))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Update", command=self.update_item).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda _: self.update_item())
    
    def update_item(self):
        """Update the item"""
        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
            self.quantity_entry.focus()
            return
        
        try:
            discount = float(self.discount_entry.get())
            if discount < 0 or discount > 100:
                raise ValueError("Discount must be between 0 and 100")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid discount percentage (0-100)")
            self.discount_entry.focus()
            return
        
        # Create updated item
        updated_item = self.original_item.copy()
        updated_item['quantity'] = quantity
        updated_item['discount_percentage'] = discount
        
        self.result = updated_item
        self.dialog.destroy()