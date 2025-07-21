#!/usr/bin/env python3
"""
Setup script for internet access to your webhook.
This script helps you choose and set up the best option for external access.
"""

import os
import subprocess
import sys

def check_command(command):
    """Check if a command is available."""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_ngrok():
    """Install ngrok."""
    print("📦 Installing ngrok...")
    try:
        # Download ngrok
        subprocess.run([
            "wget", "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz"
        ], check=True)
        
        # Extract
        subprocess.run(["tar", "xvzf", "ngrok-v3-stable-linux-amd64.tgz"], check=True)
        
        # Move to /usr/local/bin
        subprocess.run(["sudo", "mv", "ngrok", "/usr/local/bin/"], check=True)
        
        # Clean up
        subprocess.run(["rm", "ngrok-v3-stable-linux-amd64.tgz"], check=True)
        
        print("✅ ngrok installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing ngrok: {e}")
        return False

def setup_http_mode():
    """Set up HTTP mode for easier external access."""
    print("🔧 Setting up HTTP mode...")
    
    # Create a new .env file with HTTP settings
    env_content = """WEBHOOK_API_KEY=UBNfljhgZwVGTIIXMsgH27EQHz4WULkX29k3dnsN8r0
SSL_CERT_PATH=certs/server.crt
SSL_KEY_PATH=certs/server.key
DEV_PORT=8080
FLASK_ENV=development
USE_SSL=false"""
    
    with open(".env.http", "w") as f:
        f.write(env_content)
    
    print("✅ HTTP mode configured!")
    print("📝 Use: cp .env.http .env && python app.py")
    return True

def main():
    print("🌐 Internet Access Setup for Your Webhook")
    print("=" * 50)
    
    print("\nChoose your preferred method:")
    print("1. ngrok (Recommended - creates secure tunnel)")
    print("2. HTTP mode (Simpler, no SSL)")
    print("3. Manual setup instructions")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🚀 Setting up ngrok...")
        if check_command("ngrok"):
            print("✅ ngrok is already installed!")
        else:
            if install_ngrok():
                print("\n📋 Next steps:")
                print("1. Start your Flask app: python app.py")
                print("2. In another terminal, run: ngrok http 8443")
                print("3. Use the provided URL (e.g., https://abc123.ngrok.io)")
            else:
                print("❌ Failed to install ngrok")
    
    elif choice == "2":
        setup_http_mode()
        print("\n📋 Next steps:")
        print("1. Copy HTTP config: cp .env.http .env")
        print("2. Start your Flask app: python app.py")
        print("3. Use ngrok: ngrok http 8080")
    
    elif choice == "3":
        print("\n📋 Manual Setup Instructions:")
        print("=" * 40)
        print("1. Install ngrok:")
        print("   wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz")
        print("   tar xvzf ngrok-v3-stable-linux-amd64.tgz")
        print("   sudo mv ngrok /usr/local/bin/")
        print("\n2. Start your Flask app:")
        print("   python app.py")
        print("\n3. Create tunnel:")
        print("   ngrok http 8443")
        print("\n4. Use the provided URL for external access")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 