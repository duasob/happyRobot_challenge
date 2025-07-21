import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "carriers.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with the carriers table"""
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
                status TEXT DEFAULT 'pending',
                final_rate REAL,
                initial_rate REAL,
                transcript TEXT,
                call_duration INTEGER,
                booked_at TEXT
            )
        ''')
        
        # Check if status column exists, if not add it
        cursor.execute("PRAGMA table_info(carriers)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'status' not in columns:
            cursor.execute('ALTER TABLE carriers ADD COLUMN status TEXT DEFAULT "pending"')
            print("Added status column to existing database")
        
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
                'loadboard_rate': 1250.00,
                'notes': 'Fragile electronics - handle with care',
                'weight': 15000.0,
                'commodity_type': 'Electronics',
                'num_of_pieces': 500,
                'miles': 372.0,
                'dimensions': '48x48x96',
                'status': 'pending',
                'final_rate': 1250.00,
                'initial_rate': 1250.00,
                'transcript': 'Sample transcript for LOAD001',
                'call_duration': 3600,
                'booked_at': '2024-01-15 08:00:00'
            },
            {
                'load_id': 'LOAD002',
                'origin': 'Chicago, IL',
                'destination': 'Detroit, MI',
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
                'status': 'calling',
                'final_rate': 1800.00,
                'initial_rate': 1800.00,
                'transcript': 'Sample transcript for LOAD002',
                'call_duration': 2700,
                'booked_at': '2024-01-15 10:30:00'
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
                'status': 'ready',
                'final_rate': 950.00,
                'initial_rate': 950.00,
                'transcript': 'Sample transcript for LOAD003',
                'call_duration': 2100,
                'booked_at': '2024-01-15 06:00:00'
            },
            
        ]
        
        for data in sample_data:
            cursor.execute('''
                INSERT INTO carriers (
                    load_id, origin, destination, pickup_datetime, delivery_datetime,
                    equipment_type, loadboard_rate, notes, weight, commodity_type,
                    num_of_pieces, miles, dimensions, status, final_rate, initial_rate, transcript, call_duration, booked_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('load_id'), data.get('origin'), data.get('destination'),
                data.get('pickup_datetime'), data.get('delivery_datetime'),
                data.get('equipment_type'), data.get('loadboard_rate'), data.get('notes'),
                data.get('weight'), data.get('commodity_type'), data.get('num_of_pieces'),
                data.get('miles'), data.get('dimensions'), data.get('status'),
                data.get('final_rate'), data.get('initial_rate'), data.get('transcript'),
                data.get('call_duration'), data.get('booked_at')
            ))
    
    def get_all_carriers(self) -> List[Dict]:
        """Get all carrier information from the database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This allows accessing columns by name
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT load_id, origin, destination, pickup_datetime, delivery_datetime,
                   equipment_type, loadboard_rate, notes, weight, commodity_type,
                   num_of_pieces, miles, dimensions, status, final_rate, initial_rate, transcript, call_duration, booked_at
            FROM carriers
            ORDER BY pickup_datetime DESC
        ''')
        
        rows = cursor.fetchall()
        carriers = []
        
        for row in rows:
            carrier = dict(row)
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
                   num_of_pieces, miles, dimensions, status, final_rate, initial_rate, transcript, call_duration, booked_at
            FROM carriers
            WHERE load_id = ?
        ''', (load_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
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
                    num_of_pieces, miles, dimensions, status, final_rate, initial_rate, transcript, call_duration, booked_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                carrier_data.get('load_id'), carrier_data.get('origin'), carrier_data.get('destination'),
                carrier_data.get('pickup_datetime'), carrier_data.get('delivery_datetime'),
                carrier_data.get('equipment_type'), carrier_data.get('loadboard_rate'), carrier_data.get('notes'),
                carrier_data.get('weight'), carrier_data.get('commodity_type'), carrier_data.get('num_of_pieces'),
                carrier_data.get('miles'), carrier_data.get('dimensions'), carrier_data.get('status'),
                carrier_data.get('final_rate'), carrier_data.get('initial_rate'), carrier_data.get('transcript'),
                carrier_data.get('call_duration'), carrier_data.get('booked_at')
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
                    commodity_type = ?, num_of_pieces = ?, miles = ?, dimensions = ?, status = ?,
                    final_rate = ?, initial_rate = ?, transcript = ?, call_duration = ?, booked_at = ?
                WHERE load_id = ?
            ''', (
                carrier_data.get('origin'), carrier_data.get('destination'),
                carrier_data.get('pickup_datetime'), carrier_data.get('delivery_datetime'),
                carrier_data.get('equipment_type'), carrier_data.get('loadboard_rate'), carrier_data.get('notes'),
                carrier_data.get('weight'), carrier_data.get('commodity_type'), carrier_data.get('num_of_pieces'),
                carrier_data.get('miles'), carrier_data.get('dimensions'), carrier_data.get('status'),
                carrier_data.get('final_rate'), carrier_data.get('initial_rate'), carrier_data.get('transcript'),
                carrier_data.get('call_duration'), carrier_data.get('booked_at'), load_id
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating carrier: {e}")
            return False
    
    def update_booking_info(self, load_id: str, booking_data: Dict) -> bool:
        """Update booking info for a carrier (set status to 'booked')"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE carriers SET
                    status = 'booked',
                    final_rate = ?,
                    initial_rate = ?,
                    transcript = ?,
                    call_duration = ?,
                    booked_at = ?
                WHERE load_id = ?
            ''', (
                booking_data.get('final_rate'),
                booking_data.get('initial_rate'),
                booking_data.get('transcript'),
                booking_data.get('call_duration'),
                booking_data.get('booked_at'),
                load_id
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating booking info: {e}")
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

# Global database manager instance
db_manager = DatabaseManager() 