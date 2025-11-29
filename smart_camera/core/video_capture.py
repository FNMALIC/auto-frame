"""Video capture module for accessing webcam"""

import cv2
import numpy as np
from typing import Optional, Tuple


class VideoCapture:
    """Manages connection to physical webcam and provides raw video frames"""
    
    def __init__(self, camera_index: int = 0, resolution: Tuple[int, int] = (1280, 720)):
        """
        Initialize video capture
        
        Args:
            camera_index: Index of camera device (0 for default)
            resolution: Desired resolution as (width, height)
        """
        self.camera_index = camera_index
        self.resolution = resolution
        self.cap: Optional[cv2.VideoCapture] = None
        self._fps = 30
        
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the camera capture"""
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if self.cap.isOpened():
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            
            # Try to set FPS
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Read actual values
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self._fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            if (actual_width, actual_height) != self.resolution:
                print(f"Warning: Requested {self.resolution}, got ({actual_width}, {actual_height})")
                self.resolution = (actual_width, actual_height)
    
    def read_frame(self) -> Optional[np.ndarray]:
        """
        Read a frame from the camera
        
        Returns:
            Frame as numpy array (BGR format) or None if read fails
        """
        if not self.is_opened():
            return None
        
        ret, frame = self.cap.read()
        
        if not ret or frame is None:
            return None
        
        return frame
    
    def get_fps(self) -> int:
        """Get the camera FPS"""
        return self._fps
    
    def get_resolution(self) -> Tuple[int, int]:
        """Get the current resolution as (width, height)"""
        return self.resolution
    
    def is_opened(self) -> bool:
        """Check if camera is opened and ready"""
        return self.cap is not None and self.cap.isOpened()
    
    def release(self) -> None:
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()
        return False
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.release()
