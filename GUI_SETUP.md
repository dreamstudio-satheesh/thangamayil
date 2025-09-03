# GUI Setup Guide for தங்கமயில் சில்க்ஸ் Billing Software

## Quick GUI Setup

Run the automated setup script:

```bash
python setup_gui.py
```

This script will:
1. ✅ Check if tkinter is available
2. ✅ Install tkinter if needed (on Ubuntu/Debian)
3. ✅ Create virtual environment
4. ✅ Install all dependencies
5. ✅ Create GUI launcher script

After setup, run the GUI with:

```bash
python run_simple.py
```

Or try these alternatives:
```bash
python run_gui_safe.py   # Safe launcher with better error handling
python main.py          # Original launcher with splash screen
python test_gui_simple.py  # Simple test first
```

## Manual Setup

### 1. Install tkinter (if needed)

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

#### CentOS/RHEL/Fedora:
```bash
# CentOS/RHEL
sudo yum install tkinter
# Fedora
sudo dnf install python3-tkinter
```

#### macOS:
tkinter comes with Python. If missing, reinstall Python:
```bash
brew install python-tk
```

#### Windows:
tkinter is included with Python. If missing, reinstall Python from python.org with "tcl/tk and IDLE" option checked.

### 2. Setup Environment

```bash
# Create virtual environment
uv venv
# OR
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e .
# OR
pip install -e .
```

### 3. Run GUI Application

```bash
python main.py
# OR
python run_gui.py  # If created by setup script
```

## GUI Features

The GUI application includes:

### 🔐 **Authentication**
- Secure login with staff name and password
- Session management
- Default login: `admin` / `admin123`

### 🏪 **Main Dashboard**
- Clean, modern interface with menu buttons
- Status bar showing logged-in staff
- Quick access to all modules

### 🛒 **POS Billing Interface**
- **Barcode scanning** - Enter barcode and press Enter
- **Manual item search** - Type to search items by name
- **Real-time bill preview** with line items
- **Discount application** - Item-level and bill-level discounts
- **GST calculations** - Automatic CGST/SGST/IGST
- **Multiple payment modes** - Cash, Card, UPI
- **Bill totals** - Live calculation with grand total display

### 📦 **Items Management**
- **Add/Edit items** with complete details
- **Category management** with organized grouping
- **Stock management** with real-time updates
- **Search and filtering** by name, category, stock status
- **Barcode support** with uniqueness validation
- **Low stock alerts** and reporting

### 👥 **Staff Management**
- **Add new staff** with secure password hashing
- **Edit staff details** and status management
- **Password changes** for existing staff
- **Staff listing** with creation dates and status

### 📊 **Comprehensive Reports**
- **Daily Sales Report** - Sales by date range
- **Staff Performance** - Individual staff metrics
- **Bills Summary** - Detailed transaction listing
- **Payment Mode Report** - Payment method analysis
- **GST Summary** - Tax collection reporting
- **Date range selection** with quick filters
- **Export capabilities** (CSV, Print - to be implemented)

### 💾 **Database Management**
- **Automatic backup** with timestamp
- **File dialog** for save location selection
- **Backup logging** and verification

## Troubleshooting

### tkinter Not Found
- **Linux**: Install `python3-tk` package
- **Windows**: Reinstall Python with tk/tcl support
- **macOS**: Install via `brew install python-tk`

### Import Errors
```bash
# Ensure dependencies are installed
pip install -e .

# Check if you're in the virtual environment
which python  # Should show .venv/bin/python
```

### Database Issues
- Database is auto-created on first run
- Located at `thangamayil.db` in project root
- Delete to reset (will lose all data)

### Window Display Issues
- Ensure you have a display server (X11/Wayland on Linux)
- For remote systems, use X forwarding: `ssh -X`
- For WSL, install VcXsrv or use WSL2 with GUI support

## GUI Screenshots

The application provides a modern, professional interface optimized for:
- **Touch screens** - Large buttons and touch-friendly controls
- **Keyboard shortcuts** - Enter key support, tab navigation
- **Barcode scanners** - Direct input integration
- **Thermal printers** - Receipt format optimization
- **Multiple windows** - Non-blocking dialog system

## System Requirements

- **Python**: 3.8 or higher
- **OS**: Windows 10+, macOS 10.14+, Linux with GUI
- **RAM**: 512MB minimum, 1GB recommended
- **Storage**: 100MB for application + data storage
- **Display**: 1024x768 minimum, 1280x1024 recommended

## Hardware Integration

### Barcode Scanner
- Configure as keyboard input device
- Set to send barcode + Enter key
- Test with barcode entry field in POS

### Thermal Printer
- 80mm thermal receipt printers supported
- Configure via system printer settings
- Test with sample receipt printing

The GUI provides a complete, production-ready billing system suitable for retail environments!