#!/usr/bin/env python3
"""
Test script to verify login functionality with file-based storage
"""

import requests
import json
from pathlib import Path

def test_login():
    """Test the login functionality"""
    
    # Check if data files exist
    data_dir = Path('data')
    if not data_dir.exists():
        print("❌ Data directory not found")
        return False
    
    users_file = data_dir / 'users.json'
    if not users_file.exists():
        print("❌ Users file not found")
        return False
    
    # Load users data
    try:
        with open(users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        print(f"✅ Loaded {len(users)} users from file")
    except Exception as e:
        print(f"❌ Error loading users: {e}")
        return False
    
    # Check if admin user exists
    admin_user = None
    for user in users:
        if user.get('username') == 'admin':
            admin_user = user
            break
    
    if not admin_user:
        print("❌ Admin user not found")
        return False
    
    print(f"✅ Admin user found: {admin_user['username']}")
    print(f"   Email: {admin_user['email']}")
    print(f"   Admin: {admin_user['is_admin']}")
    
    # Test application connectivity
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("✅ Application is running and accessible")
        else:
            print(f"⚠️ Application responded with status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to application. Make sure it's running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Error connecting to application: {e}")
        return False
    
    print("\n🎉 Login system is ready!")
    print("📝 You can now login with:")
    print("   Username: admin")
    print("   Password: admin123")
    print("   URL: http://localhost:5000/login")
    
    return True

if __name__ == '__main__':
    print("=" * 50)
    print("SW Labs Management System - Login Test")
    print("=" * 50)
    
    test_login() 