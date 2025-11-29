#!/usr/bin/env python3
"""Smart Meeting Camera - Main entry point"""

import sys
import signal
import argparse

from smart_camera.config.settings import SettingsManager
from smart_camera.core.controller import CameraController
from smart_camera.core.logger import setup_logging
from smart_camera.ui.main_window import SmartCameraUI


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down...")
    sys.exit(0)


def main():
    """Main application entry point"""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Smart Meeting Camera - Auto-framing for video calls"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(debug=args.debug)
    
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Load settings
        logger.info("Loading configuration...")
        settings_manager = SettingsManager(config_path=args.config)
        config = settings_manager.load()
        
        # Create controller
        logger.info("Initializing camera controller...")
        controller = CameraController(config)
        
        # Create and start UI
        logger.info("Starting user interface...")
        ui = SmartCameraUI(controller)
        
        # Save settings on exit
        def on_exit():
            logger.info("Saving configuration...")
            settings_manager.save(controller.config)
        
        import atexit
        atexit.register(on_exit)
        
        # Start UI main loop
        ui.start()
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nError: {e}")
        print("Check logs for details: ~/.smart_meeting_camera/logs/app.log")
        return 1


if __name__ == "__main__":
    sys.exit(main())
