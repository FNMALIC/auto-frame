"""Frame processor for applying zoom and pan transformations"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple
from .smoothing import TransformSmoother


@dataclass
class ProcessorConfig:
    """Configuration for frame processor"""
    target_face_ratio: float = 0.4  # Face should be 40% of frame height
    min_zoom: float = 1.0
    max_zoom: float = 3.0
    smoothing_factor: float = 0.15  # Lower = smoother
    max_shift_per_frame: int = 50   # pixels


class FrameProcessor:
    """Applies zoom and pan transformations to center and frame detected faces"""
    
    def __init__(self, config: ProcessorConfig):
        """
        Initialize frame processor
        
        Args:
            config: Processor configuration
        """
        self.config = config
        self.smoother = TransformSmoother(
            alpha=config.smoothing_factor,
            max_shift_per_frame=config.max_shift_per_frame
        )
        self.frame_center: Optional[Tuple[int, int]] = None
    
    def process(
        self, 
        frame: np.ndarray, 
        target_bbox: Optional[Tuple[int, int, int, int]]
    ) -> np.ndarray:
        """
        Process frame with auto-framing
        
        Args:
            frame: Input frame
            target_bbox: Target face bounding box (x, y, w, h) or None
            
        Returns:
            Processed frame with zoom and pan applied
        """
        if frame is None or frame.size == 0:
            return frame
        
        height, width = frame.shape[:2]
        
        if self.frame_center is None:
            self.frame_center = (width // 2, height // 2)
        
        # If no target, return original frame
        if target_bbox is None:
            return frame
        
        x, y, w, h = target_bbox
        
        # Calculate face center
        face_center_x = x + w // 2
        face_center_y = y + h // 2
        
        # Calculate optimal zoom to maintain target face ratio
        target_zoom = self._calculate_zoom(h, height)
        
        # Apply smoothing
        smoothed_x, smoothed_y, smoothed_zoom = self.smoother.smooth_transform(
            float(face_center_x),
            float(face_center_y),
            target_zoom
        )
        
        # Apply transformation
        transformed_frame = self._apply_transform(
            frame,
            int(smoothed_x),
            int(smoothed_y),
            smoothed_zoom
        )
        
        return transformed_frame
    
    def _calculate_zoom(self, face_height: int, frame_height: int) -> float:
        """
        Calculate optimal zoom level
        
        Args:
            face_height: Height of detected face in pixels
            frame_height: Height of frame in pixels
            
        Returns:
            Zoom factor
        """
        if face_height <= 0:
            return self.config.min_zoom
        
        # Calculate zoom to make face occupy target ratio of frame
        current_ratio = face_height / frame_height
        target_zoom = self.config.target_face_ratio / current_ratio
        
        # Clamp zoom to limits
        target_zoom = max(self.config.min_zoom, min(self.config.max_zoom, target_zoom))
        
        return target_zoom
    
    def _apply_transform(
        self,
        frame: np.ndarray,
        center_x: int,
        center_y: int,
        zoom: float
    ) -> np.ndarray:
        """
        Apply zoom and pan transformation
        
        Args:
            frame: Input frame
            center_x: X coordinate to center on
            center_y: Y coordinate to center on
            zoom: Zoom factor
            
        Returns:
            Transformed frame
        """
        height, width = frame.shape[:2]
        
        # Calculate the size of the region to extract
        new_width = int(width / zoom)
        new_height = int(height / zoom)
        
        # Calculate top-left corner of region to extract
        # Center the region on the target point
        x1 = center_x - new_width // 2
        y1 = center_y - new_height // 2
        
        # Ensure region stays within frame bounds
        x1 = max(0, min(x1, width - new_width))
        y1 = max(0, min(y1, height - new_height))
        
        x2 = x1 + new_width
        y2 = y1 + new_height
        
        # Extract region
        roi = frame[y1:y2, x1:x2]
        
        # Resize to original frame size (this creates the zoom effect)
        zoomed_frame = cv2.resize(roi, (width, height), interpolation=cv2.INTER_LINEAR)
        
        return zoomed_frame
    
    def update_config(self, config: ProcessorConfig) -> None:
        """
        Update processor configuration
        
        Args:
            config: New configuration
        """
        self.config = config
        self.smoother.set_alpha(config.smoothing_factor)
        self.smoother.max_shift_per_frame = config.max_shift_per_frame
