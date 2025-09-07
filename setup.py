#!/usr/bin/env python3
"""
Setup script for Meeting Minutes Generator (Simplified for macOS)
"""

import subprocess
import sys
import platform
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🎤 Meeting Minutes Generator - Setup (macOS Optimized)")
    print("=" * 60)
    
    system = platform.system().lower()
    print(f"Detected OS: {system}")
    
    if system == "darwin":  # macOS
        print("\n✅ macOS detected - this version is optimized for macOS!")
        print("📝 This simplified version avoids complex audio dependencies.")
    
    # Install Python packages
    print("\n🐍 Installing Python packages...")
    
    # Read requirements
    try:
        with open('requirements.txt', 'r') as f:
            packages = f.read().strip().split('\n')
    except FileNotFoundError:
        packages = [
            "streamlit>=1.28.0",
            "SpeechRecognition>=3.10.0", 
            "python-docx>=0.8.11",
            "PyPDF2>=3.0.0",
            "audio-recorder-streamlit>=0.0.8"
        ]
        print("📄 Requirements file not found, using default packages...")
    
    failed_packages = []
    
    for package in packages:
        if package.strip() and not package.startswith('#'):
            print(f"Installing {package}...")
            if install_package(package):
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}")
                failed_packages.append(package)
    
    print("\n" + "=" * 60)
    
    if failed_packages:
        print("❌ Some packages failed to install:")
        for package in failed_packages:
            print(f"  - {package}")
        print("\nTry installing them manually:")
        for package in failed_packages:
            print(f"pip install {package}")
    else:
        print("✅ All packages installed successfully!")
        
    print("\n🚀 Setup complete! To run the app:")
    print("streamlit run app.py")
    
    print("\n🔒 Important for macOS users:")
    print("- You'll be asked for microphone permission")
    print("- Go to System Settings → Privacy & Security → Microphone if needed")
    print("- Make sure your browser has microphone access")
    
    print("\n💡 This version uses:")
    print("- Streamlit's built-in audio recorder (no PyAudio needed)")
    print("- Google's free speech recognition API")
    print("- Simple file-based processing")

if __name__ == "__main__":
    main()