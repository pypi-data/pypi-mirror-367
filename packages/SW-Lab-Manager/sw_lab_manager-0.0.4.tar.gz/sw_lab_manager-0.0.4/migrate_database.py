#!/usr/bin/env python3
"""
Database Migration Script
Adds missing columns to the Station table for scheduler and functional status
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Add missing columns to the Station table"""
    db_path = Path('instance/sw_labs.db')
    
    if not db_path.exists():
        print("Database file not found. Creating new database...")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(station)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns
        if 'occupied_until' not in columns:
            print("Adding occupied_until column...")
            cursor.execute("ALTER TABLE station ADD COLUMN occupied_until DATETIME")
        
        if 'is_functional' not in columns:
            print("Adding is_functional column...")
            cursor.execute("ALTER TABLE station ADD COLUMN is_functional BOOLEAN DEFAULT 1")
        
        # Commit changes
        conn.commit()
        print("✓ Database migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database() 