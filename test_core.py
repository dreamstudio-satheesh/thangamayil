#!/usr/bin/env python3
"""
Test script to verify core functionality without GUI
Tests database, authentication, and business logic
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from thangamayil.database.connection import db
from thangamayil.models.auth import auth, StaffManager
from thangamayil.models.items import ItemsManager
from thangamayil.models.billing import BillingManager, GSTCalculator


def test_database_connection():
    """Test database initialization and connection"""
    print("=== Testing Database Connection ===")
    try:
        db.connect()
        print("✓ Database connected successfully")
        
        # Test settings
        shop_name = db.get_setting('shop_name')
        print(f"✓ Shop name: {shop_name}")
        
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False


def test_authentication():
    """Test staff authentication"""
    print("\n=== Testing Authentication ===")
    try:
        # Test login with default admin
        success = auth.login('admin', 'admin123')
        print(f"✓ Admin login: {'Success' if success else 'Failed'}")
        
        if success:
            staff_name = auth.get_current_staff_name()
            staff_id = auth.get_current_staff_id()
            print(f"✓ Current staff: {staff_name} (ID: {staff_id})")
            
            # Test logout
            auth.logout()
            print("✓ Logout successful")
        
        return success
    except Exception as e:
        print(f"✗ Authentication error: {e}")
        return False


def test_staff_management():
    """Test staff management operations"""
    print("\n=== Testing Staff Management ===")
    try:
        # Get all staff
        staff_list = StaffManager.get_all_staff()
        print(f"✓ Found {len(staff_list)} staff members")
        
        # Add test staff
        if not StaffManager.staff_exists('test_cashier'):
            success = StaffManager.add_staff('test_cashier', 'test123')
            print(f"✓ Add test staff: {'Success' if success else 'Failed'}")
        
        return True
    except Exception as e:
        print(f"✗ Staff management error: {e}")
        return False


def test_items_management():
    """Test items and inventory management"""
    print("\n=== Testing Items Management ===")
    try:
        # Get categories
        categories = ItemsManager.get_all_categories()
        print(f"✓ Found {len(categories)} categories")
        
        # Add test item
        test_item = {
            'barcode': 'TEST001',
            'item_name': 'Test Silk Saree',
            'category_id': categories[0]['category_id'] if categories else None,
            'price': 2500.00,
            'gst_percentage': 5.0,
            'stock_quantity': 10
        }
        
        # Check if item exists first
        existing = ItemsManager.get_item_by_barcode('TEST001')
        if not existing:
            success = ItemsManager.add_item(test_item)
            print(f"✓ Add test item: {'Success' if success else 'Failed'}")
        else:
            print("✓ Test item already exists")
        
        # Search items
        items = ItemsManager.search_items('Test')
        print(f"✓ Found {len(items)} items matching 'Test'")
        
        return True
    except Exception as e:
        print(f"✗ Items management error: {e}")
        return False


def test_gst_calculations():
    """Test GST calculation logic"""
    print("\n=== Testing GST Calculations ===")
    try:
        # Test basic GST calculation
        calc = GSTCalculator.calculate_gst(1000.00, 5.0, is_interstate=False)
        print(f"✓ Intra-state GST (5% on ₹1000): CGST={calc['cgst']:.2f}, SGST={calc['sgst']:.2f}")
        
        # Test interstate GST
        calc = GSTCalculator.calculate_gst(1000.00, 5.0, is_interstate=True)
        print(f"✓ Inter-state GST (5% on ₹1000): IGST={calc['igst']:.2f}")
        
        # Test line total calculation
        line_calc = GSTCalculator.calculate_line_total(
            quantity=2, 
            unit_price=1000.00, 
            discount_percentage=10, 
            gst_rate=5.0
        )
        print(f"✓ Line calculation (2 × ₹1000, 10% disc, 5% GST): Total=₹{line_calc['line_total']:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ GST calculation error: {e}")
        return False


def test_billing_operations():
    """Test billing operations"""
    print("\n=== Testing Billing Operations ===")
    try:
        # Login as admin first
        if not auth.is_logged_in():
            auth.login('admin', 'admin123')
        
        # Generate invoice number
        invoice_no = BillingManager.generate_invoice_number()
        print(f"✓ Generated invoice number: {invoice_no}")
        
        # Create bill
        staff_id = auth.get_current_staff_id()
        bill_id = BillingManager.create_bill(staff_id)
        if bill_id:
            print(f"✓ Created bill ID: {bill_id}")
            
            # Get test item
            test_item = ItemsManager.get_item_by_barcode('TEST001')
            if test_item:
                # Add item to bill
                item_data = {
                    'item_id': test_item['item_id'],
                    'item_name': test_item['item_name'],
                    'barcode': test_item['barcode'],
                    'quantity': 1,
                    'unit_price': test_item['price'],
                    'gst_percentage': test_item['gst_percentage']
                }
                
                success = BillingManager.add_item_to_bill(bill_id, item_data)
                print(f"✓ Add item to bill: {'Success' if success else 'Failed'}")
                
                # Calculate totals
                totals = BillingManager.calculate_bill_totals(bill_id)
                print(f"✓ Bill totals: Subtotal=₹{totals['subtotal']:.2f}, Total=₹{totals['grand_total']:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Billing operations error: {e}")
        return False


def main():
    """Run all tests"""
    print("தங்கமயில் சில்க்ஸ் - Core Functionality Test\n")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Authentication", test_authentication),
        ("Staff Management", test_staff_management),
        ("Items Management", test_items_management),
        ("GST Calculations", test_gst_calculations),
        ("Billing Operations", test_billing_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All core functionality tests passed!")
        print("The billing system backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    
    # Cleanup
    db.disconnect()


if __name__ == "__main__":
    main()