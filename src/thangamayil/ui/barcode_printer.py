"""
Barcode Sticker Printer Module
Interface for printing barcode stickers with customizable MRP and quantity
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tempfile
import os
import platform
from datetime import datetime
from ..models.items import ItemsManager
from ..database.connection import db


class BarcodePrinterWindow:
    """Barcode sticker printing interface"""
    
    def __init__(self):
        self.window = None
        self.items_data = []
        self.selected_item = None
        
    def show(self, parent=None):
        """Display the barcode printer window"""
        self.window = tk.Toplevel(parent)
        self.window.title("Barcode Sticker Printer - தங்கமயில் சில்க்ஸ்")
        self.window.geometry("800x600")
        
        # Set up proper window cleanup
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
        try:
            if parent:
                self.window.transient(parent)
            self.window.grab_set()
        except tk.TclError:
            pass  # Skip if parent window is not available
        
        self.create_widgets()
        self.load_items()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def close_window(self):
        """Properly close the barcode printer window"""
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
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🏷️ Barcode Sticker Printer", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left panel - Item selection
        self.create_item_selection_panel(main_frame)
        
        # Right panel - Print settings
        self.create_print_settings_panel(main_frame)
        
        # Bottom panel - Preview and print
        self.create_preview_panel(main_frame)
    
    def create_item_selection_panel(self, parent):
        """Create item selection panel"""
        left_panel = ttk.LabelFrame(parent, text="📦 Select Item", padding="10")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=1)
        
        # Search frame
        search_frame = ttk.Frame(left_panel)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        search_frame.columnconfigure(0, weight=1)
        
        ttk.Label(search_frame, text="Search Items:").grid(row=0, column=0, sticky=tk.W)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        # Items listbox
        list_frame = ttk.Frame(left_panel)
        list_frame.pack(fill=tk.BOTH, expand=True)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Create treeview for items
        columns = ('Name', 'Barcode', 'Price', 'Stock')
        self.items_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.items_tree.heading('Name', text='Item Name')
        self.items_tree.heading('Barcode', text='Barcode')
        self.items_tree.heading('Price', text='Price (₹)')
        self.items_tree.heading('Stock', text='Stock')
        
        # Configure column widths
        self.items_tree.column('Name', width=200)
        self.items_tree.column('Barcode', width=120)
        self.items_tree.column('Price', width=80)
        self.items_tree.column('Stock', width=60)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.items_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=self.items_tree.xview)
        self.items_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid treeview and scrollbars
        self.items_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind selection
        self.items_tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        # Refresh button
        ttk.Button(left_panel, text="🔄 Refresh Items", 
                  command=self.load_items).pack(pady=(10, 0))
    
    def create_print_settings_panel(self, parent):
        """Create print settings panel"""
        right_panel = ttk.LabelFrame(parent, text="🖨️ Print Settings", padding="10")
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(1, weight=1)
        
        row = 0
        
        # Selected item display
        ttk.Label(right_panel, text="Selected Item:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        row += 1
        
        self.selected_item_label = ttk.Label(right_panel, text="No item selected", 
                                           foreground="gray", wraplength=300)
        self.selected_item_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))
        row += 1
        
        # Store name
        ttk.Label(right_panel, text="Store Name:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.store_name_var = tk.StringVar()
        store_name_entry = ttk.Entry(right_panel, textvariable=self.store_name_var, width=30)
        store_name_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Load default store name
        store_name = db.get_setting('shop_name') or 'தங்கமயில் சில்க்ஸ்'
        self.store_name_var.set(store_name)
        row += 1
        
        # Item name (editable)
        ttk.Label(right_panel, text="Item Name:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.item_name_var = tk.StringVar()
        self.item_name_entry = ttk.Entry(right_panel, textvariable=self.item_name_var, width=30)
        self.item_name_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Barcode (read-only)
        ttk.Label(right_panel, text="Barcode:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.barcode_var = tk.StringVar()
        barcode_entry = ttk.Entry(right_panel, textvariable=self.barcode_var, 
                                 width=30, state="readonly")
        barcode_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # MRP (editable)
        ttk.Label(right_panel, text="MRP (₹):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.mrp_var = tk.StringVar()
        self.mrp_entry = ttk.Entry(right_panel, textvariable=self.mrp_var, width=30)
        self.mrp_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Number of stickers
        ttk.Label(right_panel, text="No. of Stickers:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.quantity_var = tk.StringVar(value="1")
        quantity_spinbox = ttk.Spinbox(right_panel, from_=1, to=100, textvariable=self.quantity_var, 
                                      width=28)
        quantity_spinbox.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Sticker size optimized for 4-inch thermal printer
        ttk.Label(right_panel, text="Sticker Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.size_var = tk.StringVar(value="Standard (32 chars)")
        size_combo = ttk.Combobox(right_panel, textvariable=self.size_var, width=27,
                                 values=[
                                     "Small (20 chars) - 3 per row",
                                     "Standard (32 chars) - 2 per row", 
                                     "Large (48 chars) - 1 per row",
                                     "Full Width (64 chars) - 1 per row"
                                 ],
                                 state="readonly")
        size_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        size_combo.bind('<<ComboboxSelected>>', self.on_size_change)
        row += 1
        
        # Stickers per row (auto-calculated based on size)
        ttk.Label(right_panel, text="Stickers per Row:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.per_row_var = tk.StringVar(value="2")
        self.per_row_entry = ttk.Entry(right_panel, textvariable=self.per_row_var, 
                                      width=28, state="readonly")
        self.per_row_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Sticker width (characters) - auto-calculated
        ttk.Label(right_panel, text="Sticker Width:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.width_var = tk.StringVar(value="32")
        self.width_entry = ttk.Entry(right_panel, textvariable=self.width_var, 
                                    width=28, state="readonly")
        self.width_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Spacing between stickers
        ttk.Label(right_panel, text="Spacing (chars):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.spacing_var = tk.StringVar(value="2")
        spacing_spinbox = ttk.Spinbox(right_panel, from_=1, to=8, textvariable=self.spacing_var, 
                                     width=28)
        spacing_spinbox.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Separator
        ttk.Separator(right_panel, orient='horizontal').grid(row=row, column=0, columnspan=2, 
                                                           sticky=(tk.W, tk.E), pady=20)
        row += 1
        
        # Buttons
        buttons_frame = ttk.Frame(right_panel)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="👁️ Preview", 
                  command=self.preview_sticker).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🖨️ Print Stickers", 
                  command=self.print_stickers).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="💾 Save as PDF", 
                  command=self.save_as_pdf).pack(side=tk.LEFT, padx=5)
    
    def create_preview_panel(self, parent):
        """Create preview panel"""
        preview_panel = ttk.LabelFrame(parent, text="📋 Sticker Preview", padding="10")
        preview_panel.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        preview_panel.columnconfigure(0, weight=1)
        
        # Preview text area
        self.preview_text = tk.Text(preview_panel, height=8, width=80, 
                                   font=("Courier New", 9), wrap=tk.WORD,
                                   bg='white', fg='black')
        
        preview_scrollbar = ttk.Scrollbar(preview_panel, orient="vertical", 
                                        command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initial preview
        self.update_preview()
    
    def load_items(self):
        """Load all items"""
        try:
            self.items_data = ItemsManager.get_all_items()
            self.populate_items_tree(self.items_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load items: {e}")
    
    def populate_items_tree(self, items):
        """Populate the items treeview"""
        # Clear existing items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Add items
        for item in items:
            # Only show items with barcodes
            if item.get('barcode'):
                values = (
                    item['item_name'],
                    item['barcode'],
                    f"{item['price']:.2f}",
                    item['stock_quantity']
                )
                self.items_tree.insert('', 'end', values=values)
    
    def on_search(self, event):
        """Handle search input"""
        search_term = self.search_var.get().strip().lower()
        
        if not search_term:
            self.populate_items_tree(self.items_data)
            return
        
        # Filter items
        filtered_items = []
        for item in self.items_data:
            if (search_term in item['item_name'].lower() or 
                (item.get('barcode') and search_term in item['barcode'].lower())):
                filtered_items.append(item)
        
        self.populate_items_tree(filtered_items)
    
    def on_item_select(self, event):
        """Handle item selection"""
        selection = self.items_tree.selection()
        if not selection:
            return
        
        # Get selected item
        item_values = self.items_tree.item(selection[0], 'values')
        item_name = item_values[0]
        
        # Find the full item data
        self.selected_item = None
        for item in self.items_data:
            if item['item_name'] == item_name:
                self.selected_item = item
                break
        
        if self.selected_item:
            # Update display
            self.selected_item_label.config(
                text=f"{self.selected_item['item_name']} (₹{self.selected_item['price']:.2f})",
                foreground="black"
            )
            
            # Populate fields
            self.item_name_var.set(self.selected_item['item_name'])
            self.barcode_var.set(self.selected_item['barcode'] or '')
            self.mrp_var.set(f"{self.selected_item['price']:.2f}")
            
            # Update preview
            self.on_size_change()  # Update layout settings
            self.update_preview()
    
    def on_size_change(self, event=None):
        """Handle sticker size change and update layout settings"""
        size_text = self.size_var.get()
        
        if "Small (20 chars)" in size_text:
            width = 20
            per_row = 3
        elif "Standard (32 chars)" in size_text:
            width = 32
            per_row = 2
        elif "Large (48 chars)" in size_text:
            width = 48
            per_row = 1
        elif "Full Width (64 chars)" in size_text:
            width = 64
            per_row = 1
        else:
            width = 32
            per_row = 2
        
        self.width_var.set(str(width))
        self.per_row_var.set(str(per_row))
        
        # Update preview if window exists
        if hasattr(self, 'preview_text'):
            self.update_preview()
    
    def update_preview(self):
        """Update the sticker preview"""
        self.preview_text.delete(1.0, tk.END)
        
        if not self.selected_item:
            self.preview_text.insert(tk.END, "Select an item to preview barcode sticker")
            return
        
        store_name = self.store_name_var.get().strip()
        item_name = self.item_name_var.get().strip()
        barcode = self.barcode_var.get().strip()
        mrp = self.mrp_var.get().strip()
        quantity = int(self.quantity_var.get())
        size = self.size_var.get()
        
        if not all([store_name, item_name, barcode, mrp]):
            self.preview_text.insert(tk.END, "Please fill in all required fields")
            return
        
        # Generate preview
        preview_content = self.generate_sticker_content(store_name, item_name, barcode, mrp, quantity, size)
        self.preview_text.insert(tk.END, preview_content)
    
    def generate_sticker_content(self, store_name, item_name, barcode, mrp, quantity, size):
        """Generate barcode sticker content with side-by-side layout"""
        content_lines = []
        
        # Get layout settings
        try:
            sticker_width = int(self.width_var.get())
            per_row = int(self.per_row_var.get())
            spacing = int(self.spacing_var.get())
        except ValueError:
            sticker_width = 32
            per_row = 2
            spacing = 2
        
        # Calculate total width for thermal printer
        total_width = 64  # 4-inch thermal printer
        
        # Header
        content_lines.append("=" * total_width)
        content_lines.append(f"BARCODE STICKERS - {quantity} sticker(s)".center(total_width))
        content_lines.append(f"Size: {size} | {per_row} per row | Spacing: {spacing}".center(total_width))
        content_lines.append("=" * total_width)
        content_lines.append("")
        
        # Generate stickers in rows
        stickers_printed = 0
        while stickers_printed < quantity:
            # Calculate how many stickers in this row
            stickers_in_row = min(per_row, quantity - stickers_printed)
            
            # Generate individual sticker content
            sticker_blocks = []
            for i in range(stickers_in_row):
                sticker_block = self.generate_single_sticker(store_name, item_name, barcode, mrp, 
                                                           sticker_width, stickers_printed + i + 1)
                sticker_blocks.append(sticker_block)
            
            # Combine stickers side by side
            if per_row == 1:
                # Single sticker - centered
                for line in sticker_blocks[0]:
                    content_lines.append(line.center(total_width))
            else:
                # Multiple stickers - side by side
                max_lines = max(len(block) for block in sticker_blocks)
                
                for line_idx in range(max_lines):
                    combined_line = ""
                    for sticker_idx, sticker_block in enumerate(sticker_blocks):
                        if line_idx < len(sticker_block):
                            sticker_line = sticker_block[line_idx]
                        else:
                            sticker_line = " " * sticker_width
                        
                        combined_line += sticker_line
                        
                        # Add spacing between stickers (except after last one)
                        if sticker_idx < len(sticker_blocks) - 1:
                            combined_line += " " * spacing
                    
                    content_lines.append(combined_line)
            
            stickers_printed += stickers_in_row
            
            # Add separator between rows (except after last row)
            if stickers_printed < quantity:
                content_lines.append("-" * total_width)
                content_lines.append("")
        
        content_lines.append("")
        content_lines.append("=" * total_width)
        content_lines.append(f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}".center(total_width))
        content_lines.append(f"Optimized for 4-inch thermal printer".center(total_width))
        
        return "\n".join(content_lines)
    
    def generate_single_sticker(self, store_name, item_name, barcode, mrp, width, sticker_num):
        """Generate content for a single sticker"""
        lines = []
        
        # Sticker number and border
        lines.append("-" * width)
        lines.append(f"#{sticker_num}".center(width))
        lines.append("")
        
        # Store name (bold-style, truncated if needed)
        store_display = store_name[:width-4] if len(store_name) > width-4 else store_name
        lines.append(("*" + store_display + "*").center(width))
        lines.append("")
        
        # Item name (wrapped if needed)
        item_display_width = width - 2
        if len(item_name) > item_display_width:
            words = item_name.split()
            line1, line2 = "", ""
            for word in words:
                if len(line1 + word + " ") <= item_display_width:
                    line1 += word + " "
                else:
                    line2 += word + " "
            lines.append(line1.strip().center(width))
            if line2.strip():
                lines.append(line2.strip().center(width))
        else:
            lines.append(item_name.center(width))
        
        lines.append("")
        
        # Barcode representation
        lines.append("BARCODE".center(width))
        # Create barcode pattern scaled to sticker width
        pattern_chars = ["|", "|", "|", " ", "|", " ", "|", "|", "|", " ", "|", "|", " ", "|", "|", "|", " ", "|", "|"]
        pattern_width = min(len(pattern_chars), width - 4)
        pattern = "".join(pattern_chars[:pattern_width])
        lines.append(pattern.center(width))
        lines.append(barcode.center(width))
        lines.append("")
        
        # MRP
        mrp_line = f"MRP: ₹{mrp}"
        lines.append(mrp_line.center(width))
        lines.append("")
        lines.append("-" * width)
        
        return lines
    
    def preview_sticker(self):
        """Preview the sticker"""
        if not self.validate_inputs():
            return
        
        self.update_preview()
        messagebox.showinfo("Preview", "Sticker preview updated below!")
    
    def print_stickers(self):
        """Print the barcode stickers"""
        if not self.validate_inputs():
            return
        
        try:
            store_name = self.store_name_var.get().strip()
            item_name = self.item_name_var.get().strip()
            barcode = self.barcode_var.get().strip()
            mrp = self.mrp_var.get().strip()
            quantity = int(self.quantity_var.get())
            size = self.size_var.get()
            
            # Generate sticker content
            content = self.generate_sticker_content(store_name, item_name, barcode, mrp, quantity, size)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Try to print to default printer
                system = platform.system()
                
                if system == "Windows":
                    os.system(f'type "{temp_file_path}" > PRN')
                elif system == "Linux":
                    os.system(f'lp "{temp_file_path}"')
                elif system == "Darwin":  # macOS
                    os.system(f'lp "{temp_file_path}"')
                else:
                    # Fallback: Show preview
                    self.show_print_preview(content)
                    return
                
                messagebox.showinfo("Print Success", 
                                  f"Successfully sent {quantity} barcode sticker(s) to printer!")
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print stickers: {e}")
            # Show preview as fallback
            self.show_print_preview(content if 'content' in locals() else "Print failed")
    
    def save_as_pdf(self):
        """Save stickers as PDF (placeholder for now)"""
        if not self.validate_inputs():
            return
        
        try:
            # Generate content
            store_name = self.store_name_var.get().strip()
            item_name = self.item_name_var.get().strip()
            barcode = self.barcode_var.get().strip()
            mrp = self.mrp_var.get().strip()
            quantity = int(self.quantity_var.get())
            size = self.size_var.get()
            
            content = self.generate_sticker_content(store_name, item_name, barcode, mrp, quantity, size)
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                title="Save Barcode Stickers",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialvalue=f"barcode_stickers_{barcode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Save Success", f"Barcode stickers saved to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save stickers: {e}")
    
    def show_print_preview(self, content):
        """Show print preview window"""
        preview_window = tk.Toplevel(self.window)
        preview_window.title("Barcode Stickers - Print Preview")
        preview_window.geometry("700x600")
        
        try:
            preview_window.transient(self.window)
            preview_window.grab_set()
        except tk.TclError:
            pass
        
        # Create text widget
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
        
        ttk.Button(button_frame, text="💾 Save as Text", 
                  command=lambda: self.save_preview_content(content)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🖨️ Try Print Again", 
                  command=lambda: [preview_window.destroy(), self.print_stickers()]).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Close", 
                  command=preview_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def save_preview_content(self, content):
        """Save preview content to file"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Save Barcode Stickers",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialvalue=f"barcode_stickers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Save Success", f"Barcode stickers saved to:\n{file_path}")
        
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save: {e}")
    
    def validate_inputs(self):
        """Validate input fields"""
        if not self.selected_item:
            messagebox.showwarning("No Item Selected", "Please select an item first")
            return False
        
        store_name = self.store_name_var.get().strip()
        if not store_name:
            messagebox.showwarning("Missing Store Name", "Please enter store name")
            return False
        
        item_name = self.item_name_var.get().strip()
        if not item_name:
            messagebox.showwarning("Missing Item Name", "Please enter item name")
            return False
        
        barcode = self.barcode_var.get().strip()
        if not barcode:
            messagebox.showwarning("Missing Barcode", "Selected item must have a barcode")
            return False
        
        try:
            mrp = float(self.mrp_var.get())
            if mrp <= 0:
                raise ValueError("MRP must be positive")
        except ValueError:
            messagebox.showwarning("Invalid MRP", "Please enter a valid MRP amount")
            return False
        
        try:
            quantity = int(self.quantity_var.get())
            if quantity < 1 or quantity > 100:
                raise ValueError("Quantity must be between 1 and 100")
        except ValueError:
            messagebox.showwarning("Invalid Quantity", "Please enter a valid quantity (1-100)")
            return False
        
        try:
            width = int(self.width_var.get())
            if width < 20 or width > 64:
                raise ValueError("Width must be between 20 and 64")
        except ValueError:
            messagebox.showwarning("Invalid Width", "Please enter a valid sticker width (20-64 characters)")
            return False
        
        try:
            spacing = int(self.spacing_var.get())
            if spacing < 1 or spacing > 8:
                raise ValueError("Spacing must be between 1 and 8")
        except ValueError:
            messagebox.showwarning("Invalid Spacing", "Please enter a valid spacing (1-8 characters)")
            return False
        
        return True


# Standalone function to launch barcode printer
def show_barcode_printer(parent=None):
    """Show barcode printer window"""
    printer = BarcodePrinterWindow()
    printer.show(parent)
    return printer


if __name__ == "__main__":
    # For testing standalone
    root = tk.Tk()
    root.withdraw()
    show_barcode_printer()
    root.mainloop()