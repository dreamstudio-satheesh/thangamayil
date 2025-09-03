"""
Build script for creating Windows executable
Run this script to create a standalone executable for Windows
"""

import os
import sys
import shutil
import subprocess

def build_executable():
    """Build executable using PyInstaller"""
    print("🔨 Building Thangamayil Billing Software executable...")
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Single executable file
        "--windowed",  # No console window
        "--name=ThangamayilBilling",  # Executable name
        "--icon=icon.ico",  # Add icon if available
        "--add-data=db.sql;.",  # Include database schema
        "--add-data=src;src",  # Include source files
        "--hidden-import=tkinter",
        "--hidden-import=sqlite3",
        "--hidden-import=bcrypt",
        "--collect-all=tkinter",
        "main.py"
    ]
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Executable created successfully!")
        print("📁 Location: dist/ThangamayilBilling.exe")
        
        # Copy additional files to dist folder
        if os.path.exists("db.sql"):
            shutil.copy2("db.sql", "dist/")
            print("✅ Database schema copied")
        
        print("\n🎉 Build completed! Your executable is ready in the 'dist' folder.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print("Error output:", e.stderr)
        return False
    
    return True

def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller installed successfully")

if __name__ == "__main__":
    print("=" * 60)
    print("🏪 Thangamayil Billing Software - Build Script")
    print("=" * 60)
    
    # Install PyInstaller if needed
    install_pyinstaller()
    
    # Build executable
    if build_executable():
        print("\n📋 Next steps:")
        print("1. Test the executable: dist/ThangamayilBilling.exe")
        print("2. Create installer (optional): Use Inno Setup or NSIS")
        print("3. Share with users: Just send them the executable!")
    else:
        print("\n❌ Build failed. Please check the error messages above.")