#!/usr/bin/env python3
"""
Migration script to convert SQLite database to JSON files
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

def migrate_database():
    """Migrate data from SQLite to JSON files"""
    
    # Create data directory
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Database file path
    db_path = Path('instance/sw_labs.db')
    
    if not db_path.exists():
        print("❌ Database file not found. Please run the application first to create the database.")
        return False
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Starting migration from SQLite to JSON files...")
        
        # Migrate Users
        print("📝 Migrating users...")
        cursor.execute("SELECT id, username, email, password_hash, is_admin, created_at FROM user")
        users = cursor.fetchall()
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'password_hash': user[3],
                'is_admin': bool(user[4]),
                'created_at': user[5]
            })
        
        with open(data_dir / 'users.json', 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2)
        print(f"✅ Migrated {len(users_data)} users")
        
        # Migrate Labs
        print("🏢 Migrating labs...")
        cursor.execute("SELECT id, name, description, location, created_at FROM lab")
        labs = cursor.fetchall()
        
        labs_data = []
        for lab in labs:
            labs_data.append({
                'id': lab[0],
                'name': lab[1],
                'description': lab[2],
                'location': lab[3],
                'created_at': lab[4]
            })
        
        with open(data_dir / 'labs.json', 'w', encoding='utf-8') as f:
            json.dump(labs_data, f, indent=2)
        print(f"✅ Migrated {len(labs_data)} labs")
        
        # Migrate Stations
        print("🖥️ Migrating stations...")
        cursor.execute("SELECT id, name, description, lab_id, is_occupied, occupied_by, occupied_at, created_at FROM station")
        stations = cursor.fetchall()
        
        stations_data = []
        for station in stations:
            stations_data.append({
                'id': station[0],
                'name': station[1],
                'description': station[2],
                'lab_id': station[3],
                'is_occupied': bool(station[4]),
                'occupied_by': station[5],
                'occupied_at': station[6],
                'created_at': station[7]
            })
        
        with open(data_dir / 'stations.json', 'w', encoding='utf-8') as f:
            json.dump(stations_data, f, indent=2)
        print(f"✅ Migrated {len(stations_data)} stations")
        
        # Migrate Devices
        print("💻 Migrating devices...")
        cursor.execute("SELECT id, name, device_type, ip_address, os_info, special_apps, is_online, last_ping, station_id, created_at FROM device")
        devices = cursor.fetchall()
        
        devices_data = []
        for device in devices:
            devices_data.append({
                'id': device[0],
                'name': device[1],
                'device_type': device[2],
                'ip_address': device[3],
                'os_info': device[4],
                'special_apps': device[5],
                'is_online': bool(device[6]),
                'last_ping': device[7],
                'station_id': device[8],
                'created_at': device[9]
            })
        
        with open(data_dir / 'devices.json', 'w', encoding='utf-8') as f:
            json.dump(devices_data, f, indent=2)
        print(f"✅ Migrated {len(devices_data)} devices")
        
        conn.close()
        
        print("\n🎉 Migration completed successfully!")
        print("📁 Data files created in the 'data' directory:")
        print("   - users.json")
        print("   - labs.json")
        print("   - stations.json")
        print("   - devices.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_sample_data_files():
    """Create sample data files if they don't exist"""
    
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Create sample users if users.json doesn't exist
    if not (data_dir / 'users.json').exists():
        print("📝 Creating sample users...")
        sample_users = [
            {
                'id': 1,
                'username': 'admin',
                'email': 'admin@swlabs.com',
                'password_hash': 'pbkdf2:sha256:600000$your-hash-here',  # Will be updated by app
                'is_admin': True,
                'created_at': datetime.utcnow().isoformat()
            }
        ]
        with open(data_dir / 'users.json', 'w', encoding='utf-8') as f:
            json.dump(sample_users, f, indent=2)
    
    # Create sample labs if labs.json doesn't exist
    if not (data_dir / 'labs.json').exists():
        print("🏢 Creating sample labs...")
        sample_labs = [
            {
                'id': 1,
                'name': 'Computer Science Lab',
                'description': 'Main computer science laboratory with development workstations',
                'location': 'Building A, Room 101',
                'created_at': datetime.utcnow().isoformat()
            },
            {
                'id': 2,
                'name': 'Network Lab',
                'description': 'Networking and infrastructure testing laboratory',
                'location': 'Building B, Room 205',
                'created_at': datetime.utcnow().isoformat()
            }
        ]
        with open(data_dir / 'labs.json', 'w', encoding='utf-8') as f:
            json.dump(sample_labs, f, indent=2)
    
    # Create sample stations if stations.json doesn't exist
    if not (data_dir / 'stations.json').exists():
        print("🖥️ Creating sample stations...")
        sample_stations = [
            {
                'id': 1,
                'name': 'Station 1',
                'description': 'Development workstation with dual monitors',
                'lab_id': 1,
                'is_occupied': False,
                'occupied_by': None,
                'occupied_at': None,
                'created_at': datetime.utcnow().isoformat()
            },
            {
                'id': 2,
                'name': 'Station 2',
                'description': 'Testing workstation with specialized software',
                'lab_id': 1,
                'is_occupied': False,
                'occupied_by': None,
                'occupied_at': None,
                'created_at': datetime.utcnow().isoformat()
            }
        ]
        with open(data_dir / 'stations.json', 'w', encoding='utf-8') as f:
            json.dump(sample_stations, f, indent=2)
    
    # Create sample devices if devices.json doesn't exist
    if not (data_dir / 'devices.json').exists():
        print("💻 Creating sample devices...")
        sample_devices = [
            {
                'id': 1,
                'name': 'Dev-PC-01',
                'device_type': 'PC',
                'ip_address': '192.168.1.10',
                'os_info': 'Windows 11 Pro',
                'special_apps': 'Visual Studio, Docker, Git',
                'is_online': False,
                'last_ping': None,
                'station_id': 1,
                'created_at': datetime.utcnow().isoformat()
            },
            {
                'id': 2,
                'name': 'Test-Server-01',
                'device_type': 'Server',
                'ip_address': '192.168.1.20',
                'os_info': 'Ubuntu Server 22.04',
                'special_apps': 'Jenkins, Docker, MySQL',
                'is_online': False,
                'last_ping': None,
                'station_id': 2,
                'created_at': datetime.utcnow().isoformat()
            }
        ]
        with open(data_dir / 'devices.json', 'w', encoding='utf-8') as f:
            json.dump(sample_devices, f, indent=2)
    
    print("✅ Sample data files created!")

if __name__ == '__main__':
    print("=" * 50)
    print("SW Labs Management System - Data Migration")
    print("=" * 50)
    
    # Check if database exists and migrate
    if Path('instance/sw_labs.db').exists():
        migrate_database()
    else:
        print("📁 No existing database found. Creating sample data files...")
        create_sample_data_files()
    
    print("\n🚀 You can now run the application with file-based storage!")
    print("   Run: python run.py") 