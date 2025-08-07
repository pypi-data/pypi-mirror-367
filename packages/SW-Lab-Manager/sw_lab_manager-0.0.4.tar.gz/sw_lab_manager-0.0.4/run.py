#!/usr/bin/env python3
"""
SW Labs Management System - Startup Script
This script provides an easy way to start the application with sample data.
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        import ping3
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False

def create_sample_data():
    """Create sample data if database is empty"""
    try:
        from app import app, db, Lab
        with app.app_context():
            if Lab.query.count() == 0:
                print("Database is empty. Creating sample data...")
                from sample_data import create_sample_data
                create_sample_data()
                print("✓ Sample data created")
            else:
                print("✓ Database already contains data")
        return True
    except Exception as e:
        print(f"✗ Error creating sample data: {e}")
        return False

def setup_file_storage():
    """Setup file-based storage"""
    try:
        print("Setting up file-based storage...")
        from migrate_to_files import create_sample_data_files
        create_sample_data_files()
        print("✓ File-based storage setup complete")
        return True
    except Exception as e:
        print(f"✗ Error setting up file storage: {e}")
        return False

def main():
    """Main startup function"""
    print("=" * 50)
    print("SW Labs Management System")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("✗ Error: app.py not found. Please run this script from the project directory.")
        return
    
    # Check dependencies
    if not check_dependencies():
        response = input("Would you like to install dependencies now? (y/n): ")
        if response.lower() == 'y':
            if not install_dependencies():
                return
        else:
            return
    
    # Setup file-based storage
    setup_file_storage()
    
    # Create sample data (for backward compatibility)
    create_sample_data()
    
    print("\nStarting SW Labs Management System...")
    print("Access the application at: http://localhost:5000")
    print("Default admin credentials: admin / admin123")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start the application
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\n✗ Error starting server: {e}")

if __name__ == '__main__':
    main()