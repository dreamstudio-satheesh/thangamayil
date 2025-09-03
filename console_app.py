#!/usr/bin/env python3
"""
Console-based interface for தங்கமயில் சில்க்ஸ் Billing Software
Provides a text-based menu system for all operations
"""

import sys
import os
from datetime import datetime
from typing import Optional

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from thangamayil.database.connection import db
from thangamayil.models.auth import auth, StaffManager
from thangamayil.models.items import ItemsManager
from thangamayil.models.billing import BillingManager, GSTCalculator
from thangamayil import APP_NAME, APP_VERSION


class ConsoleApp:
    """Console-based billing application"""
    
    def __init__(self):
        self.current_bill_id = None
        self.running = True
    
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str = ""):
        """Print application header"""
        print("=" * 60)
        print(f"  {APP_NAME}")
        print(f"  Version {APP_VERSION}")
        if title:
            print(f"  {title}")
        print("=" * 60)
    
    def print_menu(self, title: str, options: list):
        """Print menu options"""
        print(f"\n{title}")
        print("-" * len(title))
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        print("0. Back/Exit")
        print()
    
    def get_input(self, prompt: str, input_type: type = str, required: bool = True):
        """Get validated input from user"""
        while True:
            try:
                value = input(f"{prompt}: ").strip()
                
                if not value and required:
                    print("This field is required. Please try again.")
                    continue
                
                if not value and not required:
                    return None
                
                if input_type == int:
                    return int(value)
                elif input_type == float:
                    return float(value)
                else:
                    return value
                    
            except ValueError:
                print(f"Please enter a valid {input_type.__name__}")
            except KeyboardInterrupt:
                return None
    
    def wait_for_enter(self):
        """Wait for user to press Enter"""
        input("\nPress Enter to continue...")
    
    def login(self) -> bool:
        """Handle user login"""
        self.clear_screen()
        self.print_header("Staff Login")
        
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            username = self.get_input("Staff Name")
            if not username:
                return False
            
            password = self.get_input("Password")
            if not password:
                return False
            
            if auth.login(username, password):
                print(f"\n✓ Welcome, {username}!")
                self.wait_for_enter()
                return True
            else:
                attempts += 1
                remaining = max_attempts - attempts
                print(f"\n✗ Invalid credentials. {remaining} attempts remaining.")
                if remaining > 0:
                    self.wait_for_enter()
        
        print("Too many failed attempts. Exiting...")
        return False
    
    def main_menu(self):
        """Display main menu"""
        while self.running:
            self.clear_screen()
            self.print_header("Main Menu")
            
            staff_name = auth.get_current_staff_name()
            print(f"Logged in as: {staff_name}")
            
            options = [
                "🛒 New Bill / POS",
                "📦 Items Management",
                "👥 Staff Management", 
                "📊 Reports",
                "💾 Database Backup",
                "🚪 Logout"
            ]
            
            self.print_menu("Select Operation:", options)
            
            choice = self.get_input("Enter choice", int, required=False)
            
            if choice == 1:
                self.pos_billing()
            elif choice == 2:
                self.items_management()
            elif choice == 3:
                self.staff_management()
            elif choice == 4:
                self.reports()
            elif choice == 5:
                self.database_backup()
            elif choice == 6:
                self.logout()
            elif choice == 0:
                self.running = False
            else:
                print("Invalid choice. Please try again.")
                self.wait_for_enter()
    
    def pos_billing(self):
        """POS billing interface"""
        while True:
            self.clear_screen()
            self.print_header("POS Billing")
            
            if self.current_bill_id:
                # Show current bill details
                bill_details = BillingManager.get_bill_details(self.current_bill_id)
                if bill_details:
                    bill = bill_details['bill']
                    items = bill_details['items']
                    
                    print(f"Current Bill: {bill['invoice_number']}")
                    print(f"Items: {len(items)}")
                    if items:
                        print("\nCurrent Items:")
                        for i, item in enumerate(items, 1):
                            print(f"{i}. {item['item_name']} x{item['quantity']} = ₹{item['line_total']:.2f}")
                        
                        totals = BillingManager.calculate_bill_totals(self.current_bill_id)
                        print(f"\nSubtotal: ₹{totals['subtotal']:.2f}")
                        print(f"GST: ₹{totals['total_gst']:.2f}")
                        print(f"Grand Total: ₹{totals['grand_total']:.2f}")
            
            options = [
                "🆕 Start New Bill",
                "➕ Add Item to Bill",
                "📄 View Current Bill",
                "💳 Finalize & Print Bill",
                "❌ Cancel Current Bill"
            ]
            
            self.print_menu("POS Operations:", options)
            
            choice = self.get_input("Enter choice", int, required=False)
            
            if choice == 1:
                self.start_new_bill()
            elif choice == 2:
                self.add_item_to_bill()
            elif choice == 3:
                self.view_current_bill()
            elif choice == 4:
                self.finalize_bill()
            elif choice == 5:
                self.cancel_current_bill()
            elif choice == 0:
                break
            else:
                print("Invalid choice. Please try again.")
                self.wait_for_enter()
    
    def start_new_bill(self):
        """Start a new bill"""
        if self.current_bill_id:
            confirm = input("Current bill will be lost. Continue? (y/N): ").lower()
            if confirm != 'y':
                return
        
        staff_id = auth.get_current_staff_id()
        self.current_bill_id = BillingManager.create_bill(staff_id)
        
        if self.current_bill_id:
            print(f"✓ New bill created (ID: {self.current_bill_id})")
        else:
            print("✗ Failed to create bill")
        
        self.wait_for_enter()
    
    def add_item_to_bill(self):
        """Add item to current bill"""
        if not self.current_bill_id:
            print("No active bill. Please start a new bill first.")
            self.wait_for_enter()
            return
        
        print("\nAdd Item to Bill")
        print("-" * 20)
        
        # Search for item
        search_term = self.get_input("Enter item name or barcode to search")
        if not search_term:
            return
        
        # Try barcode first, then search
        item = ItemsManager.get_item_by_barcode(search_term)
        if not item:
            items = ItemsManager.search_items(search_term)
            if not items:
                print("No items found.")
                self.wait_for_enter()
                return
            elif len(items) == 1:
                item = items[0]
            else:
                print("\nMultiple items found:")
                for i, itm in enumerate(items, 1):
                    print(f"{i}. {itm['item_name']} - ₹{itm['price']:.2f} (Stock: {itm['stock_quantity']})")
                
                choice = self.get_input("Select item", int, required=False)
                if choice and 1 <= choice <= len(items):
                    item = items[choice - 1]
                else:
                    return
        
        if not item:
            return
        
        # Display item details
        print(f"\nSelected: {item['item_name']}")
        print(f"Price: ₹{item['price']:.2f}")
        print(f"Available Stock: {item['stock_quantity']}")
        print(f"GST: {item['gst_percentage']}%")
        
        # Get quantity
        quantity = self.get_input("Quantity", int)
        if not quantity or quantity <= 0:
            return
        
        if quantity > item['stock_quantity']:
            print("Insufficient stock!")
            self.wait_for_enter()
            return
        
        # Get discount (optional)
        discount = self.get_input("Discount % (optional)", float, required=False) or 0
        
        # Prepare item data
        item_data = {
            'item_id': item['item_id'],
            'item_name': item['item_name'],
            'barcode': item['barcode'],
            'quantity': quantity,
            'unit_price': item['price'],
            'gst_percentage': item['gst_percentage'],
            'discount_percentage': discount
        }
        
        # Add to bill
        success = BillingManager.add_item_to_bill(self.current_bill_id, item_data)
        if success:
            # Recalculate totals
            BillingManager.calculate_bill_totals(self.current_bill_id)
            print("✓ Item added to bill successfully")
        else:
            print("✗ Failed to add item to bill")
        
        self.wait_for_enter()
    
    def view_current_bill(self):
        """View current bill details"""
        if not self.current_bill_id:
            print("No active bill.")
            self.wait_for_enter()
            return
        
        bill_details = BillingManager.get_bill_details(self.current_bill_id)
        if not bill_details:
            print("Failed to load bill details.")
            self.wait_for_enter()
            return
        
        self.clear_screen()
        self.print_header("Bill Details")
        
        bill = bill_details['bill']
        items = bill_details['items']
        
        # Bill header
        print(f"Invoice: {bill['invoice_number']}")
        print(f"Date: {bill['bill_date']}")
        print(f"Staff: {bill['staff_name']}")
        print(f"Customer: {bill['customer_name'] or 'Walk-in Customer'}")
        print("\n" + "=" * 60)
        
        # Items
        print(f"{'SN':<3} {'Item':<25} {'Qty':<4} {'Price':<8} {'Disc%':<6} {'GST%':<5} {'Total':<8}")
        print("-" * 60)
        
        for i, item in enumerate(items, 1):
            print(f"{i:<3} {item['item_name'][:24]:<25} {item['quantity']:<4} "
                  f"{item['unit_price']:<8.2f} {item['discount_percentage']:<6.1f} "
                  f"{item['gst_percentage']:<5.1f} {item['line_total']:<8.2f}")
        
        print("-" * 60)
        
        # Totals
        print(f"{'Subtotal:':<45} ₹{bill['subtotal']:.2f}")
        print(f"{'Discount:':<45} ₹{bill['discount_amount']:.2f}")
        print(f"{'CGST:':<45} ₹{bill['cgst_amount']:.2f}")
        print(f"{'SGST:':<45} ₹{bill['sgst_amount']:.2f}")
        print(f"{'IGST:':<45} ₹{bill['igst_amount']:.2f}")
        print(f"{'Round Off:':<45} ₹{bill['round_off']:.2f}")
        print("=" * 60)
        print(f"{'GRAND TOTAL:':<45} ₹{bill['grand_total']:.2f}")
        print("=" * 60)
        
        self.wait_for_enter()
    
    def finalize_bill(self):
        """Finalize and print bill"""
        if not self.current_bill_id:
            print("No active bill.")
            self.wait_for_enter()
            return
        
        # Show bill summary first
        self.view_current_bill()
        
        confirm = input("\nFinalize this bill? (y/N): ").lower()
        if confirm != 'y':
            return
        
        # Get payment mode
        print("\nPayment Modes:")
        print("1. CASH")
        print("2. CARD") 
        print("3. UPI")
        
        payment_choice = self.get_input("Select payment mode", int, required=False) or 1
        payment_modes = {1: "CASH", 2: "CARD", 3: "UPI"}
        payment_mode = payment_modes.get(payment_choice, "CASH")
        
        # Finalize bill
        success = BillingManager.finalize_bill(self.current_bill_id, payment_mode)
        if success:
            print(f"\n✓ Bill finalized successfully!")
            print(f"Payment Mode: {payment_mode}")
            print("Stock has been updated.")
            
            # Clear current bill
            self.current_bill_id = None
        else:
            print("✗ Failed to finalize bill")
        
        self.wait_for_enter()
    
    def cancel_current_bill(self):
        """Cancel current bill"""
        if not self.current_bill_id:
            print("No active bill to cancel.")
            self.wait_for_enter()
            return
        
        confirm = input("Cancel current bill? (y/N): ").lower()
        if confirm == 'y':
            self.current_bill_id = None
            print("✓ Bill cancelled.")
        
        self.wait_for_enter()
    
    def items_management(self):
        """Items management interface"""
        while True:
            self.clear_screen()
            self.print_header("Items Management")
            
            # Show some stats
            items = ItemsManager.get_all_items()
            low_stock = ItemsManager.get_low_stock_items()
            
            print(f"Total Items: {len(items)}")
            print(f"Low Stock Items: {len(low_stock)}")
            
            options = [
                "📋 View All Items",
                "🔍 Search Items",
                "➕ Add New Item",
                "📊 Stock Report",
                "⚠️  Low Stock Items"
            ]
            
            self.print_menu("Items Operations:", options)
            
            choice = self.get_input("Enter choice", int, required=False)
            
            if choice == 1:
                self.view_all_items()
            elif choice == 2:
                self.search_items()
            elif choice == 3:
                self.add_new_item()
            elif choice == 4:
                self.stock_report()
            elif choice == 5:
                self.low_stock_items()
            elif choice == 0:
                break
            else:
                print("Invalid choice. Please try again.")
                self.wait_for_enter()
    
    def view_all_items(self):
        """Display all items"""
        self.clear_screen()
        self.print_header("All Items")
        
        items = ItemsManager.get_all_items()
        if not items:
            print("No items found.")
            self.wait_for_enter()
            return
        
        print(f"{'ID':<4} {'Barcode':<12} {'Name':<25} {'Category':<15} {'Price':<8} {'Stock':<6} {'GST%':<5}")
        print("-" * 80)
        
        for item in items:
            print(f"{item['item_id']:<4} {item['barcode'] or 'N/A':<12} "
                  f"{item['item_name'][:24]:<25} {item['category_name'] or 'N/A':<15} "
                  f"{item['price']:<8.2f} {item['stock_quantity']:<6} {item['gst_percentage']:<5.1f}")
        
        self.wait_for_enter()
    
    def search_items(self):
        """Search and display items"""
        search_term = self.get_input("Enter search term (name or barcode)")
        if not search_term:
            return
        
        items = ItemsManager.search_items(search_term)
        
        self.clear_screen()
        self.print_header(f"Search Results for '{search_term}'")
        
        if not items:
            print("No items found.")
        else:
            print(f"{'ID':<4} {'Barcode':<12} {'Name':<25} {'Price':<8} {'Stock':<6}")
            print("-" * 60)
            
            for item in items:
                print(f"{item['item_id']:<4} {item['barcode'] or 'N/A':<12} "
                      f"{item['item_name'][:24]:<25} {item['price']:<8.2f} {item['stock_quantity']:<6}")
        
        self.wait_for_enter()
    
    def add_new_item(self):
        """Add new item"""
        self.clear_screen()
        self.print_header("Add New Item")
        
        # Get categories
        categories = ItemsManager.get_all_categories()
        
        print("Available Categories:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat['category_name']}")
        
        # Get item details
        item_name = self.get_input("Item Name")
        if not item_name:
            return
        
        barcode = self.get_input("Barcode (optional)", required=False)
        if barcode and ItemsManager.barcode_exists(barcode):
            print("Barcode already exists!")
            self.wait_for_enter()
            return
        
        price = self.get_input("Price", float)
        if price is None or price <= 0:
            return
        
        gst_percentage = self.get_input("GST Percentage", float, required=False) or 5.0
        stock_quantity = self.get_input("Initial Stock Quantity", int, required=False) or 0
        
        # Category selection
        cat_choice = self.get_input("Select Category", int, required=False)
        category_id = None
        if cat_choice and 1 <= cat_choice <= len(categories):
            category_id = categories[cat_choice - 1]['category_id']
        
        # Prepare item data
        item_data = {
            'item_name': item_name,
            'barcode': barcode,
            'category_id': category_id,
            'price': price,
            'gst_percentage': gst_percentage,
            'stock_quantity': stock_quantity
        }
        
        # Add item
        success = ItemsManager.add_item(item_data)
        if success:
            print("✓ Item added successfully!")
        else:
            print("✗ Failed to add item")
        
        self.wait_for_enter()
    
    def stock_report(self):
        """Display stock report"""
        self.clear_screen()
        self.print_header("Stock Report")
        
        items = ItemsManager.get_all_items()
        
        total_items = len(items)
        total_stock_value = sum(item['price'] * item['stock_quantity'] for item in items)
        
        print(f"Total Items: {total_items}")
        print(f"Total Stock Value: ₹{total_stock_value:.2f}")
        print()
        
        print(f"{'Name':<30} {'Stock':<6} {'Value':<10}")
        print("-" * 50)
        
        for item in items:
            stock_value = item['price'] * item['stock_quantity']
            print(f"{item['item_name'][:29]:<30} {item['stock_quantity']:<6} ₹{stock_value:<9.2f}")
        
        self.wait_for_enter()
    
    def low_stock_items(self):
        """Display low stock items"""
        self.clear_screen()
        self.print_header("Low Stock Items")
        
        items = ItemsManager.get_low_stock_items()
        
        if not items:
            print("No low stock items found.")
        else:
            print(f"{'Name':<30} {'Current Stock':<6} {'Status':<12}")
            print("-" * 50)
            
            for item in items:
                status = "OUT OF STOCK" if item['stock_quantity'] == 0 else "LOW STOCK"
                print(f"{item['item_name'][:29]:<30} {item['stock_quantity']:<12} {status:<12}")
        
        self.wait_for_enter()
    
    def staff_management(self):
        """Staff management interface"""
        while True:
            self.clear_screen()
            self.print_header("Staff Management")
            
            staff_list = StaffManager.get_all_staff()
            active_staff = [s for s in staff_list if s['is_active']]
            
            print(f"Total Staff: {len(staff_list)}")
            print(f"Active Staff: {len(active_staff)}")
            
            options = [
                "👥 View All Staff",
                "➕ Add New Staff",
                "🔐 Change Password"
            ]
            
            self.print_menu("Staff Operations:", options)
            
            choice = self.get_input("Enter choice", int, required=False)
            
            if choice == 1:
                self.view_all_staff()
            elif choice == 2:
                self.add_new_staff()
            elif choice == 3:
                self.change_password()
            elif choice == 0:
                break
            else:
                print("Invalid choice. Please try again.")
                self.wait_for_enter()
    
    def view_all_staff(self):
        """Display all staff"""
        self.clear_screen()
        self.print_header("All Staff")
        
        staff_list = StaffManager.get_all_staff()
        
        print(f"{'ID':<4} {'Name':<20} {'Status':<8} {'Created':<20}")
        print("-" * 55)
        
        for staff in staff_list:
            status = "Active" if staff['is_active'] else "Inactive"
            created = staff['created_at'][:19] if staff['created_at'] else 'N/A'
            print(f"{staff['staff_id']:<4} {staff['staff_name']:<20} {status:<8} {created:<20}")
        
        self.wait_for_enter()
    
    def add_new_staff(self):
        """Add new staff member"""
        self.clear_screen()
        self.print_header("Add New Staff")
        
        staff_name = self.get_input("Staff Name")
        if not staff_name:
            return
        
        if StaffManager.staff_exists(staff_name):
            print("Staff name already exists!")
            self.wait_for_enter()
            return
        
        password = self.get_input("Password")
        if not password:
            return
        
        success = StaffManager.add_staff(staff_name, password)
        if success:
            print("✓ Staff added successfully!")
        else:
            print("✗ Failed to add staff")
        
        self.wait_for_enter()
    
    def change_password(self):
        """Change staff password"""
        self.clear_screen()
        self.print_header("Change Password")
        
        # Show active staff
        staff_list = StaffManager.get_active_staff()
        
        print("Active Staff:")
        for i, staff in enumerate(staff_list, 1):
            print(f"{i}. {staff['staff_name']}")
        
        choice = self.get_input("Select staff", int, required=False)
        if not choice or choice < 1 or choice > len(staff_list):
            return
        
        selected_staff = staff_list[choice - 1]
        
        new_password = self.get_input(f"New password for {selected_staff['staff_name']}")
        if not new_password:
            return
        
        success = StaffManager.change_password(selected_staff['staff_id'], new_password)
        if success:
            print("✓ Password changed successfully!")
        else:
            print("✗ Failed to change password")
        
        self.wait_for_enter()
    
    def reports(self):
        """Reports interface"""
        while True:
            self.clear_screen()
            self.print_header("Reports")
            
            options = [
                "📈 Daily Sales Report",
                "📊 Staff Performance Report",
                "🏪 All Bills Today"
            ]
            
            self.print_menu("Reports:", options)
            
            choice = self.get_input("Enter choice", int, required=False)
            
            if choice == 1:
                self.daily_sales_report()
            elif choice == 2:
                self.staff_performance_report()
            elif choice == 3:
                self.bills_today()
            elif choice == 0:
                break
            else:
                print("Invalid choice. Please try again.")
                self.wait_for_enter()
    
    def daily_sales_report(self):
        """Show daily sales report"""
        today = datetime.now().strftime("%Y-%m-%d")
        bills = BillingManager.get_bills_by_date(today, today)
        
        self.clear_screen()
        self.print_header(f"Daily Sales Report - {today}")
        
        if not bills:
            print("No sales today.")
            self.wait_for_enter()
            return
        
        total_sales = sum(bill['grand_total'] for bill in bills)
        total_bills = len(bills)
        
        print(f"Total Bills: {total_bills}")
        print(f"Total Sales: ₹{total_sales:.2f}")
        print(f"Average Bill: ₹{total_sales/total_bills:.2f}")
        print()
        
        print(f"{'Invoice':<12} {'Time':<8} {'Staff':<15} {'Items':<6} {'Total':<10}")
        print("-" * 60)
        
        for bill in bills:
            time_str = bill['bill_date'][11:16] if len(bill['bill_date']) > 11 else 'N/A'
            print(f"{bill['invoice_number']:<12} {time_str:<8} "
                  f"{bill['staff_name']:<15} {bill['item_count']:<6} ₹{bill['grand_total']:<9.2f}")
        
        self.wait_for_enter()
    
    def staff_performance_report(self):
        """Show staff performance report"""
        today = datetime.now().strftime("%Y-%m-%d")
        bills = BillingManager.get_bills_by_date(today, today)
        
        self.clear_screen()
        self.print_header(f"Staff Performance Report - {today}")
        
        if not bills:
            print("No sales data available.")
            self.wait_for_enter()
            return
        
        # Group by staff
        staff_performance = {}
        for bill in bills:
            staff_name = bill['staff_name']
            if staff_name not in staff_performance:
                staff_performance[staff_name] = {
                    'bills': 0,
                    'total_sales': 0,
                    'total_items': 0
                }
            
            staff_performance[staff_name]['bills'] += 1
            staff_performance[staff_name]['total_sales'] += bill['grand_total']
            staff_performance[staff_name]['total_items'] += bill['item_count']
        
        print(f"{'Staff':<15} {'Bills':<6} {'Items':<6} {'Sales':<10} {'Avg/Bill':<10}")
        print("-" * 55)
        
        for staff_name, perf in staff_performance.items():
            avg_bill = perf['total_sales'] / perf['bills'] if perf['bills'] > 0 else 0
            print(f"{staff_name:<15} {perf['bills']:<6} {perf['total_items']:<6} "
                  f"₹{perf['total_sales']:<9.2f} ₹{avg_bill:<9.2f}")
        
        self.wait_for_enter()
    
    def bills_today(self):
        """Show all bills for today"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.view_bills_by_date(today, today)
    
    def view_bills_by_date(self, date_from: str, date_to: str):
        """View bills for date range"""
        bills = BillingManager.get_bills_by_date(date_from, date_to)
        
        self.clear_screen()
        self.print_header(f"Bills from {date_from} to {date_to}")
        
        if not bills:
            print("No bills found for the selected date range.")
            self.wait_for_enter()
            return
        
        print(f"{'Invoice':<12} {'Date/Time':<20} {'Staff':<15} {'Items':<6} {'Total':<10}")
        print("-" * 70)
        
        for bill in bills:
            date_time = bill['bill_date'][:16] if bill['bill_date'] else 'N/A'
            print(f"{bill['invoice_number']:<12} {date_time:<20} "
                  f"{bill['staff_name']:<15} {bill['item_count']:<6} ₹{bill['grand_total']:<9.2f}")
        
        self.wait_for_enter()
    
    def database_backup(self):
        """Create database backup"""
        self.clear_screen()
        self.print_header("Database Backup")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"thangamayil_backup_{timestamp}.db"
        
        print(f"Backup will be saved as: {backup_filename}")
        confirm = input("Proceed with backup? (Y/n): ").lower()
        
        if confirm in ('', 'y', 'yes'):
            try:
                success = db.backup_database(backup_filename)
                if success:
                    print(f"✓ Database backup created successfully!")
                    print(f"File: {backup_filename}")
                else:
                    print("✗ Backup failed")
            except Exception as e:
                print(f"✗ Backup error: {e}")
        else:
            print("Backup cancelled.")
        
        self.wait_for_enter()
    
    def logout(self):
        """Logout current user"""
        confirm = input("Are you sure you want to logout? (y/N): ").lower()
        if confirm == 'y':
            auth.logout()
            self.running = False
    
    def run(self):
        """Run the console application"""
        try:
            # Initialize database
            db.connect()
            
            # Show welcome message
            self.clear_screen()
            self.print_header()
            print("Welcome to the console-based billing system!")
            print("Note: This is the console version since GUI is not available in this environment.")
            self.wait_for_enter()
            
            # Login
            if not self.login():
                print("Login failed. Exiting...")
                return
            
            # Main application loop
            self.main_menu()
            
        except KeyboardInterrupt:
            print("\n\nApplication interrupted by user.")
        except Exception as e:
            print(f"Application error: {e}")
        finally:
            db.disconnect()
            print("\nThank you for using தங்கமயில் சில்க்ஸ் Billing Software!")


def main():
    """Main entry point"""
    app = ConsoleApp()
    app.run()


if __name__ == "__main__":
    main()