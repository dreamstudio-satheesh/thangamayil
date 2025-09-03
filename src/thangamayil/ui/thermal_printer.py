"""
Thermal Printer Module
Handles thermal printer bill generation and printing based on billprint.md format
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import tempfile
import os
import platform


class ThermalPrinter:
    """Handles thermal printer operations"""
    
    def __init__(self):
        self.line_width = 64  # 4 inch (101.6mm) thermal paper width in characters
    
    def print_bill(self, bill_data, parent_window=None):
        """Print bill to thermal printer"""
        try:
            # Generate thermal printer content
            bill_content = self.generate_thermal_bill(bill_data)
            if bill_content:
                # Send to thermal printer
                self.send_to_thermal_printer(bill_content, parent_window)
                messagebox.showinfo("Print", f"Bill {bill_data['invoice_number']} sent to thermal printer successfully!")
            else:
                messagebox.showerror("Error", "Failed to generate bill content")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print bill: {e}")
    
    def generate_thermal_bill(self, bill_data):
        """Generate thermal printer bill format (4 inch width)"""
        try:
            from ..database.connection import db
            
            # Get bill items from database
            items_query = '''
            SELECT * FROM bill_items 
            WHERE bill_id = ? 
            ORDER BY bill_item_id
            '''
            bill_items = db.execute_query(items_query, (bill_data['bill_id'],))
            
            # Check if bill items exist
            if not bill_items:
                raise Exception(f"Cannot print bill {bill_data.get('invoice_number', bill_data['bill_id'])}: No items found. This bill appears to be empty.")
            
            # Get customer info
            customer_query = '''
            SELECT c.customer_name, c.phone_number, c.address 
            FROM customers c 
            JOIN bills b ON c.customer_id = b.customer_id 
            WHERE b.bill_id = ?
            '''
            customer_result = db.execute_query(customer_query, (bill_data['bill_id'],))
            customer_name = customer_result[0]['customer_name'] if customer_result else "Walk-in Customer"
            customer_phone = customer_result[0]['phone_number'] if customer_result else ""
            
            # Get shop settings
            shop_name = db.get_setting('shop_name') or 'தங்கமயில் சில்க்ஸ்'
            shop_address = db.get_setting('shop_address') or 'No.1 Main Road, Tamil Nadu, IN'
            shop_phone = db.get_setting('shop_phone') or '+91-9876543210'
            gstin = db.get_setting('gstin') or '33AAACT9454F1ZB'
            
            # Build thermal printer content
            bill_lines = []
            
            # Header
            bill_lines.append("=" * self.line_width)
            bill_lines.append(shop_name.center(self.line_width))
            bill_lines.append(shop_address.center(self.line_width))
            bill_lines.append(f"Ph: {shop_phone}".center(self.line_width))
            bill_lines.append(f"GSTIN: {gstin}".center(self.line_width))
            bill_lines.append("=" * self.line_width)
            bill_lines.append("*** TAX INVOICE ***".center(self.line_width))
            bill_lines.append("(GST Compliant Bill)".center(self.line_width))
            bill_lines.append("=" * self.line_width)
            
            # Bill details
            bill_date = datetime.strptime(bill_data['bill_date'], '%Y-%m-%d %H:%M:%S')
            bill_lines.append(f"Invoice: {bill_data['invoice_number']}")
            bill_lines.append(f"Date: {bill_date.strftime('%d-%m-%Y %H:%M')}")
            
            if customer_name != "Walk-in Customer":
                bill_lines.append(f"Customer: {customer_name}")
                if customer_phone:
                    bill_lines.append(f"Phone: {customer_phone}")
            
            bill_lines.append("-" * self.line_width)
            
            # Items header - right-aligned numeric columns
            bill_lines.append("Item                    Qty   Rate  Total")
            bill_lines.append("-" * self.line_width)
            
            # Items
            subtotal = 0
            total_discount = 0
            total_gst = 0
            
            for item in bill_items:
                try:
                    # Calculate amounts - handle Row objects safely
                    unit_price = float(item['unit_price'] if item['unit_price'] is not None else 0)
                    quantity = int(item['quantity'] if item['quantity'] is not None else 1)
                    discount_percentage = float(item['discount_percentage'] if item['discount_percentage'] is not None else 0)
                    gst_percentage = float(item['gst_percentage'] if item['gst_percentage'] is not None else 0)
                except KeyError as e:
                    raise Exception(f"Missing column in bill_items: {e}. Available columns: {list(item.keys()) if hasattr(item, 'keys') else 'Unknown'}")
                
                line_subtotal = unit_price * quantity
                discount_amount = (line_subtotal * discount_percentage) / 100
                taxable_amount = line_subtotal - discount_amount
                gst_amount = (taxable_amount * gst_percentage) / 100
                line_total = taxable_amount + gst_amount
                
                subtotal += line_subtotal
                total_discount += discount_amount
                total_gst += gst_amount
                
                # Format item name (truncate if too long)
                try:
                    item_name = str(item['item_name'] if item['item_name'] is not None else 'Unknown Item')
                except KeyError:
                    raise Exception(f"Missing 'item_name' column in bill_items. Available columns: {list(item.keys()) if hasattr(item, 'keys') else 'Unknown'}")
                
                if len(item_name) > 20:
                    item_name = item_name[:17] + "..."
                
                # Format line with right-aligned numeric columns
                qty_str = str(quantity)
                rate_str = f"{unit_price:.0f}"
                total_str = f"{line_total:.0f}"
                
                # Right-align numeric columns: Item(24) + Qty(5) + Rate(6) + Total(8)
                name_width = 24
                qty_width = 5
                rate_width = 6
                total_width = 8
                
                # Truncate item name if needed
                if len(item_name) > name_width:
                    display_name = item_name[:name_width-3] + "..."
                else:
                    display_name = item_name
                
                # Build line with right-aligned columns
                line = f"{display_name:<{name_width}}{qty_str:>{qty_width}}{rate_str:>{rate_width}}{total_str:>{total_width}}"
                bill_lines.append(line)
                
                # Add discount info if applicable
                if discount_percentage > 0:
                    bill_lines.append(f"  Disc: {discount_percentage:.1f}% = -{discount_amount:.0f}")
                
                # Add GST info
                if gst_percentage > 0:
                    bill_lines.append(f"  GST: {gst_percentage:.1f}% = +{gst_amount:.0f}")
            
            bill_lines.append("=" * self.line_width)
            bill_lines.append("BILL SUMMARY".center(self.line_width))
            bill_lines.append("=" * self.line_width)
            
            # Summary calculations
            bill_discount_amount = bill_data['discount_amount'] if bill_data['discount_amount'] is not None else 0
            cgst_amount = bill_data['cgst_amount'] if bill_data['cgst_amount'] is not None else 0
            sgst_amount = bill_data['sgst_amount'] if bill_data['sgst_amount'] is not None else 0
            igst_amount = bill_data['igst_amount'] if bill_data['igst_amount'] is not None else 0
            round_off = bill_data['round_off'] if bill_data['round_off'] is not None else 0
            
            # Subtotal and discounts section
            bill_lines.append(f"Subtotal:{str(int(subtotal)).rjust(self.line_width - 9)}")
            
            if total_discount > 0:
                bill_lines.append(f"Item Disc:{('-' + str(int(total_discount))).rjust(self.line_width - 10)}")
            
            if bill_discount_amount > 0:
                bill_lines.append(f"Bill Disc:{('-' + str(int(bill_discount_amount))).rjust(self.line_width - 10)}")
            
            # GST section separator
            if cgst_amount > 0 or igst_amount > 0:
                bill_lines.append("-" * self.line_width)
                bill_lines.append("GST BREAKDOWN".center(self.line_width))
                bill_lines.append("-" * self.line_width)
            
            # GST calculations
            if cgst_amount > 0:
                # Calculate average GST rate for display (assuming CGST = SGST)
                taxable_amount = subtotal - total_discount - bill_discount_amount
                total_gst_rate = (cgst_amount + sgst_amount) / (taxable_amount / 100) if taxable_amount > 0 else 0
                cgst_rate = total_gst_rate / 2
                bill_lines.append(f"CGST@{cgst_rate:.1f}%:{str(int(cgst_amount)).rjust(self.line_width - 12)}")
                bill_lines.append(f"SGST@{cgst_rate:.1f}%:{str(int(sgst_amount)).rjust(self.line_width - 12)}")
            
            if igst_amount > 0:
                # Calculate IGST rate for display
                taxable_amount = subtotal - total_discount - bill_discount_amount
                igst_rate = (igst_amount / (taxable_amount / 100)) if taxable_amount > 0 else 0
                bill_lines.append(f"IGST@{igst_rate:.1f}%:{str(int(igst_amount)).rjust(self.line_width - 12)}")
            
            # Round off section
            if round_off != 0:
                bill_lines.append("-" * self.line_width)
                sign = "+" if round_off > 0 else ""
                bill_lines.append(f"Round Off:{(sign + str(round_off)).rjust(self.line_width - 10)}")
            
            # Final total section
            bill_lines.append("=" * self.line_width)
            bill_lines.append(f"TOTAL:{str(int(bill_data['grand_total'])).rjust(self.line_width - 6)}")
            bill_lines.append("=" * self.line_width)
            
            # Payment info
            bill_lines.append(f"Payment: {bill_data['payment_mode']}")
            bill_lines.append("")
            
            # Footer - GST Compliance
            bill_lines.append("")
            bill_lines.append("*** TERMS & CONDITIONS ***".center(self.line_width))
            bill_lines.append("This is a Computer Generated Invoice".center(self.line_width))
            bill_lines.append("Subject to Local Jurisdiction".center(self.line_width))
            bill_lines.append("No Exchange | No Refund".center(self.line_width))
            bill_lines.append("")
            bill_lines.append("Thank you for shopping with us!".center(self.line_width))
            bill_lines.append("-" * self.line_width)
            bill_lines.append("")
            bill_lines.append("")  # Extra lines for paper cutting
            
            return "\n".join(bill_lines)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate bill: {str(e)}")
            return None
    
    def send_to_thermal_printer(self, content, parent_window=None):
        """Send content to thermal printer"""
        try:
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
                    self.show_print_preview(content, parent_window)
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            # Fallback: Show enhanced print preview
            self.show_enhanced_preview(content, parent_window, is_preview_mode=False)
            messagebox.showinfo("Print Method", 
                "Automatic printing failed. Please copy the text from the preview window and print manually.")
    
    def show_print_preview(self, content, parent_window=None):
        """Show print preview window"""
        preview_window = tk.Toplevel()
        preview_window.title("Print Preview - Thermal Receipt")
        preview_window.geometry("600x800")
        
        if parent_window:
            try:
                preview_window.transient(parent_window)
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
                  command=lambda: self.send_to_thermal_printer(content, parent_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Close", 
                  command=preview_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def copy_to_clipboard(self, content):
        """Copy content to clipboard"""
        try:
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
    
    def generate_thermal_bill_preview(self, temp_bill_data, bill_items):
        """Generate thermal bill preview from temporary data without database access"""
        try:
            from ..database.connection import db
            
            # Get shop settings
            shop_name = db.get_setting('shop_name') or 'தங்கமயில் சில்க்ஸ்'
            shop_address = db.get_setting('shop_address') or 'No.1 Main Road, Tamil Nadu, IN'
            shop_phone = db.get_setting('shop_phone') or '+91-9876543210'
            gstin = db.get_setting('gstin') or '33AAACT9454F1ZB'
            
            # Build thermal printer content
            bill_lines = []
            
            # Header
            bill_lines.append("=" * self.line_width)
            bill_lines.append(shop_name.center(self.line_width))
            bill_lines.append(shop_address.center(self.line_width))
            bill_lines.append(f"Ph: {shop_phone}".center(self.line_width))
            bill_lines.append(f"GSTIN: {gstin}".center(self.line_width))
            bill_lines.append("=" * self.line_width)
            bill_lines.append("*** TAX INVOICE (PREVIEW) ***".center(self.line_width))
            bill_lines.append("(GST Compliant Bill)".center(self.line_width))
            bill_lines.append("=" * self.line_width)
            
            # Bill details
            bill_date = datetime.strptime(temp_bill_data['bill_date'], '%Y-%m-%d %H:%M:%S')
            bill_lines.append(f"Invoice: {temp_bill_data['invoice_number']}")
            bill_lines.append(f"Date: {bill_date.strftime('%d-%m-%Y %H:%M')}")
            bill_lines.append("Customer: Preview Mode")
            bill_lines.append("-" * self.line_width)
            
            # Items header - right-aligned numeric columns
            bill_lines.append("Item                    Qty   Rate  Total")
            bill_lines.append("-" * self.line_width)
            
            # Items
            subtotal = 0
            total_discount = 0
            total_gst = 0
            
            for item in bill_items:
                # Calculate amounts
                unit_price = float(item['unit_price'])
                quantity = int(item['quantity'])
                discount_percentage = float(item['discount_percentage'])
                gst_percentage = float(item['gst_percentage'])
                
                line_subtotal = unit_price * quantity
                discount_amount = (line_subtotal * discount_percentage) / 100
                taxable_amount = line_subtotal - discount_amount
                gst_amount = (taxable_amount * gst_percentage) / 100
                line_total = taxable_amount + gst_amount
                
                subtotal += line_subtotal
                total_discount += discount_amount
                total_gst += gst_amount
                
                # Format item name (truncate if too long)
                item_name = str(item['item_name'])
                if len(item_name) > 20:
                    item_name = item_name[:17] + "..."
                
                # Format line with right-aligned numeric columns
                qty_str = str(quantity)
                rate_str = f"{unit_price:.0f}"
                total_str = f"{line_total:.0f}"
                
                # Right-align numeric columns: Item(24) + Qty(5) + Rate(6) + Total(8)
                name_width = 24
                qty_width = 5
                rate_width = 6
                total_width = 8
                
                # Truncate item name if needed
                if len(item_name) > name_width:
                    display_name = item_name[:name_width-3] + "..."
                else:
                    display_name = item_name
                
                # Build line with right-aligned columns
                line = f"{display_name:<{name_width}}{qty_str:>{qty_width}}{rate_str:>{rate_width}}{total_str:>{total_width}}"
                bill_lines.append(line)
                
                # Add discount info if applicable
                if discount_percentage > 0:
                    bill_lines.append(f"  Disc: {discount_percentage:.1f}% = -{discount_amount:.0f}")
                
                # Add GST info
                if gst_percentage > 0:
                    bill_lines.append(f"  GST: {gst_percentage:.1f}% = +{gst_amount:.0f}")
            
            bill_lines.append("=" * self.line_width)
            bill_lines.append("BILL SUMMARY".center(self.line_width))
            bill_lines.append("=" * self.line_width)
            
            # Summary section
            bill_lines.append(f"Subtotal:{str(int(subtotal)).rjust(self.line_width - 9)}")
            
            if total_discount > 0:
                bill_lines.append(f"Item Disc:{('-' + str(int(total_discount))).rjust(self.line_width - 10)}")
            
            # Get GST amounts from preview data
            bill_discount_amount = temp_bill_data.get('discount_amount', 0)
            cgst_amount = temp_bill_data.get('cgst_amount', 0) 
            sgst_amount = temp_bill_data.get('sgst_amount', 0)
            round_off = temp_bill_data.get('round_off', 0)
            
            if bill_discount_amount > 0:
                bill_lines.append(f"Bill Disc:{('-' + str(int(bill_discount_amount))).rjust(self.line_width - 10)}")
            
            # GST section separator
            if cgst_amount > 0:
                bill_lines.append("-" * self.line_width)
                bill_lines.append("GST BREAKDOWN".center(self.line_width))
                bill_lines.append("-" * self.line_width)
                
                # Calculate average GST rate for display (assuming CGST = SGST)
                taxable_amount = subtotal - total_discount - bill_discount_amount
                total_gst_rate = (cgst_amount + sgst_amount) / (taxable_amount / 100) if taxable_amount > 0 else 0
                cgst_rate = total_gst_rate / 2
                bill_lines.append(f"CGST@{cgst_rate:.1f}%:{str(int(cgst_amount)).rjust(self.line_width - 12)}")
                bill_lines.append(f"SGST@{cgst_rate:.1f}%:{str(int(sgst_amount)).rjust(self.line_width - 12)}")
            
            # Round off section
            if round_off != 0:
                bill_lines.append("-" * self.line_width)
                sign = "+" if round_off > 0 else ""
                bill_lines.append(f"Round Off:{(sign + str(round_off)).rjust(self.line_width - 10)}")
            
            # Final total section
            bill_lines.append("=" * self.line_width)
            bill_lines.append(f"TOTAL:{str(int(temp_bill_data['grand_total'])).rjust(self.line_width - 6)}")
            bill_lines.append("=" * self.line_width)
            
            # Payment info
            bill_lines.append(f"Payment: {temp_bill_data['payment_mode']}")
            bill_lines.append("")
            
            # Footer
            bill_lines.append("***** PREVIEW MODE *****".center(self.line_width))
            bill_lines.append("This is a preview only".center(self.line_width))
            bill_lines.append("Thank you for shopping with us!".center(self.line_width))
            bill_lines.append("")
            bill_lines.append("-" * self.line_width)
            
            return "\n".join(bill_lines)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate preview: {str(e)}")
            return None
    
    def show_enhanced_preview(self, content, parent_window=None, is_preview_mode=False):
        """Show enhanced preview window with thermal printer styling"""
        preview_window = tk.Toplevel()
        title = "Print Preview - Thermal Receipt" + (" (PREVIEW MODE)" if is_preview_mode else "")
        preview_window.title(title)
        preview_window.geometry("700x900")
        
        if parent_window:
            try:
                preview_window.transient(parent_window)
                preview_window.grab_set()
            except tk.TclError:
                pass
        
        # Configure window background
        preview_window.configure(bg='#1e1e1e')  # Dark background
        
        # Create main frame
        main_frame = tk.Frame(preview_window, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title label
        title_label = tk.Label(main_frame, 
                              text="🧾 Thermal Receipt Preview" + (" - PREVIEW MODE" if is_preview_mode else ""),
                              font=("Arial", 14, "bold"),
                              fg='white', bg='#1e1e1e')
        title_label.pack(pady=(0, 10))
        
        # Receipt container with thermal styling
        receipt_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        receipt_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Receipt content area
        content_frame = tk.Frame(receipt_frame, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Text widget with thermal printer styling
        text_widget = tk.Text(content_frame, 
                             font=("Courier New", 10), 
                             wrap=tk.NONE,
                             fg='black',
                             bg='white',
                             relief='flat',
                             bd=0,
                             width=50)
        
        # Add scrollbars
        scrollbar_v = tk.Scrollbar(content_frame, orient="vertical", command=text_widget.yview)
        scrollbar_h = tk.Scrollbar(content_frame, orient="horizontal", command=text_widget.xview)
        
        text_widget.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Pack widgets
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Insert content
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
        
        # Button frame with dark theme
        button_frame = tk.Frame(main_frame, bg='#1e1e1e')
        button_frame.pack(fill=tk.X)
        
        # Export buttons
        tk.Button(button_frame, text="💾 Save as Text", 
                 command=lambda: self.save_as_text(content),
                 bg='#0078d4', fg='white', font=("Arial", 10),
                 relief='flat', padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="📄 Copy to Clipboard", 
                 command=lambda: self.copy_to_clipboard(content),
                 bg='#107c10', fg='white', font=("Arial", 10),
                 relief='flat', padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        if not is_preview_mode:
            tk.Button(button_frame, text="🖨️ Try Print Again", 
                     command=lambda: self.send_to_thermal_printer(content, parent_window),
                     bg='#d13438', fg='white', font=("Arial", 10),
                     relief='flat', padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="❌ Close", 
                 command=preview_window.destroy,
                 bg='#5a5a5a', fg='white', font=("Arial", 10),
                 relief='flat', padx=15, pady=5).pack(side=tk.RIGHT, padx=5)
    
    def save_as_text(self, content):
        """Save receipt content as text file"""
        try:
            from tkinter import filedialog
            import datetime
            
            # Generate default filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"thermal_receipt_{timestamp}.txt"
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                title="Save Receipt as Text File",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialvalue=default_filename
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Receipt saved successfully at:\n{file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save receipt: {e}")