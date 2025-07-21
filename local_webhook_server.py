#!/usr/bin/env python3
"""
Local Webhook Server for Testing
Run this to see POST data printed directly in your terminal.
"""

from flask import Flask, request, jsonify
import json
from datetime import datetime
import sys
import os

# Add the parent directory to the path so we can import database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database manager
from database import DatabaseManager

app = Flask(__name__)

# Initialize database manager
db_manager = DatabaseManager()

# Your API key
API_KEY = "UBNfljhgZwVGTIIXMsgH27EQHz4WULkX29k3dnsN8r0"

@app.before_request
def enforce_api_key():
    """Reject requests without the correct X-API-KEY header."""
    # Skip API key check for health checks
    if request.path == "/webhook/" and request.method == "GET":
        return
    if request.path == "/":
        return
    
    key = request.headers.get("X-API-KEY") or request.args.get("api_key")
    if not key or key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

@app.route("/webhook/", methods=["GET", "POST"])
def webhook():
    """Webhook endpoint for receiving events."""
    if request.method == "GET":
        # Return all carriers data
        carriers = db_manager.get_all_carriers()
        return jsonify({
            "status": "webhook_active",
            "message": "All carriers data",
            "timestamp": "2024-01-01T12:00:00Z",
            "carriers": carriers,
            "count": len(carriers)
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
        print("\n" + "=" * 60)
        print("🚛 WEBHOOK POST RECEIVED (LOCAL SERVER)")
        print("=" * 60)
        print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 URL: {request.url}")
        print(f"📋 Method: {request.method}")
        print(f"🔑 API Key: {headers.get('X-API-KEY', 'Not provided')}")
        print(f"🌍 Remote IP: {request.remote_addr}")
        print(f"👤 User Agent: {headers.get('User-Agent', 'Unknown')}")
        
        print("\n📦 PAYLOAD DATA:")
        print(json.dumps(payload, indent=2))
        
        print("\n🔗 QUERY PARAMETERS:")
        print(json.dumps(params, indent=2))
        
        print("\n📋 HEADERS:")
        for key, value in headers.items():
            if key.lower() not in ['x-api-key', 'authorization']:  # Don't log sensitive headers
                print(f"   {key}: {value}")
        
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
            print(f"   Equipment: {carrier['equipment_type']}")
            print(f"   Weight: {carrier['weight']} lbs")
            print(f"   Commodity: {carrier['commodity_type']}")
            
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
            print("=" * 60)
            
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

@app.route("/")
def home():
    """Home page."""
    return jsonify({
        "message": "Local Webhook Server is running",
        "webhook_url": "http://localhost:5000/webhook/",
        "api_key": API_KEY,
        "example": {
            "method": "POST",
            "url": "http://localhost:5000/webhook/",
            "headers": {
                "Content-Type": "application/json",
                "X-API-KEY": API_KEY
            },
            "payload": {
                "mc_num": "1023",
                "chosen_id": "LOAD001",
                "initial_rate": "1200field2field2",
                "final_rate": "1300"
            }
        }
    })

if __name__ == "__main__":
    print("🚛 Starting Local Webhook Server...")
    print("=" * 50)
    print("📡 Server will be available at: http://localhost:5000/")
    print("🔗 Webhook endpoint: http://localhost:5000/webhook/")
    print("🔑 API Key: " + API_KEY)
    print("=" * 50)
    print("💡 Test with: curl -X POST http://localhost:5000/webhook/ \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -H 'X-API-KEY: " + API_KEY + "' \\")
    print("  -d '{\"mc_num\": \"1023\", \"chosen_id\": \"LOAD001\", \"initial_rate\": \"1200field2field2\", \"final_rate\": \"1300\"}'")
    print("=" * 50)
    
    app.run(debug=True, host="0.0.0.0", port=5000) 