#!/usr/bin/env python3
"""
Quick Start Script for Ransomware Detection System
Run this script to get started quickly
"""

import os
import sys
import subprocess
from pathlib import Path


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("  AI-Based Real-Time Ransomware Detection System")
    print("  Using File Entropy & Access Pattern Intelligence")
    print("="*70 + "\n")


def check_dependencies():
    """Check if required packages are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'numpy',
        'sklearn',
        'watchdog',
        'flask',
        'flask_socketio'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages detected!")
        print(f"\nTo install missing packages, run:")
        print(f"  pip install -r requirements.txt")
        print("\nOr install manually:")
        print(f"  pip install {' '.join(missing_packages)}")
        
        response = input("\nWould you like to install them now? (y/n): ")
        if response.lower() == 'y':
            print("\nInstalling packages...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✓ Installation complete!")
        else:
            print("\nPlease install dependencies before continuing.")
            return False
    else:
        print("\n✓ All dependencies installed!\n")
    
    return True


def show_menu():
    """Display main menu"""
    print("\n" + "="*70)
    print("Select an option to get started:")
    print("="*70)
    print("\n1. 🖥️  Launch Web Dashboard (Recommended)")
    print("2. 🧪 Run Interactive Testing")
    print("3. 🤖 Run Automated Tests")
    print("4. 👁️  Monitor a Directory (Console Mode)")
    print("5. 📖 View Documentation")
    print("6. 🚪 Exit")
    print("\n" + "="*70)


def run_web_dashboard():
    """Launch the web dashboard"""
    print("\n" + "="*70)
    print("Launching Web Dashboard...")
    print("="*70)
    print("\nThe dashboard will open at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        from webdashboard import run_dashboard
        run_dashboard()
    except KeyboardInterrupt:
        print("\n\nDashboard stopped.")
    except Exception as e:
        print(f"\nError: {e}")


def run_interactive_test():
    """Run interactive testing"""
    print("\n" + "="*70)
    print("Launching Interactive Testing Menu...")
    print("="*70 + "\n")
    
    try:
        from testransomewaredetect import interactive_menu
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\nTesting stopped.")
    except Exception as e:
        print(f"\nError: {e}")


def run_automated_test():
    """Run automated tests"""
    print("\n" + "="*70)
    print("Running Automated Test Suite...")
    print("="*70 + "\n")
    
    try:
        from testransomewaredetect import run_detection_test
        run_detection_test()
    except KeyboardInterrupt:
        print("\n\nTest interrupted.")
    except Exception as e:
        print(f"\nError: {e}")


def monitor_directory():
    """Monitor a specific directory"""
    print("\n" + "="*70)
    print("Directory Monitoring Mode")
    print("="*70)
    
    default_dir = "./monitored_directory"
    directory = input(f"\nEnter directory to monitor (default: {default_dir}): ").strip()
    
    if not directory:
        directory = default_dir
    
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    print(f"\nStarting monitoring of: {directory}")
    print("Press Ctrl+C to stop\n")
    
    try:
        from ransomware_detector import start_monitoring
        start_monitoring(directory)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
    except Exception as e:
        print(f"\nError: {e}")


def view_documentation():
    """Display documentation"""
    print("\n" + "="*70)
    print("Documentation")
    print("="*70 + "\n")
    
    if os.path.exists('README.md'):
        print("Opening README.md...\n")
        try:
            if sys.platform == 'darwin':  # macOS
                subprocess.call(['open', 'README.md'])
            elif sys.platform == 'win32':  # Windows
                os.startfile('README.md')
            else:  # Linux
                subprocess.call(['xdg-open', 'README.md'])
        except:
            print("Please open README.md manually to view full documentation.\n")
        
        print("\nQuick Start Guide:")
        print("-" * 70)
        print("""
1. INSTALLATION:
   pip install -r requirements.txt

2. WEB DASHBOARD (Recommended for beginners):
   python web_dashboard.py
   Open: http://127.0.0.1:5000

3. COMMAND LINE MONITORING:
   python ransomware_detector.py /path/to/monitor

4. TESTING:
   python test_ransomware_detection.py

5. FEATURES:
   - Real-time file entropy analysis
   - Access pattern intelligence
   - Machine learning detection
   - Web-based monitoring dashboard
   - Automated testing suite

For detailed documentation, see README.md
        """)
    else:
        print("README.md not found!")


def main():
    """Main entry point"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                run_web_dashboard()
            elif choice == '2':
                run_interactive_test()
            elif choice == '3':
                run_automated_test()
            elif choice == '4':
                monitor_directory()
            elif choice == '5':
                view_documentation()
            elif choice == '6':
                print("\nExiting... Goodbye! 👋\n")
                break
            else:
                print("\n❌ Invalid choice! Please select 1-6.")
        
        except KeyboardInterrupt:
            print("\n\nExiting... Goodbye! 👋\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()