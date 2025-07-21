#!/usr/bin/env python3
"""
Quick setup for internet access without ngrok authentication.
"""

import subprocess
import os

def check_node():
    """Check if Node.js is available."""
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_localtunnel():
    """Install localtunnel."""
    print("📦 Installing localtunnel...")
    try:
        subprocess.run(["npm", "install", "-g", "localtunnel"], check=True)
        print("✅ localtunnel installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing localtunnel: {e}")
        return False

def setup_http_mode():
    """Create HTTP configuration."""
    print("🔧 Setting up HTTP mode...")
    
    env_content = """WEBHOOK_API_KEY=UBNfljhgZwVGTIIXMsgH27EQHz4WULkX29k3dnsN8r0
SSL_CERT_PATH=certs/server.crt
SSL_KEY_PATH=certs/server.key
DEV_PORT=8080
FLASK_ENV=development
USE_SSL=false"""
    
    with open(".env.http", "w") as f:
        f.write(env_content)
    
    print("✅ HTTP mode configured!")
    return True

def main():
    print("🌐 Quick Internet Access Setup")
    print("=" * 40)
    
    print("\nChoose your method:")
    print("1. localtunnel (Recommended - free, no signup)")
    print("2. HTTP mode + localtunnel (Simpler)")
    print("3. Manual instructions")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        if not check_node():
            print("❌ Node.js not found. Please install Node.js first.")
            return
        
        if install_localtunnel():
            print("\n📋 Next steps:")
            print("1. Start your Flask app: python app.py")
            print("2. In another terminal, run: lt --port 8443")
            print("3. Use the provided URL for external access")
    
    elif choice == "2":
        setup_http_mode()
        if not check_node():
            print("❌ Node.js not found. Please install Node.js first.")
            return
        
        if install_localtunnel():
            print("\n📋 Next steps:")
            print("1. Switch to HTTP mode: cp .env.http .env")
            print("2. Start your Flask app: python app.py")
            print("3. In another terminal, run: lt --port 8080")
            print("4. Use the provided URL for external access")
    
    elif choice == "3":
        print("\n📋 Manual Setup Instructions:")
        print("=" * 40)
        print("Option A - localtunnel:")
        print("1. Install: npm install -g localtunnel")
        print("2. Start Flask: python app.py")
        print("3. Create tunnel: lt --port 8443")
        print("\nOption B - serveo.net:")
        print("1. Start Flask: python app.py")
        print("2. Create tunnel: ssh -R 80:localhost:8443 serveo.net")
        print("\nOption C - HTTP mode:")
        print("1. Create .env.http file with USE_SSL=false")
        print("2. Copy: cp .env.http .env")
        print("3. Start Flask: python app.py")
        print("4. Use localtunnel: lt --port 8080")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 