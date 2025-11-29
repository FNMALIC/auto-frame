"""Smoothing filters for camera movements"""

from typing import Optional, Tuple


class ExponentialSmoother:
    """Exponential moving average smoother for single values"""
    
    def __init__(self, alpha: float = 0.15):
        """
        Initialize smoother
        
        Args:
            alpha: Smoothing factor (0.0 to 1.0)
                   Lower = smoother, Higher = more responsive
        """
        self.alpha = max(0.0, min(1.0, alpha))
        self.smoothed_value: Optional[float] = None
    
    def smooth(self, new_value: float) -> float:
        """
        Apply exponential smoothing to new value
        
        Args:
            new_value: New input value
            
        Returns:
            Smoothed value
        """
        if self.smoothed_value is None:
            # First value - no smoothing
            self.smoothed_value = new_value
        else:
            # Apply exponential moving average
            self.smoothed_value = self.alpha * new_value + (1 - self.alpha) * self.smoothed_value
        
        return self.smoothed_value
    
    def reset(self) -> None:
        """Reset smoother state"""
        self.smoothed_value = None
    
    def set_alpha(self, alpha: float) -> None:
        """Update smoothing factor"""
        self.alpha = max(0.0, min(1.0, alpha))


class TransformSmoother:
    """Smoother for camera transform parameters (x, y, zoom)"""
    
    def __init__(self, alpha: float = 0.15, max_shift_per_frame: int = 50):
        """
        Initialize transform smoother
        
        Args:
            alpha: Smoothing factor for exponential smoothing
            max_shift_per_frame: Maximum pixel shift per frame (velocity limiting)
        """
        self.x_smoother = ExponentialSmoother(alpha)
        self.y_smoother = ExponentialSmoother(alpha)
        self.zoom_smoother = ExponentialSmoother(alpha)
        self.max_shift_per_frame = max_shift_per_frame
    
    def smooth_transform(
        self, 
        target_x: float, 
        target_y: float, 
        target_zoom: float
    ) -> Tuple[float, float, float]:
        """
        Apply smoothing to transform parameters
        
        Args:
            target_x: Target x position
            target_y: Target y position
            target_zoom: Target zoom level
            
        Returns:
            Tuple of (smoothed_x, smoothed_y, smoothed_zoom)
        """
        # Apply exponential smoothing
        smoothed_x = self.x_smoother.smooth(target_x)
        smoothed_y = self.y_smoother.smooth(target_y)
        smoothed_zoom = self.zoom_smoother.smooth(target_zoom)
        
        # Apply velocity limiting to x and y
        if self.x_smoother.smoothed_value is not None:
            prev_x = self.x_smoother.smoothed_value
            delta_x = smoothed_x - prev_x
            if abs(delta_x) > self.max_shift_per_frame:
                smoothed_x = prev_x + (self.max_shift_per_frame if delta_x > 0 else -self.max_shift_per_frame)
                self.x_smoother.smoothed_value = smoothed_x
        
        if self.y_smoother.smoothed_value is not None:
            prev_y = self.y_smoother.smoothed_value
            delta_y = smoothed_y - prev_y
            if abs(delta_y) > self.max_shift_per_frame:
                smoothed_y = prev_y + (self.max_shift_per_frame if delta_y > 0 else -self.max_shift_per_frame)
                self.y_smoother.smoothed_value = smoothed_y
        
        return smoothed_x, smoothed_y, smoothed_zoom
    
    def reset(self) -> None:
        """Reset all smoothers"""
        self.x_smoother.reset()
        self.y_smoother.reset()
        self.zoom_smoother.reset()
    
    def set_alpha(self, alpha: float) -> None:
        """Update smoothing factor for all smoothers"""
        self.x_smoother.set_alpha(alpha)
        self.y_smoother.set_alpha(alpha)
        self.zoom_smoother.set_alpha(alpha)
