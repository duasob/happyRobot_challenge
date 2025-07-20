from flask import Blueprint, request, abort, current_app, jsonify

webhook_bp = Blueprint("webhook", __name__, url_prefix="/webhook")

@webhook_bp.before_request
def enforce_api_key():
    """Reject requests without the correct X-API-KEY header."""
    key = request.headers.get("X-API-KEY") or request.args.get("api_key")
    if not key or key != current_app.config["API_KEY"]:
        abort(401, description="Unauthorized")  # :contentReference[oaicite:5]{index=5}

@webhook_bp.route("/", methods=["GET", "POST"])
def receive_event():
    """
    Your webhook handler. Parse JSON, verify signature if needed,
    then process the event payload.
    """
    if request.method == "GET":
        # Handle GET requests (for testing/health checks)
        return jsonify({
            "status": "webhook_active",
            "message": "Webhook is running and ready to receive POST requests",
            "timestamp": "2024-01-01T12:00:00Z"
        }), 200
    
    elif request.method == "POST":
        # Handle POST requests with JSON payload
        payload = request.get_json(force=True, silent=True)
        if not payload:
            abort(400, description="Invalid JSON")  # :contentReference[oaicite:6]{index=6}

        # TODO: handle the payload (e.g., enqueue, log, etc.)
        return jsonify({
            "status": "received",
            "message": "Webhook received your data",
            "data": payload
        }), 200
