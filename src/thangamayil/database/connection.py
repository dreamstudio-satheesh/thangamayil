"""
Database connection and initialization module
Handles SQLite database operations for Thangamayil Billing Software
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional, Any, List, Dict
import bcrypt


class DatabaseConnection:
    """Handles SQLite database connection and operations"""
    
    def __init__(self, db_path: str = "thangamayil.db"):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Create database and tables if they don't exist"""
        if not os.path.exists(self.db_path):
            self.connect()
            self.initialize_database()
    
    def connect(self) -> sqlite3.Connection:
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            return self.connection
        except sqlite3.Error as e:
            raise Exception(f"Database connection failed: {e}")
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize_database(self):
        """Initialize database with schema from db.sql"""
        try:
            # Read and execute schema file
            schema_path = Path(__file__).parent.parent.parent.parent / "db.sql"
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = f.read()
                
                # Execute schema
                cursor = self.connection.cursor()
                cursor.executescript(schema)
                self.connection.commit()
                
                # Hash the default admin password
                self.update_admin_password()
                
                # Run database migrations
                self.run_migrations()
                
                print("Database initialized successfully")
            else:
                raise FileNotFoundError("db.sql schema file not found")
                
        except Exception as e:
            raise Exception(f"Database initialization failed: {e}")
    
    def update_admin_password(self):
        """Hash the default admin password"""
        try:
            cursor = self.connection.cursor()
            
            # Check if admin exists with unhashed password
            cursor.execute("SELECT staff_id, password_hash FROM staff WHERE staff_name = 'admin'")
            admin = cursor.fetchone()
            
            if admin and admin['password_hash'] == 'admin123':
                # Hash the password
                hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
                cursor.execute(
                    "UPDATE staff SET password_hash = ? WHERE staff_name = 'admin'",
                    (hashed_password.decode('utf-8'),)
                )
                self.connection.commit()
                print("Admin password hashed successfully")
                
        except Exception as e:
            print(f"Warning: Could not hash admin password: {e}")
    
    def run_migrations(self):
        """Run database migrations for schema updates"""
        try:
            cursor = self.connection.cursor()
            
            # Migration 1: Add address column to customers table if it doesn't exist
            cursor.execute("PRAGMA table_info(customers)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'address' not in columns:
                cursor.execute("ALTER TABLE customers ADD COLUMN address TEXT")
                print("Migration: Added address column to customers table")
            
            # Migration 2: Insert default Cash customer if it doesn't exist
            cursor.execute("SELECT customer_id FROM customers WHERE phone_number = '1234567899'")
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO customers (customer_name, phone_number, address) VALUES (?, ?, ?)",
                    ('Cash Customer', '1234567899', 'Walk-in Customer')
                )
                print("Migration: Added default Cash Customer")
            
            # Migration 3: Add hsn_code column to items table if it doesn't exist
            cursor.execute("PRAGMA table_info(items)")
            item_columns = [row[1] for row in cursor.fetchall()]
            
            if 'hsn_code' not in item_columns:
                cursor.execute("ALTER TABLE items ADD COLUMN hsn_code TEXT")
                print("Migration: Added hsn_code column to items table")
            
            self.connection.commit()
            
        except Exception as e:
            print(f"Warning: Migration failed: {e}")
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute SELECT query and return results"""
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
            
        except sqlite3.Error as e:
            raise Exception(f"Query execution failed: {e}")
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount
            
        except sqlite3.Error as e:
            self.connection.rollback()
            raise Exception(f"Update execution failed: {e}")
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT query and return the last inserted row ID"""
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            self.connection.rollback()
            raise Exception(f"Insert execution failed: {e}")
    
    def get_single_result(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Execute query and return single result"""
        results = self.execute_query(query, params)
        return results[0] if results else None
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            # Log the backup
            self.execute_insert(
                "INSERT INTO backup_log (file_path) VALUES (?)",
                (backup_path,)
            )
            return True
            
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get system setting value"""
        result = self.get_single_result(
            "SELECT setting_value FROM settings WHERE setting_key = ?",
            (key,)
        )
        return result['setting_value'] if result else None
    
    def update_setting(self, key: str, value: str) -> bool:
        """Update system setting"""
        try:
            # Try update first
            affected = self.execute_update(
                "UPDATE settings SET setting_value = ?, modified_at = CURRENT_TIMESTAMP WHERE setting_key = ?",
                (value, key)
            )
            
            # If no rows affected, insert new setting
            if affected == 0:
                self.execute_insert(
                    "INSERT INTO settings (setting_key, setting_value) VALUES (?, ?)",
                    (key, value)
                )
            
            return True
            
        except Exception as e:
            print(f"Setting update failed: {e}")
            return False


# Global database instance
db = DatabaseConnection()