"""Virtual webcam module using pyvirtualcam"""

import cv2
import numpy as np
import pyvirtualcam
from typing import Optional


class VirtualCamera:
    """Creates and manages virtual webcam device"""
    
    def __init__(
        self, 
        width: int, 
        height: int, 
        fps: int, 
        device_name: str = "Smart Meeting Camera"
    ):
        """
        Initialize virtual camera
        
        Args:
            width: Frame width
            height: Frame height
            fps: Frames per second
            device_name: Name of virtual camera device
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.device_name = device_name
        self.cam: Optional[pyvirtualcam.Camera] = None
        
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the virtual camera"""
        try:
            self.cam = pyvirtualcam.Camera(
                width=self.width,
                height=self.height,
                fps=self.fps,
                fmt=pyvirtualcam.PixelFormat.RGB
            )
            print(f"Virtual camera created: {self.cam.device}")
        except Exception as e:
            raise RuntimeError(f"Failed to create virtual camera: {e}")
    
    def send_frame(self, frame: np.ndarray) -> None:
        """
        Send frame to virtual camera
        
        Args:
            frame: Frame in BGR format (OpenCV default)
        """
        if not self.is_active():
            return
        
        # Validate frame
        if frame is None or frame.size == 0:
            return
        
        # Ensure frame is correct size
        if frame.shape[:2] != (self.height, self.width):
            frame = cv2.resize(frame, (self.width, self.height))
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Send to virtual camera
        try:
            self.cam.send(rgb_frame)
        except Exception as e:
            print(f"Error sending frame to virtual camera: {e}")
    
    def is_active(self) -> bool:
        """Check if virtual camera is active"""
        return self.cam is not None
    
    def close(self) -> None:
        """Close virtual camera"""
        if self.cam is not None:
            self.cam.close()
            self.cam = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.close()
