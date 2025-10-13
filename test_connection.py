#!/usr/bin/env python3
"""Simple test script to verify ConnectionManager functionality."""
import sys
import time
from src.utils.logging_setup import setup_logging
from src.services.connection_manager import ConnectionManager

def status_callback(message: str, connected: bool):
    """Print connection status changes."""
    status = "✓ CONNECTED" if connected else "✗ DISCONNECTED"
    print(f"[{status}] {message}")

def main():
    """Test connection manager."""
    print("=" * 60)
    print("Dashcam Connection Manager Test")
    print("=" * 60)

    # Setup logging
    setup_logging(log_level="INFO")

    # Create connection manager
    print("\n1. Creating ConnectionManager...")
    manager = ConnectionManager(on_status_change=status_callback)

    # Test discovery
    print("\n2. Testing dashcam discovery...")
    found = manager.discover_dashcam(timeout=3.0)
    if found:
        print("   ✓ Dashcam found!")
    else:
        print("   ✗ Dashcam not found (make sure you're connected to dashcam WiFi)")
        return 1

    # Test connection
    print("\n3. Connecting to dashcam...")
    success = manager.connect()
    if not success:
        print("   ✗ Connection failed")
        return 1

    print("   ✓ Connected successfully!")

    # Test getting device info
    print("\n4. Getting device information...")
    device_info = manager.get_device_info()
    if device_info:
        print(f"   Device info: {device_info[:100]}...")

    # Test getting storage info
    print("\n5. Getting storage information...")
    storage_info = manager.get_storage_info()
    if storage_info:
        print(f"   Storage info: {storage_info[:100]}...")

    # Test connectivity check
    print("\n6. Testing connectivity check...")
    is_alive = manager.test_connectivity()
    print(f"   Connection alive: {is_alive}")

    # Start monitoring
    print("\n7. Starting connection monitoring for 15 seconds...")
    manager.start_monitoring(interval=5.0, auto_reconnect=True)

    try:
        for i in range(15, 0, -1):
            print(f"   Monitoring... {i}s remaining", end="\r")
            time.sleep(1)
        print("\n   ✓ Monitoring completed")
    except KeyboardInterrupt:
        print("\n   Interrupted by user")

    # Cleanup
    print("\n8. Disconnecting...")
    manager.disconnect()

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)
    return 0

if __name__ == '__main__':
    sys.exit(main())
