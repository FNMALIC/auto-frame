"""Tracking state management for face tracking"""

import time
from enum import Enum
from typing import Optional, Tuple
from .face_detector import FaceDetection


class TrackingStatus(Enum):
    """Status of face tracking"""
    TRACKING = "tracking"
    LOST_RECENT = "lost_recent"  # Lost < 2 seconds
    LOST_LONG = "lost_long"      # Lost > 2 seconds


class TrackingState:
    """Maintains tracking state and handles face loss scenarios"""
    
    def __init__(self, memory_duration: float = 2.0):
        """
        Initialize tracking state
        
        Args:
            memory_duration: How long to remember last position after face loss (seconds)
        """
        self.memory_duration = memory_duration
        self.last_bbox: Optional[Tuple[int, int, int, int]] = None
        self.last_detection_time: Optional[float] = None
        self.status = TrackingStatus.LOST_LONG
    
    def update(self, detection: Optional[FaceDetection], timestamp: float) -> TrackingStatus:
        """
        Update tracking state with new detection
        
        Args:
            detection: Face detection result or None
            timestamp: Current timestamp in seconds
            
        Returns:
            Current tracking status
        """
        if detection is not None:
            # Face detected - update state
            self.last_bbox = detection.bbox
            self.last_detection_time = timestamp
            self.status = TrackingStatus.TRACKING
        else:
            # No face detected
            if self.last_detection_time is None:
                # Never detected a face
                self.status = TrackingStatus.LOST_LONG
            else:
                # Calculate time since last detection
                time_since_detection = timestamp - self.last_detection_time
                
                if time_since_detection < self.memory_duration:
                    # Recently lost - keep last position
                    self.status = TrackingStatus.LOST_RECENT
                else:
                    # Lost for too long
                    self.status = TrackingStatus.LOST_LONG
        
        return self.status
    
    def get_target_bbox(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Get target bounding box for framing
        
        Returns:
            Last known bbox if available, None otherwise
        """
        if self.status == TrackingStatus.TRACKING or self.status == TrackingStatus.LOST_RECENT:
            return self.last_bbox
        return None
    
    def reset(self) -> None:
        """Reset tracking state"""
        self.last_bbox = None
        self.last_detection_time = None
        self.status = TrackingStatus.LOST_LONG
