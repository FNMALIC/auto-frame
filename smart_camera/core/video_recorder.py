"""Video recorder for saving processed frames to video files"""

import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional
import threading

from .logger import get_logger

logger = get_logger('video_recorder')


class VideoRecorder:
    """Handles video recording with OpenCV VideoWriter"""
    
    def __init__(self, output_dir: str, codec: str = 'mp4v', fps: int = 30):
        """
        Initialize video recorder
        
        Args:
            output_dir: Directory to save recordings
            codec: Video codec (default: 'mp4v' for MP4)
            fps: Frames per second for output video
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.codec = codec
        self.fps = fps
        
        self.writer: Optional[cv2.VideoWriter] = None
        self.current_file: Optional[Path] = None
        self.is_recording = False
        self.frame_count = 0
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info(f"Video recorder initialized. Output dir: {self.output_dir}")
    
    def start_recording(self, width: int, height: int) -> bool:
        """
        Start recording video
        
        Args:
            width: Frame width
            height: Frame height
            
        Returns:
            True if recording started successfully
        """
        with self.lock:
            if self.is_recording:
                logger.warning("Recording already in progress")
                return False
            
            try:
                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"recording_{timestamp}.mp4"
                self.current_file = self.output_dir / filename
                
                # Create VideoWriter
                fourcc = cv2.VideoWriter_fourcc(*self.codec)
                self.writer = cv2.VideoWriter(
                    str(self.current_file),
                    fourcc,
                    self.fps,
                    (width, height)
                )
                
                if not self.writer.isOpened():
                    logger.error("Failed to open video writer")
                    self.writer = None
                    self.current_file = None
                    return False
                
                self.is_recording = True
                self.frame_count = 0
                logger.info(f"Recording started: {self.current_file}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to start recording: {e}", exc_info=True)
                self.writer = None
                self.current_file = None
                return False
    
    def write_frame(self, frame: np.ndarray) -> bool:
        """
        Write a frame to the video file
        
        Args:
            frame: Frame to write (BGR format)
            
        Returns:
            True if frame was written successfully
        """
        with self.lock:
            if not self.is_recording or self.writer is None:
                return False
            
            try:
                self.writer.write(frame)
                self.frame_count += 1
                return True
            except Exception as e:
                logger.error(f"Failed to write frame: {e}")
                return False
    
    def stop_recording(self) -> Optional[str]:
        """
        Stop recording and finalize video file
        
        Returns:
            Path to saved video file, or None if not recording
        """
        with self.lock:
            if not self.is_recording:
                return None
            
            try:
                if self.writer is not None:
                    self.writer.release()
                    self.writer = None
                
                saved_file = str(self.current_file) if self.current_file else None
                logger.info(f"Recording stopped. Saved {self.frame_count} frames to: {saved_file}")
                
                self.is_recording = False
                self.frame_count = 0
                self.current_file = None
                
                return saved_file
                
            except Exception as e:
                logger.error(f"Error stopping recording: {e}", exc_info=True)
                self.is_recording = False
                self.writer = None
                self.current_file = None
                return None
    
    def get_recording_info(self) -> dict:
        """
        Get current recording information
        
        Returns:
            Dictionary with recording status and info
        """
        with self.lock:
            return {
                'is_recording': self.is_recording,
                'frame_count': self.frame_count,
                'current_file': str(self.current_file) if self.current_file else None,
                'duration_seconds': self.frame_count / self.fps if self.fps > 0 else 0
            }
    
    def close(self) -> None:
        """Clean up resources"""
        if self.is_recording:
            self.stop_recording()
