"""
Items Management Window
Interface for managing items, categories, and inventory
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ..models.items import ItemsManager


class ItemsManagementWindow:
    """Items management interface"""
    
    def __init__(self):
        self.window = None
        self.items_tree = None
        self.items_data = []
        self.categories_data = []
    
    def show(self, parent=None):
        """Display the items management window"""
        self.window = tk.Toplevel(parent)
        self.window.title("Items Management - தங்கமயில் சில்க்ஸ்")
        self.window.geometry("1000x700")
        
        # Set up proper window cleanup
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
        try:
            if parent:
                self.window.transient(parent)
            self.window.grab_set()
        except tk.TclError:
            pass  # Skip if parent window is not available
        
        self.create_widgets()
        self.load_data()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def close_window(self):
        """Properly close the items management window"""
        if self.window:
            try:
                self.window.grab_release()
            except tk.TclError:
                pass
            self.window.destroy()
            self.window = None
    
    def create_widgets(self):
        """Create the UI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title and toolbar
        self.create_toolbar(main_frame)
        
        # Search frame
        self.create_search_frame(main_frame)
        
        # Items tree view
        self.create_items_tree(main_frame)
        
        # Bottom buttons
        self.create_bottom_buttons(main_frame)
    
    def create_toolbar(self, parent):
        """Create toolbar with action buttons"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Title
        ttk.Label(toolbar_frame, text="Items Management", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Action buttons
        button_frame = ttk.Frame(toolbar_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Add Item", command=self.add_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Edit Item", command=self.edit_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Update Stock", command=self.update_stock).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Categories", command=self.manage_categories).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Refresh", command=self.load_data).pack(side=tk.LEFT, padx=2)
    
    def create_search_frame(self, parent):
        """Create search frame"""
        search_frame = ttk.LabelFrame(parent, text="Search & Filter", padding="10")
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky=tk.W)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        ttk.Button(search_frame, text="Clear", command=self.clear_search).grid(row=0, column=2)
        
        # Filters
        ttk.Label(search_frame, text="Category:").grid(row=0, column=3, sticky=tk.W, padx=(20, 5))
        self.category_var = tk.StringVar(value="All Categories")
        self.category_combo = ttk.Combobox(search_frame, textvariable=self.category_var, 
                                          state="readonly", width=15)
        self.category_combo.grid(row=0, column=4, padx=(0, 10))
        self.category_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        ttk.Label(search_frame, text="Stock:").grid(row=0, column=5, sticky=tk.W)
        self.stock_var = tk.StringVar(value="All Items")
        stock_combo = ttk.Combobox(search_frame, textvariable=self.stock_var, 
                                  values=["All Items", "In Stock", "Low Stock", "Out of Stock"], 
                                  state="readonly", width=12)
        stock_combo.grid(row=0, column=6)
        stock_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
    
    def create_items_tree(self, parent):
        """Create items treeview"""
        tree_frame = ttk.LabelFrame(parent, text="Items List", padding="10")
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Create treeview
        columns = ('ID', 'Barcode', 'Name', 'Category', 'Price', 'GST%', 'Stock', 'Status')
        self.items_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.items_tree.heading('ID', text='ID')
        self.items_tree.heading('Barcode', text='Barcode')
        self.items_tree.heading('Name', text='Item Name')
        self.items_tree.heading('Category', text='Category')
        self.items_tree.heading('Price', text='Price (₹)')
        self.items_tree.heading('GST%', text='GST%')
        self.items_tree.heading('Stock', text='Stock')
        self.items_tree.heading('Status', text='Status')
        
        # Configure column widths
        self.items_tree.column('ID', width=50)
        self.items_tree.column('Barcode', width=100)
        self.items_tree.column('Name', width=200)
        self.items_tree.column('Category', width=120)
        self.items_tree.column('Price', width=80)
        self.items_tree.column('GST%', width=60)
        self.items_tree.column('Stock', width=80)
        self.items_tree.column('Status', width=80)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.items_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.items_tree.xview)
        self.items_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid treeview and scrollbars
        self.items_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind double-click event
        self.items_tree.bind('<Double-1>', lambda e: self.edit_item())
    
    def create_bottom_buttons(self, parent):
        """Create bottom action buttons"""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.grid(row=3, column=0, pady=(10, 0))
        
        ttk.Button(bottom_frame, text="Close", command=self.window.destroy).pack()
    
    def load_data(self):
        """Load items and categories data"""
        try:
            # Load categories
            self.categories_data = ItemsManager.get_all_categories()
            category_names = ["All Categories"] + [cat['category_name'] for cat in self.categories_data]
            self.category_combo['values'] = category_names
            
            # Load items
            self.items_data = ItemsManager.get_all_items()
            self.populate_items_tree(self.items_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
    
    def populate_items_tree(self, items):
        """Populate the items treeview"""
        # Clear existing items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Add items
        for item in items:
            status = "Active" if item.get('is_active', 1) else "Inactive"
            stock_status = ""
            if item['stock_quantity'] == 0:
                stock_status = " (Out)"
            elif item['stock_quantity'] <= 10:  # Assuming 10 is low stock threshold
                stock_status = " (Low)"
            
            values = (
                item['item_id'],
                item['barcode'] or '',
                item['item_name'],
                item['category_name'] or 'N/A',
                f"{item['price']:.2f}",
                f"{item['gst_percentage']:.1f}",
                f"{item['stock_quantity']}{stock_status}",
                status
            )
            
            # Color coding for stock levels
            item_id = self.items_tree.insert('', 'end', values=values)
            if item['stock_quantity'] == 0:
                self.items_tree.set(item_id, 'Stock', f"{item['stock_quantity']} (Out)")
            elif item['stock_quantity'] <= 10:
                self.items_tree.set(item_id, 'Stock', f"{item['stock_quantity']} (Low)")
    
    def on_search(self, event=None):
        """Handle search input"""
        search_term = self.search_entry.get().strip()
        if search_term:
            try:
                filtered_items = ItemsManager.search_items(search_term)
                self.populate_items_tree(filtered_items)
            except Exception as e:
                messagebox.showerror("Error", f"Search failed: {e}")
        else:
            self.apply_filters()
    
    def on_filter_change(self, event=None):
        """Handle filter changes"""
        self.apply_filters()
    
    def apply_filters(self):
        """Apply category and stock filters"""
        try:
            filtered_items = self.items_data
            
            # Apply category filter
            category = self.category_var.get()
            if category != "All Categories":
                filtered_items = [item for item in filtered_items 
                                if item['category_name'] == category]
            
            # Apply stock filter
            stock_filter = self.stock_var.get()
            if stock_filter == "In Stock":
                filtered_items = [item for item in filtered_items if item['stock_quantity'] > 10]
            elif stock_filter == "Low Stock":
                filtered_items = [item for item in filtered_items 
                                if 0 < item['stock_quantity'] <= 10]
            elif stock_filter == "Out of Stock":
                filtered_items = [item for item in filtered_items if item['stock_quantity'] == 0]
            
            self.populate_items_tree(filtered_items)
            
        except Exception as e:
            messagebox.showerror("Error", f"Filter failed: {e}")
    
    def clear_search(self):
        """Clear search and reset filters"""
        self.search_entry.delete(0, tk.END)
        self.category_var.set("All Categories")
        self.stock_var.set("All Items")
        self.populate_items_tree(self.items_data)
    
    def add_item(self):
        """Add new item"""
        dialog = ItemEditDialog(self.window, self.categories_data)
        if dialog.result:
            self.load_data()
    
    def edit_item(self):
        """Edit selected item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to edit")
            return
        
        item_values = self.items_tree.item(selection[0])['values']
        item_id = item_values[0]
        
        # Find the item data
        item = next((i for i in self.items_data if i['item_id'] == item_id), None)
        if not item:
            messagebox.showerror("Error", "Item not found")
            return
        
        dialog = ItemEditDialog(self.window, self.categories_data, item)
        if dialog.result:
            self.load_data()
    
    def update_stock(self):
        """Update stock for selected item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to update stock")
            return
        
        item_values = self.items_tree.item(selection[0])['values']
        item_id = item_values[0]
        item_name = item_values[2]
        current_stock = item_values[6].split()[0]  # Remove status text
        
        dialog = StockUpdateDialog(self.window, item_name, current_stock)
        if dialog.result is not None:
            try:
                from ..models.auth import auth
                staff_id = auth.get_current_staff_id()
                success = ItemsManager.update_stock(
                    item_id, dialog.result, "ADJUSTMENT", staff_id, dialog.notes
                )
                if success:
                    messagebox.showinfo("Success", "Stock updated successfully!")
                    self.load_data()
                else:
                    messagebox.showerror("Error", "Failed to update stock")
            except Exception as e:
                messagebox.showerror("Error", f"Stock update failed: {e}")
    
    def manage_categories(self):
        """Open categories management dialog"""
        dialog = CategoriesDialog(self.window)
        if dialog.result:
            self.load_data()


class ItemEditDialog:
    """Dialog for adding/editing items"""
    
    def __init__(self, parent, categories, item=None):
        self.result = False
        self.item = item
        self.categories = categories
        
        self.dialog = tk.Toplevel(parent)
        title = "Edit Item" if item else "Add New Item"
        self.dialog.title(title)
        self.dialog.geometry("500x400")
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
        
        if item:
            self.populate_fields()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title = "Edit Item" if self.item else "Add New Item"
        ttk.Label(main_frame, text=title, font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Form fields
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        fields_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Item Name
        ttk.Label(fields_frame, text="Item Name *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(fields_frame, width=40)
        self.name_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.name_entry.focus()
        row += 1
        
        # Barcode
        ttk.Label(fields_frame, text="Barcode:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.barcode_entry = ttk.Entry(fields_frame, width=40)
        self.barcode_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Category
        ttk.Label(fields_frame, text="Category:").grid(row=row, column=0, sticky=tk.W, pady=5)
        category_names = [""] + [cat['category_name'] for cat in self.categories]
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(fields_frame, textvariable=self.category_var, 
                                          values=category_names, state="readonly", width=37)
        self.category_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Price
        ttk.Label(fields_frame, text="Price (₹) *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.price_entry = ttk.Entry(fields_frame, width=40)
        self.price_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # GST Percentage
        ttk.Label(fields_frame, text="GST % *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.gst_entry = ttk.Entry(fields_frame, width=40)
        self.gst_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.gst_entry.insert(0, "5.0")  # Default GST rate
        row += 1
        
        # Stock Quantity
        ttk.Label(fields_frame, text="Stock Quantity:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.stock_entry = ttk.Entry(fields_frame, width=40)
        self.stock_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.stock_entry.insert(0, "0")
        row += 1
        
        # Status (for edit mode)
        if self.item:
            ttk.Label(fields_frame, text="Status:").grid(row=row, column=0, sticky=tk.W, pady=5)
            self.status_var = tk.StringVar(value="Active")
            status_combo = ttk.Combobox(fields_frame, textvariable=self.status_var, 
                                       values=["Active", "Inactive"], state="readonly", width=37)
            status_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        save_text = "Update Item" if self.item else "Add Item"
        ttk.Button(buttons_frame, text=save_text, command=self.save_item).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def populate_fields(self):
        """Populate fields with item data"""
        if not self.item:
            return
        
        self.name_entry.insert(0, self.item['item_name'])
        if self.item['barcode']:
            self.barcode_entry.insert(0, self.item['barcode'])
        
        if self.item['category_name']:
            self.category_var.set(self.item['category_name'])
        
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, str(self.item['price']))
        
        self.gst_entry.delete(0, tk.END)
        self.gst_entry.insert(0, str(self.item['gst_percentage']))
        
        self.stock_entry.delete(0, tk.END)
        self.stock_entry.insert(0, str(self.item['stock_quantity']))
        
        if hasattr(self, 'status_var'):
            self.status_var.set("Active" if self.item.get('is_active', 1) else "Inactive")
    
    def save_item(self):
        """Save the item"""
        # Validate inputs
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Item name is required")
            self.name_entry.focus()
            return
        
        barcode = self.barcode_entry.get().strip() or None
        
        # Check barcode uniqueness
        if barcode:
            exclude_id = self.item['item_id'] if self.item else None
            if ItemsManager.barcode_exists(barcode, exclude_id):
                messagebox.showerror("Error", "Barcode already exists")
                self.barcode_entry.focus()
                return
        
        try:
            price = float(self.price_entry.get())
            if price <= 0:
                raise ValueError("Price must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid price")
            self.price_entry.focus()
            return
        
        try:
            gst_percentage = float(self.gst_entry.get())
            if gst_percentage < 0 or gst_percentage > 28:
                raise ValueError("GST must be between 0 and 28")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid GST percentage (0-28)")
            self.gst_entry.focus()
            return
        
        try:
            stock_quantity = int(self.stock_entry.get())
            if stock_quantity < 0:
                raise ValueError("Stock cannot be negative")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid stock quantity")
            self.stock_entry.focus()
            return
        
        # Get category ID
        category_id = None
        category_name = self.category_var.get()
        if category_name:
            category = next((cat for cat in self.categories if cat['category_name'] == category_name), None)
            if category:
                category_id = category['category_id']
        
        # Prepare item data
        item_data = {
            'item_name': name,
            'barcode': barcode,
            'category_id': category_id,
            'price': price,
            'gst_percentage': gst_percentage,
            'stock_quantity': stock_quantity
        }
        
        if self.item:
            item_data['is_active'] = self.status_var.get() == "Active"
        
        try:
            if self.item:
                success = ItemsManager.update_item(self.item['item_id'], item_data)
                message = "Item updated successfully!"
            else:
                success = ItemsManager.add_item(item_data)
                message = "Item added successfully!"
            
            if success:
                self.result = True
                messagebox.showinfo("Success", message)
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", f"Failed to {'update' if self.item else 'add'} item")
        
        except Exception as e:
            messagebox.showerror("Error", f"Operation failed: {e}")


class StockUpdateDialog:
    """Dialog for updating item stock"""
    
    def __init__(self, parent, item_name, current_stock):
        self.result = None
        self.notes = ""
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Update Stock - {item_name}")
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
        
        self.create_widgets(item_name, current_stock)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_widgets(self, item_name, current_stock):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=f"Update Stock", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        ttk.Label(main_frame, text=f"Item: {item_name}", font=("Arial", 10)).pack(pady=(0, 5))
        ttk.Label(main_frame, text=f"Current Stock: {current_stock}", font=("Arial", 10)).pack(pady=(0, 20))
        
        # Form fields
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.X, pady=(0, 20))
        fields_frame.columnconfigure(1, weight=1)
        
        ttk.Label(fields_frame, text="New Stock Quantity:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.stock_entry = ttk.Entry(fields_frame, width=30)
        self.stock_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.stock_entry.insert(0, str(current_stock))
        self.stock_entry.focus()
        self.stock_entry.select_range(0, tk.END)
        
        ttk.Label(fields_frame, text="Notes (optional):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.notes_entry = ttk.Entry(fields_frame, width=30)
        self.notes_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Update Stock", command=self.update_stock).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.update_stock())
    
    def update_stock(self):
        """Update the stock"""
        try:
            new_stock = int(self.stock_entry.get())
            if new_stock < 0:
                raise ValueError("Stock cannot be negative")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid stock quantity")
            self.stock_entry.focus()
            return
        
        self.result = new_stock
        self.notes = self.notes_entry.get().strip()
        self.dialog.destroy()


class CategoriesDialog:
    """Dialog for managing categories"""
    
    def __init__(self, parent):
        self.result = False
        self.categories_data = []
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Manage Categories")
        self.dialog.geometry("400x300")
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
        self.load_categories()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Manage Categories", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Categories list
        list_frame = ttk.LabelFrame(main_frame, text="Categories", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.categories_listbox = tk.Listbox(list_frame, height=8)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.categories_listbox.yview)
        self.categories_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.categories_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add category frame
        add_frame = ttk.LabelFrame(main_frame, text="Add Category", padding="10")
        add_frame.pack(fill=tk.X, pady=(0, 20))
        add_frame.columnconfigure(0, weight=1)
        
        entry_frame = ttk.Frame(add_frame)
        entry_frame.pack(fill=tk.X)
        entry_frame.columnconfigure(0, weight=1)
        
        self.new_category_entry = ttk.Entry(entry_frame)
        self.new_category_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.new_category_entry.bind('<Return>', lambda e: self.add_category())
        
        ttk.Button(entry_frame, text="Add", command=self.add_category).grid(row=0, column=1)
        
        # Bottom buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Close", command=self.close_dialog).pack(side=tk.RIGHT)
    
    def load_categories(self):
        """Load categories from database"""
        try:
            self.categories_data = ItemsManager.get_all_categories()
            
            # Clear listbox
            self.categories_listbox.delete(0, tk.END)
            
            # Populate listbox
            for category in self.categories_data:
                self.categories_listbox.insert(tk.END, category['category_name'])
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load categories: {e}")
    
    def add_category(self):
        """Add new category"""
        category_name = self.new_category_entry.get().strip()
        if not category_name:
            messagebox.showerror("Error", "Category name is required")
            self.new_category_entry.focus()
            return
        
        # Check if category exists
        if any(cat['category_name'].lower() == category_name.lower() for cat in self.categories_data):
            messagebox.showerror("Error", "Category already exists")
            self.new_category_entry.focus()
            return
        
        try:
            success = ItemsManager.add_category(category_name)
            if success:
                self.result = True
                self.new_category_entry.delete(0, tk.END)
                self.load_categories()
                messagebox.showinfo("Success", "Category added successfully!")
            else:
                messagebox.showerror("Error", "Failed to add category")
        
        except Exception as e:
            messagebox.showerror("Error", f"Add category failed: {e}")
    
    def close_dialog(self):
        """Close the dialog"""
        self.dialog.destroy()