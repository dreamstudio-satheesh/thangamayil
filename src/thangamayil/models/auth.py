"""
Authentication models and operations
Handles staff login, session management, and password operations
"""

import bcrypt
from typing import Optional, Dict, Any
from ..database.connection import db


class AuthManager:
    """Handles authentication operations"""
    
    def __init__(self):
        self.current_staff: Optional[Dict[str, Any]] = None
    
    def login(self, staff_name: str, password: str) -> bool:
        """
        Authenticate staff member
        Returns True if login successful, False otherwise
        """
        try:
            # Get staff record
            staff = db.get_single_result(
                "SELECT * FROM staff WHERE staff_name = ? AND is_active = 1",
                (staff_name,)
            )
            
            if not staff:
                return False
            
            # Check password
            stored_hash = staff['password_hash'].encode('utf-8')
            
            # Handle both hashed and plain passwords (for initial setup)
            if staff['password_hash'] == password:
                # Plain password - hash it and update
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                db.execute_update(
                    "UPDATE staff SET password_hash = ? WHERE staff_id = ?",
                    (hashed_password.decode('utf-8'), staff['staff_id'])
                )
                password_valid = True
            else:
                # Check hashed password
                try:
                    password_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
                except:
                    password_valid = False
            
            if password_valid:
                self.current_staff = {
                    'staff_id': staff['staff_id'],
                    'staff_name': staff['staff_name'],
                    'login_time': 'CURRENT_TIMESTAMP'
                }
                return True
            
            return False
            
        except Exception as e:
            print(f"Login error: {e}")
            return False
    
    def logout(self):
        """Clear current session"""
        self.current_staff = None
    
    def get_current_staff(self) -> Optional[Dict[str, Any]]:
        """Get currently logged-in staff information"""
        return self.current_staff
    
    def is_logged_in(self) -> bool:
        """Check if a staff member is logged in"""
        return self.current_staff is not None
    
    def get_current_staff_id(self) -> Optional[int]:
        """Get current staff ID"""
        return self.current_staff['staff_id'] if self.current_staff else None
    
    def get_current_staff_name(self) -> Optional[str]:
        """Get current staff name"""
        return self.current_staff['staff_name'] if self.current_staff else None


class StaffManager:
    """Handles staff management operations"""
    
    @staticmethod
    def get_all_staff():
        """Get all staff members"""
        return db.execute_query("SELECT * FROM staff ORDER BY staff_name")
    
    @staticmethod
    def get_active_staff():
        """Get all active staff members"""
        return db.execute_query(
            "SELECT * FROM staff WHERE is_active = 1 ORDER BY staff_name"
        )
    
    @staticmethod
    def add_staff(staff_name: str, password: str) -> bool:
        """Add new staff member"""
        try:
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            db.execute_insert(
                "INSERT INTO staff (staff_name, password_hash, is_active) VALUES (?, ?, 1)",
                (staff_name, hashed_password.decode('utf-8'))
            )
            return True
            
        except Exception as e:
            print(f"Add staff error: {e}")
            return False
    
    @staticmethod
    def update_staff(staff_id: int, staff_name: str, is_active: bool = True) -> bool:
        """Update staff information"""
        try:
            db.execute_update(
                "UPDATE staff SET staff_name = ?, is_active = ?, modified_at = CURRENT_TIMESTAMP WHERE staff_id = ?",
                (staff_name, 1 if is_active else 0, staff_id)
            )
            return True
            
        except Exception as e:
            print(f"Update staff error: {e}")
            return False
    
    @staticmethod
    def change_password(staff_id: int, new_password: str) -> bool:
        """Change staff password"""
        try:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            db.execute_update(
                "UPDATE staff SET password_hash = ?, modified_at = CURRENT_TIMESTAMP WHERE staff_id = ?",
                (hashed_password.decode('utf-8'), staff_id)
            )
            return True
            
        except Exception as e:
            print(f"Change password error: {e}")
            return False
    
    @staticmethod
    def deactivate_staff(staff_id: int) -> bool:
        """Deactivate staff member (soft delete)"""
        try:
            db.execute_update(
                "UPDATE staff SET is_active = 0, modified_at = CURRENT_TIMESTAMP WHERE staff_id = ?",
                (staff_id,)
            )
            return True
            
        except Exception as e:
            print(f"Deactivate staff error: {e}")
            return False
    
    @staticmethod
    def staff_exists(staff_name: str) -> bool:
        """Check if staff name already exists"""
        result = db.get_single_result(
            "SELECT staff_id FROM staff WHERE staff_name = ?",
            (staff_name,)
        )
        return result is not None


# Global authentication manager
auth = AuthManager()