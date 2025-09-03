# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**தங்கமயில் சில்க்ஸ் – Offline Billing Software** is a Python-based POS (Point of Sale) application designed specifically for silk shops. The software is intended to be a lightweight, offline billing solution with barcode scanning capabilities, GST calculations, and thermal printer support.

## Technology Stack

- **Frontend**: Python with Tkinter/PyQt for desktop UI
- **Database**: SQLite for local data storage
- **PDF Generation**: ReportLab for invoice generation
- **Target Platform**: Windows (single executable deployment)

## Core Architecture

The system should follow a modular architecture with these key components:

### Database Layer
- SQLite database with tables for items, customers, bills, and transactions
- Schema should support: barcode, item name, category, price, GST%, stock quantity
- Customer data (optional): name, phone number

### Business Logic Layer
- **Items Management**: CRUD operations for inventory
- **Billing Engine**: Barcode scanning, manual entry, discount calculations
- **GST Calculator**: Automatic CGST/SGST calculation
- **Report Generator**: Daily sales, GST summaries, stock reports

### UI Layer
- Touch-friendly interface optimized for cashier use
- Barcode scanner integration
- Real-time bill preview and editing
- Print dialog integration

### Report System
- Daily sales reports
- GST summary reports  
- Item-wise sales analysis
- Stock level reports
- Export capabilities (CSV/Excel)

## Key Features to Implement

### Master Data Management
- Items master with barcode support
- Customer master (optional)
- Category management

### POS Billing
- Barcode scanning with auto-entry
- Manual item search and selection
- Quantity editing and discount application
- Real-time GST calculation (CGST + SGST)
- Invoice number generation
- Thermal printer integration

### GST Invoice Format
Reference the bill format structure in `billprint.md` for proper GST invoice layout including:
- Header with shop details and GSTIN
- Itemized table with GST calculations
- Summary section with tax breakdowns
- Footer with payment mode and terms

## Development Guidelines

### Database Schema Design
- Use proper indexing for barcode and item lookups
- Implement referential integrity
- Plan for data backup/restore functionality

### Performance Requirements
- Billing entry should complete in < 2 seconds per item
- Application must work completely offline
- Optimize for barcode scanner input latency

### UI/UX Considerations
- Design for touch-screen compatibility
- Large, clear buttons for cashier operations
- Keyboard shortcuts for power users
- Error handling with clear user messages

### Deployment
- Package as single Windows executable
- Include thermal printer drivers/configuration
- Provide database backup utilities
- Local installation with minimal dependencies

## Future Enhancement Roadmap
- Multi-user login with role-based access
- Cloud synchronization for multi-branch operations
- Mobile app integration
- Customer loyalty program features

## Getting Started

### Installation
```bash
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Running the Application

#### Console Version (Recommended for development/testing)
```bash
python console_app.py
# OR
python run_console.py
```

#### GUI Version (requires tkinter)
```bash
python main.py
```

### Default Credentials
- **Username:** admin
- **Password:** admin123

## Application Structure

```
src/thangamayil/
├── __init__.py           # Package initialization with app metadata
├── database/
│   ├── __init__.py
│   └── connection.py     # SQLite connection, schema initialization
├── models/
│   ├── __init__.py
│   ├── auth.py          # AuthManager, StaffManager classes
│   ├── items.py         # ItemsManager for inventory operations
│   └── billing.py       # BillingManager, GSTCalculator classes
├── ui/                   # Complete Tkinter GUI components
│   ├── __init__.py
│   ├── login.py         # Staff login window
│   ├── main_window.py   # Main application dashboard
│   ├── pos_billing.py   # POS billing interface
│   ├── items_management.py  # Items CRUD interface
│   ├── staff_management.py  # Staff administration
│   ├── bill_management.py   # Bill history and management
│   ├── bill_edit.py     # Individual bill editing
│   ├── bill_details.py  # Bill detail viewer
│   ├── item_edit.py     # Item editor dialog
│   ├── reports.py       # Reports generation interface
│   └── thermal_printer.py  # Printer integration
├── reports/             # Report generation modules
└── utils/               # Utility functions
```

## Entry Points

- **console_app.py** - Full-featured console interface (recommended for development)
- **main.py** - Primary GUI application entry point
- **run_console.py** - Alternative console launcher
- **run_gui.py** - GUI launcher with error handling
- **run_gui_safe.py** - GUI launcher with enhanced safety checks

## Key Features Implemented

### 1. Staff Authentication System
- Secure login with bcrypt password hashing
- Session management
- Staff management (add, edit, deactivate)

### 2. Items Master Management
- Add/edit items with barcode support
- Category management
- Stock tracking with movement history
- Low stock alerts

### 3. POS Billing System
- Barcode scanning support (ready for hardware integration)
- Manual item search and selection
- Real-time GST calculations (CGST/SGST/IGST)
- Multiple discount options (item-level and bill-level)
- Invoice generation with proper GST format

### 4. GST Compliance
- Automatic CGST+SGST for intra-state transactions
- IGST for inter-state transactions
- Proper tax calculations with rounding
- GST-compliant invoice format

### 5. Inventory Management
- Real-time stock updates
- Stock movement tracking
- Low stock alerts
- Stock valuation reports

### 6. Reporting System
- Daily sales reports
- Staff performance reports
- Stock reports
- GST summary reports

## Database Management

### Architecture
The application uses a `DatabaseConnection` class that:
- Automatically creates `thangamayil.db` on first run
- Initializes schema from `db.sql` file  
- Provides connection pooling and row factory for named column access
- Handles transaction management and error recovery

### Key Tables
- **staff** - Authentication with bcrypt password hashing
- **items** - Product catalog with barcode, price, GST%, stock
- **categories** - Item categorization
- **customers** - Optional customer data
- **bills** - Invoice headers with staff association
- **bill_items** - Line items with quantity, discounts, GST calculations
- **stock_movements** - Inventory tracking
- **settings** - Application configuration

### Initialize Database
The database is automatically created and initialized on first run using `db.sql` schema.

### Backup Database
Use the application's built-in backup feature or manually copy the SQLite file:
```bash
cp thangamayil.db backup/thangamayil_$(date +%Y%m%d_%H%M%S).db
```

## Development Commands

### Testing
```bash
# Run core functionality tests
python test_core.py

# Run GUI tests (requires tkinter)
python test_gui_simple.py

# Run with activated virtual environment
source .venv/bin/activate && python test_core.py
```

### Code Quality
```bash
# Format code (configured for line-length 88)
black src/ *.py

# Lint code
flake8 src/ *.py

# Run with optional dev dependencies
uv pip install -e ".[dev]"
```

### Package Building
```bash
# Build distribution package
uv build

# Install in development mode
uv pip install -e .

# Create Windows executable
pip install pyinstaller
pyinstaller --onefile --windowed main.py --name="ThangamayilBilling"
```

## Hardware Integration Notes

### Barcode Scanner
- Configure scanner to send barcode + Enter key
- Application automatically processes barcode input in POS mode

### Thermal Printer
- Update printer settings in database settings table
- Use system's default printer or configure specific thermal printer
- Invoice format optimized for 80mm thermal paper

## Deployment

### Standalone Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed main.py --name="ThangamayilBilling"
```

### Production Setup
1. Copy entire project directory to target system
2. Install Python 3.8+ on target system
3. Run installation commands
4. Configure printer and barcode scanner
5. Update shop details in settings

## Troubleshooting

### Database Issues
- Check if `thangamayil.db` file has proper permissions
- Ensure SQLite3 is available on the system
- Database is automatically created if missing

### Import Errors
- Ensure virtual environment is activated
- Run `uv pip install -e .` to install dependencies
- Check Python path includes `src/` directory

### GUI Not Working
- Use console version: `python console_app.py`
- Install tkinter: `sudo apt-get install python3-tk` (Linux)
- For Windows/macOS, tkinter comes with Python

## File Locations

- **Database:** `thangamayil.db` (SQLite file)
- **Schema:** `db.sql` (database initialization script)
- **Backups:** Created in project root or user-specified location
- **Logs:** Application prints to console
- **Configuration:** Stored in database settings table

## Architecture Patterns

### Global Database Instance
The application uses a global `db` instance from `thangamayil.database.connection` that provides:
- `get_single_result()` - Single row queries
- `get_multiple_results()` - Multi-row queries  
- `execute_query()` - Insert/Update/Delete operations
- Automatic connection management and error handling

### Manager Pattern
Business logic is organized into manager classes:
- **AuthManager** - Login/logout, session management
- **StaffManager** - Staff CRUD operations
- **ItemsManager** - Inventory management 
- **BillingManager** - Invoice creation and management
- **GSTCalculator** - Tax calculations (CGST/SGST/IGST)

### UI Architecture
GUI components follow a consistent pattern:
- Each window/dialog is a separate module in `ui/`
- Manager classes handle business logic
- UI components focus on presentation and user interaction
- Consistent error handling and user feedback