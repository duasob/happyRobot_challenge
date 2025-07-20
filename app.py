from flask import Flask, redirect, request
from webhooks.routes import webhook_bp
from routes.carriers import carriers_bp
from config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register the webhook Blueprint
    app.register_blueprint(webhook_bp)
    
    # Register the carriers Blueprint
    app.register_blueprint(carriers_bp, url_prefix='/carriers')

    @app.before_request
    def enforce_https():
        """
        Redirect incoming HTTP to HTTPS. On dev, you may bypass this.
        """
        if not request.is_secure and app.env != "development":
            url = request.url.replace("http://", "https://", 1)
            return redirect(url, code=301)  # :contentReference[oaicite:10]{index=10}

    return app

if __name__ == "__main__":
    flask_app = create_app()
    
    # Check if we're in development mode
    is_development = os.environ.get("FLASK_ENV") == "development" or os.environ.get("FLASK_DEBUG") == "1"
    
    if is_development:
        # Development mode - use non-privileged port
        port = Config.DEVELOPMENT_PORT
        print(f"🚀 Starting development server on https://localhost:{port}/webhook/")
    else:
        # Production mode - use privileged port
        port = Config.PRODUCTION_PORT
        print(f"🚀 Starting production server on https://localhost:{port}/webhook/")
    
    # Run with SSL context
    flask_app.run(
        host="0.0.0.0",
        port=port,
        ssl_context=(Config.SSL_CERT_PATH, Config.SSL_KEY_PATH),
        debug=is_development
    )  # :contentReference[oaicite:11]{index=11}
