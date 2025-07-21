from flask import Flask, request, jsonify, render_template
import os
import json
import sys
import math
import requests
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Add the parent directory to the path so we can import database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database manager
from database import DatabaseManager

app = Flask(__name__)

# Initialize database manager
db_manager = DatabaseManager()

# Your API key from environment variable
API_KEY = os.environ.get("WEBHOOK_API_KEY", "CHANGE_ME")

class DistanceCalculator:
    def __init__(self):
        self.geocoding_url = "https://nominatim.openstreetmap.org/search"
        
    def geocode_city(self, city_name: str) -> Optional[Tuple[float, float]]:
        """Convert city name to coordinates."""
        try:
            params = {
                'q': city_name,
                'format': 'json',
                'limit': 1
            }
            
            response = requests.get(self.geocoding_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return (lat, lon)
            return None
            
        except Exception as e:
            return None
    
    def calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates."""
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in miles
        r = 3959
        
        return c * r

# Initialize distance calculator
distance_calc = DistanceCalculator()

@app.before_request
def enforce_api_key():
    # Allow public access to the config endpoint and favicon only
    if request.path in ["/api/public_config", "/favicon.ico"]:
        return
    if request.path.startswith("/static/"):
        return
    # All /api/webhook requests require API key (no exceptions)
    if request.path.startswith("/api/webhook"):
        key = (
            request.headers.get("X-API-KEY") or 
            request.headers.get("x-api-key") or
            request.args.get("api_key") or
            request.args.get("key")
        )
        if not key or key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        else:
            return
    # All other endpoints (including /, /dashboard, /carriers/api/carriers) require API key
    key = (
        request.headers.get("X-API-KEY") or 
        request.headers.get("x-api-key") or
        request.args.get("api_key") or
        request.args.get("key")
    )
    if not key or key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

@app.route("/webhook/", methods=["GET", "POST"])
def webhook():
    """Webhook endpoint for receiving events."""
    if request.method == "GET":
        # Get query parameters
        params = dict(request.args)
        load_id = params.get('load_id')
        city = params.get('city')
        
        if city:
            # Find closest load to city
            result = find_closest_load_to_city(city)
            return jsonify(result)
        elif load_id:
            # Return specific carrier data
            carrier = db_manager.get_carrier_by_id(load_id)
            if carrier:
                return jsonify({
                    "status": "webhook_active",
                    "message": f"Carrier data for load {load_id}",
                    "timestamp": "2024-01-01T12:00:00Z",
                    "carrier": carrier,
                    "received_params": params
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": f"Carrier with load_id {load_id} not found",
                    "timestamp": "2024-01-01T12:00:00Z",
                    "received_params": params
                }), 404
        else:
            # Return all carriers data
            carriers = db_manager.get_all_carriers()
            return jsonify({
                "status": "webhook_active",
                "message": "All carriers data",
                "timestamp": "2024-01-01T12:00:00Z",
                "carriers": carriers,
                "count": len(carriers),
                "received_params": params
            }), 200
    
    elif request.method == "POST":
        payload = request.get_json(force=True, silent=True)
        print("[DEBUG] Received POST to /api/webhook/")
        print("[DEBUG] Raw payload:", payload)
        if not payload:
            print("[DEBUG] Invalid JSON payload received.")
            return jsonify({"error": "Invalid JSON"}), 400

        # New booking payload fields
        mc_num = payload.get('mc_num')
        chosen_id = payload.get('chosen_id')
        final_rate = payload.get('final_rate')
        initial_rate = payload.get('initial_rate')
        transcript = payload.get('transcript')
        sentiment = payload.get('sentiment')
        duration = payload.get('duration')
        timestamp = datetime.utcnow().isoformat()

        # Validate required fields
        if not mc_num or not chosen_id:
            return jsonify({"error": "Missing required field: mc_num or chosen_id"}), 400

        # Find the carrier
        carrier = db_manager.get_carrier_by_id(chosen_id)
        if not carrier:
            return jsonify({"error": f"Carrier with load_id {chosen_id} not found"}), 404

        # Update carrier status to 'booked'
        carrier['status'] = 'booked'
        db_manager.update_carrier(chosen_id, carrier)
        # Debug: print all carrier statuses after update
        all_carriers_debug = db_manager.get_all_carriers()
        print('[DEBUG] All carriers after booking:')
        for c in all_carriers_debug:
            print(f"[DEBUG] {c['load_id']}: {c['status']}")

        # Store booking info
        booking_data = {
            'load_id': chosen_id,
            'mc_num': mc_num,
            'final_rate': final_rate,
            'initial_rate': initial_rate,
            'transcript': transcript,
            'sentiment': sentiment,
            'duration': duration,
            'timestamp': timestamp
        }
        db_manager.add_booking(booking_data)

        response_data = {
            "status": "booked",
            "message": "Booking received and load marked as booked.",
            "carrier": carrier,
            "booking": booking_data
        }
        print(f"[DEBUG] Response data: {response_data}")
        print("=" * 50)
        return jsonify(response_data), 200

@app.route("/carriers/api/carriers", methods=["GET", "POST"])
def carriers():
    """Carriers API endpoint."""
    if request.method == "GET":
        # Return carriers data from database
        carriers = db_manager.get_all_carriers()
        print('[DEBUG] /carriers/api/carriers called. Statuses:')
        for c in carriers:
            print(f"[DEBUG] {c['load_id']}: {c['status']}")
        params = dict(request.args)
        
        return jsonify({
            "success": True,
            "carriers": carriers,
            "count": len(carriers),
            "params_received": params
        })
    
    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        params = dict(request.args)
        
        # TODO: Add carrier to database
        return jsonify({
            "success": True,
            "message": "Carrier added successfully",
            "params_received": params
        })

@app.route("/")
def home():
    """Home page."""
    return jsonify({
        "message": "Webhook API is running",
        "endpoints": {
            "webhook": "/webhook/",
            "carriers": "/carriers/api/carriers",
            "closest_load": "/distance/closest?city=City, State",
            "load_details": "/distance/load/<load_id>"
        },
        "authentication": {
            "headers": "Use X-API-KEY header for POST requests",
            "params": "Use api_key parameter for POST requests",
            "api_key": "UBNfljhgZwVGTIIXMsgH27EQHz4WULkX29k3dnsN8r0"
        },
        "examples": {
            "get_all_carriers": "GET /webhook/",
            "get_specific_carrier": "GET /webhook/?load_id=LOAD001",
            "find_closest_load": "GET /webhook/?city=New York, NY",
            "closest_load_endpoint": "GET /distance/closest?city=Los Angeles, CA",
            "load_distance_details": "GET /distance/load/LOAD001",
            "post_rate_negotiation": {
                "url": "POST /webhook/",
                "payload": {
                    "mc_num": "1023",
                    "chosen_id": "LOAD001", 
                    "initial_rate": "1200field2field2",
                    "final_rate": "1300"
                }
            },
            "headers": {
                "X-API-KEY": "UBNfljhgZwVGTIIXMsgH27EQHz4WULkX29k3dnsN8r0",
                "Content-Type": "application/json"
            },
            "params": {
                "api_key": "UBNfljhgZwVGTIIXMsgH27EQHz4WULkX29k3dnsN8r0",
                "load_id": "LOAD001",
                "city": "New York, NY",
                "source": "myapp",
                "version": "1.0"
            }
        }
    })

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/carriers/api/bookings", methods=["GET"])
def get_bookings():
    """Return all bookings with their associated carrier info."""
    # Get all bookings
    conn = db_manager.db_path
    import sqlite3
    sql_conn = sqlite3.connect(conn)
    sql_conn.row_factory = sqlite3.Row
    cursor = sql_conn.cursor()
    cursor.execute('SELECT * FROM bookings ORDER BY timestamp DESC')
    bookings = []
    for row in cursor.fetchall():
        booking = dict(row)
        # Attach carrier info
        carrier = db_manager.get_carrier_by_id(booking['load_id'])
        booking['carrier'] = carrier
        bookings.append(booking)
    sql_conn.close()
    return jsonify({"success": True, "bookings": bookings, "count": len(bookings)})

# For Vercel deployment
if __name__ == "__main__":
    app.run(debug=True) 