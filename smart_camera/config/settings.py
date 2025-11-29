"""Settings management for application configuration"""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Tuple


@dataclass
class AppConfig:
    """Application configuration"""
    # Camera settings
    camera_index: int = 0
    resolution: Tuple[int, int] = (1280, 720)
    fps: int = 30
    
    # Tracking settings
    tracking_speed: float = 0.15  # smoothing alpha: 0.1 (smooth) to 0.9 (responsive)
    zoom_level: str = "medium"    # "close", "medium", "wide"
    face_size_ratio: float = 0.4  # 0.3 to 0.5
    
    # Detection settings
    min_detection_confidence: float = 0.5  # 0.5 to 0.9
    
    # Performance settings
    max_cpu_percent: float = 25.0
    enable_gpu: bool = False


class SettingsManager:
    """Manages loading and saving of application settings"""
    
    # Preset mappings for zoom levels
    ZOOM_PRESETS = {
        "close": 0.5,   # Face is 50% of frame
        "medium": 0.4,  # Face is 40% of frame
        "wide": 0.3     # Face is 30% of frame
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize settings manager
        
        Args:
            config_path: Path to config file, or None for default
        """
        if config_path is None:
            # Use default path in user's home directory
            home = Path.home()
            config_dir = home / ".smart_meeting_camera"
            config_dir.mkdir(exist_ok=True)
            self.config_path = config_dir / "config.json"
        else:
            self.config_path = Path(config_path)
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> AppConfig:
        """
        Load configuration from file
        
        Returns:
            AppConfig object (defaults if file doesn't exist or is invalid)
        """
        if not self.config_path.exists():
            print(f"Config file not found, using defaults: {self.config_path}")
            return AppConfig()
        
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            
            # Convert resolution from list to tuple if needed
            if 'resolution' in data and isinstance(data['resolution'], list):
                data['resolution'] = tuple(data['resolution'])
            
            # Validate and apply zoom preset
            if 'zoom_level' in data:
                zoom_level = data['zoom_level']
                if zoom_level in self.ZOOM_PRESETS:
                    data['face_size_ratio'] = self.ZOOM_PRESETS[zoom_level]
            
            config = AppConfig(**data)
            print(f"Loaded config from: {self.config_path}")
            return config
            
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Using default configuration")
            return AppConfig()
    
    def save(self, config: AppConfig) -> None:
        """
        Save configuration to file
        
        Args:
            config: Configuration to save
        """
        try:
            # Convert to dict
            data = asdict(config)
            
            # Convert tuple to list for JSON serialization
            if isinstance(data['resolution'], tuple):
                data['resolution'] = list(data['resolution'])
            
            # Write to file
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Saved config to: {self.config_path}")
            
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def reset_to_defaults(self) -> AppConfig:
        """
        Reset configuration to defaults
        
        Returns:
            Default AppConfig
        """
        config = AppConfig()
        self.save(config)
        return config
    
    @staticmethod
    def get_face_ratio_for_zoom(zoom_level: str) -> float:
        """
        Get face size ratio for zoom level preset
        
        Args:
            zoom_level: Zoom level name
            
        Returns:
            Face size ratio
        """
        return SettingsManager.ZOOM_PRESETS.get(zoom_level, 0.4)
