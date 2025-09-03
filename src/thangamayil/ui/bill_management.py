"""
Bill Management Window
Comprehensive bill management with view, edit, delete, and print functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class BillManagementWindow:
    """Window for managing existing bills - view, edit, delete, print"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.bills_data = []
        
    def show(self):
        """Display the bill management window"""
        self.window = tk.Toplevel()
        self.window.title("Bill Management - தங்கமயில் சில்க்ஸ்")
        self.window.geometry("1000x600")
        
        if self.parent:
            try:
                self.window.transient(self.parent)
                self.window.grab_set()
            except tk.TclError:
                pass
        
        self.create_widgets()
        self.load_bills()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        # Bind keyboard shortcuts
        self.window.bind('<F5>', lambda e: self.load_bills())
        self.window.bind('<Delete>', lambda e: self.delete_selected_bill())
        self.window.bind('<Escape>', lambda e: self.window.destroy())
    
    def create_widgets(self):
        """Create the UI widgets"""
        main_container = ttk.Frame(self.window, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="📋 Bill Management", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Refresh button
        ttk.Button(header_frame, text="🔄 Refresh (F5)", 
                  command=self.load_bills).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Filter frame
        filter_frame = ttk.LabelFrame(main_container, text="Filters", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Date filter
        ttk.Label(filter_frame, text="Date:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.date_filter = ttk.Combobox(filter_frame, values=["All", "Today", "Yesterday", "This Week", "This Month"], 
                                       state="readonly", width=15)
        self.date_filter.set("All")
        self.date_filter.grid(row=0, column=1, padx=(0, 10))
        self.date_filter.bind('<<ComboboxSelected>>', lambda e: self.load_bills())
        
        # Status filter
        ttk.Label(filter_frame, text="Status:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.status_filter = ttk.Combobox(filter_frame, values=["All", "Active", "Cancelled"], 
                                         state="readonly", width=15)
        self.status_filter.set("All")
        self.status_filter.grid(row=0, column=3, padx=(0, 10))
        self.status_filter.bind('<<ComboboxSelected>>', lambda e: self.load_bills())
        
        # Search
        ttk.Label(filter_frame, text="Search:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=5, padx=(0, 10))
        search_entry.bind('<KeyRelease>', lambda e: self.load_bills())
        
        # Bills list
        list_frame = ttk.Frame(main_container)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create Treeview
        columns = ('Invoice', 'Date', 'Customer', 'Items', 'Total', 'Payment', 'Status')
        self.bills_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.bills_tree.heading('Invoice', text='Invoice #')
        self.bills_tree.heading('Date', text='Date')
        self.bills_tree.heading('Customer', text='Customer')
        self.bills_tree.heading('Items', text='Items')
        self.bills_tree.heading('Total', text='Total')
        self.bills_tree.heading('Payment', text='Payment')
        self.bills_tree.heading('Status', text='Status')
        
        # Configure column widths
        self.bills_tree.column('Invoice', width=100)
        self.bills_tree.column('Date', width=120)
        self.bills_tree.column('Customer', width=150)
        self.bills_tree.column('Items', width=80)
        self.bills_tree.column('Total', width=100)
        self.bills_tree.column('Payment', width=80)
        self.bills_tree.column('Status', width=80)
        
        # Add scrollbar
        bills_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.bills_tree.yview)
        self.bills_tree.configure(yscrollcommand=bills_scrollbar.set)
        
        self.bills_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        bills_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to view bill
        self.bills_tree.bind('<Double-1>', self.view_selected_bill)
        
        # Action buttons
        buttons_frame = ttk.Frame(main_container)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="👁️ View", command=self.view_selected_bill, 
                  width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="✏️ Edit", command=self.edit_selected_bill, 
                  width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="🖨️ Print", command=self.print_selected_bill, 
                  width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="❌ Delete", command=self.delete_selected_bill, 
                  width=12).pack(side=tk.LEFT, padx=(0, 5))
        
        # Separator
        ttk.Separator(buttons_frame, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Bulk operations
        ttk.Button(buttons_frame, text="🗑️ Delete Empty Bills", command=self.delete_empty_bills, 
                  width=18).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(buttons_frame, text="❌ Close", command=self.window.destroy, 
                  width=12).pack(side=tk.RIGHT)
    
    def load_bills(self):
        """Load bills from database with filters"""
        try:
            from ..database.connection import db
            
            # Build query based on filters
            query = '''
            SELECT 
                b.bill_id, b.invoice_number, b.bill_date, b.grand_total, 
                b.payment_mode, b.is_cancelled,
                c.customer_name,
                COUNT(bi.bill_item_id) as item_count
            FROM bills b
            LEFT JOIN customers c ON b.customer_id = c.customer_id
            LEFT JOIN bill_items bi ON b.bill_id = bi.bill_id
            WHERE 1=1
            '''
            params = []
            
            # Date filter
            date_filter = self.date_filter.get()
            if date_filter == "Today":
                query += " AND DATE(b.bill_date) = DATE('now')"
            elif date_filter == "Yesterday":
                query += " AND DATE(b.bill_date) = DATE('now', '-1 day')"
            elif date_filter == "This Week":
                query += " AND DATE(b.bill_date) >= DATE('now', 'weekday 0', '-7 days')"
            elif date_filter == "This Month":
                query += " AND strftime('%Y-%m', b.bill_date) = strftime('%Y-%m', 'now')"
            
            # Status filter
            status_filter = self.status_filter.get()
            if status_filter == "Active":
                query += " AND b.is_cancelled = 0"
            elif status_filter == "Cancelled":
                query += " AND b.is_cancelled = 1"
            
            # Search filter
            search_term = self.search_var.get().strip()
            if search_term:
                query += " AND (b.invoice_number LIKE ? OR c.customer_name LIKE ?)"
                params.extend([f'%{search_term}%', f'%{search_term}%'])
            
            query += " GROUP BY b.bill_id ORDER BY b.bill_date DESC"
            
            results = db.execute_query(query, tuple(params))
            
            # Clear existing items
            for item in self.bills_tree.get_children():
                self.bills_tree.delete(item)
            
            # Add bills to tree
            self.bills_data = []
            for bill in results:
                # Format date
                bill_date = datetime.strptime(bill['bill_date'], '%Y-%m-%d %H:%M:%S')
                formatted_date = bill_date.strftime('%d/%m/%Y %H:%M')
                
                # Format status
                status = "Cancelled" if bill['is_cancelled'] else "Active"
                
                # Customer name
                customer = bill['customer_name'] or "Walk-in"
                
                values = (
                    bill['invoice_number'],
                    formatted_date,
                    customer,
                    bill['item_count'],
                    f"₹{bill['grand_total']:.2f}",
                    bill['payment_mode'],
                    status
                )
                
                item_id = self.bills_tree.insert('', 'end', values=values)
                self.bills_data.append({
                    'item_id': item_id,
                    'bill_data': bill
                })
            
            # Update window title with count
            count = len(results)
            self.window.title(f"Bill Management - {count} bills - தங்கமயில் சில்க்ஸ்")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bills: {e}")
    
    def get_selected_bill(self):
        """Get the currently selected bill data"""
        selection = self.bills_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a bill first")
            return None
        
        # Find bill data by tree item
        for bill_info in self.bills_data:
            if bill_info['item_id'] == selection[0]:
                return bill_info['bill_data']
        return None
    
    def view_selected_bill(self, event=None):
        """View selected bill details"""
        bill = self.get_selected_bill()
        if not bill:
            return
        
        # Create bill details window
        from .bill_details import BillDetailsWindow
        BillDetailsWindow(bill, self.window).show()
    
    def edit_selected_bill(self):
        """Edit selected bill"""
        bill = self.get_selected_bill()
        if not bill:
            return
        
        if bill['is_cancelled']:
            messagebox.showwarning("Cancelled Bill", "Cannot edit a cancelled bill")
            return
        
        # Open bill edit dialog
        from .bill_edit import EditBillDialog
        EditBillDialog(bill, self.window).show()
        # Refresh the bills list after editing
        self.load_bills()
    
    def print_selected_bill(self):
        """Print selected bill"""
        bill = self.get_selected_bill()
        if not bill:
            return
        
        if bill['is_cancelled']:
            if not messagebox.askyesno("Cancelled Bill", "This bill is cancelled. Print anyway?"):
                return
        
        # Print using thermal printer
        try:
            from .thermal_printer import ThermalPrinter
            printer = ThermalPrinter()
            printer.print_bill(bill)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print bill: {e}")
    
    def delete_selected_bill(self):
        """Delete selected bill"""
        bill = self.get_selected_bill()
        if not bill:
            return
        
        if bill['grand_total'] > 0:
            if not messagebox.askyesno("Delete Bill", 
                f"Are you sure you want to delete bill {bill['invoice_number']} with amount ₹{bill['grand_total']:.2f}?\n\nThis action cannot be undone."):
                return
        else:
            if not messagebox.askyesno("Delete Empty Bill", 
                f"Delete empty bill {bill['invoice_number']}?"):
                return
        
        try:
            from ..database.connection import db
            
            # Delete bill items first
            db.execute_update("DELETE FROM bill_items WHERE bill_id = ?", (bill['bill_id'],))
            
            # Delete the bill
            db.execute_update("DELETE FROM bills WHERE bill_id = ?", (bill['bill_id'],))
            
            messagebox.showinfo("Success", f"Bill {bill['invoice_number']} deleted successfully")
            self.load_bills()  # Refresh the list
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete bill: {e}")
    
    def delete_empty_bills(self):
        """Delete all empty bills (bills with no items or zero total)"""
        try:
            from ..database.connection import db
            
            # Find empty bills
            query = '''
            SELECT b.bill_id, b.invoice_number 
            FROM bills b 
            LEFT JOIN bill_items bi ON b.bill_id = bi.bill_id 
            WHERE bi.bill_id IS NULL OR b.grand_total = 0
            '''
            empty_bills = db.execute_query(query)
            
            if not empty_bills:
                messagebox.showinfo("No Empty Bills", "No empty bills found to delete")
                return
            
            count = len(empty_bills)
            if not messagebox.askyesno("Delete Empty Bills", 
                f"Found {count} empty bills. Delete all of them?\n\nThis action cannot be undone."):
                return
            
            # Delete empty bills
            for bill in empty_bills:
                db.execute_update("DELETE FROM bill_items WHERE bill_id = ?", (bill['bill_id'],))
                db.execute_update("DELETE FROM bills WHERE bill_id = ?", (bill['bill_id'],))
            
            messagebox.showinfo("Success", f"Deleted {count} empty bills successfully")
            self.load_bills()  # Refresh the list
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete empty bills: {e}")