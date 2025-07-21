from flask import Flask, request, jsonify
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
    """Reject requests without the correct X-API-KEY header or api_key param."""
    # Skip API key check for health checks and home page
    if request.path == "/webhook/" and request.method == "GET":
        return
    if request.path == "/":
        return
    
    # Check for API key in headers OR query parameters
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
        # Handle POST requests with JSON payload
        payload = request.get_json(force=True, silent=True)
        if not payload:
            return jsonify({"error": "Invalid JSON"}), 400

        # Get query parameters and headers
        params = dict(request.args)
        headers = dict(request.headers)
        
        # Print/log the received data
        print("=" * 50)
        print("🚛 WEBHOOK POST RECEIVED")
        print("=" * 50)
        print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 URL: {request.url}")
        print(f"📋 Method: {request.method}")
        print(f"🔑 API Key: {headers.get('X-API-KEY', 'Not provided')}")
        print("\n📦 PAYLOAD DATA:")
        print(json.dumps(payload, indent=2))
        print("\n🔗 QUERY PARAMETERS:")
        print(json.dumps(params, indent=2))
        print("\n📋 HEADERS:")
        for key, value in headers.items():
            if key.lower() not in ['x-api-key', 'authorization']:  # Don't log sensitive headers
                print(f"   {key}: {value}")
        print("=" * 50)
        
        # Process the specific payload format
        try:
            mc_num = payload.get('mc_num')
            chosen_id = payload.get('chosen_id')
            initial_rate = payload.get('initial_rate')
            final_rate = payload.get('final_rate')
            
            print(f"\n🔍 PROCESSING DATA:")
            print(f"   MC Number: {mc_num}")
            print(f"   Chosen Load ID: {chosen_id}")
            print(f"   Initial Rate: {initial_rate}")
            print(f"   Final Rate: {final_rate}")
            
            # Validate required fields
            if not all([mc_num, chosen_id, initial_rate, final_rate]):
                print("❌ ERROR: Missing required fields")
                return jsonify({
                    "error": "Missing required fields: mc_num, chosen_id, initial_rate, final_rate"
                }), 400
            
            # Get carrier details for the chosen load
            carrier = db_manager.get_carrier_by_id(chosen_id)
            if not carrier:
                print(f"❌ ERROR: Load {chosen_id} not found in database")
                return jsonify({
                    "error": f"Load {chosen_id} not found in database"
                }), 404
            
            print(f"✅ Load found: {carrier['origin']} → {carrier['destination']}")
            
            # Process the rate negotiation
            rate_difference = float(final_rate) - float(initial_rate.replace('field2field2', ''))
            print(f"💰 Rate difference: ${rate_difference}")
            
            # Create response with processed data
            response_data = {
                "status": "received",
                "message": "Rate negotiation processed successfully",
                "data": {
                    "mc_number": mc_num,
                    "chosen_load_id": chosen_id,
                    "initial_rate": initial_rate,
                    "final_rate": final_rate,
                    "rate_difference": rate_difference,
                    "load_details": {
                        "origin": carrier['origin'],
                        "destination": carrier['destination'],
                        "equipment_type": carrier['equipment_type'],
                        "weight": carrier['weight'],
                        "commodity_type": carrier['commodity_type']
                    }
                },
                "params_received": params,
                "headers_received": headers
            }
            
            print(f"✅ SUCCESS: Rate negotiation processed")
            print("=" * 50)
            
            return jsonify(response_data), 200
            
        except ValueError as e:
            print(f"❌ ERROR: Invalid rate format - {str(e)}")
            return jsonify({
                "error": f"Invalid rate format: {str(e)}"
            }), 400
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return jsonify({
                "error": f"Error processing payload: {str(e)}"
            }), 500

@app.route("/carriers/api/carriers", methods=["GET", "POST"])
def carriers():
    """Carriers API endpoint."""
    if request.method == "GET":
        # Return carriers data from database
        carriers = db_manager.get_all_carriers()
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

@app.route("/distance/closest", methods=["GET"])
def closest_load():
    """Find closest load to a city."""
    city = request.args.get('city')
    if not city:
        return jsonify({
            "error": "City parameter is required",
            "example": "/distance/closest?city=New York, NY"
        }), 400
    
    result = find_closest_load_to_city(city)
    return jsonify(result)

@app.route("/distance/load/<load_id>", methods=["GET"])
def load_distance_details(load_id):
    """Get distance details for a specific load."""
    carrier = db_manager.get_carrier_by_id(load_id)
    if not carrier:
        return jsonify({
            "error": f"Load {load_id} not found"
        }), 404
    
    # Geocode origin and destination
    origin_coords = distance_calc.geocode_city(carrier['origin'])
    dest_coords = distance_calc.geocode_city(carrier['destination'])
    
    if origin_coords and dest_coords:
        route_distance = distance_calc.calculate_distance(origin_coords, dest_coords)
    else:
        route_distance = None
    
    return jsonify({
        "success": True,
        "load": carrier,
        "origin_coordinates": origin_coords,
        "destination_coordinates": dest_coords,
        "route_distance_miles": round(route_distance, 1) if route_distance else None
    })

def find_closest_load_to_city(city_name: str) -> Dict:
    """Find the closest load to a given city."""
    # Geocode the input city
    city_coords = distance_calc.geocode_city(city_name)
    if not city_coords:
        return {
            "error": f"Could not find coordinates for {city_name}",
            "success": False
        }
    
    # Get all carriers from database
    carriers = db_manager.get_all_carriers()
    
    closest_load = None
    min_distance = float('inf')
    distances = []
    
    for carrier in carriers:
        # Geocode origin and destination
        origin_coords = distance_calc.geocode_city(carrier['origin'])
        dest_coords = distance_calc.geocode_city(carrier['destination'])
        
        if origin_coords and dest_coords:
            # Calculate distances
            distance_to_origin = distance_calc.calculate_distance(city_coords, origin_coords)
            distance_to_dest = distance_calc.calculate_distance(city_coords, dest_coords)
            
            # Use the closer of origin or destination
            min_carrier_distance = min(distance_to_origin, distance_to_dest)
            
            distances.append({
                'load_id': carrier['load_id'],
                'origin': carrier['origin'],
                'destination': carrier['destination'],
                'distance_to_origin': round(distance_to_origin, 1),
                'distance_to_dest': round(distance_to_dest, 1),
                'min_distance': round(min_carrier_distance, 1),
                'carrier': carrier
            })
            
            if min_carrier_distance < min_distance:
                min_distance = min_carrier_distance
                closest_load = carrier
    
    if not closest_load:
        return {
            "error": "No loads found with valid coordinates",
            "success": False
        }
    
    # Sort distances for ranking
    distances.sort(key=lambda x: x['min_distance'])
    
    return {
        "success": True,
        "input_city": city_name,
        "input_coordinates": city_coords,
        "closest_load": closest_load,
        "closest_distance": round(min_distance, 1),
        "all_distances": distances[:5],  # Top 5 closest
        "total_loads_checked": len(carriers)
    }

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

# For Vercel deployment
if __name__ == "__main__":
    app.run(debug=True) 