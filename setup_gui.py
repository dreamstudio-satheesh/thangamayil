#!/usr/bin/env python3
"""
Setup script to ensure GUI dependencies are available and launch the GUI application
"""

import sys
import subprocess
import os
from pathlib import Path

def check_tkinter():
    """Check if tkinter is available"""
    try:
        import tkinter as tk
        print("✓ tkinter is available")
        return True
    except ImportError:
        print("✗ tkinter not found")
        return False

def install_tkinter_ubuntu():
    """Install tkinter on Ubuntu/Debian systems"""
    try:
        print("Installing tkinter for Ubuntu/Debian...")
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'python3-tk'], check=True)
        print("✓ tkinter installation completed")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install tkinter")
        return False
    except FileNotFoundError:
        print("✗ apt-get not found (not Ubuntu/Debian system)")
        return False

def setup_virtual_environment():
    """Setup virtual environment and install dependencies"""
    venv_path = Path('.venv')
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', '.venv'], check=True)
        print("✓ Virtual environment created")
    
    # Activate and install dependencies
    if sys.platform == 'win32':
        activate_script = venv_path / 'Scripts' / 'activate'
        python_exe = venv_path / 'Scripts' / 'python.exe'
    else:
        activate_script = venv_path / 'bin' / 'activate'
        python_exe = venv_path / 'bin' / 'python'
    
    print("Installing dependencies...")
    subprocess.run([str(python_exe), '-m', 'pip', 'install', '-e', '.'], check=True)
    print("✓ Dependencies installed")
    
    return python_exe

def create_gui_launcher():
    """Create a GUI launcher script"""
    launcher_content = '''#!/usr/bin/env python3
"""
GUI Application Launcher for தங்கமயில் சில்க்ஸ் Billing Software
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from thangamayil.ui.login import show_login
    from thangamayil.ui.main_window import MainWindow
    from thangamayil.database.connection import db
    from thangamayil import APP_NAME, APP_VERSION
except ImportError as e:
    print(f"Import error: {e}")
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Import Error", 
        f"Failed to import required modules:\\n{e}\\n\\nPlease run: pip install -e ."
    )
    sys.exit(1)

def main():
    """Main GUI application entry point"""
    print(f"Starting {APP_NAME} GUI v{APP_VERSION}")
    
    try:
        # Initialize database
        db.connect()
        print("✓ Database connected")
        
        # Show login
        if show_login():
            print("✓ Login successful")
            # Start main application
            main_app = MainWindow()
            main_app.run()
        else:
            print("Login cancelled or failed")
    
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Application error:\\n{str(e)}")
        print(f"Error: {e}")
    
    finally:
        db.disconnect()
        print("Application closed")

if __name__ == "__main__":
    main()
'''
    
    with open('run_gui.py', 'w') as f:
        f.write(launcher_content)
    
    # Make executable on Unix systems
    if sys.platform != 'win32':
        os.chmod('run_gui.py', 0o755)
    
    print("✓ GUI launcher created: run_gui.py")

def main():
    """Main setup function"""
    print("তङ্গময়িল সিল্কস্ - GUI Setup")
    print("=" * 50)
    
    # Check if we're on a system that might not have tkinter
    if not check_tkinter():
        print("\ntkinter is required for the GUI version.")
        
        if sys.platform.startswith('linux'):
            response = input("Would you like to try installing tkinter? (y/N): ")
            if response.lower() == 'y':
                if install_tkinter_ubuntu():
                    print("Please restart this script to continue with GUI setup")
                    return
                else:
                    print("Manual installation required. Please install python3-tk package.")
                    return
        else:
            print("On Windows/macOS, tkinter should be included with Python.")
            print("Please reinstall Python with tkinter support.")
            return
    
    # Setup virtual environment and dependencies
    try:
        python_exe = setup_virtual_environment()
        print(f"✓ Using Python: {python_exe}")
    except Exception as e:
        print(f"✗ Setup failed: {e}")
        return
    
    # Create GUI launcher
    create_gui_launcher()
    
    print("\n" + "=" * 50)
    print("GUI Setup Complete!")
    print("\nTo run the GUI application:")
    print("  python run_gui.py")
    print("\nOr with virtual environment:")
    print("  source .venv/bin/activate  # Linux/Mac")
    print("  .venv\\Scripts\\activate     # Windows")
    print("  python run_gui.py")
    print("\nDefault login: admin / admin123")

if __name__ == "__main__":
    main()