"""
Items management models
Handles inventory operations, categories, and stock management
"""

from typing import List, Optional, Dict, Any
from ..database.connection import db


class ItemsManager:
    """Handles items and inventory operations"""
    
    @staticmethod
    def get_all_categories() -> List[Dict[str, Any]]:
        """Get all item categories"""
        return [dict(row) for row in db.execute_query(
            "SELECT * FROM categories ORDER BY category_name"
        )]
    
    @staticmethod
    def add_category(category_name: str) -> bool:
        """Add new category"""
        try:
            db.execute_insert(
                "INSERT INTO categories (category_name) VALUES (?)",
                (category_name,)
            )
            return True
        except Exception as e:
            print(f"Add category error: {e}")
            return False
    
    @staticmethod
    def get_all_items(include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Get all items with category information"""
        query = """
            SELECT i.*, c.category_name 
            FROM items i 
            LEFT JOIN categories c ON i.category_id = c.category_id
        """
        
        if not include_inactive:
            query += " WHERE i.is_active = 1"
        
        query += " ORDER BY i.item_name"
        
        return [dict(row) for row in db.execute_query(query)]
    
    @staticmethod
    def get_item_by_id(item_id: int) -> Optional[Dict[str, Any]]:
        """Get item by ID"""
        result = db.get_single_result(
            """
            SELECT i.*, c.category_name 
            FROM items i 
            LEFT JOIN categories c ON i.category_id = c.category_id
            WHERE i.item_id = ?
            """,
            (item_id,)
        )
        return dict(result) if result else None
    
    @staticmethod
    def get_item_by_barcode(barcode: str) -> Optional[Dict[str, Any]]:
        """Get item by barcode"""
        result = db.get_single_result(
            """
            SELECT i.*, c.category_name 
            FROM items i 
            LEFT JOIN categories c ON i.category_id = c.category_id
            WHERE i.barcode = ? AND i.is_active = 1
            """,
            (barcode,)
        )
        return dict(result) if result else None
    
    @staticmethod
    def search_items(search_term: str) -> List[Dict[str, Any]]:
        """Search items by name or barcode"""
        search_pattern = f"%{search_term}%"
        return [dict(row) for row in db.execute_query(
            """
            SELECT i.*, c.category_name 
            FROM items i 
            LEFT JOIN categories c ON i.category_id = c.category_id
            WHERE i.is_active = 1 
            AND (i.item_name LIKE ? OR i.barcode LIKE ?)
            ORDER BY i.item_name
            """,
            (search_pattern, search_pattern)
        )]
    
    @staticmethod
    def add_item(item_data: Dict[str, Any]) -> bool:
        """Add new item"""
        try:
            db.execute_insert(
                """
                INSERT INTO items 
                (barcode, item_name, hsn_code, category_id, price, gst_percentage, stock_quantity, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    item_data.get('barcode'),
                    item_data['item_name'],
                    item_data.get('hsn_code'),
                    item_data.get('category_id'),
                    item_data['price'],
                    item_data.get('gst_percentage', 5.0),
                    item_data.get('stock_quantity', 0)
                )
            )
            return True
        except Exception as e:
            print(f"Add item error: {e}")
            return False
    
    @staticmethod
    def update_item(item_id: int, item_data: Dict[str, Any]) -> bool:
        """Update existing item"""
        try:
            db.execute_update(
                """
                UPDATE items SET 
                barcode = ?, item_name = ?, hsn_code = ?, category_id = ?, price = ?, 
                gst_percentage = ?, stock_quantity = ?, is_active = ?,
                modified_at = CURRENT_TIMESTAMP
                WHERE item_id = ?
                """,
                (
                    item_data.get('barcode'),
                    item_data['item_name'],
                    item_data.get('hsn_code'),
                    item_data.get('category_id'),
                    item_data['price'],
                    item_data.get('gst_percentage', 5.0),
                    item_data.get('stock_quantity', 0),
                    1 if item_data.get('is_active', True) else 0,
                    item_id
                )
            )
            return True
        except Exception as e:
            print(f"Update item error: {e}")
            return False
    
    @staticmethod
    def deactivate_item(item_id: int) -> bool:
        """Deactivate item (soft delete)"""
        try:
            db.execute_update(
                "UPDATE items SET is_active = 0, modified_at = CURRENT_TIMESTAMP WHERE item_id = ?",
                (item_id,)
            )
            return True
        except Exception as e:
            print(f"Deactivate item error: {e}")
            return False
    
    @staticmethod
    def update_stock(item_id: int, new_quantity: int, movement_type: str = "ADJUSTMENT", 
                    staff_id: Optional[int] = None, notes: str = "") -> bool:
        """Update item stock and log movement"""
        try:
            # Get current stock
            current_item = ItemsManager.get_item_by_id(item_id)
            if not current_item:
                return False
            
            current_stock = current_item['stock_quantity']
            change = new_quantity - current_stock
            
            # Update item stock
            db.execute_update(
                "UPDATE items SET stock_quantity = ?, modified_at = CURRENT_TIMESTAMP WHERE item_id = ?",
                (new_quantity, item_id)
            )
            
            # Log stock movement if there's a change
            if change != 0:
                db.execute_insert(
                    """
                    INSERT INTO stock_movements 
                    (item_id, movement_type, quantity, reference_type, staff_id, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (item_id, movement_type, change, "STOCK_ADJUSTMENT", staff_id, notes)
                )
            
            return True
        except Exception as e:
            print(f"Update stock error: {e}")
            return False
    
    @staticmethod
    def reduce_stock_for_sale(item_id: int, quantity: int, bill_id: int, staff_id: int) -> bool:
        """Reduce stock for sale and log movement"""
        try:
            # Get current stock
            current_item = ItemsManager.get_item_by_id(item_id)
            if not current_item:
                return False
            
            if current_item['stock_quantity'] < quantity:
                print(f"Insufficient stock for item {item_id}")
                return False
            
            new_stock = current_item['stock_quantity'] - quantity
            
            # Update stock
            db.execute_update(
                "UPDATE items SET stock_quantity = ?, modified_at = CURRENT_TIMESTAMP WHERE item_id = ?",
                (new_stock, item_id)
            )
            
            # Log movement
            db.execute_insert(
                """
                INSERT INTO stock_movements 
                (item_id, movement_type, quantity, reference_type, reference_id, staff_id)
                VALUES (?, 'OUT', ?, 'BILL', ?, ?)
                """,
                (item_id, -quantity, bill_id, staff_id)
            )
            
            return True
        except Exception as e:
            print(f"Reduce stock error: {e}")
            return False
    
    @staticmethod
    def get_low_stock_items(threshold: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get items with low stock"""
        if threshold is None:
            threshold_query = "(SELECT CAST(setting_value AS INTEGER) FROM settings WHERE setting_key = 'low_stock_threshold')"
        else:
            threshold_query = str(threshold)
        
        return [dict(row) for row in db.execute_query(
            f"""
            SELECT i.*, c.category_name 
            FROM items i 
            LEFT JOIN categories c ON i.category_id = c.category_id
            WHERE i.is_active = 1 AND i.stock_quantity <= {threshold_query}
            ORDER BY i.stock_quantity ASC, i.item_name
            """
        )]
    
    @staticmethod
    def get_stock_movements(item_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get stock movement history"""
        query = """
            SELECT sm.*, i.item_name, s.staff_name
            FROM stock_movements sm
            LEFT JOIN items i ON sm.item_id = i.item_id
            LEFT JOIN staff s ON sm.staff_id = s.staff_id
        """
        params = ()
        
        if item_id:
            query += " WHERE sm.item_id = ?"
            params = (item_id,)
        
        query += f" ORDER BY sm.movement_date DESC LIMIT {limit}"
        
        return [dict(row) for row in db.execute_query(query, params)]
    
    @staticmethod
    def barcode_exists(barcode: str, exclude_item_id: Optional[int] = None) -> bool:
        """Check if barcode already exists"""
        query = "SELECT item_id FROM items WHERE barcode = ?"
        params = [barcode]
        
        if exclude_item_id:
            query += " AND item_id != ?"
            params.append(exclude_item_id)
        
        result = db.get_single_result(query, tuple(params))
        return result is not None