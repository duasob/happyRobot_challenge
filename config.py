import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Your shared secret API key (rotate and store securely in env vars)
    API_KEY = os.environ.get("WEBHOOK_API_KEY", "CHANGE_ME")  # :contentReference[oaicite:0]{index=0}

    # Paths to your SSL certificate and private key
    SSL_CERT_PATH = os.environ.get("SSL_CERT_PATH", "certs/server.crt")  # :contentReference[oaicite:1]{index=1}
    SSL_KEY_PATH = os.environ.get("SSL_KEY_PATH", "certs/server.key")   # :contentReference[oaicite:2]{index=2}

    # Only allow HTTPS (used in before_request)
    PREFERRED_URL_SCHEME = "https"  # :contentReference[oaicite:3]{index=3}
    SESSION_COOKIE_SECURE = True    # :contentReference[oaicite:4]{index=4}
    
    # Development settings
    DEVELOPMENT_PORT = int(os.environ.get("DEV_PORT", "8443"))
    PRODUCTION_PORT = 443
