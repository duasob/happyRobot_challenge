from http.server import BaseHTTPRequestHandler
import json
import os

def handler(request, context):
    """Vercel serverless function handler."""
    
    # Get the path from the request
    path = request.get('path', '')
    method = request.get('method', 'GET')
    headers = request.get('headers', {})
    body = request.get('body', '')
    
    # API key from environment
    api_key = os.environ.get("WEBHOOK_API_KEY", "CHANGE_ME")
    
    # Handle webhook endpoint
    if path == "/webhook/":
        if method == "GET":
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    "status": "webhook_active",
                    "message": "Webhook is running and ready to receive POST requests",
                    "timestamp": "2024-01-01T12:00:00Z"
                })
            }
        
        elif method == "POST":
            # Check API key
            request_api_key = headers.get('X-API-KEY') or headers.get('x-api-key')
            if not request_api_key or request_api_key != api_key:
                return {
                    'statusCode': 401,
                    'headers': {
                        'Content-Type': 'application/json',
                    },
                    'body': json.dumps({"error": "Unauthorized"})
                }
            
            # Parse JSON body
            try:
                payload = json.loads(body) if body else {}
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                    },
                    'body': json.dumps({"error": "Invalid JSON"})
                }
            
            # Process webhook
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    "status": "received",
                    "message": "Webhook received your data",
                    "data": payload
                })
            }
    
    # Handle carriers endpoint
    elif path == "/carriers/api/carriers":
        if method == "GET":
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    "success": True,
                    "carriers": [
                        {"load_id": "123", "origin": "NYC", "destination": "LA"},
                        {"load_id": "456", "origin": "CHI", "destination": "MIA"}
                    ],
                    "count": 2
                })
            }
        
        elif method == "POST":
            # Check API key
            request_api_key = headers.get('X-API-KEY') or headers.get('x-api-key')
            if not request_api_key or request_api_key != api_key:
                return {
                    'statusCode': 401,
                    'headers': {
                        'Content-Type': 'application/json',
                    },
                    'body': json.dumps({"error": "Unauthorized"})
                }
            
            try:
                data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                    },
                    'body': json.dumps({"error": "Invalid JSON"})
                }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': json.dumps({
                    "success": True,
                    "message": "Carrier added successfully"
                })
            }
    
    # Handle home page
    elif path == "/":
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({
                "message": "Webhook API is running",
                "endpoints": {
                    "webhook": "/webhook/",
                    "carriers": "/carriers/api/carriers"
                },
                "api_key_required": "Use X-API-KEY header for POST requests"
            })
        }
    
    # 404 for unknown paths
    else:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({"error": "Not found"})
        } 