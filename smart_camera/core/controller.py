"""Application controller that orchestrates all components"""

import time
import threading
from queue import Queue, Empty
from dataclasses import dataclass
from typing import Optional

from .video_capture import VideoCapture
from .face_detector import FaceDetector
from .tracking_state import TrackingState, TrackingStatus
from .frame_processor import FrameProcessor, ProcessorConfig
from .virtual_camera import VirtualCamera
from .logger import get_logger
from ..config.settings import AppConfig

logger = get_logger('controller')


@dataclass
class ControllerStatus:
    """Status information from controller"""
    is_running: bool
    current_fps: float
    face_detected: bool
    tracking_status: TrackingStatus
    current_zoom: float
    error_message: Optional[str]


class CameraController:
    """Orchestrates all components and manages application lifecycle"""
    
    def __init__(self, config: AppConfig):
        """
        Initialize camera controller
        
        Args:
            config: Application configuration
        """
        self.config = config
        
        # Components
        self.video_capture: Optional[VideoCapture] = None
        self.face_detector: Optional[FaceDetector] = None
        self.tracking_state: Optional[TrackingState] = None
        self.frame_processor: Optional[FrameProcessor] = None
        self.virtual_camera: Optional[VirtualCamera] = None
        
        # Threading
        self.processing_thread: Optional[threading.Thread] = None
        self.running = False
        self.frame_queue = Queue(maxsize=2)
        
        # Performance monitoring
        self.fps_counter = 0
        self.fps_start_time = 0
        self.current_fps = 0.0
        self.current_zoom = 1.0
        self.low_fps_counter = 0
        self.low_fps_warning_shown = False
        
        # Error tracking
        self.error_message: Optional[str] = None
        self.frame_read_failures = 0
    
    def start(self) -> bool:
        """
        Start the camera and processing
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.running:
            return True
        
        try:
            # Initialize video capture
            self.video_capture = VideoCapture(
                camera_index=self.config.camera_index,
                resolution=self.config.resolution
            )
            
            if not self.video_capture.is_opened():
                self.error_message = "No camera detected. Please connect a webcam."
                logger.error(self.error_message)
                return False
            
            # Initialize face detector
            try:
                self.face_detector = FaceDetector(
                    min_detection_confidence=self.config.min_detection_confidence
                )
            except Exception as e:
                self.error_message = f"Face detection failed to initialize: {str(e)}"
                logger.error(self.error_message)
                return False
            
            # Initialize tracking state
            self.tracking_state = TrackingState(memory_duration=2.0)
            
            # Initialize frame processor
            processor_config = ProcessorConfig(
                target_face_ratio=self.config.face_size_ratio,
                smoothing_factor=self.config.tracking_speed
            )
            self.frame_processor = FrameProcessor(processor_config)
            
            # Initialize virtual camera
            width, height = self.config.resolution
            try:
                self.virtual_camera = VirtualCamera(
                    width=width,
                    height=height,
                    fps=self.config.fps
                )
            except RuntimeError as e:
                self.error_message = f"Virtual camera failed: {str(e)}"
                logger.error(self.error_message)
                return False
            
            # Start processing thread
            self.running = True
            self.fps_start_time = time.time()
            self.processing_thread = threading.Thread(target=self._process_loop, daemon=True)
            self.processing_thread.start()
            
            logger.info("Camera controller started successfully")
            return True
            
        except Exception as e:
            self.error_message = f"Failed to start: {str(e)}"
            logger.error(f"Error starting controller: {e}", exc_info=True)
            self.stop()
            return False
    
    def stop(self) -> None:
        """Stop the camera and processing"""
        if not self.running:
            return
        
        logger.info("Stopping camera controller...")
        self.running = False
        
        # Wait for processing thread to finish (with timeout)
        if self.processing_thread is not None:
            self.processing_thread.join(timeout=2.0)
        
        # Clean up components
        if self.virtual_camera is not None:
            self.virtual_camera.close()
            self.virtual_camera = None
        
        if self.face_detector is not None:
            self.face_detector.close()
            self.face_detector = None
        
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None
        
        self.tracking_state = None
        self.frame_processor = None
        
        logger.info("Camera controller stopped")
    
    def _process_loop(self) -> None:
        """Main processing loop (runs in separate thread)"""
        frame_start_time = time.time()
        
        while self.running:
            try:
                # Track frame processing time
                frame_start_time = time.time()
                
                # Read frame
                frame = self.video_capture.read_frame()
                
                if frame is None:
                    self.frame_read_failures += 1
                    if self.frame_read_failures > 3:
                        self.error_message = "Camera connection lost"
                        logger.error(self.error_message)
                        self.running = False
                        break
                    continue
                
                # Reset failure counter on successful read
                self.frame_read_failures = 0
                
                # Detect face
                detection = self.face_detector.detect(frame)
                
                # Update tracking state
                current_time = time.time()
                status = self.tracking_state.update(detection, current_time)
                
                # Get target bbox
                target_bbox = self.tracking_state.get_target_bbox()
                
                # Process frame
                processed_frame = self.frame_processor.process(frame, target_bbox)
                
                # Send to virtual camera
                self.virtual_camera.send_frame(processed_frame)
                
                # Send to UI preview (non-blocking)
                try:
                    self.frame_queue.put_nowait(processed_frame.copy())
                except:
                    pass  # Queue full, skip this frame for preview
                
                # Update FPS counter
                self.fps_counter += 1
                elapsed = current_time - self.fps_start_time
                if elapsed >= 1.0:
                    self.current_fps = self.fps_counter / elapsed
                    self.fps_counter = 0
                    self.fps_start_time = current_time
                    
                    # Check for low FPS
                    if self.current_fps < 15:
                        self.low_fps_counter += 1
                        if self.low_fps_counter >= 5 and not self.low_fps_warning_shown:
                            logger.warning(f"Performance warning: Low frame rate detected ({self.current_fps:.1f} fps)")
                            self.low_fps_warning_shown = True
                    else:
                        self.low_fps_counter = 0
                        self.low_fps_warning_shown = False
                
                # Calculate frame processing time
                frame_time = time.time() - frame_start_time
                
                # Log warning if frame takes too long
                if frame_time > 0.033:  # 33ms for 30fps
                    logger.debug(f"Frame processing took {frame_time*1000:.1f}ms (target: 33ms)")
                
                # Small sleep to prevent CPU overuse
                # Adjust sleep based on processing time to maintain target fps
                target_frame_time = 1.0 / self.config.fps
                sleep_time = max(0.001, target_frame_time - frame_time)
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}", exc_info=True)
                self.error_message = str(e)
    
    def get_preview_frame(self, timeout: float = 0.1):
        """
        Get frame for UI preview
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Frame or None
        """
        try:
            return self.frame_queue.get(timeout=timeout)
        except Empty:
            return None
    
    def update_settings(self, config: AppConfig) -> None:
        """
        Update settings while running
        
        Args:
            config: New configuration
        """
        self.config = config
        
        if self.frame_processor is not None:
            processor_config = ProcessorConfig(
                target_face_ratio=config.face_size_ratio,
                smoothing_factor=config.tracking_speed
            )
            self.frame_processor.update_config(processor_config)
        
        if self.face_detector is not None:
            # Note: MediaPipe confidence can't be changed after init
            # Would need to recreate detector for this
            pass
    
    def get_status(self) -> ControllerStatus:
        """
        Get current controller status
        
        Returns:
            ControllerStatus object
        """
        face_detected = False
        tracking_status = TrackingStatus.LOST_LONG
        
        if self.tracking_state is not None:
            tracking_status = self.tracking_state.status
            face_detected = tracking_status == TrackingStatus.TRACKING
        
        return ControllerStatus(
            is_running=self.running,
            current_fps=self.current_fps,
            face_detected=face_detected,
            tracking_status=tracking_status,
            current_zoom=self.current_zoom,
            error_message=self.error_message
        )
