"""
POS Billing Window
Point of Sale interface for creating bills and processing transactions
"""

import tkinter as tk
from tkinter import ttk, messagebox
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
    
    def show(self):
        """Display the POS billing window"""
        self.window = tk.Toplevel()
        self.window.title("POS Billing - தங்கமயில் சில்க்ஸ்")
        self.window.geometry("1200x800")
        try:
            self.window.transient()
            self.window.grab_set()
        except tk.TclError:
            pass  # Skip if parent window is not available
        
        self.create_widgets()
        self.start_new_bill()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        # Focus on barcode entry
        self.barcode_entry.focus()
        
        # Bind keyboard shortcuts
        self.window.bind('<Control-w>', lambda e: self.window.destroy())
        self.window.bind('<Escape>', lambda e: self.window.destroy())
        self.window.bind('<Control-u>', lambda e: self.create_new_customer())  # Ctrl+Shift+C for new customer
    
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
        
        ttk.Button(actions_frame, text="Save & Print", command=self.save_and_print, 
                  style="Accent.TButton").pack(fill=tk.X, pady=2)
        
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
        if not self.current_bill_id:
            messagebox.showwarning("No Bill", "Please start a new bill first")
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
        """Confirm new bill creation"""
        if self.bill_items:
            if not messagebox.askyesno("New Bill", "Current bill will be lost. Continue?"):
                return
        
        self.start_new_bill()
    
    def save_and_print(self):
        """Save and print the current bill"""
        if not self.current_bill_id or not self.bill_items:
            messagebox.showwarning("No Items", "Please add items to the bill first")
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
                
                # TODO: Add printing functionality here
                messagebox.showinfo("Print", "Printing functionality to be implemented")
                
                # Start new bill
                self.start_new_bill()
            else:
                messagebox.showerror("Error", "Failed to save bill")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save bill: {e}")
    
    def hold_bill(self):
        """Hold current bill"""
        if not self.bill_items:
            messagebox.showwarning("No Items", "No items to hold")
            return
        
        # TODO: Implement bill holding functionality
        messagebox.showinfo("Hold Bill", "Bill holding functionality to be implemented")
    
    def cancel_bill(self):
        """Cancel current bill"""
        if self.bill_items:
            if messagebox.askyesno("Cancel Bill", "Cancel current bill and lose all items?"):
                self.start_new_bill()
        else:
            messagebox.showinfo("No Items", "No items to cancel")


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