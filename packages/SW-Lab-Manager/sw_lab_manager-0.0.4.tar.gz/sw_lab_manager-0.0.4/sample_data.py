#!/usr/bin/env python3
"""
Sample Data Generator for SW Labs Management System
This script populates the database with sample labs, stations, and devices for testing.
"""

from app import app, db, User, Lab, Station, Device
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_sample_data():
    """Create sample data for the SW Labs Management System"""
    
    with app.app_context():
        # Clear existing data (except admin user)
        Device.query.delete()
        Station.query.delete()
        Lab.query.delete()
        User.query.filter(User.username != 'admin').delete()
        
        print("Creating sample data...")
        
        # Create sample users
        users = [
            User(
                username='john_doe',
                email='john.doe@company.com',
                password_hash=generate_password_hash('password123'),
                is_admin=False
            ),
            User(
                username='jane_smith',
                email='jane.smith@company.com',
                password_hash=generate_password_hash('password123'),
                is_admin=False
            ),
            User(
                username='tech_admin',
                email='tech.admin@company.com',
                password_hash=generate_password_hash('admin456'),
                is_admin=True
            )
        ]
        
        for user in users:
            db.session.add(user)
        
        # Create sample labs
        labs = [
            Lab(
                name='Software Development Lab A',
                description='Main software development laboratory with modern equipment',
                location='Building A, Floor 2, Room 201'
            ),
            Lab(
                name='Hardware Testing Lab',
                description='Dedicated lab for hardware testing and validation',
                location='Building B, Floor 1, Room 105'
            ),
            Lab(
                name='Network Security Lab',
                description='Specialized lab for network security testing and training',
                location='Building A, Floor 3, Room 301'
            ),
            Lab(
                name='Mobile Development Lab',
                description='Lab equipped for mobile app development and testing',
                location='Building C, Floor 2, Room 205'
            )
        ]
        
        for lab in labs:
            db.session.add(lab)
        
        db.session.commit()
        
        # Create sample stations
        stations = [
            # Software Development Lab A
            Station(name='Station 1', description='Primary development workstation', lab_id=1),
            Station(name='Station 2', description='Secondary development workstation', lab_id=1),
            Station(name='Station 3', description='Testing and QA workstation', lab_id=1),
            Station(name='Station 4', description='Code review and documentation station', lab_id=1),
            
            # Hardware Testing Lab
            Station(name='Test Bench 1', description='Hardware testing and validation station', lab_id=2),
            Station(name='Test Bench 2', description='Component testing station', lab_id=2),
            Station(name='Assembly Station', description='Hardware assembly and configuration', lab_id=2),
            
            # Network Security Lab
            Station(name='Security Station 1', description='Network security testing workstation', lab_id=3),
            Station(name='Security Station 2', description='Penetration testing station', lab_id=3),
            Station(name='Monitoring Station', description='Network monitoring and analysis', lab_id=3),
            
            # Mobile Development Lab
            Station(name='Mobile Dev 1', description='iOS development station', lab_id=4),
            Station(name='Mobile Dev 2', description='Android development station', lab_id=4),
            Station(name='Testing Station', description='Mobile app testing station', lab_id=4)
        ]
        
        for station in stations:
            db.session.add(station)
        
        db.session.commit()
        
        # Create sample devices
        devices = [
            # Software Development Lab A - Station 1
            Device(
                name='Dev-PC-01',
                device_type='PC',
                ip_address='192.168.1.101',
                os_info='Windows 11 Pro',
                special_apps='Visual Studio 2022, Docker Desktop, Git, Node.js',
                station_id=1
            ),
            Device(
                name='Dev-Server-01',
                device_type='Server',
                ip_address='192.168.1.201',
                os_info='Ubuntu Server 22.04 LTS',
                special_apps='Apache, MySQL, Redis, Jenkins',
                station_id=1
            ),
            
            # Software Development Lab A - Station 2
            Device(
                name='Dev-PC-02',
                device_type='PC',
                ip_address='192.168.1.102',
                os_info='macOS Ventura',
                special_apps='Xcode, Android Studio, VS Code, Postman',
                station_id=2
            ),
            Device(
                name='Dev-Server-02',
                device_type='Server',
                ip_address='192.168.1.202',
                os_info='CentOS 8',
                special_apps='Nginx, PostgreSQL, MongoDB, GitLab',
                station_id=2
            ),
            
            # Software Development Lab A - Station 3
            Device(
                name='QA-PC-01',
                device_type='PC',
                ip_address='192.168.1.103',
                os_info='Windows 10 Pro',
                special_apps='Selenium, JUnit, TestNG, BrowserStack',
                station_id=3
            ),
            
            # Software Development Lab A - Station 4
            Device(
                name='Doc-PC-01',
                device_type='PC',
                ip_address='192.168.1.104',
                os_info='Ubuntu 22.04 Desktop',
                special_apps='LaTeX, Doxygen, Sphinx, Markdown Editor',
                station_id=4
            ),
            
            # Hardware Testing Lab - Test Bench 1
            Device(
                name='Test-PC-01',
                device_type='PC',
                ip_address='192.168.2.101',
                os_info='Windows 11 Pro',
                special_apps='AIDA64, Prime95, 3DMark, CPU-Z',
                station_id=5
            ),
            Device(
                name='Test-Server-01',
                device_type='Server',
                ip_address='192.168.2.201',
                os_info='Windows Server 2022',
                special_apps='Hyper-V, VMware, Performance Monitor',
                station_id=5
            ),
            
            # Hardware Testing Lab - Test Bench 2
            Device(
                name='Test-PC-02',
                device_type='PC',
                ip_address='192.168.2.102',
                os_info='Linux Mint 21',
                special_apps='Stress-ng, Memtest86, Hardinfo',
                station_id=6
            ),
            
            # Hardware Testing Lab - Assembly Station
            Device(
                name='Assembly-PC-01',
                device_type='PC',
                ip_address='192.168.2.103',
                os_info='Windows 10 Pro',
                special_apps='Partition Magic, Clonezilla, Rufus',
                station_id=7
            ),
            
            # Network Security Lab - Security Station 1
            Device(
                name='Sec-PC-01',
                device_type='PC',
                ip_address='192.168.3.101',
                os_info='Kali Linux 2023.1',
                special_apps='Wireshark, Nmap, Metasploit, Burp Suite',
                station_id=8
            ),
            Device(
                name='Sec-Server-01',
                device_type='Server',
                ip_address='192.168.3.201',
                os_info='Ubuntu Server 22.04 LTS',
                special_apps='Snort, Suricata, OSSEC, ELK Stack',
                station_id=8
            ),
            
            # Network Security Lab - Security Station 2
            Device(
                name='Sec-PC-02',
                device_type='PC',
                ip_address='192.168.3.102',
                os_info='Parrot Security OS',
                special_apps='Aircrack-ng, John the Ripper, Hydra',
                station_id=9
            ),
            
            # Network Security Lab - Monitoring Station
            Device(
                name='Monitor-PC-01',
                device_type='PC',
                ip_address='192.168.3.103',
                os_info='Windows 11 Pro',
                special_apps='SolarWinds, PRTG, Nagios, Zabbix',
                station_id=10
            ),
            
            # Mobile Development Lab - Mobile Dev 1
            Device(
                name='Mobile-PC-01',
                device_type='PC',
                ip_address='192.168.4.101',
                os_info='macOS Ventura',
                special_apps='Xcode, iOS Simulator, TestFlight, Instruments',
                station_id=11
            ),
            
            # Mobile Development Lab - Mobile Dev 2
            Device(
                name='Mobile-PC-02',
                device_type='PC',
                ip_address='192.168.4.102',
                os_info='Windows 11 Pro',
                special_apps='Android Studio, Genymotion, ADB, Gradle',
                station_id=12
            ),
            
            # Mobile Development Lab - Testing Station
            Device(
                name='Mobile-Test-PC-01',
                device_type='PC',
                ip_address='192.168.4.103',
                os_info='Ubuntu 22.04 Desktop',
                special_apps='Appium, Robot Framework, BrowserStack, Firebase',
                station_id=13
            )
        ]
        
        for device in devices:
            db.session.add(device)
        
        db.session.commit()
        
        print("Sample data created successfully!")
        print(f"Created {len(users)} users")
        print(f"Created {len(labs)} labs")
        print(f"Created {len(stations)} stations")
        print(f"Created {len(devices)} devices")
        print("\nSample user credentials:")
        print("Username: john_doe, Password: password123")
        print("Username: jane_smith, Password: password123")
        print("Username: tech_admin, Password: admin456 (Admin)")
        print("\nAdmin credentials:")
        print("Username: admin, Password: admin123")

if __name__ == '__main__':
    create_sample_data()