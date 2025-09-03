# 🏪 Thangamayil Billing Software - Installation Guide

## 📋 **What Users Need to Install**

### ✅ **SIMPLE METHOD (Recommended for Users):**
**Users DON'T need to install anything else!** Just download and run the executable.

### 📁 **Files to Share with Users:**
1. `ThangamayilBilling.exe` - Main application (standalone)
2. `Installation Guide.pdf` - Simple instructions
3. Optional: `ThangamayilBilling_Setup.exe` - Installer version

---

## 🛠️ **For You (Developer) - How to Build:**

### **Step 1: Install PyInstaller**
```bash
pip install pyinstaller
```

### **Step 2: Build Executable**
```bash
# Simple method
python build_exe.py

# Or manual method
pyinstaller --onefile --windowed --name=ThangamayilBilling main.py
```

### **Step 3: Create Installer (Optional)**
1. Download **Inno Setup**: https://jrsoftware.org/isdl.php
2. Open `build_installer.iss` in Inno Setup
3. Click "Compile" to create setup.exe

---

## 👥 **For Users - Installation Instructions**

### 📦 **Method 1: Direct Executable (Easiest)**
1. Download `ThangamayilBilling.exe`
2. Create folder: `C:\ThangamayilBilling\`
3. Copy `ThangamayilBilling.exe` to this folder
4. Double-click to run
5. **First time**: Enter admin/admin123 to login

### 📦 **Method 2: Using Installer**
1. Download `ThangamayilBilling_Setup.exe`
2. Right-click → "Run as Administrator"
3. Follow setup wizard
4. Click desktop shortcut to run

---

## 🖥️ **Windows 11 Requirements**

### ✅ **What's Already Built-in:**
- Windows 11 (any version)
- No additional software needed
- No Python installation required
- No dependencies to install

### 🖨️ **For Thermal Printer (Optional):**
- USB thermal printer (4-inch recommended)
- Install printer driver from manufacturer
- Set as default printer in Windows

### 📱 **For Barcode Scanner (Optional):**
- USB barcode scanner
- Configure to send "Enter" after scan
- No additional software needed

---

## 🚀 **First Time Setup**

### 📋 **After Installation:**
1. Run `ThangamayilBilling.exe`
2. **Login:** admin / admin123
3. **Setup Shop:** Go to Settings → Configure shop details
4. **Add Items:** Items Master → Add your products
5. **Ready!** Start billing with F1 or New Bill button

### 🔧 **Configure Thermal Printer:**
1. Connect USB thermal printer
2. Install printer driver
3. Set as default printer in Windows Settings
4. Test with sample bill

### 📊 **Configure Barcode Scanner:**
1. Connect USB barcode scanner
2. Test in any text editor (should type + Enter)
3. Use in billing: Scan barcode → Item auto-adds

---

## 💼 **What Users Get**

### 🎯 **Core Features:**
- ✅ Complete offline billing system
- ✅ GST compliant invoices
- ✅ Thermal printer support
- ✅ Barcode scanning
- ✅ Item management
- ✅ Staff management
- ✅ Reports and analytics
- ✅ Database backup/restore

### 📁 **File Structure After Install:**
```
C:\ThangamayilBilling\
├── ThangamayilBilling.exe    # Main application
├── thangamayil.db           # Database (created on first run)
├── backups\                 # Backup folder (auto-created)
└── temp\                    # Temporary files
```

---

## 🆘 **Troubleshooting**

### ❌ **"Windows protected your PC"**
- Click "More info" → "Run anyway"
- Or right-click exe → Properties → Unblock

### ❌ **"App won't start"**
- Run as Administrator
- Check Windows Defender didn't quarantine
- Disable antivirus temporarily

### ❌ **Thermal printer not working**
- Check USB connection
- Install printer driver
- Set as default printer
- Test with Notepad print

### ❌ **Database issues**
- Delete `thangamayil.db` to reset
- Application will recreate with default data
- Use backup feature regularly

---

## 📞 **Support**

For technical support:
- Check logs in application
- Use backup/restore feature
- Contact developer with error screenshots

---

## 🔒 **Security Note**

The application:
- ✅ Works completely offline
- ✅ No internet connection required
- ✅ All data stored locally
- ✅ No data sharing with external servers
- ✅ Secure password hashing (bcrypt)

Perfect for shops that want complete data privacy!