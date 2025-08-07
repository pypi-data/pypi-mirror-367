from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import threading
import time
from ping3 import ping
import psutil
import json
import csv
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# File-based storage configuration
DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)

USERS_FILE = DATA_DIR / 'users.json'
LABS_FILE = DATA_DIR / 'labs.json'
STATIONS_FILE = DATA_DIR / 'stations.json'
DEVICES_FILE = DATA_DIR / 'devices.json'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Data Models (for template compatibility)
class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.email = user_data['email']
        self.password_hash = user_data['password_hash']
        self.is_admin = user_data['is_admin']
        self.created_at = datetime.fromisoformat(user_data['created_at'])

class Lab:
    def __init__(self, lab_data):
        self.id = lab_data['id']
        self.name = lab_data['name']
        self.description = lab_data.get('description', '')
        self.location = lab_data.get('location', '')
        self.created_at = datetime.fromisoformat(lab_data['created_at'])
        self.stations = []

class Station:
    def __init__(self, station_data):
        self.id = station_data['id']
        self.name = station_data['name']
        self.description = station_data.get('description', '')
        self.lab_id = station_data['lab_id']
        self.is_occupied = station_data['is_occupied']
        self.occupied_by = station_data.get('occupied_by')
        self.occupied_at = datetime.fromisoformat(station_data['occupied_at']) if station_data.get('occupied_at') else None
        self.occupied_until = datetime.fromisoformat(station_data['occupied_until']) if station_data.get('occupied_until') else None
        self.is_functional = station_data.get('is_functional', True)
        self.created_at = datetime.fromisoformat(station_data['created_at'])
        self.devices = []
        self.lab = None  # Will be set when needed

class Device:
    def __init__(self, device_data):
        self.id = device_data['id']
        self.name = device_data['name']
        self.device_type = device_data['device_type']
        self.ip_address = device_data['ip_address']
        self.os_info = device_data.get('os_info', '')
        self.special_apps = device_data.get('special_apps', '')
        self.is_online = device_data.get('is_online', False)
        self.last_ping = datetime.fromisoformat(device_data['last_ping']) if device_data.get('last_ping') else None
        self.station_id = device_data['station_id']
        self.created_at = datetime.fromisoformat(device_data['created_at'])
        self.station = None  # Will be set when needed

# File-based storage functions
def load_json_data(filename):
    """Load data from JSON file"""
    if filename.exists():
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_json_data(filename, data):
    """Save data to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving to {filename}: {e}")
        return False

def get_next_id(data_list):
    """Get next available ID for a list of objects"""
    if not data_list:
        return 1
    return max(item.get('id', 0) for item in data_list) + 1

# File-based user management
def get_user_by_username(username):
    """Get user by username from file storage"""
    users = load_json_data(USERS_FILE)
    for user in users:
        if user.get('username') == username:
            return user
    return None

# File-based data management functions
def get_all_labs():
    """Get all labs from file storage"""
    labs_data = load_json_data(LABS_FILE)
    stations_data = load_json_data(STATIONS_FILE)
    devices_data = load_json_data(DEVICES_FILE)
    
    labs = []
    for lab_data in labs_data:
        lab = Lab(lab_data)
        
        # Get stations for this lab
        for station_data in stations_data:
            if station_data['lab_id'] == lab.id:
                station = Station(station_data)
                
                # Get devices for this station
                for device_data in devices_data:
                    if device_data['station_id'] == station.id:
                        device = Device(device_data)
                        station.devices.append(device)
                
                lab.stations.append(station)
        
        labs.append(lab)
    return labs

def get_lab_by_id(lab_id):
    """Get a specific lab by ID"""
    labs = get_all_labs()
    for lab in labs:
        if lab.id == lab_id:
            return lab
    return None

def get_station_by_id(station_id):
    """Get a specific station by ID"""
    stations_data = load_json_data(STATIONS_FILE)
    devices_data = load_json_data(DEVICES_FILE)
    labs_data = load_json_data(LABS_FILE)
    
    for station_data in stations_data:
        if station_data['id'] == station_id:
            station = Station(station_data)
            
            # Get lab for this station
            for lab_data in labs_data:
                if lab_data['id'] == station.lab_id:
                    station.lab = Lab(lab_data)
                    break
            
            # Get devices for this station
            for device_data in devices_data:
                if device_data['station_id'] == station.id:
                    device = Device(device_data)
                    station.devices.append(device)
            
            return station
    return None

def get_all_stations():
    """Get all stations from file storage"""
    stations_data = load_json_data(STATIONS_FILE)
    devices_data = load_json_data(DEVICES_FILE)
    labs_data = load_json_data(LABS_FILE)
    
    stations = []
    for station_data in stations_data:
        station = Station(station_data)
        
        # Get lab for this station
        for lab_data in labs_data:
            if lab_data['id'] == station.lab_id:
                station.lab = Lab(lab_data)
                break
        
        # Get devices for this station
        for device_data in devices_data:
            if device_data['station_id'] == station.id:
                device = Device(device_data)
                station.devices.append(device)
        
        stations.append(station)
    return stations

def get_all_devices():
    """Get all devices from file storage"""
    devices_data = load_json_data(DEVICES_FILE)
    stations_data = load_json_data(STATIONS_FILE)
    
    devices = []
    for device_data in devices_data:
        device = Device(device_data)
        
        # Get station for this device
        for station_data in stations_data:
            if station_data['id'] == device.station_id:
                device.station = Station(station_data)
                break
        
        devices.append(device)
    return devices

def get_device_by_id(device_id):
    """Get a specific device by ID"""
    devices_data = load_json_data(DEVICES_FILE)
    for device_data in devices_data:
        if device_data['id'] == device_id:
            return Device(device_data)
    return None

def get_all_users():
    """Get all users from file storage"""
    users_data = load_json_data(USERS_FILE)
    return [User(user_data) for user_data in users_data]

def create_user(username, email, password, is_admin=False):
    """Create a new user in file storage"""
    users = load_json_data(USERS_FILE)
    user_id = get_next_id(users)
    
    new_user = {
        'id': user_id,
        'username': username,
        'email': email,
        'password_hash': generate_password_hash(password),
        'is_admin': is_admin,
        'created_at': datetime.now().isoformat()
    }
    
    users.append(new_user)
    if save_json_data(USERS_FILE, users):
        return new_user
    return None

def get_user_by_id(user_id):
    """Get user by ID from file storage"""
    users = load_json_data(USERS_FILE)
    for user in users:
        if user.get('id') == user_id:
            return user
    return None

@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(int(user_id))
    if user_data:
        return User(user_data)
    return None

# Auto-release monitoring thread
def auto_release_stations():
    """Automatically release stations whose time has expired"""
    while True:
        try:
            stations_data = load_json_data(STATIONS_FILE)
            current_time = datetime.now()
            updated = False
            
            for station_data in stations_data:
                if (station_data['is_occupied'] and 
                    station_data['occupied_until'] and 
                    datetime.fromisoformat(station_data['occupied_until']) <= current_time):
                    
                    # Auto-release the station
                    station_data['is_occupied'] = False
                    station_data['occupied_by'] = None
                    station_data['occupied_at'] = None
                    station_data['occupied_until'] = None
                    updated = True
                    print(f"Auto-released station {station_data['name']} (ID: {station_data['id']})")
            
            if updated:
                save_json_data(STATIONS_FILE, stations_data)
                
        except Exception as e:
            print(f"Error in auto-release monitoring: {e}")
        
        time.sleep(60)  # Check every minute

# Ping monitoring thread
def ping_devices():
    while True:
        try:
            devices_data = load_json_data(DEVICES_FILE)
            updated = False
            
            for device_data in devices_data:
                try:
                    result = ping(device_data['ip_address'], timeout=2)
                    device_data['is_online'] = isinstance(result, (int, float))
                    device_data['last_ping'] = datetime.now().isoformat()
                    updated = True
                except:
                    device_data['is_online'] = False
                    device_data['last_ping'] = datetime.now().isoformat()
                    updated = True
            
            if updated:
                save_json_data(DEVICES_FILE, devices_data)
                
        except Exception as e:
            print(f"Error in ping monitoring: {e}")
        
        time.sleep(30)  # Ping every 30 seconds

# Routes
@app.route('/')
def index():
    labs = get_all_labs()
    
    # Calculate statistics
    total_labs = len(labs)
    total_stations = sum(len(lab.stations) for lab in labs)
    available_stations = sum(len([s for s in lab.stations if not s.is_occupied]) for lab in labs)
    occupied_stations = sum(len([s for s in lab.stations if s.is_occupied]) for lab in labs)
    
    return render_template('index.html', 
                         labs=labs, 
                         total_labs=total_labs,
                         total_stations=total_stations,
                         available_stations=available_stations,
                         occupied_stations=occupied_stations)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user_data = get_user_by_username(username)
        if user_data:
            user = User(user_data)
            if check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password')
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/lab/<int:lab_id>')
def lab_detail(lab_id):
    lab = get_lab_by_id(lab_id)
    if not lab:
        flash('Lab not found')
        return redirect(url_for('index'))
    return render_template('lab_detail.html', lab=lab)

@app.route('/station/<int:station_id>')
def station_detail(station_id):
    station = get_station_by_id(station_id)
    if not station:
        flash('Station not found')
        return redirect(url_for('index'))
    
    occupied_by_user = None
    if station.is_occupied and station.occupied_by:
        user_data = get_user_by_id(int(station.occupied_by))
        if user_data:
            occupied_by_user = User(user_data)
            
    return render_template('station_detail.html', station=station, occupied_by_user=occupied_by_user)

@app.route('/occupy_station/<int:station_id>', methods=['GET', 'POST'])
@login_required
def occupy_station(station_id):
    if request.method == 'GET':
        # Show occupation form with scheduler
        station = get_station_by_id(station_id)
        if not station:
            flash('Station not found')
            return redirect(url_for('index'))
        return render_template('occupy_station.html', station=station)
    
    # Handle POST request
    station = get_station_by_id(station_id)
    if not station:
        flash('Station not found')
        return redirect(url_for('index'))
    
    if station.is_occupied:
        flash('Station is already occupied')
        return redirect(url_for('station_detail', station_id=station_id))
    
    # Get occupation duration/end time
    occupation_type = request.form.get('occupation_type')
    occupation_until = None
    
    if occupation_type == 'duration':
        duration_hours = int(request.form.get('duration_hours', 1))
        occupation_until = datetime.now() + timedelta(hours=duration_hours)
    elif occupation_type == 'until':
        occupation_until_str = request.form.get('occupation_until')
        if occupation_until_str:
            occupation_until = datetime.fromisoformat(occupation_until_str.replace('T', ' '))
    
    # Update file-based storage
    stations_data = load_json_data(STATIONS_FILE)
    for station_data in stations_data:
        if station_data['id'] == station_id:
            station_data['is_occupied'] = True
            station_data['occupied_by'] = current_user.id
            station_data['occupied_at'] = datetime.now().isoformat()
            station_data['occupied_until'] = occupation_until.isoformat() if occupation_until else None
            break
    save_json_data(STATIONS_FILE, stations_data)
    
    if occupation_until:
        flash(f'Station occupied successfully until {occupation_until.strftime("%Y-%m-%d %H:%M")}')
    else:
        flash('Station occupied successfully (no time limit)')
    
    return redirect(url_for('station_detail', station_id=station_id))

@app.route('/release_station/<int:station_id>', methods=['POST'])
@login_required
def release_station(station_id):
    station = get_station_by_id(station_id)
    if not station:
        flash('Station not found')
        return redirect(url_for('index'))
    
    if not station.is_occupied:
        flash('Station is not occupied')
        return redirect(url_for('station_detail', station_id=station_id))
    
    if station.occupied_by != current_user.id and not current_user.is_admin:
        flash('You can only release stations you occupied')
        return redirect(url_for('station_detail', station_id=station_id))
    
    # Update file-based storage
    stations_data = load_json_data(STATIONS_FILE)
    for station_data in stations_data:
        if station_data['id'] == station_id:
            station_data['is_occupied'] = False
            station_data['occupied_by'] = None
            station_data['occupied_at'] = None
            station_data['occupied_until'] = None
            break
    save_json_data(STATIONS_FILE, stations_data)
    
    flash('Station released successfully')
    return redirect(url_for('station_detail', station_id=station_id))

# Admin routes
@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    labs = get_all_labs()
    stations = get_all_stations()
    devices = get_all_devices()
    users = get_all_users()
    
    return render_template('admin_panel.html', labs=labs, stations=stations, devices=devices, users=users)

@app.route('/admin/lab/add', methods=['GET', 'POST'])
@login_required
def add_lab():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        
        # Add to file-based storage
        labs_data = load_json_data(LABS_FILE)
        lab_id = get_next_id(labs_data)
        
        new_lab = {
            'id': lab_id,
            'name': name,
            'description': description,
            'location': location,
            'created_at': datetime.now().isoformat()
        }
        
        labs_data.append(new_lab)
        save_json_data(LABS_FILE, labs_data)
        
        flash('Lab added successfully')
        return redirect(url_for('admin_panel'))
    
    return render_template('add_lab.html')

@app.route('/admin/station/add', methods=['GET', 'POST'])
@login_required
def add_station():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        lab_id = int(request.form['lab_id'])
        is_functional = 'is_functional' in request.form
        
        # Add to file-based storage
        stations_data = load_json_data(STATIONS_FILE)
        station_id = get_next_id(stations_data)
        
        new_station = {
            'id': station_id,
            'name': name,
            'description': description,
            'lab_id': lab_id,
            'is_occupied': False,
            'occupied_by': None,
            'occupied_at': None,
            'occupied_until': None,
            'is_functional': is_functional,
            'created_at': datetime.now().isoformat()
        }
        
        stations_data.append(new_station)
        save_json_data(STATIONS_FILE, stations_data)
        
        flash('Station added successfully')
        return redirect(url_for('admin_panel'))
    
    labs = get_all_labs()
    return render_template('add_station.html', labs=labs)

@app.route('/admin/station/<int:station_id>/toggle_functional', methods=['POST'])
@login_required
def toggle_station_functional(station_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    # Update file-based storage
    stations_data = load_json_data(STATIONS_FILE)
    station_name = None
    for station_data in stations_data:
        if station_data['id'] == station_id:
            station_data['is_functional'] = not station_data['is_functional']
            station_name = station_data['name']
            break
    
    if station_name:
        save_json_data(STATIONS_FILE, stations_data)
        status = "functional" if station_data['is_functional'] else "non-functional"
        flash(f'Station {station_name} marked as {status}')
    else:
        flash('Station not found')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/device/add', methods=['GET', 'POST'])
@login_required
def add_device():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        device_type = request.form['device_type']
        ip_address = request.form['ip_address']
        os_info = request.form['os_info']
        special_apps = request.form['special_apps']
        station_id = int(request.form['station_id'])
        
        # Add to file-based storage
        devices_data = load_json_data(DEVICES_FILE)
        device_id = get_next_id(devices_data)
        
        new_device = {
            'id': device_id,
            'name': name,
            'device_type': device_type,
            'ip_address': ip_address,
            'os_info': os_info,
            'special_apps': special_apps,
            'station_id': station_id,
            'is_online': False,
            'last_ping': None,
            'created_at': datetime.now().isoformat()
        }
        
        devices_data.append(new_device)
        save_json_data(DEVICES_FILE, devices_data)
        
        flash('Device added successfully')
        return redirect(url_for('admin_panel'))
    
    stations = get_all_stations()
    return render_template('add_device.html', stations=stations)

@app.route('/admin/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_admin = 'is_admin' in request.form
        
        # Add to file-based storage
        users_data = load_json_data(USERS_FILE)
        user_id = get_next_id(users_data)
        
        new_user = {
            'id': user_id,
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'is_admin': is_admin,
            'created_at': datetime.now().isoformat()
        }
        
        users_data.append(new_user)
        save_json_data(USERS_FILE, users_data)
        
        flash('User added successfully')
        return redirect(url_for('admin_panel'))
    
    return render_template('add_user.html')

@app.route('/admin/lab/<int:lab_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lab(lab_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))

    labs_data = load_json_data(LABS_FILE)
    lab_data = next((lab for lab in labs_data if lab['id'] == lab_id), None)

    if not lab_data:
        flash('Lab not found')
        return redirect(url_for('admin_panel'))

    if request.method == 'POST':
        lab_data['name'] = request.form['name']
        lab_data['description'] = request.form['description']
        lab_data['location'] = request.form['location']
        save_json_data(LABS_FILE, labs_data)
        flash('Lab updated successfully')
        return redirect(url_for('admin_panel'))

    return render_template('edit_lab.html', lab=lab_data)

@app.route('/admin/station/<int:station_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_station(station_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))

    stations_data = load_json_data(STATIONS_FILE)
    station_data = next((station for station in stations_data if station['id'] == station_id), None)

    if not station_data:
        flash('Station not found')
        return redirect(url_for('admin_panel'))

    if request.method == 'POST':
        station_data['name'] = request.form['name']
        station_data['description'] = request.form['description']
        station_data['lab_id'] = int(request.form['lab_id'])
        station_data['is_functional'] = 'is_functional' in request.form
        save_json_data(STATIONS_FILE, stations_data)
        flash('Station updated successfully')
        return redirect(url_for('admin_panel'))

    labs = get_all_labs()
    return render_template('edit_station.html', station=station_data, labs=labs)

@app.route('/admin/device/<int:device_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_device(device_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))

    devices_data = load_json_data(DEVICES_FILE)
    device_data = next((device for device in devices_data if device['id'] == device_id), None)

    if not device_data:
        flash('Device not found')
        return redirect(url_for('admin_panel'))

    if request.method == 'POST':
        device_data['name'] = request.form['name']
        device_data['device_type'] = request.form['device_type']
        device_data['ip_address'] = request.form['ip_address']
        device_data['os_info'] = request.form['os_info']
        device_data['special_apps'] = request.form['special_apps']
        device_data['station_id'] = int(request.form['station_id'])
        save_json_data(DEVICES_FILE, devices_data)
        flash('Device updated successfully')
        return redirect(url_for('admin_panel'))

    stations = get_all_stations()
    return render_template('edit_device.html', device=device_data, stations=stations)

@app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))

    users_data = load_json_data(USERS_FILE)
    user_data = next((user for user in users_data if user['id'] == user_id), None)

    if not user_data:
        flash('User not found')
        return redirect(url_for('admin_panel'))

    if request.method == 'POST':
        user_data['username'] = request.form['username']
        user_data['email'] = request.form['email']
        if request.form['password']:
            user_data['password_hash'] = generate_password_hash(request.form['password'])
        user_data['is_admin'] = 'is_admin' in request.form
        save_json_data(USERS_FILE, users_data)
        flash('User updated successfully')
        return redirect(url_for('admin_panel'))

    return render_template('edit_user.html', user=user_data)

@app.route('/admin/lab/<int:lab_id>/delete', methods=['POST'])
@login_required
def delete_lab(lab_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))

    labs_data = load_json_data(LABS_FILE)
    labs_data = [lab for lab in labs_data if lab['id'] != lab_id]
    save_json_data(LABS_FILE, labs_data)
    
    flash('Lab deleted successfully')
    return redirect(url_for('admin_panel'))

@app.route('/admin/station/<int:station_id>/delete', methods=['POST'])
@login_required
def delete_station(station_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))

    stations_data = load_json_data(STATIONS_FILE)
    stations_data = [station for station in stations_data if station['id'] != station_id]
    save_json_data(STATIONS_FILE, stations_data)
    
    flash('Station deleted successfully')
    return redirect(url_for('admin_panel'))

@app.route('/admin/device/<int:device_id>/delete', methods=['POST'])
@login_required
def delete_device(device_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))

    devices_data = load_json_data(DEVICES_FILE)
    devices_data = [device for device in devices_data if device['id'] != device_id]
    save_json_data(DEVICES_FILE, devices_data)
    
    flash('Device deleted successfully')
    return redirect(url_for('admin_panel'))

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))

    users_data = load_json_data(USERS_FILE)
    users_data = [user for user in users_data if user['id'] != user_id]
    save_json_data(USERS_FILE, users_data)
    
    flash('User deleted successfully')
    return redirect(url_for('admin_panel'))

# API routes for AJAX updates
@app.route('/api/device_status')
def device_status():
    devices_data = load_json_data(DEVICES_FILE)
    status_data = []
    
    for device_data in devices_data:
        status_data.append({
            'id': device_data['id'],
            'name': device_data['name'],
            'is_online': device_data.get('is_online', False),
            'last_ping': device_data.get('last_ping')
        })
    
    return jsonify(status_data)

@app.route('/api/all_data')
def all_data():
    labs = get_all_labs()
    stations = get_all_stations()
    devices = get_all_devices()
    users = get_all_users()

    labs_data = [{'id': lab.id, 'name': lab.name, 'location': lab.location, 'stations': len(lab.stations), 'created_at': lab.created_at.strftime('%Y-%m-%d')} for lab in labs]
    stations_data = [{'id': station.id, 'name': station.name, 'lab': station.lab.name, 'is_functional': station.is_functional, 'is_occupied': station.is_occupied, 'occupied_until': station.occupied_until.strftime('%H:%M') if station.occupied_until else None, 'devices': len(station.devices), 'created_at': station.created_at.strftime('%Y-%m-%d')} for station in stations]
    devices_data = [{'id': device.id, 'name': device.name, 'device_type': device.device_type, 'ip_address': device.ip_address, 'station': device.station.name, 'is_online': device.is_online, 'created_at': device.created_at.strftime('%Y-%m-%d')} for device in devices]
    users_data = [{'id': user.id, 'username': user.username, 'email': user.email, 'is_admin': user.is_admin, 'created_at': user.created_at.strftime('%Y-%m-%d')} for user in users]

    return jsonify({
        'labs': labs_data,
        'stations': stations_data,
        'devices': devices_data,
        'users': users_data
    })

# Start monitoring threads
ping_thread = threading.Thread(target=ping_devices, daemon=True)
ping_thread.start()

auto_release_thread = threading.Thread(target=auto_release_stations, daemon=True)
auto_release_thread.start()

if __name__ == '__main__':
    # Create admin user in file storage if none exists
    admin_data = get_user_by_username('admin')
    if not admin_data:
        create_user('admin', 'admin@swlabs.com', 'admin123', is_admin=True)
        print("✓ Admin user created in file storage")
    
    app.run(debug=True, host='0.0.0.0', port=5000)