-- Staff table (authentication + association with bills)
CREATE TABLE staff (
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_name TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers (optional, mostly for loyalty/future)
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    phone_number TEXT UNIQUE,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Item Categories
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Items master
CREATE TABLE items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT UNIQUE,
    item_name TEXT NOT NULL,
    category_id INTEGER,
    price REAL NOT NULL,
    gst_percentage REAL DEFAULT 5.0,  -- GST % (0–28)
    stock_quantity INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(category_id) REFERENCES categories(category_id)
);

-- Bills (one entry per invoice)
CREATE TABLE bills (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT UNIQUE NOT NULL,
    bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    customer_id INTEGER,
    staff_id INTEGER NOT NULL,
    subtotal REAL DEFAULT 0.00,
    discount_amount REAL DEFAULT 0.00,
    discount_percentage REAL DEFAULT 0.00,
    cgst_amount REAL DEFAULT 0.00,
    sgst_amount REAL DEFAULT 0.00,
    igst_amount REAL DEFAULT 0.00,
    round_off REAL DEFAULT 0.00,
    grand_total REAL NOT NULL,
    payment_mode TEXT DEFAULT 'CASH',   -- CASH / CARD / UPI
    is_cancelled INTEGER DEFAULT 0,     -- 0=Active, 1=Cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY(staff_id) REFERENCES staff(staff_id)
);

-- Bill Items (line-level details)
CREATE TABLE bill_items (
    bill_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,        -- Store for historical data
    barcode TEXT,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price REAL NOT NULL,
    discount_percentage REAL DEFAULT 0.00,
    discount_amount REAL DEFAULT 0.00,
    gst_percentage REAL NOT NULL,
    gst_amount REAL DEFAULT 0.00,
    line_total REAL NOT NULL,       -- (price*qty - discount) + gst
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(bill_id) REFERENCES bills(bill_id),
    FOREIGN KEY(item_id) REFERENCES items(item_id)
);

-- Stock movements (audit for stock report)
CREATE TABLE stock_movements (
    movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    movement_type TEXT NOT NULL,    -- 'IN', 'OUT', 'ADJUSTMENT'
    quantity INTEGER NOT NULL,      -- + for IN, - for OUT
    reference_type TEXT,            -- 'BILL', 'STOCK_ADJUSTMENT', 'INITIAL'
    reference_id INTEGER,           -- link to bill_id if BILL
    notes TEXT,
    staff_id INTEGER,
    movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(item_id) REFERENCES items(item_id),
    FOREIGN KEY(staff_id) REFERENCES staff(staff_id)
);

-- System Settings
CREATE TABLE settings (
    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    description TEXT,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Backup log (to track exports)
CREATE TABLE backup_log (
    backup_id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    backup_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schema migrations tracking
CREATE TABLE schema_migrations (
    migration_id TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_items_barcode ON items(barcode);
CREATE INDEX IF NOT EXISTS idx_items_name ON items(item_name);
CREATE INDEX IF NOT EXISTS idx_bills_date ON bills(bill_date);
CREATE INDEX IF NOT EXISTS idx_bills_invoice ON bills(invoice_number);
CREATE INDEX IF NOT EXISTS idx_bills_staff ON bills(staff_id);
CREATE INDEX IF NOT EXISTS idx_bill_items_bill ON bill_items(bill_id);
CREATE INDEX IF NOT EXISTS idx_stock_movements_item ON stock_movements(item_id);

-- Insert Default Data
INSERT OR IGNORE INTO categories (category_name) VALUES 
('Silk Sarees'),
('Cotton Sarees'),
('Designer Sarees'),
('Wedding Collection'),
('Casual Wear'),
('Accessories');

INSERT OR IGNORE INTO settings (setting_key, setting_value, description) VALUES 
('shop_name', 'தங்கமயில் சில்க்ஸ்', 'Shop Name'),
('shop_address', 'No.1 Main Road, Tamil Nadu, IN', 'Shop Address'),
('shop_phone', '+91-9876543210', 'Shop Phone Number'),
('gstin', '33AAACT9454F1ZB', 'GST Identification Number'),
('state_code', '33', 'State Code for GST'),
('invoice_prefix', 'TSK', 'Invoice Number Prefix'),
('low_stock_threshold', '10', 'Low Stock Alert Threshold');

-- Insert Default Admin Staff (password: admin123)
INSERT OR IGNORE INTO staff (staff_name, password_hash, is_active) VALUES 
('admin', 'admin123', 1);

-- Insert Default Cash Customer
INSERT OR IGNORE INTO customers (customer_name, phone_number, address) VALUES 
('Cash Customer', '1234567899', 'Walk-in Customer');
