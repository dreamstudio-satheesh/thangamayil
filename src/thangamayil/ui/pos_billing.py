"""
POS Billing Window
Point of Sale interface for creating bills and processing transactions
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ..models.items import ItemsManager
from ..models.billing import BillingManager
from ..models.auth import auth


class POSBillingWindow:
    """POS billing interface"""
    
    def __init__(self):
        self.window = None
        self.current_bill_id = None
        self.bill_items = []
        
        # GUI variables
        self.barcode_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.discount_var = tk.StringVar(value="0")
        self.payment_mode_var = tk.StringVar(value="CASH")
        self.customer_var = tk.StringVar()
        self.selected_customer_id = None
        
        # Total variables
        self.subtotal_var = tk.StringVar(value="₹0.00")
        self.discount_amount_var = tk.StringVar(value="₹0.00")
        self.gst_var = tk.StringVar(value="₹0.00")
        self.total_var = tk.StringVar(value="₹0.00")
    
    def show(self, parent=None):
        """Display the POS billing window"""
        self.window = tk.Toplevel(parent)
        self.window.title("POS Billing - தங்கமயில் சில்க்ஸ்")
        self.window.geometry("1200x800")
        
        # Set up proper window cleanup
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
        try:
            if parent:
                self.window.transient(parent)
            self.window.grab_set()
        except tk.TclError:
            pass  # Skip if parent window is not available
        
        self.create_widgets()
        self.reset_bill_display()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        # Focus on barcode entry
        self.barcode_entry.focus()
        
        # Bind keyboard shortcuts
        self.window.bind('<Control-w>', lambda e: self.close_window())
        self.window.bind('<Escape>', lambda e: self.close_window())
        self.window.bind('<Control-u>', lambda e: self.create_new_customer())  # Ctrl+U for new customer
        self.window.bind('<Control-s>', lambda e: self.save_only())  # Ctrl+S for save only
        self.window.bind('<Control-p>', lambda e: self.save_and_print())  # Ctrl+P for save and print
        self.window.bind('<F9>', lambda e: self.save_only())  # F9 for save only
        self.window.bind('<F10>', lambda e: self.save_and_print())  # F10 for save and print
        self.window.bind('<Control-Shift-P>', lambda e: self.preview_only())  # Ctrl+Shift+P for preview only
    
    def close_window(self):
        """Properly close the POS billing window"""
        if self.window:
            try:
                self.window.grab_release()
            except tk.TclError:
                pass
            self.window.destroy()
            self.window = None
    
    def create_widgets(self):
        """Create the UI widgets"""
        # Main container
        main_container = ttk.Frame(self.window, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure main container grid
        main_container.columnconfigure(0, weight=2)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Create sections
        self.create_header(main_container)
        self.create_left_panel(main_container)
        self.create_right_panel(main_container)
    
    def create_header(self, parent):
        """Create header with title and bill info"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Title
        ttk.Label(header_frame, text="POS Billing System", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Bill info
        bill_info_frame = ttk.Frame(header_frame)
        bill_info_frame.pack(side=tk.RIGHT)
        
        self.invoice_label = ttk.Label(bill_info_frame, text="No Active Bill", 
                                      font=("Arial", 12, "bold"))
        self.invoice_label.pack()
        
        staff_name = auth.get_current_staff_name()
        ttk.Label(bill_info_frame, text=f"Staff: {staff_name}").pack()
    
    def create_left_panel(self, parent):
        """Create left panel with item entry and bill items"""
        left_panel = ttk.Frame(parent)
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.rowconfigure(1, weight=1)
        
        # Item entry section
        self.create_item_entry_section(left_panel)
        
        # Bill items section
        self.create_bill_items_section(left_panel)
    
    def create_item_entry_section(self, parent):
        """Create item entry section"""
        entry_frame = ttk.LabelFrame(parent, text="Add Items", padding="10")
        entry_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        entry_frame.columnconfigure(1, weight=1)
        
        # Barcode entry
        ttk.Label(entry_frame, text="Barcode:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.barcode_entry = ttk.Entry(entry_frame, textvariable=self.barcode_var, width=20)
        self.barcode_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=2)
        self.barcode_entry.bind('<Return>', self.on_barcode_scan)
        self.barcode_entry.bind('<Tab>', self.on_barcode_scan)
        
        ttk.Button(entry_frame, text="Add", command=self.add_by_barcode).grid(row=0, column=2, pady=2)
        
        # Manual search
        ttk.Label(entry_frame, text="Search:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.search_entry = ttk.Entry(entry_frame, textvariable=self.search_var, width=20)
        self.search_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=2)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        ttk.Button(entry_frame, text="Search", command=self.manual_search).grid(row=1, column=2, pady=2)
        
        # Search results listbox (hidden initially)
        self.search_results_frame = ttk.Frame(entry_frame)
        self.search_results_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        self.search_results_frame.grid_remove()  # Hide initially
        
        self.search_listbox = tk.Listbox(self.search_results_frame, height=4)
        search_scrollbar = ttk.Scrollbar(self.search_results_frame, orient="vertical", 
                                        command=self.search_listbox.yview)
        self.search_listbox.configure(yscrollcommand=search_scrollbar.set)
        
        self.search_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        search_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.search_listbox.bind('<Double-1>', self.add_selected_item)
        self.search_listbox.bind('<Return>', self.add_selected_item)
    
    def create_bill_items_section(self, parent):
        """Create bill items section"""
        items_frame = ttk.LabelFrame(parent, text="Bill Items", padding="10")
        items_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        items_frame.columnconfigure(0, weight=1)
        items_frame.rowconfigure(0, weight=1)
        
        # Bill items tree
        columns = ('Item', 'Qty', 'Price', 'Disc%', 'GST%', 'Total')
        self.bill_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        self.bill_tree.heading('Item', text='Item Name')
        self.bill_tree.heading('Qty', text='Qty')
        self.bill_tree.heading('Price', text='Price')
        self.bill_tree.heading('Disc%', text='Disc%')
        self.bill_tree.heading('GST%', text='GST%')
        self.bill_tree.heading('Total', text='Total')
        
        # Configure column widths
        self.bill_tree.column('Item', width=200)
        self.bill_tree.column('Qty', width=60)
        self.bill_tree.column('Price', width=80)
        self.bill_tree.column('Disc%', width=60)
        self.bill_tree.column('GST%', width=60)
        self.bill_tree.column('Total', width=80)
        
        # Add scrollbar
        bill_scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=self.bill_tree.yview)
        self.bill_tree.configure(yscrollcommand=bill_scrollbar.set)
        
        self.bill_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        bill_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind events
        self.bill_tree.bind('<Double-1>', self.edit_bill_item)
        self.bill_tree.bind('<Delete>', self.remove_bill_item)
    
    def create_right_panel(self, parent):
        """Create right panel with totals and actions"""
        right_panel = ttk.Frame(parent)
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Totals section
        self.create_totals_section(right_panel)
        
        # Customer section
        self.create_customer_section(right_panel)
        
        # Payment section
        self.create_payment_section(right_panel)
        
        # Action buttons
        self.create_action_buttons(right_panel)
    
    def create_totals_section(self, parent):
        """Create totals section"""
        totals_frame = ttk.LabelFrame(parent, text="Bill Summary", padding="15")
        totals_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Bill discount
        discount_frame = ttk.Frame(totals_frame)
        discount_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(discount_frame, text="Bill Discount %:").pack(side=tk.LEFT)
        discount_entry = ttk.Entry(discount_frame, textvariable=self.discount_var, width=10)
        discount_entry.pack(side=tk.RIGHT)
        discount_entry.bind('<KeyRelease>', self.on_discount_change)
        
        # Totals display
        totals_display = ttk.Frame(totals_frame)
        totals_display.pack(fill=tk.X)
        
        # Create total labels
        total_labels = [
            ("Subtotal:", self.subtotal_var),
            ("Discount:", self.discount_amount_var),
            ("GST:", self.gst_var),
            ("GRAND TOTAL:", self.total_var)
        ]
        
        for i, (label_text, var) in enumerate(total_labels):
            if label_text == "GRAND TOTAL:":
                # Grand total with emphasis
                grand_frame = ttk.Frame(totals_display)
                grand_frame.pack(fill=tk.X, pady=(10, 0))
                
                ttk.Label(grand_frame, text=label_text, font=("Arial", 12, "bold")).pack(side=tk.LEFT)
                ttk.Label(grand_frame, textvariable=var, font=("Arial", 14, "bold"), 
                         foreground="red").pack(side=tk.RIGHT)
            else:
                row_frame = ttk.Frame(totals_display)
                row_frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(row_frame, text=label_text).pack(side=tk.LEFT)
                ttk.Label(row_frame, textvariable=var).pack(side=tk.RIGHT)
    
    def create_payment_section(self, parent):
        """Create payment section"""
        payment_frame = ttk.LabelFrame(parent, text="Payment", padding="15")
        payment_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(payment_frame, text="Payment Mode:").pack()
        
        payment_modes = ["CASH", "CARD", "UPI"]
        for mode in payment_modes:
            ttk.Radiobutton(payment_frame, text=mode, variable=self.payment_mode_var, 
                           value=mode).pack(anchor=tk.W)
    
    def create_action_buttons(self, parent):
        """Create action buttons"""
        actions_frame = ttk.LabelFrame(parent, text="Actions", padding="15")
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Main action buttons
        ttk.Button(actions_frame, text="New Bill", command=self.new_bill_confirm, 
                  style="Accent.TButton").pack(fill=tk.X, pady=2)
        
        ttk.Button(actions_frame, text="💾 Save Only (Ctrl+S, F9)", command=self.save_only, 
                  style="Primary.TButton").pack(fill=tk.X, pady=2)
        
        ttk.Button(actions_frame, text="🖨️ Save & Print (Ctrl+P, F10)", command=self.save_and_print, 
                  style="Accent.TButton").pack(fill=tk.X, pady=2)
        
        ttk.Button(actions_frame, text="👁️ Preview Only (Ctrl+Shift+P)", command=self.preview_only, 
                  style="Secondary.TButton").pack(fill=tk.X, pady=2)
        
        ttk.Button(actions_frame, text="Hold Bill", command=self.hold_bill).pack(fill=tk.X, pady=2)
        
        ttk.Button(actions_frame, text="Cancel Bill", command=self.cancel_bill).pack(fill=tk.X, pady=2)
        
        # Separator
        ttk.Separator(actions_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        ttk.Button(actions_frame, text="Close", command=self.window.destroy).pack(fill=tk.X, pady=2)
    
    def start_new_bill(self):
        """Start a new bill"""
        try:
            staff_id = auth.get_current_staff_id()
            self.current_bill_id = BillingManager.create_bill(staff_id)
            
            if self.current_bill_id:
                # Get bill details to show invoice number
                bill_details = BillingManager.get_bill_details(self.current_bill_id)
                if bill_details:
                    invoice_number = bill_details['bill']['invoice_number']
                    self.invoice_label.config(text=f"Invoice: {invoice_number}")
                
                # Clear bill items
                self.bill_items = []
                self.refresh_bill_display()
                self.update_totals()
            else:
                messagebox.showerror("Error", "Failed to create new bill")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start new bill: {e}")
    
    def reset_bill_display(self):
        """Reset bill display without creating a database bill"""
        self.current_bill_id = None
        self.bill_items = []
        self.selected_customer_id = None
        self.customer_var.set("")
        self.discount_var.set("0")
        
        # Reset invoice label
        self.invoice_label.config(text="No Active Bill")
        
        # Clear customer selection
        self.selected_customer_label.config(text="No customer selected", foreground="gray")
        
        # Clear bill display and totals
        self.refresh_bill_display()
        self.update_totals()
    
    def on_barcode_scan(self, event):
        """Handle barcode scan (Enter or Tab key)"""
        self.add_by_barcode()
    
    def add_by_barcode(self):
        """Add item by barcode"""
        barcode = self.barcode_var.get().strip()
        if not barcode:
            return
        
        try:
            item = ItemsManager.get_item_by_barcode(barcode)
            if item:
                self.add_item_to_bill(item)
                self.barcode_var.set("")  # Clear barcode entry
            else:
                messagebox.showwarning("Item Not Found", f"No item found with barcode: {barcode}")
                self.barcode_entry.focus()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to find item: {e}")
    
    def on_search_change(self, event):
        """Handle search text changes"""
        search_term = self.search_var.get().strip()
        if len(search_term) >= 2:  # Start searching after 2 characters
            self.perform_search(search_term)
        else:
            self.hide_search_results()
    
    def manual_search(self):
        """Perform manual search"""
        search_term = self.search_var.get().strip()
        if search_term:
            self.perform_search(search_term)
    
    def perform_search(self, search_term):
        """Perform item search"""
        try:
            items = ItemsManager.search_items(search_term)
            
            # Clear previous results
            self.search_listbox.delete(0, tk.END)
            
            if items:
                # Show results
                for item in items[:10]:  # Limit to 10 results
                    display_text = f"{item['item_name']} - ₹{item['price']:.2f} (Stock: {item['stock_quantity']})"
                    self.search_listbox.insert(tk.END, display_text)
                
                # Store items data
                self.search_items_data = items[:10]
                self.show_search_results()
            else:
                self.hide_search_results()
        
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {e}")
    
    def show_search_results(self):
        """Show search results listbox"""
        self.search_results_frame.grid()
    
    def hide_search_results(self):
        """Hide search results listbox"""
        self.search_results_frame.grid_remove()
    
    def add_selected_item(self, event):
        """Add selected item from search results"""
        selection = self.search_listbox.curselection()
        if selection and hasattr(self, 'search_items_data'):
            item = self.search_items_data[selection[0]]
            self.add_item_to_bill(item)
            self.search_var.set("")  # Clear search
            self.hide_search_results()
    
    def add_item_to_bill(self, item, quantity=1):
        """Add item to current bill"""
        # Create bill if this is the first item being added
        if not self.current_bill_id:
            try:
                staff_id = auth.get_current_staff_id()
                self.current_bill_id = BillingManager.create_bill(staff_id)
                
                if self.current_bill_id:
                    # Get bill details to show invoice number
                    bill_details = BillingManager.get_bill_details(self.current_bill_id)
                    if bill_details:
                        invoice_number = bill_details['bill']['invoice_number']
                        self.invoice_label.config(text=f"Invoice: {invoice_number}")
                else:
                    messagebox.showerror("Error", "Failed to create new bill")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create bill: {e}")
                return
        
        # Check stock
        if item['stock_quantity'] < quantity:
            messagebox.showwarning("Insufficient Stock", 
                                 f"Only {item['stock_quantity']} units available")
            return
        
        # Check if item already exists in bill
        existing_item = None
        for bill_item in self.bill_items:
            if bill_item['item_id'] == item['item_id']:
                existing_item = bill_item
                break
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item['quantity'] + quantity
            if new_quantity > item['stock_quantity']:
                messagebox.showwarning("Insufficient Stock", 
                                     f"Cannot add more. Only {item['stock_quantity']} units available")
                return
            existing_item['quantity'] = new_quantity
        else:
            # Add new item
            bill_item = {
                'item_id': item['item_id'],
                'item_name': item['item_name'],
                'barcode': item['barcode'],
                'quantity': quantity,
                'unit_price': item['price'],
                'gst_percentage': item['gst_percentage'],
                'discount_percentage': 0.0
            }
            self.bill_items.append(bill_item)
        
        self.refresh_bill_display()
        self.update_totals()
    
    def refresh_bill_display(self):
        """Refresh the bill items display"""
        # Clear existing items
        for item in self.bill_tree.get_children():
            self.bill_tree.delete(item)
        
        # Add bill items
        for bill_item in self.bill_items:
            values = (
                bill_item['item_name'],
                bill_item['quantity'],
                f"₹{bill_item['unit_price']:.2f}",
                f"{bill_item['discount_percentage']:.1f}%",
                f"{bill_item['gst_percentage']:.1f}%",
                f"₹{self.calculate_line_total(bill_item):.2f}"
            )
            self.bill_tree.insert('', 'end', values=values)
    
    def calculate_line_total(self, bill_item):
        """Calculate line total for a bill item"""
        from ..models.billing import GSTCalculator
        
        calc = GSTCalculator.calculate_line_total(
            quantity=bill_item['quantity'],
            unit_price=bill_item['unit_price'],
            discount_percentage=bill_item['discount_percentage'],
            gst_rate=bill_item['gst_percentage']
        )
        return calc['line_total']
    
    def update_totals(self):
        """Update bill totals display"""
        if not self.bill_items:
            self.subtotal_var.set("₹0.00")
            self.discount_amount_var.set("₹0.00")
            self.gst_var.set("₹0.00")
            self.total_var.set("₹0.00")
            return
        
        # Calculate totals
        subtotal = 0
        total_gst = 0
        
        for bill_item in self.bill_items:
            from ..models.billing import GSTCalculator
            
            calc = GSTCalculator.calculate_line_total(
                quantity=bill_item['quantity'],
                unit_price=bill_item['unit_price'],
                discount_percentage=bill_item['discount_percentage'],
                gst_rate=bill_item['gst_percentage']
            )
            
            subtotal += calc['taxable_amount']
            total_gst += calc['gst_amount']
        
        # Apply bill discount
        try:
            bill_discount_percent = float(self.discount_var.get() or 0)
        except ValueError:
            bill_discount_percent = 0
        
        bill_discount_amount = (subtotal * bill_discount_percent) / 100
        discounted_subtotal = subtotal - bill_discount_amount
        
        # Recalculate GST on discounted amount
        if bill_discount_percent > 0:
            gst_ratio = total_gst / subtotal if subtotal > 0 else 0
            total_gst = discounted_subtotal * gst_ratio
        
        grand_total = discounted_subtotal + total_gst
        
        # Update display
        self.subtotal_var.set(f"₹{subtotal:.2f}")
        self.discount_amount_var.set(f"₹{bill_discount_amount:.2f}")
        self.gst_var.set(f"₹{total_gst:.2f}")
        self.total_var.set(f"₹{grand_total:.2f}")
    
    def create_customer_section(self, parent):
        """Create customer section"""
        customer_frame = ttk.LabelFrame(parent, text="👤 Customer", padding="15")
        customer_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Customer entry with search
        customer_entry_frame = ttk.Frame(customer_frame)
        customer_entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(customer_entry_frame, text="Customer:").pack(anchor=tk.W)
        
        entry_button_frame = ttk.Frame(customer_entry_frame)
        entry_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.customer_entry = ttk.Entry(entry_button_frame, textvariable=self.customer_var)
        self.customer_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.customer_entry.bind('<KeyRelease>', self.on_customer_search)
        
        ttk.Button(entry_button_frame, text="➕ New (Ctrl+U)", command=self.create_new_customer, 
                  width=18).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Customer search results (hidden initially)
        self.customer_results_frame = ttk.Frame(customer_frame)
        self.customer_results_frame.pack(fill=tk.X, pady=(5, 0))
        self.customer_results_frame.pack_forget()  # Hide initially
        
        self.customer_listbox = tk.Listbox(self.customer_results_frame, height=3)
        self.customer_listbox.pack(fill=tk.X)
        self.customer_listbox.bind('<Double-1>', self.select_customer)
        self.customer_listbox.bind('<Return>', self.select_customer)
        
        # Selected customer display
        self.selected_customer_label = ttk.Label(customer_frame, text="No customer selected", 
                                               foreground="gray")
        self.selected_customer_label.pack(anchor=tk.W, pady=(5, 0))
    
    def on_customer_search(self, event):
        """Handle customer search"""
        search_term = self.customer_var.get().strip()
        if len(search_term) >= 2:
            self.search_customers(search_term)
        else:
            self.hide_customer_results()
    
    def search_customers(self, search_term):
        """Search for customers"""
        try:
            from ..database.connection import db
            
            query = '''
            SELECT customer_id, customer_name, phone_number 
            FROM customers 
            WHERE customer_name LIKE ? OR phone_number LIKE ?
            ORDER BY customer_name
            LIMIT 10
            '''
            
            results = db.execute_query(query, (f'%{search_term}%', f'%{search_term}%'))
            
            # Clear previous results
            self.customer_listbox.delete(0, tk.END)
            
            if results:
                # Show results
                for customer in results:
                    display_text = f"{customer['customer_name']}"
                    if customer['phone_number']:
                        display_text += f" - {customer['phone_number']}"
                    self.customer_listbox.insert(tk.END, display_text)
                
                # Store customer data
                self.customer_search_results = results
                self.show_customer_results()
            else:
                self.hide_customer_results()
                
        except Exception as e:
            messagebox.showerror("Error", f"Customer search failed: {e}")
    
    def show_customer_results(self):
        """Show customer search results"""
        self.customer_results_frame.pack(fill=tk.X, pady=(5, 0))
    
    def hide_customer_results(self):
        """Hide customer search results"""
        self.customer_results_frame.pack_forget()
    
    def select_customer(self, event):
        """Select customer from search results"""
        selection = self.customer_listbox.curselection()
        if selection and hasattr(self, 'customer_search_results'):
            customer = self.customer_search_results[selection[0]]
            self.selected_customer_id = customer['customer_id']
            self.customer_var.set(customer['customer_name'])
            
            # Update display
            display_text = f"✓ {customer['customer_name']}"
            if customer['phone_number']:
                display_text += f" - {customer['phone_number']}"
            self.selected_customer_label.config(text=display_text, foreground="green")
            
            self.hide_customer_results()
    
    def create_new_customer(self):
        """Open dialog to create new customer"""
        dialog = CreateCustomerDialog(self.window)
        if dialog.result:
            # Customer created, select it
            customer = dialog.result
            self.selected_customer_id = customer['customer_id']
            self.customer_var.set(customer['customer_name'])
            
            # Update display
            display_text = f"✓ {customer['customer_name']}"
            if customer['phone_number']:
                display_text += f" - {customer['phone_number']}"
            self.selected_customer_label.config(text=display_text, foreground="green")
    
    def on_discount_change(self, event):
        """Handle bill discount change"""
        self.update_totals()
    
    def edit_bill_item(self, event):
        """Edit selected bill item"""
        selection = self.bill_tree.selection()
        if not selection:
            return
        
        # Get item index
        item_index = self.bill_tree.index(selection[0])
        bill_item = self.bill_items[item_index]
        
        # Show edit dialog
        dialog = EditBillItemDialog(self.window, bill_item)
        if dialog.result:
            self.bill_items[item_index] = dialog.result
            self.refresh_bill_display()
            self.update_totals()
    
    def remove_bill_item(self, event):
        """Remove selected bill item"""
        selection = self.bill_tree.selection()
        if not selection:
            return
        
        if messagebox.askyesno("Remove Item", "Remove selected item from bill?"):
            item_index = self.bill_tree.index(selection[0])
            del self.bill_items[item_index]
            self.refresh_bill_display()
            self.update_totals()
    
    def new_bill_confirm(self):
        """Confirm new bill reset"""
        if self.bill_items:
            if not messagebox.askyesno("New Bill", "Current bill will be lost. Continue?"):
                return
        
        self.reset_bill_display()
    
    def validate_bill_before_save(self):
        """Validate bill before saving"""
        if not self.current_bill_id:
            messagebox.showwarning("No Bill", "Please start a new bill first")
            return False
            
        if not self.bill_items:
            messagebox.showwarning("No Items", "Cannot create bill without items. Please add items to the bill first")
            return False
        
        # Check if customer is selected
        customer_name = self.customer_var.get()
        if not customer_name or customer_name == "Select Customer":
            result = messagebox.askyesno("No Customer", "No customer selected. Continue with 'Cash Customer'?")
            if result:
                # Set default cash customer
                self.customer_var.set("Cash Customer (1234567899)")
                self.customer_id = 1  # Assuming Cash Customer has ID 1
            else:
                return False
        
        # Check if payment mode is selected
        payment_mode = self.payment_mode_var.get()
        if not payment_mode:
            messagebox.showwarning("Payment Mode", "Please select a payment mode")
            return False
        
        return True
    
    def save_and_print(self):
        """Save and print the current bill"""
        if not self.validate_bill_before_save():
            return
        
        try:
            # Add all items to database
            for bill_item in self.bill_items:
                BillingManager.add_item_to_bill(self.current_bill_id, bill_item)
            
            # Calculate totals
            try:
                bill_discount_percent = float(self.discount_var.get() or 0)
            except ValueError:
                bill_discount_percent = 0
            
            BillingManager.calculate_bill_totals(self.current_bill_id, bill_discount_percent)
            
            # Finalize bill
            payment_mode = self.payment_mode_var.get()
            success = BillingManager.finalize_bill(self.current_bill_id, payment_mode)
            
            if success:
                messagebox.showinfo("Success", "Bill saved successfully!")
                
                # Print the bill
                try:
                    from .thermal_printer import ThermalPrinter
                    from ..database.connection import db
                    
                    # Get the saved bill data
                    bill_query = "SELECT * FROM bills WHERE bill_id = ?"
                    bill_result = db.execute_query(bill_query, (self.current_bill_id,))
                    if bill_result:
                        bill_data = bill_result[0]
                        printer = ThermalPrinter()
                        printer.print_bill(bill_data, self.window)
                    else:
                        messagebox.showerror("Print Error", "Could not retrieve bill data for printing")
                except Exception as e:
                    messagebox.showerror("Print Error", f"Failed to print bill: {e}")
                
                # Reset for new bill
                self.reset_bill_display()
            else:
                messagebox.showerror("Error", "Failed to save bill")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save bill: {e}")
    
    def save_only(self):
        """Save the current bill without printing"""
        if not self.validate_bill_before_save():
            return
        
        try:
            # Add all items to database
            for bill_item in self.bill_items:
                BillingManager.add_item_to_bill(self.current_bill_id, bill_item)
            
            # Calculate totals
            try:
                bill_discount_percent = float(self.discount_var.get() or 0)
            except ValueError:
                bill_discount_percent = 0
            
            BillingManager.calculate_bill_totals(self.current_bill_id, bill_discount_percent)
            
            # Finalize bill
            payment_mode = self.payment_mode_var.get()
            success = BillingManager.finalize_bill(self.current_bill_id, payment_mode)
            
            if success:
                messagebox.showinfo("Success", "Bill saved successfully!")
                
                # Ask if user wants to print later
                print_later = messagebox.askyesno("Print Bill", "Bill saved successfully! Do you want to print it now?")
                if print_later:
                    try:
                        from .thermal_printer import ThermalPrinter
                        from ..database.connection import db
                        
                        # Get the saved bill data
                        bill_query = "SELECT * FROM bills WHERE bill_id = ?"
                        bill_result = db.execute_query(bill_query, (self.current_bill_id,))
                        if bill_result:
                            bill_data = bill_result[0]
                            printer = ThermalPrinter()
                            printer.print_bill(bill_data, self.window)
                        else:
                            messagebox.showerror("Print Error", "Could not retrieve bill data for printing")
                    except Exception as e:
                        messagebox.showerror("Print Error", f"Failed to print bill: {e}")
                
                # Reset for new bill
                self.reset_bill_display()
            else:
                messagebox.showerror("Error", "Failed to save bill")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save bill: {e}")
    
    def preview_only(self):
        """Preview the bill without saving or printing"""
        if not self.current_bill_id:
            messagebox.showwarning("No Bill", "Please start a new bill first")
            return
            
        if not self.bill_items:
            messagebox.showwarning("No Items", "Cannot preview bill without items. Please add items to the bill first")
            return
        
        try:
            from .thermal_printer import ThermalPrinter
            from ..database.connection import db
            
            # Calculate GST amounts for preview
            total_cgst = 0
            total_sgst = 0
            subtotal = 0
            
            try:
                if not self.bill_items:
                    print("No bill items for preview")
                else:
                    for item in self.bill_items:
                        try:
                            # Safe access to item properties with defaults (handle both 'price' and 'unit_price')
                            quantity = float(item.get('quantity', 0))
                            price = float(item.get('unit_price', item.get('price', 0)))
                            discount_percentage = float(item.get('discount_percentage', 0))
                            gst_percentage = float(item.get('gst_percentage', 0))
                            
                            item_subtotal = quantity * price
                            item_discount = (item_subtotal * discount_percentage) / 100
                            taxable_amount = item_subtotal - item_discount
                            item_gst_amount = (taxable_amount * gst_percentage) / 100
                            
                            subtotal += taxable_amount
                            total_cgst += item_gst_amount / 2  # CGST is half of total GST
                            total_sgst += item_gst_amount / 2  # SGST is half of total GST
                        except (TypeError, ValueError, KeyError) as item_error:
                            print(f"Error processing item {item}: {item_error}")
                            continue
            except Exception as e:
                print(f"Error calculating GST for preview: {e}")
                # Fallback to zero values if calculation fails
                total_cgst = 0
                total_sgst = 0
            
            # Create a temporary bill data structure for preview
            temp_bill_data = {
                'bill_id': 'PREVIEW',
                'invoice_number': f'PREVIEW-{self.current_bill_id}',
                'bill_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'customer_id': getattr(self, 'customer_id', 1),
                'discount_amount': 0,
                'cgst_amount': total_cgst,
                'sgst_amount': total_sgst,
                'igst_amount': 0,
                'round_off': 0,
                'grand_total': self.calculate_preview_total(),
                'payment_mode': self.payment_mode_var.get() or 'CASH',
                'is_cancelled': 0
            }
            
            # Generate preview content
            printer = ThermalPrinter()
            content = printer.generate_thermal_bill_preview(temp_bill_data, self.bill_items)
            
            if content:
                # Show enhanced preview window
                printer.show_enhanced_preview(content, self.window, is_preview_mode=True)
            else:
                messagebox.showerror("Error", "Failed to generate bill preview")
                
        except Exception as e:
            print(f"Preview error details: {e}")
            print(f"Bill items: {self.bill_items}")
            messagebox.showerror("Error", f"Failed to preview bill: {e}")
    
    def calculate_preview_total(self):
        """Calculate total for preview without saving to database"""
        total = 0
        try:
            bill_discount_percent = float(self.discount_var.get() or 0)
        except ValueError:
            bill_discount_percent = 0
            
        for item in self.bill_items:
            line_total = item['unit_price'] * item['quantity']
            discount = (line_total * item['discount_percentage']) / 100
            after_discount = line_total - discount
            gst_amount = (after_discount * item['gst_percentage']) / 100
            total += after_discount + gst_amount
        
        # Apply bill discount
        if bill_discount_percent > 0:
            total = total - (total * bill_discount_percent / 100)
            
        return total
    
    def hold_bill(self):
        """Hold current bill"""
        if not self.bill_items:
            messagebox.showwarning("No Items", "No items to hold")
            return
        
        # TODO: Implement bill holding functionality
        messagebox.showinfo("Hold Bill", "Bill holding functionality to be implemented")
    
    def cancel_bill(self):
        """Cancel current bill"""
        if self.bill_items or self.current_bill_id:
            if messagebox.askyesno("Cancel Bill", "Cancel current bill and lose all items?"):
                self.reset_bill_display()
        else:
            messagebox.showinfo("No Bill", "No active bill to cancel")


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
                from datetime import datetime
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
        
        # Create a temporary BillDetailsWindow to use its print functionality
        try:
            temp_bill_window = BillDetailsWindow(bill)
            temp_bill_window.print_bill()
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
        from datetime import datetime
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
        """Print the bill to thermal printer"""
        try:
            # Generate thermal printer content
            bill_content = self.generate_thermal_bill()
            if bill_content:
                # Send to thermal printer
                self.send_to_thermal_printer(bill_content)
                messagebox.showinfo("Print", f"Bill {self.bill_data['invoice_number']} sent to thermal printer successfully!")
            else:
                messagebox.showerror("Error", "Failed to generate bill content")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print bill: {e}")
    
    def generate_thermal_bill(self):
        """Generate thermal printer bill format (4 inch width)"""
        try:
            from ..database.connection import db
            from datetime import datetime
            
            # Get bill items from database
            items_query = '''
            SELECT * FROM bill_items 
            WHERE bill_id = ? 
            ORDER BY bill_item_id
            '''
            bill_items = db.execute_query(items_query, (self.bill_data['bill_id'],))
            
            # Get customer info
            customer_query = '''
            SELECT c.customer_name, c.phone_number, c.address 
            FROM customers c 
            JOIN bills b ON c.customer_id = b.customer_id 
            WHERE b.bill_id = ?
            '''
            customer_result = db.execute_query(customer_query, (self.bill_data['bill_id'],))
            customer_name = customer_result[0]['customer_name'] if customer_result else "Walk-in Customer"
            customer_phone = customer_result[0]['phone_number'] if customer_result else ""
            
            # Get shop settings
            shop_name = db.get_setting('shop_name') or 'தங்கமயில் சில்க்ஸ்'
            shop_address = db.get_setting('shop_address') or 'No.1 Main Road, Tamil Nadu, IN'
            shop_phone = db.get_setting('shop_phone') or '+91-9876543210'
            gstin = db.get_setting('gstin') or '33AAACT9454F1ZB'
            
            # Build thermal printer content (64 characters width for 4 inch)
            bill_lines = []
            line_width = 64
            
            # Header
            bill_lines.append("=" * line_width)
            bill_lines.append(shop_name.center(line_width))
            bill_lines.append(shop_address.center(line_width))
            bill_lines.append(f"Ph: {shop_phone}".center(line_width))
            bill_lines.append(f"GSTIN: {gstin}".center(line_width))
            bill_lines.append("=" * line_width)
            bill_lines.append("*** TAX INVOICE ***".center(line_width))
            bill_lines.append("(GST Compliant Bill)".center(line_width))
            bill_lines.append("=" * line_width)
            
            # Bill details
            bill_date = datetime.strptime(self.bill_data['bill_date'], '%Y-%m-%d %H:%M:%S')
            bill_lines.append(f"Invoice: {self.bill_data['invoice_number']}")
            bill_lines.append(f"Date: {bill_date.strftime('%d-%m-%Y %H:%M')}")
            
            if customer_name != "Walk-in Customer":
                bill_lines.append(f"Customer: {customer_name}")
                if customer_phone:
                    bill_lines.append(f"Phone: {customer_phone}")
            
            bill_lines.append("-" * line_width)
            
            # Items header
            bill_lines.append("Item                    Qty  Rate   Total")
            bill_lines.append("-" * line_width)
            
            # Items
            subtotal = 0
            total_discount = 0
            total_gst = 0
            
            for item in bill_items:
                # Calculate amounts - handle Row objects safely
                unit_price = float(item['unit_price'] if item['unit_price'] is not None else 0)
                quantity = int(item['quantity'] if item['quantity'] is not None else 1)
                discount_percentage = float(item['discount_percentage'] if item['discount_percentage'] is not None else 0)
                gst_percentage = float(item['gst_percentage'] if item['gst_percentage'] is not None else 0)
                
                line_subtotal = unit_price * quantity
                discount_amount = (line_subtotal * discount_percentage) / 100
                taxable_amount = line_subtotal - discount_amount
                gst_amount = (taxable_amount * gst_percentage) / 100
                line_total = taxable_amount + gst_amount
                
                subtotal += line_subtotal
                total_discount += discount_amount
                total_gst += gst_amount
                
                # Format item name (truncate if too long)
                item_name = str(item['item_name'] if item['item_name'] is not None else 'Unknown Item')
                if len(item_name) > 20:
                    item_name = item_name[:17] + "..."
                
                # Format line: "Item name           Qty  Rate   Total"
                qty_str = str(quantity)
                rate_str = f"{unit_price:.0f}"
                total_str = f"{line_total:.0f}"
                
                # Build line with proper spacing
                spaces_after_name = max(1, 20 - len(item_name))
                spaces_after_qty = max(1, 4 - len(qty_str))
                spaces_after_rate = max(1, 7 - len(rate_str))
                
                line = f"{item_name}{' ' * spaces_after_name}{qty_str}{' ' * spaces_after_qty}{rate_str}{' ' * spaces_after_rate}{total_str}"
                bill_lines.append(line)
                
                # Add discount info if applicable
                if discount_percentage > 0:
                    bill_lines.append(f"  Disc: {discount_percentage:.1f}% = -{discount_amount:.0f}")
                
                # Add GST info
                if gst_percentage > 0:
                    bill_lines.append(f"  GST: {gst_percentage:.1f}% = +{gst_amount:.0f}")
            
            bill_lines.append("=" * line_width)
            bill_lines.append("BILL SUMMARY".center(line_width))
            bill_lines.append("=" * line_width)
            
            # Summary calculations
            bill_discount_amount = self.bill_data.get('discount_amount', 0)
            cgst_amount = self.bill_data.get('cgst_amount', 0)
            sgst_amount = self.bill_data.get('sgst_amount', 0)
            igst_amount = self.bill_data.get('igst_amount', 0)
            round_off = self.bill_data.get('round_off', 0)
            
            # Subtotal and discounts section
            bill_lines.append(f"Subtotal:{str(int(subtotal)).rjust(line_width - 9)}")
            
            if total_discount > 0:
                bill_lines.append(f"Item Disc:{('-' + str(int(total_discount))).rjust(line_width - 10)}")
            
            if bill_discount_amount > 0:
                bill_lines.append(f"Bill Disc:{('-' + str(int(bill_discount_amount))).rjust(line_width - 10)}")
            
            # GST section separator
            if cgst_amount > 0 or igst_amount > 0:
                bill_lines.append("-" * line_width)
                bill_lines.append("GST BREAKDOWN".center(line_width))
                bill_lines.append("-" * line_width)
            
            # GST calculations
            if cgst_amount > 0:
                # Calculate average GST rate for display (assuming CGST = SGST)
                taxable_amount = subtotal - total_discount - bill_discount_amount
                total_gst_rate = (cgst_amount + sgst_amount) / (taxable_amount / 100) if taxable_amount > 0 else 0
                cgst_rate = total_gst_rate / 2
                bill_lines.append(f"CGST@{cgst_rate:.1f}%:{str(int(cgst_amount)).rjust(line_width - 12)}")
                bill_lines.append(f"SGST@{cgst_rate:.1f}%:{str(int(sgst_amount)).rjust(line_width - 12)}")
            
            if igst_amount > 0:
                # Calculate IGST rate for display
                taxable_amount = subtotal - total_discount - bill_discount_amount
                igst_rate = (igst_amount / (taxable_amount / 100)) if taxable_amount > 0 else 0
                bill_lines.append(f"IGST@{igst_rate:.1f}%:{str(int(igst_amount)).rjust(line_width - 12)}")
            
            # Round off section
            if round_off != 0:
                bill_lines.append("-" * line_width)
                sign = "+" if round_off > 0 else ""
                bill_lines.append(f"Round Off:{(sign + str(round_off)).rjust(line_width - 10)}")
            
            # Final total section
            bill_lines.append("=" * line_width)
            bill_lines.append(f"TOTAL:{str(int(self.bill_data['grand_total'])).rjust(line_width - 6)}")
            bill_lines.append("=" * line_width)
            
            # Payment info
            bill_lines.append(f"Payment: {self.bill_data['payment_mode']}")
            bill_lines.append("")
            
            # Footer - GST Compliance
            bill_lines.append("")
            bill_lines.append("*** TERMS & CONDITIONS ***".center(line_width))
            bill_lines.append("This is a Computer Generated Invoice".center(line_width))
            bill_lines.append("Subject to Local Jurisdiction".center(line_width))
            bill_lines.append("No Exchange | No Refund".center(line_width))
            bill_lines.append("")
            bill_lines.append("Thank you for shopping with us!".center(line_width))
            bill_lines.append("-" * line_width)
            bill_lines.append("")
            bill_lines.append("")  # Extra lines for paper cutting
            
            return "\n".join(bill_lines)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate bill: {str(e)}")
            return None
    
    def send_to_thermal_printer(self, content):
        """Send content to thermal printer"""
        try:
            import tempfile
            import os
            import platform
            
            # Create temporary file with bill content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Try to print to default printer
                system = platform.system()
                
                if system == "Windows":
                    # Windows: Print to default printer
                    os.system(f'type "{temp_file_path}" > PRN')
                    # Alternative: Use notepad /p for formatted printing
                    # os.system(f'notepad /p "{temp_file_path}"')
                    
                elif system == "Linux":
                    # Linux: Use lp command
                    os.system(f'lp "{temp_file_path}"')
                    
                elif system == "Darwin":  # macOS
                    # macOS: Use lp command
                    os.system(f'lp "{temp_file_path}"')
                
                else:
                    # Fallback: Show content in a dialog for manual printing
                    self.show_print_preview(content)
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            # Fallback: Show print preview
            self.show_print_preview(content)
            messagebox.showinfo("Print Method", 
                "Automatic printing failed. Please copy the text from the preview window and print manually.")
    
    def show_print_preview(self, content):
        """Show print preview window"""
        preview_window = tk.Toplevel()
        preview_window.title(f"Print Preview - {self.bill_data['invoice_number']}")
        preview_window.geometry("600x800")
        
        if self.window:
            try:
                preview_window.transient(self.window)
                preview_window.grab_set()
            except tk.TclError:
                pass
        
        # Create text widget with monospace font
        text_frame = ttk.Frame(preview_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, font=("Courier New", 10), wrap=tk.NONE)
        scrollbar_v = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        scrollbar_h = ttk.Scrollbar(text_frame, orient="horizontal", command=text_widget.xview)
        
        text_widget.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Insert content
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(preview_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="📄 Copy to Clipboard", 
                  command=lambda: self.copy_to_clipboard(content)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🖨️ Try Print Again", 
                  command=lambda: self.send_to_thermal_printer(content)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Close", 
                  command=preview_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def copy_to_clipboard(self, content):
        """Copy content to clipboard"""
        try:
            import tkinter as tk
            # Create a temporary root if needed
            temp_root = tk.Tk()
            temp_root.withdraw()
            temp_root.clipboard_clear()
            temp_root.clipboard_append(content)
            temp_root.update()
            temp_root.destroy()
            messagebox.showinfo("Copied", "Bill content copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {e}")
    
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


class EditBillDialog:
    """Dialog for editing existing bills"""
    
    def __init__(self, bill_data, parent=None):
        self.bill_data = bill_data
        self.parent = parent
        self.window = None
        self.bill_items = []
        
    def show(self):
        """Display the edit bill dialog"""
        self.window = tk.Toplevel()
        self.window.title(f"Edit Bill - {self.bill_data['invoice_number']}")
        self.window.geometry("900x700")
        
        if self.parent:
            try:
                self.window.transient(self.parent)
                self.window.grab_set()
            except tk.TclError:
                pass
        
        self.create_widgets()
        self.load_bill_data()
        
        # Center the window
        self.window.update_idletasks()
        if self.parent:
            x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.window.winfo_width() // 2)
            y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.window.winfo_height() // 2)
        else:
            x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
            y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Create the UI widgets"""
        main_container = ttk.Frame(self.window, padding="15")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.LabelFrame(main_container, text="Bill Information", padding="10")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Bill info
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(fill=tk.X)
        info_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(3, weight=1)
        
        ttk.Label(info_frame, text="Invoice:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=self.bill_data['invoice_number']).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        from datetime import datetime
        bill_date = datetime.strptime(self.bill_data['bill_date'], '%Y-%m-%d %H:%M:%S')
        ttk.Label(info_frame, text="Date:", font=("Arial", 10, "bold")).grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        ttk.Label(info_frame, text=bill_date.strftime('%d/%m/%Y %H:%M')).grid(row=0, column=3, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Payment mode
        ttk.Label(info_frame, text="Payment:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.payment_var = tk.StringVar(value=self.bill_data['payment_mode'])
        payment_combo = ttk.Combobox(info_frame, textvariable=self.payment_var, 
                                   values=["CASH", "CARD", "UPI"], state="readonly", width=15)
        payment_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Customer selection
        ttk.Label(info_frame, text="Customer:", font=("Arial", 10, "bold")).grid(row=1, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(info_frame, textvariable=self.customer_var, width=20)
        self.customer_combo.grid(row=1, column=3, sticky=tk.W, padx=(10, 0), pady=2)
        self.load_customers()
        
        # Items section
        items_frame = ttk.LabelFrame(main_container, text="Bill Items", padding="10")
        items_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Items tree
        columns = ('Item', 'Qty', 'Price', 'Disc%', 'GST%', 'Total')
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        self.items_tree.heading('Item', text='Item Name')
        self.items_tree.heading('Qty', text='Qty')
        self.items_tree.heading('Price', text='Unit Price')
        self.items_tree.heading('Disc%', text='Discount%')
        self.items_tree.heading('GST%', text='GST%')
        self.items_tree.heading('Total', text='Line Total')
        
        # Configure column widths
        self.items_tree.column('Item', width=300)
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
        
        # Bind events
        self.items_tree.bind('<Double-1>', self.edit_item)
        
        # Item action buttons
        item_buttons_frame = ttk.Frame(items_frame)
        item_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(item_buttons_frame, text="✏️ Edit Item", 
                  command=self.edit_item, width=15).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(item_buttons_frame, text="🗑️ Remove Item", 
                  command=self.remove_item, width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        # Bill totals
        totals_frame = ttk.LabelFrame(main_container, text="Bill Totals", padding="10")
        totals_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Bill discount
        discount_frame = ttk.Frame(totals_frame)
        discount_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(discount_frame, text="Bill Discount %:").pack(side=tk.LEFT)
        self.discount_var = tk.StringVar(value=str(self.bill_data.get('discount_percentage', 0)))
        discount_entry = ttk.Entry(discount_frame, textvariable=self.discount_var, width=10)
        discount_entry.pack(side=tk.RIGHT)
        discount_entry.bind('<KeyRelease>', self.update_totals)
        
        # Totals display
        self.totals_display = ttk.Frame(totals_frame)
        self.totals_display.pack(fill=tk.X)
        
        # Action buttons
        buttons_frame = ttk.Frame(main_container)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="💾 Save Changes", command=self.save_changes, 
                  style="Accent.TButton", width=15).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="🖨️ Print Bill", command=self.print_bill, 
                  width=15).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="❌ Cancel", command=self.window.destroy, 
                  width=15).pack(side=tk.RIGHT)
    
    def load_customers(self):
        """Load customers for dropdown"""
        try:
            from ..database.connection import db
            customers = db.execute_query("SELECT customer_id, customer_name FROM customers ORDER BY customer_name")
            
            customer_names = ["Walk-in Customer"] + [c['customer_name'] for c in customers]
            self.customer_combo['values'] = customer_names
            
            # Set current customer
            current_customer = db.execute_query(
                "SELECT c.customer_name FROM customers c JOIN bills b ON c.customer_id = b.customer_id WHERE b.bill_id = ?",
                (self.bill_data['bill_id'],)
            )
            if current_customer:
                self.customer_var.set(current_customer[0]['customer_name'])
            else:
                self.customer_var.set("Walk-in Customer")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {e}")
    
    def load_bill_data(self):
        """Load bill items and totals"""
        try:
            from ..database.connection import db
            
            # Get bill items
            query = '''
            SELECT * FROM bill_items 
            WHERE bill_id = ? 
            ORDER BY bill_item_id
            '''
            self.bill_items = db.execute_query(query, (self.bill_data['bill_id'],))
            
            # Clear and populate items tree
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            
            for item in self.bill_items:
                values = (
                    item['item_name'],
                    item['quantity'],
                    f"₹{item['unit_price']:.2f}",
                    f"{item['discount_percentage']:.1f}%",
                    f"{item['gst_percentage']:.1f}%",
                    f"₹{item['line_total']:.2f}"
                )
                self.items_tree.insert('', 'end', values=values)
            
            # Update totals display
            self.update_totals()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bill data: {e}")
    
    def edit_item(self, event=None):
        """Edit selected item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to edit")
            return
        
        # Get item index
        item_index = self.items_tree.index(selection[0])
        bill_item = self.bill_items[item_index]
        
        # Create edit dialog similar to EditBillItemDialog
        dialog = EditBillItemDialog(self.window, bill_item)
        if dialog.result:
            self.bill_items[item_index] = dialog.result
            self.refresh_items_display()
            self.update_totals()
    
    def remove_item(self):
        """Remove selected item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to remove")
            return
        
        if messagebox.askyesno("Remove Item", "Remove selected item from bill?"):
            item_index = self.items_tree.index(selection[0])
            del self.bill_items[item_index]
            self.refresh_items_display()
            self.update_totals()
    
    def refresh_items_display(self):
        """Refresh the items display"""
        # Clear existing items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Add items
        for item in self.bill_items:
            values = (
                item['item_name'],
                item['quantity'],
                f"₹{item['unit_price']:.2f}",
                f"{item['discount_percentage']:.1f}%",
                f"{item['gst_percentage']:.1f}%",
                f"₹{item['line_total']:.2f}"
            )
            self.items_tree.insert('', 'end', values=values)
    
    def update_totals(self, event=None):
        """Update bill totals display"""
        # Clear existing totals display
        for widget in self.totals_display.winfo_children():
            widget.destroy()
        
        if not self.bill_items:
            ttk.Label(self.totals_display, text="No items in bill").pack()
            return
        
        # Calculate totals
        subtotal = 0
        item_discount = 0
        
        for item in self.bill_items:
            item_unit_price = float(item.get('unit_price', 0))
            item_quantity = int(item.get('quantity', 1))
            item_discount_percent = float(item.get('discount_percentage', 0))
            
            item_subtotal = item_unit_price * item_quantity
            item_discount_amt = (item_subtotal * item_discount_percent) / 100
            
            subtotal += item_subtotal
            item_discount += item_discount_amt
        
        try:
            bill_discount_percent = float(self.discount_var.get() or 0)
        except ValueError:
            bill_discount_percent = 0
        
        bill_discount_amount = ((subtotal - item_discount) * bill_discount_percent) / 100
        discounted_subtotal = subtotal - item_discount - bill_discount_amount
        
        # Calculate GST
        total_gst = 0
        for item in self.bill_items:
            item_unit_price = float(item.get('unit_price', 0))
            item_quantity = int(item.get('quantity', 1))
            item_discount_percent = float(item.get('discount_percentage', 0))
            item_gst_percent = float(item.get('gst_percentage', 0))
            
            item_subtotal = item_unit_price * item_quantity
            item_discount_amt = (item_subtotal * item_discount_percent) / 100
            item_taxable = item_subtotal - item_discount_amt
            item_gst = (item_taxable * item_gst_percent) / 100
            total_gst += item_gst
        
        # Apply bill discount to GST proportionally
        if bill_discount_percent > 0 and subtotal > 0:
            gst_ratio = total_gst / (subtotal - item_discount) if (subtotal - item_discount) > 0 else 0
            total_gst = discounted_subtotal * gst_ratio
        
        grand_total = discounted_subtotal + total_gst
        
        # Display totals
        totals_data = [
            ("Subtotal:", f"₹{subtotal:.2f}"),
            ("Item Discount:", f"-₹{item_discount:.2f}") if item_discount > 0 else None,
            ("Bill Discount:", f"-₹{bill_discount_amount:.2f}") if bill_discount_amount > 0 else None,
            ("GST Total:", f"₹{total_gst:.2f}"),
            ("GRAND TOTAL:", f"₹{grand_total:.2f}")
        ]
        
        for i, item in enumerate([x for x in totals_data if x is not None]):
            label, value = item
            row_frame = ttk.Frame(self.totals_display)
            row_frame.pack(fill=tk.X, pady=1)
            
            font_style = ("Arial", 12, "bold") if "GRAND" in label else ("Arial", 10)
            color = "red" if "GRAND" in label else "black"
            
            ttk.Label(row_frame, text=label, font=font_style).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=value, font=font_style, foreground=color).pack(side=tk.RIGHT)
    
    def save_changes(self):
        """Save changes to the bill"""
        try:
            from ..database.connection import db
            from ..models.billing import BillingManager, GSTCalculator
            
            if not self.bill_items:
                messagebox.showerror("Error", "Cannot save bill without items")
                return
            
            # Update payment mode
            db.execute_update("UPDATE bills SET payment_mode = ? WHERE bill_id = ?",
                            (self.payment_var.get(), self.bill_data['bill_id']))
            
            # Update customer
            customer_name = self.customer_var.get()
            if customer_name and customer_name != "Walk-in Customer":
                customer_result = db.execute_query(
                    "SELECT customer_id FROM customers WHERE customer_name = ?", 
                    (customer_name,)
                )
                if customer_result:
                    db.execute_update("UPDATE bills SET customer_id = ? WHERE bill_id = ?",
                                    (customer_result[0]['customer_id'], self.bill_data['bill_id']))
            else:
                db.execute_update("UPDATE bills SET customer_id = NULL WHERE bill_id = ?",
                                (self.bill_data['bill_id'],))
            
            # Delete existing bill items
            db.execute_update("DELETE FROM bill_items WHERE bill_id = ?", (self.bill_data['bill_id'],))
            
            # Insert updated items
            for item in self.bill_items:
                # Recalculate line total
                calc = GSTCalculator.calculate_line_total(
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    discount_percentage=item['discount_percentage'],
                    gst_rate=item['gst_percentage']
                )
                
                query = '''
                INSERT INTO bill_items (
                    bill_id, item_id, item_name, barcode, quantity, unit_price, 
                    discount_percentage, discount_amount, gst_percentage, gst_amount, line_total
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                
                db.execute_update(query, (
                    self.bill_data['bill_id'],
                    item.get('item_id'),
                    item['item_name'],
                    item.get('barcode', ''),
                    item['quantity'],
                    item['unit_price'],
                    item['discount_percentage'],
                    calc['discount_amount'],
                    item['gst_percentage'],
                    calc['gst_amount'],
                    calc['line_total']
                ))
            
            # Recalculate bill totals
            try:
                bill_discount_percent = float(self.discount_var.get() or 0)
            except ValueError:
                bill_discount_percent = 0
            
            BillingManager.calculate_bill_totals(self.bill_data['bill_id'], bill_discount_percent)
            
            messagebox.showinfo("Success", "Bill updated successfully!")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {e}")
    
    def print_bill(self):
        """Print the bill"""
        # Create a temporary BillDetailsWindow to use its print functionality
        temp_bill_window = BillDetailsWindow(self.bill_data)
        temp_bill_window.print_bill()


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
        self.quantity_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.quantity_entry.insert(0, str(self.original_item['quantity']))
        self.quantity_entry.focus()
        self.quantity_entry.select_range(0, tk.END)
        
        ttk.Label(fields_frame, text="Discount %:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.discount_entry = ttk.Entry(fields_frame, width=20)
        self.discount_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.discount_entry.insert(0, str(self.original_item['discount_percentage']))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Update", command=self.update_item).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.update_item())
    
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


class CreateCustomerDialog:
    """Dialog for creating new customer"""
    
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Customer")
        self.dialog.geometry("400x250")
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
        
        ttk.Label(main_frame, text="👤 Create New Customer", 
                 font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))
        
        # Form fields
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.X, pady=(0, 20))
        fields_frame.columnconfigure(1, weight=1)
        
        ttk.Label(fields_frame, text="Customer Name:*").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.name_entry = ttk.Entry(fields_frame, width=25, font=("Segoe UI", 11))
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=8, padx=(10, 0))
        self.name_entry.focus()
        
        ttk.Label(fields_frame, text="Phone Number:").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.phone_entry = ttk.Entry(fields_frame, width=25, font=("Segoe UI", 11))
        self.phone_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=8, padx=(10, 0))
        
        ttk.Label(fields_frame, text="Address:").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.address_entry = ttk.Entry(fields_frame, width=25, font=("Segoe UI", 11))
        self.address_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=8, padx=(10, 0))
        
        # Required field note
        ttk.Label(main_frame, text="* Required field", 
                 font=("Segoe UI", 9), foreground="gray").pack(anchor=tk.W)
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(buttons_frame, text="✓ Create", command=self.create_customer,
                  style="Accent.TButton", width=12).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="✗ Cancel", command=self.dialog.destroy, 
                  width=12).pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda _: self.create_customer())
        self.dialog.bind('<Escape>', lambda _: self.dialog.destroy())
    
    def create_customer(self):
        """Create the customer"""
        customer_name = self.name_entry.get().strip()
        if not customer_name:
            messagebox.showerror("Error", "Customer name is required")
            self.name_entry.focus()
            return
        
        phone_number = self.phone_entry.get().strip()
        if phone_number:
            # Basic phone number validation - allow digits, spaces, hyphens, plus sign
            cleaned_phone = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            if not cleaned_phone.isdigit() or len(cleaned_phone) < 10:
                messagebox.showerror("Error", "Please enter a valid phone number (minimum 10 digits)")
                self.phone_entry.focus()
                return
        
        address = self.address_entry.get().strip()
        
        try:
            from ..database.connection import db
            
            # Check if phone number already exists (only if phone number is provided)
            if phone_number:
                existing = db.execute_query(
                    "SELECT customer_id FROM customers WHERE phone_number = ?",
                    (phone_number,)
                )
                
                if existing:
                    messagebox.showerror("Error", "Customer with this phone number already exists")
                    return
            
            # Insert new customer
            query = '''
            INSERT INTO customers (customer_name, phone_number, address)
            VALUES (?, ?, ?)
            '''
            
            customer_id = db.execute_insert(query, (customer_name, phone_number or None, address or None))
            if customer_id:
                
                # Create result
                self.result = {
                    'customer_id': customer_id,
                    'customer_name': customer_name,
                    'phone_number': phone_number,
                    'address': address
                }
                
                messagebox.showinfo("Success", f"Customer '{customer_name}' created successfully!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to create customer")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create customer: {e}")