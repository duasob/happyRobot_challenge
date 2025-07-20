#!/usr/bin/env python3
"""
Generate self-signed SSL certificates for development.
Run this script to create the certs directory and SSL files.
"""

import os
import subprocess
import secrets

def generate_ssl_certificates():
    """Generate self-signed SSL certificates for development."""
    
    # Create certs directory if it doesn't exist
    os.makedirs("certs", exist_ok=True)
    
    # Generate a random API key
    api_key = secrets.token_urlsafe(32)
    
    # Generate self-signed certificate
    try:
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:4096", 
            "-keyout", "certs/server.key", "-out", "certs/server.crt",
            "-days", "365", "-nodes", "-subj", 
            "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        ], check=True)
        
        print("✅ SSL certificates generated successfully!")
        print(f"📁 Certificate files created in: certs/")
        
        # Create .env file with the generated API key
        with open(".env", "w") as f:
            f.write(f"WEBHOOK_API_KEY={api_key}\n")
            f.write("SSL_CERT_PATH=certs/server.crt\n")
            f.write("SSL_KEY_PATH=certs/server.key\n")
            f.write("DEV_PORT=8443\n")
            f.write("FLASK_ENV=development\n")
        
        print(f"🔑 API Key generated: {api_key}")
        print("📝 .env file created with your configuration")
        print("\n🚀 You can now run your webhook server!")
        print("   python app.py")
        print("\n📡 Your webhook will be available at: https://localhost:8443/webhook/")
        
    except subprocess.CalledProcessError:
        print("❌ Error: OpenSSL not found. Please install OpenSSL:")
        print("   Ubuntu/Debian: sudo apt-get install openssl")
        print("   macOS: brew install openssl")
        print("   Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
    except FileNotFoundError:
        print("❌ Error: OpenSSL command not found. Please install OpenSSL.")

if __name__ == "__main__":
    generate_ssl_certificates() 