#!/usr/bin/env python3
"""
Simple script to run the Streamlit YouTube Downloader app
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import yt_dlp
        print("✅ Dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg found")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️  FFmpeg not found - audio conversion may not work")
    print("Install FFmpeg:")
    print("  Windows: Download from https://ffmpeg.org/download.html")
    print("  macOS: brew install ffmpeg")
    print("  Linux: sudo apt-get install ffmpeg")
    return False

def main():
    print("🎵 YouTube Downloader - Starting Streamlit App")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check FFmpeg (warning only)
    check_ffmpeg()
    
    # Create downloads directory
    os.makedirs("downloads", exist_ok=True)
    print("📁 Downloads directory ready")
    
    # Run Streamlit app
    print("🚀 Starting Streamlit server...")
    print("📱 App will open in your browser")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped")

if __name__ == "__main__":
    main()