"""
Billing and invoice management models
Handles bill creation, GST calculations, and transaction operations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from ..database.connection import db
from .items import ItemsManager


class GSTCalculator:
    """Handles GST calculations"""
    
    @staticmethod
    def calculate_gst(amount: float, gst_rate: float, is_interstate: bool = False) -> Dict[str, float]:
        """
        Calculate GST amounts
        Returns dict with cgst, sgst, igst, and total_gst
        """
        gst_amount = (amount * gst_rate) / 100
        
        if is_interstate:
            return {
                'cgst': 0.0,
                'sgst': 0.0,
                'igst': gst_amount,
                'total_gst': gst_amount
            }
        else:
            half_gst = gst_amount / 2
            return {
                'cgst': half_gst,
                'sgst': half_gst,
                'igst': 0.0,
                'total_gst': gst_amount
            }
    
    @staticmethod
    def calculate_line_total(quantity: int, unit_price: float, discount_percentage: float = 0, 
                           gst_rate: float = 5.0, is_interstate: bool = False) -> Dict[str, float]:
        """Calculate line item totals with GST"""
        # Base amount
        line_amount = quantity * unit_price
        
        # Apply discount
        discount_amount = (line_amount * discount_percentage) / 100
        taxable_amount = line_amount - discount_amount
        
        # Calculate GST
        gst_calc = GSTCalculator.calculate_gst(taxable_amount, gst_rate, is_interstate)
        
        return {
            'line_amount': line_amount,
            'discount_amount': discount_amount,
            'taxable_amount': taxable_amount,
            'gst_amount': gst_calc['total_gst'],
            'cgst_amount': gst_calc['cgst'],
            'sgst_amount': gst_calc['sgst'],
            'igst_amount': gst_calc['igst'],
            'line_total': taxable_amount + gst_calc['total_gst']
        }


class BillingManager:
    """Handles billing operations"""
    
    @staticmethod
    def generate_invoice_number() -> str:
        """Generate unique invoice number"""
        try:
            prefix = db.get_setting('invoice_prefix') or 'TSK'
            
            # Get next sequence number
            result = db.get_single_result(
                "SELECT MAX(CAST(SUBSTR(invoice_number, LENGTH(?) + 1) AS INTEGER)) as max_num FROM bills WHERE invoice_number LIKE ?",
                (prefix, f"{prefix}%")
            )
            
            next_num = 1 if not result or not result['max_num'] else result['max_num'] + 1
            return f"{prefix}{next_num:06d}"
            
        except Exception:
            # Fallback to timestamp-based
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"TSK{timestamp}"
    
    @staticmethod
    def create_bill(staff_id: int, customer_id: Optional[int] = None) -> Optional[int]:
        """Create new bill and return bill_id"""
        try:
            invoice_number = BillingManager.generate_invoice_number()
            
            bill_id = db.execute_insert(
                """
                INSERT INTO bills 
                (invoice_number, staff_id, customer_id, subtotal, grand_total)
                VALUES (?, ?, ?, 0.00, 0.00)
                """,
                (invoice_number, staff_id, customer_id)
            )
            
            return bill_id
            
        except Exception as e:
            print(f"Create bill error: {e}")
            return None
    
    @staticmethod
    def add_item_to_bill(bill_id: int, item_data: Dict[str, Any], is_interstate: bool = False) -> bool:
        """Add item to bill"""
        try:
            # Calculate totals
            calc = GSTCalculator.calculate_line_total(
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                discount_percentage=item_data.get('discount_percentage', 0),
                gst_rate=item_data['gst_percentage'],
                is_interstate=is_interstate
            )
            
            # Add item to bill
            db.execute_insert(
                """
                INSERT INTO bill_items 
                (bill_id, item_id, item_name, barcode, quantity, unit_price, 
                 discount_percentage, discount_amount, gst_percentage, gst_amount, line_total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    bill_id,
                    item_data['item_id'],
                    item_data['item_name'],
                    item_data.get('barcode'),
                    item_data['quantity'],
                    item_data['unit_price'],
                    item_data.get('discount_percentage', 0),
                    calc['discount_amount'],
                    item_data['gst_percentage'],
                    calc['gst_amount'],
                    calc['line_total']
                )
            )
            
            return True
            
        except Exception as e:
            print(f"Add item to bill error: {e}")
            return False
    
    @staticmethod
    def update_bill_item(bill_item_id: int, quantity: int, discount_percentage: float = 0, 
                        is_interstate: bool = False) -> bool:
        """Update existing bill item"""
        try:
            # Get current item details
            item_result = db.get_single_result(
                "SELECT * FROM bill_items WHERE bill_item_id = ?",
                (bill_item_id,)
            )
            
            if not item_result:
                return False
            
            # Calculate new totals
            calc = GSTCalculator.calculate_line_total(
                quantity=quantity,
                unit_price=item_result['unit_price'],
                discount_percentage=discount_percentage,
                gst_rate=item_result['gst_percentage'],
                is_interstate=is_interstate
            )
            
            # Update item
            db.execute_update(
                """
                UPDATE bill_items SET 
                quantity = ?, discount_percentage = ?, discount_amount = ?,
                gst_amount = ?, line_total = ?
                WHERE bill_item_id = ?
                """,
                (
                    quantity,
                    discount_percentage,
                    calc['discount_amount'],
                    calc['gst_amount'],
                    calc['line_total'],
                    bill_item_id
                )
            )
            
            return True
            
        except Exception as e:
            print(f"Update bill item error: {e}")
            return False
    
    @staticmethod
    def remove_item_from_bill(bill_item_id: int) -> bool:
        """Remove item from bill"""
        try:
            db.execute_update(
                "DELETE FROM bill_items WHERE bill_item_id = ?",
                (bill_item_id,)
            )
            return True
        except Exception as e:
            print(f"Remove item from bill error: {e}")
            return False
    
    @staticmethod
    def calculate_bill_totals(bill_id: int, bill_discount_percentage: float = 0, 
                             is_interstate: bool = False) -> Dict[str, float]:
        """Calculate and update bill totals"""
        try:
            # Get all bill items
            items = db.execute_query(
                "SELECT * FROM bill_items WHERE bill_id = ?",
                (bill_id,)
            )
            
            if not items:
                return {'subtotal': 0, 'total_gst': 0, 'grand_total': 0}
            
            subtotal = 0
            total_cgst = 0
            total_sgst = 0
            total_igst = 0
            
            for item in items:
                # Recalculate each item with current settings
                calc = GSTCalculator.calculate_line_total(
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    discount_percentage=item['discount_percentage'],
                    gst_rate=item['gst_percentage'],
                    is_interstate=is_interstate
                )
                
                subtotal += calc['taxable_amount']
                total_cgst += calc['cgst_amount']
                total_sgst += calc['sgst_amount']
                total_igst += calc['igst_amount']
            
            # Apply bill-level discount
            bill_discount_amount = (subtotal * bill_discount_percentage) / 100
            discounted_subtotal = subtotal - bill_discount_amount
            
            # Recalculate GST on discounted amount
            if bill_discount_percentage > 0:
                gst_ratio = (total_cgst + total_sgst + total_igst) / subtotal if subtotal > 0 else 0
                total_gst_after_discount = discounted_subtotal * gst_ratio
                
                if is_interstate:
                    total_cgst = 0
                    total_sgst = 0
                    total_igst = total_gst_after_discount
                else:
                    total_cgst = total_gst_after_discount / 2
                    total_sgst = total_gst_after_discount / 2
                    total_igst = 0
            
            total_gst = total_cgst + total_sgst + total_igst
            pre_round_total = discounted_subtotal + total_gst
            
            # Apply rounding
            grand_total = round(pre_round_total)
            round_off = grand_total - pre_round_total
            
            # Update bill
            db.execute_update(
                """
                UPDATE bills SET 
                subtotal = ?, discount_amount = ?, discount_percentage = ?,
                cgst_amount = ?, sgst_amount = ?, igst_amount = ?,
                round_off = ?, grand_total = ?
                WHERE bill_id = ?
                """,
                (
                    subtotal,
                    bill_discount_amount,
                    bill_discount_percentage,
                    total_cgst,
                    total_sgst,
                    total_igst,
                    round_off,
                    grand_total,
                    bill_id
                )
            )
            
            return {
                'subtotal': subtotal,
                'discount_amount': bill_discount_amount,
                'cgst_amount': total_cgst,
                'sgst_amount': total_sgst,
                'igst_amount': total_igst,
                'total_gst': total_gst,
                'round_off': round_off,
                'grand_total': grand_total
            }
            
        except Exception as e:
            print(f"Calculate bill totals error: {e}")
            return {'subtotal': 0, 'total_gst': 0, 'grand_total': 0}
    
    @staticmethod
    def finalize_bill(bill_id: int, payment_mode: str = 'CASH') -> bool:
        """Finalize bill and update stock"""
        try:
            # Get bill details
            bill = db.get_single_result("SELECT * FROM bills WHERE bill_id = ?", (bill_id,))
            if not bill:
                return False
            
            # Get all bill items
            items = db.execute_query("SELECT * FROM bill_items WHERE bill_id = ?", (bill_id,))
            
            # Update stock for each item
            for item in items:
                ItemsManager.reduce_stock_for_sale(
                    item_id=item['item_id'],
                    quantity=item['quantity'],
                    bill_id=bill_id,
                    staff_id=bill['staff_id']
                )
            
            # Update payment mode
            db.execute_update(
                "UPDATE bills SET payment_mode = ? WHERE bill_id = ?",
                (payment_mode, bill_id)
            )
            
            return True
            
        except Exception as e:
            print(f"Finalize bill error: {e}")
            return False
    
    @staticmethod
    def get_bill_details(bill_id: int) -> Optional[Dict[str, Any]]:
        """Get complete bill details"""
        try:
            # Get bill header
            bill = db.get_single_result(
                """
                SELECT b.*, s.staff_name, c.customer_name, c.phone_number
                FROM bills b
                LEFT JOIN staff s ON b.staff_id = s.staff_id
                LEFT JOIN customers c ON b.customer_id = c.customer_id
                WHERE b.bill_id = ?
                """,
                (bill_id,)
            )
            
            if not bill:
                return None
            
            # Get bill items
            items = db.execute_query(
                "SELECT * FROM bill_items WHERE bill_id = ? ORDER BY bill_item_id",
                (bill_id,)
            )
            
            return {
                'bill': dict(bill),
                'items': [dict(item) for item in items]
            }
            
        except Exception as e:
            print(f"Get bill details error: {e}")
            return None
    
    @staticmethod
    def get_bills_by_date(date_from: str, date_to: str, staff_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get bills within date range"""
        query = """
            SELECT b.*, s.staff_name, c.customer_name,
            COUNT(bi.bill_item_id) as item_count
            FROM bills b
            LEFT JOIN staff s ON b.staff_id = s.staff_id
            LEFT JOIN customers c ON b.customer_id = c.customer_id
            LEFT JOIN bill_items bi ON b.bill_id = bi.bill_id
            WHERE DATE(b.bill_date) BETWEEN ? AND ?
            AND b.is_cancelled = 0
        """
        
        params = [date_from, date_to]
        
        if staff_id:
            query += " AND b.staff_id = ?"
            params.append(staff_id)
        
        query += " GROUP BY b.bill_id ORDER BY b.bill_date DESC"
        
        return [dict(row) for row in db.execute_query(query, params)]
    
    @staticmethod
    def cancel_bill(bill_id: int, staff_id: int) -> bool:
        """Cancel a bill and restore stock"""
        try:
            # Get bill items to restore stock
            items = db.execute_query("SELECT * FROM bill_items WHERE bill_id = ?", (bill_id,))
            
            for item in items:
                # Restore stock
                current_item = ItemsManager.get_item_by_id(item['item_id'])
                if current_item:
                    new_stock = current_item['stock_quantity'] + item['quantity']
                    db.execute_update(
                        "UPDATE items SET stock_quantity = ? WHERE item_id = ?",
                        (new_stock, item['item_id'])
                    )
                    
                    # Log stock movement
                    db.execute_insert(
                        """
                        INSERT INTO stock_movements 
                        (item_id, movement_type, quantity, reference_type, reference_id, staff_id, notes)
                        VALUES (?, 'IN', ?, 'BILL_CANCEL', ?, ?, 'Stock restored from cancelled bill')
                        """,
                        (item['item_id'], item['quantity'], bill_id, staff_id)
                    )
            
            # Mark bill as cancelled
            db.execute_update(
                "UPDATE bills SET is_cancelled = 1 WHERE bill_id = ?",
                (bill_id,)
            )
            
            return True
            
        except Exception as e:
            print(f"Cancel bill error: {e}")
            return False