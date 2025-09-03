"""
Bill Details Window
Shows detailed view of a bill with printing and cancellation options
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class BillDetailsWindow:
    """Window to show detailed view of a bill"""
    
    def __init__(self, bill_data, parent=None):
        self.bill_data = bill_data
        self.parent = parent
        self.window = None
    
    def show(self):
        """Display the bill details window"""
        self.window = tk.Toplevel()
        self.window.title(f"Bill Details - {self.bill_data['invoice_number']}")
        self.window.geometry("800x600")
        
        if self.parent:
            try:
                self.window.transient(self.parent)
                self.window.grab_set()
            except tk.TclError:
                pass
        
        self.create_widgets()
        self.load_bill_details()
    
    def create_widgets(self):
        """Create the UI widgets"""
        main_container = ttk.Frame(self.window, padding="15")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Bill header
        header_frame = ttk.LabelFrame(main_container, text="Bill Information", padding="10")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create header info in a grid
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(fill=tk.X)
        info_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(3, weight=1)
        
        # Left column
        ttk.Label(info_frame, text="Invoice Number:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=self.bill_data['invoice_number'], font=("Arial", 10)).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(info_frame, text="Date:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        bill_date = datetime.strptime(self.bill_data['bill_date'], '%Y-%m-%d %H:%M:%S')
        ttk.Label(info_frame, text=bill_date.strftime('%d/%m/%Y %H:%M'), font=("Arial", 10)).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Right column
        ttk.Label(info_frame, text="Total Amount:", font=("Arial", 10, "bold")).grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        ttk.Label(info_frame, text=f"₹{self.bill_data['grand_total']:.2f}", font=("Arial", 10)).grid(row=0, column=3, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(info_frame, text="Payment Mode:", font=("Arial", 10, "bold")).grid(row=1, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        ttk.Label(info_frame, text=self.bill_data['payment_mode'], font=("Arial", 10)).grid(row=1, column=3, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Status
        status_text = "CANCELLED" if self.bill_data['is_cancelled'] else "ACTIVE"
        status_color = "red" if self.bill_data['is_cancelled'] else "green"
        ttk.Label(info_frame, text="Status:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=2)
        status_label = ttk.Label(info_frame, text=status_text, font=("Arial", 10, "bold"), foreground=status_color)
        status_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Bill items
        items_frame = ttk.LabelFrame(main_container, text="Bill Items", padding="10")
        items_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Items tree
        columns = ('Item', 'Qty', 'Price', 'Disc%', 'GST%', 'Total')
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=10)
        
        # Configure columns
        self.items_tree.heading('Item', text='Item Name')
        self.items_tree.heading('Qty', text='Qty')
        self.items_tree.heading('Price', text='Unit Price')
        self.items_tree.heading('Disc%', text='Discount%')
        self.items_tree.heading('GST%', text='GST%')
        self.items_tree.heading('Total', text='Line Total')
        
        # Configure column widths
        self.items_tree.column('Item', width=250)
        self.items_tree.column('Qty', width=80)
        self.items_tree.column('Price', width=100)
        self.items_tree.column('Disc%', width=80)
        self.items_tree.column('GST%', width=80)
        self.items_tree.column('Total', width=100)
        
        # Add scrollbar for items
        items_scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=items_scrollbar.set)
        
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        items_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        buttons_frame = ttk.Frame(main_container)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="🖨️ Print", command=self.print_bill, 
                  width=12).pack(side=tk.LEFT, padx=(0, 5))
        
        if not self.bill_data['is_cancelled']:
            ttk.Button(buttons_frame, text="❌ Cancel Bill", command=self.cancel_bill, 
                      width=12).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(buttons_frame, text="❌ Close", command=self.window.destroy, 
                  width=12).pack(side=tk.RIGHT)
    
    def load_bill_details(self):
        """Load detailed bill information"""
        try:
            from ..database.connection import db
            
            # Get bill items
            query = '''
            SELECT * FROM bill_items 
            WHERE bill_id = ? 
            ORDER BY bill_item_id
            '''
            items = db.execute_query(query, (self.bill_data['bill_id'],))
            
            # Clear existing items
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            
            # Add items to tree
            for item in items:
                values = (
                    item['item_name'],
                    item['quantity'],
                    f"₹{item['unit_price']:.2f}",
                    f"{item['discount_percentage']:.1f}%",
                    f"{item['gst_percentage']:.1f}%",
                    f"₹{item['line_total']:.2f}"
                )
                self.items_tree.insert('', 'end', values=values)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bill details: {e}")
    
    def print_bill(self):
        """Print the bill using thermal printer"""
        try:
            from .thermal_printer import ThermalPrinter
            printer = ThermalPrinter()
            printer.print_bill(self.bill_data, self.window)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print bill: {e}")
    
    def cancel_bill(self):
        """Cancel the bill"""
        if messagebox.askyesno("Cancel Bill", 
            f"Are you sure you want to cancel bill {self.bill_data['invoice_number']}?\n\nThis will mark the bill as cancelled but keep it for records."):
            try:
                from ..database.connection import db
                db.execute_update("UPDATE bills SET is_cancelled = 1 WHERE bill_id = ?", 
                                (self.bill_data['bill_id'],))
                messagebox.showinfo("Success", "Bill cancelled successfully")
                self.window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cancel bill: {e}")