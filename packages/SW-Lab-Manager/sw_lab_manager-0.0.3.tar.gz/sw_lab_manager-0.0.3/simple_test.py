#!/usr/bin/env python3
"""
Simple test script to verify file-based storage functionality
"""

import json
from pathlib import Path
from werkzeug.security import check_password_hash

def test_file_storage():
    """Test the file-based storage functionality"""
    
    print("=" * 50)
    print("SW Labs Management System - File Storage Test")
    print("=" * 50)
    
    # Check if data directory exists
    data_dir = Path('data')
    if not data_dir.exists():
        print("❌ Data directory not found")
        return False
    
    print("✅ Data directory found")
    
    # Check all required files
    required_files = ['users.json', 'labs.json', 'stations.json', 'devices.json']
    for filename in required_files:
        file_path = data_dir / filename
        if file_path.exists():
            print(f"✅ {filename} exists")
        else:
            print(f"❌ {filename} not found")
            return False
    
    # Test users.json
    try:
        with open(data_dir / 'users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        print(f"✅ Loaded {len(users)} users from users.json")
        
        # Check for admin user
        admin_user = None
        for user in users:
            if user.get('username') == 'admin':
                admin_user = user
                break
        
        if admin_user:
            print("✅ Admin user found in users.json")
            print(f"   Username: {admin_user['username']}")
            print(f"   Email: {admin_user['email']}")
            print(f"   Admin: {admin_user['is_admin']}")
            
            # Test password hash
            test_password = 'admin123'
            if check_password_hash(admin_user['password_hash'], test_password):
                print("✅ Password hash verification works")
            else:
                print("❌ Password hash verification failed")
                return False
        else:
            print("❌ Admin user not found in users.json")
            return False
            
    except Exception as e:
        print(f"❌ Error reading users.json: {e}")
        return False
    
    # Test other files
    for filename in ['labs.json', 'stations.json', 'devices.json']:
        try:
            with open(data_dir / filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ {filename} contains {len(data)} records")
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")
            return False
    
    print("\n🎉 File-based storage test passed!")
    print("📝 The system is ready for use.")
    print("🔑 Login credentials: admin / admin123")
    
    return True

if __name__ == '__main__':
    test_file_storage() 