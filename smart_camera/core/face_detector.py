"""Face detection module using MediaPipe"""

import cv2
import numpy as np
import mediapipe as mp
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class FaceDetection:
    """Face detection result"""
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float
    center: Tuple[int, int]


class FaceDetector:
    """Detects faces in video frames using MediaPipe"""
    
    def __init__(self, min_detection_confidence: float = 0.5):
        """
        Initialize face detector
        
        Args:
            min_detection_confidence: Minimum confidence threshold (0.0 to 1.0)
        """
        self.min_detection_confidence = min_detection_confidence
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            min_detection_confidence=min_detection_confidence,
            model_selection=0  # 0 for short-range (< 2m), 1 for full-range
        )
    
    def detect(self, frame: np.ndarray) -> Optional[FaceDetection]:
        """
        Detect faces in frame
        
        Args:
            frame: Input frame in BGR format
            
        Returns:
            FaceDetection object for largest face, or None if no face detected
        """
        if frame is None or frame.size == 0:
            return None
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame
        results = self.face_detection.process(rgb_frame)
        
        if not results.detections:
            return None
        
        # Get frame dimensions
        height, width = frame.shape[:2]
        
        # Find largest face by area
        largest_detection = None
        largest_area = 0
        
        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box
            
            # Convert normalized coordinates to pixels
            x = int(bbox.xmin * width)
            y = int(bbox.ymin * height)
            w = int(bbox.width * width)
            h = int(bbox.height * height)
            
            # Ensure bbox is within frame bounds
            x = max(0, x)
            y = max(0, y)
            w = min(w, width - x)
            h = min(h, height - y)
            
            area = w * h
            
            if area > largest_area:
                largest_area = area
                center_x = x + w // 2
                center_y = y + h // 2
                
                largest_detection = FaceDetection(
                    bbox=(x, y, w, h),
                    confidence=detection.score[0],
                    center=(center_x, center_y)
                )
        
        return largest_detection
    
    def close(self) -> None:
        """Release MediaPipe resources"""
        if self.face_detection:
            self.face_detection.close()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.close()
