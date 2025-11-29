#!/usr/bin/env python3
"""Setup script to verify dependencies and virtual camera installation"""

import sys
import platform
import subprocess


def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_dependencies():
    """Check if required Python packages are installed"""
    required = ["cv2", "mediapipe", "pyvirtualcam", "numpy"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")
            missing.append(package)
    
    if missing:
        print("\n📦 Install missing dependencies with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True


def check_virtual_camera():
    """Check virtual camera driver based on platform"""
    system = platform.system()
    
    if system == "Windows":
        print("\n🎥 Virtual Camera Check (Windows):")
        print("   OBS Virtual Camera is required")
        print("   Install OBS Studio from: https://obsproject.com/")
        print("   The virtual camera is included with OBS Studio")
        
    elif system == "Linux":
        print("\n🎥 Virtual Camera Check (Linux):")
        try:
            result = subprocess.run(
                ["modinfo", "v4l2loopback"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✅ v4l2loopback module is installed")
            else:
                print("❌ v4l2loopback module not found")
                print("   Install with: sudo apt install v4l2loopback-dkms")
                print("   Or: sudo modprobe v4l2loopback")
                return False
        except FileNotFoundError:
            print("⚠️  Could not verify v4l2loopback (modinfo not found)")
            print("   Install with: sudo apt install v4l2loopback-dkms")
            
    elif system == "Darwin":  # macOS
        print("\n🎥 Virtual Camera Check (macOS):")
        print("   obs-mac-virtualcam is required")
        print("   Install from: https://github.com/johnboiles/obs-mac-virtualcam")
        
    else:
        print(f"\n⚠️  Unknown platform: {system}")
        print("   Virtual camera setup may require manual configuration")
    
    return True


def main():
    """Run all setup checks"""
    print("=" * 60)
    print("Smart Meeting Camera - Setup Verification")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_virtual_camera()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ Setup verification complete!")
        print("\n🚀 Next steps:")
        print("   1. Run the application: python main.py")
        print("   2. Click 'Start' to activate the virtual camera")
        print("   3. Select 'Smart Meeting Camera' in your video app")
    else:
        print("⚠️  Some checks failed. Please resolve the issues above.")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
