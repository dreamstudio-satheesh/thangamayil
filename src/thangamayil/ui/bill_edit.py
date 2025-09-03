"""
Bill Edit Dialog
Comprehensive bill editing interface with item management and totals calculation
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


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
        
        # Create edit dialog
        from .item_edit import EditBillItemDialog
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
            item_unit_price = float(item['unit_price'] if item['unit_price'] is not None else 0)
            item_quantity = int(item['quantity'] if item['quantity'] is not None else 1)
            item_discount_percent = float(item['discount_percentage'] if item['discount_percentage'] is not None else 0)
            
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
            item_unit_price = float(item['unit_price'] if item['unit_price'] is not None else 0)
            item_quantity = int(item['quantity'] if item['quantity'] is not None else 1)
            item_discount_percent = float(item['discount_percentage'] if item['discount_percentage'] is not None else 0)
            item_gst_percent = float(item['gst_percentage'] if item['gst_percentage'] is not None else 0)
            
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
        
        for item in [x for x in totals_data if x is not None]:
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
        try:
            from .thermal_printer import ThermalPrinter
            printer = ThermalPrinter()
            printer.print_bill(self.bill_data, self.window)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print bill: {e}")