import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
import shutil


class DatabaseManager:
    def __init__(self, db_path: str = "carriers.db"):
        # Always reset /tmp/carriers.db to a fresh copy (or an empty file)
        tmp_db = "/tmp/carriers.db"
        project_db = os.path.join(os.getcwd(), db_path)

        # Remove any old tmp copy
        if os.path.exists(tmp_db):
            os.remove(tmp_db)

        # Seed a fresh DB into /tmp
        if os.path.exists(project_db):
            print(f"Seeding fresh DB: copying {project_db} → {tmp_db}")
            shutil.copyfile(project_db, tmp_db)
        else:
            print(f"No bundled DB found; creating new empty DB at {tmp_db}")
            open(tmp_db, "a").close()

        # From here on, always use the tmp copy
        self.db_path = tmp_db
        self.init_database()
    
    def init_database(self):
        """Initialize the database with the carriers table and bookings table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create carriers table with all required fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carriers (
                load_id TEXT PRIMARY KEY,
                origin TEXT,
                destination TEXT,
                pickup_datetime TEXT,
                delivery_datetime TEXT,
                equipment_type TEXT,
                loadboard_rate REAL,
                notes TEXT,
                weight REAL,
                commodity_type TEXT,
                num_of_pieces INTEGER,
                miles REAL,
                dimensions TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Check if status column exists, if not add it
        cursor.execute("PRAGMA table_info(carriers)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'status' not in columns:
            cursor.execute('ALTER TABLE carriers ADD COLUMN status TEXT DEFAULT "pending"')
            print("Added status column to existing database")
        
        # Create bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                load_id TEXT,
                mc_num TEXT,
                final_rate TEXT,
                initial_rate TEXT,
                transcript TEXT,
                sentiment TEXT,
                duration TEXT,
                timestamp TEXT,
                FOREIGN KEY(load_id) REFERENCES carriers(load_id)
            )
        ''')
        
        # Insert sample data if table is empty
        cursor.execute("SELECT COUNT(*) FROM carriers")
        if cursor.fetchone()[0] == 0:
            self.insert_sample_data(cursor)
        
        conn.commit()
        conn.close()
    
    def insert_sample_data(self, cursor):
        """Insert sample carrier data for demonstration"""
        sample_data = [
            {
                'load_id': 'LOAD001',
                'origin': 'Los Angeles, CA',
                'destination': 'Phoenix, AZ',
                'pickup_datetime': '2024-01-15 08:00:00',
                'delivery_datetime': '2024-01-16 14:00:00',
                'equipment_type': 'Dry Van',
                'loadboard_rate': 1400.00,
                'notes': 'Fragile electronics - handle with care',
                'weight': 15000.0,
                'commodity_type': 'Electronics',
                'num_of_pieces': 500,
                'miles': 372.0,
                'dimensions': '48x48x96',
                'status': 'pending'
            },
            {
                'load_id': 'LOAD002',
                'origin': 'San Francisco, CA',
                'destination': 'Seattle, WA',
                'pickup_datetime': '2024-01-15 10:30:00',
                'delivery_datetime': '2024-01-15 18:00:00',
                'equipment_type': 'Reefer',
                'loadboard_rate': 1800.00,
                'notes': 'Temperature controlled - maintain 35-40°F',
                'weight': 22000.0,
                'commodity_type': 'Frozen Foods',
                'num_of_pieces': 1200,
                'miles': 283.0,
                'dimensions': '53x102x102',
                'status': 'pending'
            },
            {
                'load_id': 'LOAD003',
                'origin': 'Dallas, TX',
                'destination': 'Houston, TX',
                'pickup_datetime': '2024-01-15 06:00:00',
                'delivery_datetime': '2024-01-15 12:00:00',
                'equipment_type': 'Flatbed',
                'loadboard_rate': 950.00,
                'notes': 'Heavy machinery - secure properly',
                'weight': 45000.0,
                'commodity_type': 'Industrial Equipment',
                'num_of_pieces': 8,
                'miles': 239.0,
                'dimensions': '48x96x120',
                'status': 'pending'
            },
            
        ]
        
        for data in sample_data:
            cursor.execute('''
                INSERT INTO carriers (
                    load_id, origin, destination, pickup_datetime, delivery_datetime,
                    equipment_type, loadboard_rate, notes, weight, commodity_type,
                    num_of_pieces, miles, dimensions, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['load_id'], data['origin'], data['destination'],
                data['pickup_datetime'], data['delivery_datetime'],
                data['equipment_type'], data['loadboard_rate'], data['notes'],
                data['weight'], data['commodity_type'], data['num_of_pieces'],
                data['miles'], data['dimensions'], data['status']
            ))
    
    def get_all_carriers(self) -> List[Dict]:
        """Get all carrier information from the database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This allows accessing columns by name
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT load_id, origin, destination, pickup_datetime, delivery_datetime,
                   equipment_type, loadboard_rate, notes, weight, commodity_type,
                   num_of_pieces, miles, dimensions, status
            FROM carriers
            ORDER BY pickup_datetime DESC
        ''')
        
        rows = cursor.fetchall()
        carriers = []
        
        for row in rows:
            carrier = {
                'load_id': row['load_id'],
                'origin': row['origin'],
                'destination': row['destination'],
                'pickup_datetime': row['pickup_datetime'],
                'delivery_datetime': row['delivery_datetime'],
                'equipment_type': row['equipment_type'],
                'loadboard_rate': row['loadboard_rate'],
                'notes': row['notes'],
                'weight': row['weight'],
                'commodity_type': row['commodity_type'],
                'num_of_pieces': row['num_of_pieces'],
                'miles': row['miles'],
                'dimensions': row['dimensions'],
                'status': row['status']
            }
            carriers.append(carrier)
        
        conn.close()
        return carriers
    
    def get_carrier_by_id(self, load_id: str) -> Optional[Dict]:
        """Get a specific carrier by load_id"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT load_id, origin, destination, pickup_datetime, delivery_datetime,
                   equipment_type, loadboard_rate, notes, weight, commodity_type,
                   num_of_pieces, miles, dimensions, status
            FROM carriers
            WHERE load_id = ?
        ''', (load_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'load_id': row['load_id'],
                'origin': row['origin'],
                'destination': row['destination'],
                'pickup_datetime': row['pickup_datetime'],
                'delivery_datetime': row['delivery_datetime'],
                'equipment_type': row['equipment_type'],
                'loadboard_rate': row['loadboard_rate'],
                'notes': row['notes'],
                'weight': row['weight'],
                'commodity_type': row['commodity_type'],
                'num_of_pieces': row['num_of_pieces'],
                'miles': row['miles'],
                'dimensions': row['dimensions'],
                'status': row['status']
            }
        return None
    
    def add_carrier(self, carrier_data: Dict) -> bool:
        """Add a new carrier to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO carriers (
                    load_id, origin, destination, pickup_datetime, delivery_datetime,
                    equipment_type, loadboard_rate, notes, weight, commodity_type,
                    num_of_pieces, miles, dimensions, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                carrier_data['load_id'], carrier_data['origin'], carrier_data['destination'],
                carrier_data['pickup_datetime'], carrier_data['delivery_datetime'],
                carrier_data['equipment_type'], carrier_data['loadboard_rate'], carrier_data['notes'],
                carrier_data['weight'], carrier_data['commodity_type'], carrier_data['num_of_pieces'],
                carrier_data['miles'], carrier_data['dimensions'], carrier_data['status']
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding carrier: {e}")
            return False
    
    def update_carrier(self, load_id: str, carrier_data: Dict) -> bool:
        """Update an existing carrier in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE carriers SET
                    origin = ?, destination = ?, pickup_datetime = ?, delivery_datetime = ?,
                    equipment_type = ?, loadboard_rate = ?, notes = ?, weight = ?,
                    commodity_type = ?, num_of_pieces = ?, miles = ?, dimensions = ?, status = ?
                WHERE load_id = ?
            ''', (
                carrier_data['origin'], carrier_data['destination'],
                carrier_data['pickup_datetime'], carrier_data['delivery_datetime'],
                carrier_data['equipment_type'], carrier_data['loadboard_rate'], carrier_data['notes'],
                carrier_data['weight'], carrier_data['commodity_type'], carrier_data['num_of_pieces'],
                carrier_data['miles'], carrier_data['dimensions'], carrier_data['status'], load_id
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating carrier: {e}")
            return False
    
    def delete_carrier(self, load_id: str) -> bool:
        """Delete a carrier from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM carriers WHERE load_id = ?', (load_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting carrier: {e}")
            return False

    def add_booking(self, booking_data: Dict) -> bool:
        """Add a new booking to the bookings table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bookings (
                    load_id, mc_num, final_rate, initial_rate, transcript, sentiment, duration, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                booking_data['load_id'],
                booking_data['mc_num'],
                booking_data['final_rate'],
                booking_data['initial_rate'],
                booking_data['transcript'],
                booking_data['sentiment'],
                booking_data['duration'],
                booking_data['timestamp']
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding booking: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager("carriers.db") 