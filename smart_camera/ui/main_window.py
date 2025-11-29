"""Main UI window for Smart Meeting Camera"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
from typing import Optional

from ..core.controller import CameraController
from ..core.tracking_state import TrackingStatus


class SmartCameraUI:
    """Main user interface for Smart Meeting Camera"""
    
    def __init__(self, controller: CameraController):
        """
        Initialize UI
        
        Args:
            controller: Camera controller instance
        """
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Smart Meeting Camera")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Preview
        self.preview_width = 640
        self.preview_height = 480
        self.current_image = None
        
        # Update flag
        self.updating = False
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create UI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Smart Meeting Camera",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Video preview
        self.canvas = tk.Canvas(
            main_frame,
            width=self.preview_width,
            height=self.preview_height,
            bg="black"
        )
        self.canvas.grid(row=1, column=0, columnspan=3, pady=10)
        
        # Status
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, columnspan=3, pady=5)
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(status_frame, text="● Inactive", foreground="red")
        self.status_label.pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(
            button_frame,
            text="Start",
            command=self._on_start,
            width=15
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="Stop",
            command=self._on_stop,
            width=15,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # FPS display
        self.fps_label = ttk.Label(main_frame, text="FPS: 0.0")
        self.fps_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Settings panel
        self._create_settings_panel(main_frame)
    
    def _create_settings_panel(self, parent: ttk.Frame) -> None:
        """Create settings panel"""
        settings_frame = ttk.LabelFrame(parent, text="Settings", padding="10")
        settings_frame.grid(row=5, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # Tracking speed
        ttk.Label(settings_frame, text="Tracking Speed:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        speed_frame = ttk.Frame(settings_frame)
        speed_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(speed_frame, text="Slow").pack(side=tk.LEFT)
        self.speed_slider = ttk.Scale(
            speed_frame,
            from_=0.1,
            to=0.9,
            orient=tk.HORIZONTAL,
            command=self._on_speed_change
        )
        self.speed_slider.set(self.controller.config.tracking_speed)
        self.speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(speed_frame, text="Fast").pack(side=tk.LEFT)
        
        # Zoom level
        ttk.Label(settings_frame, text="Zoom Level:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.zoom_var = tk.StringVar(value=self.controller.config.zoom_level)
        zoom_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.zoom_var,
            values=["close", "medium", "wide"],
            state="readonly",
            width=15
        )
        zoom_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        zoom_combo.bind("<<ComboboxSelected>>", self._on_zoom_change)
        
        # Face size
        ttk.Label(settings_frame, text="Face Size:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        size_frame = ttk.Frame(settings_frame)
        size_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.size_slider = ttk.Scale(
            size_frame,
            from_=0.3,
            to=0.5,
            orient=tk.HORIZONTAL,
            command=self._on_size_change
        )
        self.size_slider.set(self.controller.config.face_size_ratio)
        self.size_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.size_label = ttk.Label(size_frame, text=f"{int(self.controller.config.face_size_ratio * 100)}%")
        self.size_label.pack(side=tk.LEFT, padx=5)
    
    def _on_speed_change(self, value: str) -> None:
        """Handle tracking speed change"""
        speed = float(value)
        self.controller.config.tracking_speed = speed
        self.controller.update_settings(self.controller.config)
    
    def _on_zoom_change(self, event) -> None:
        """Handle zoom level change"""
        from ..config.settings import SettingsManager
        zoom_level = self.zoom_var.get()
        self.controller.config.zoom_level = zoom_level
        self.controller.config.face_size_ratio = SettingsManager.get_face_ratio_for_zoom(zoom_level)
        self.size_slider.set(self.controller.config.face_size_ratio)
        self.size_label.config(text=f"{int(self.controller.config.face_size_ratio * 100)}%")
        self.controller.update_settings(self.controller.config)
    
    def _on_size_change(self, value: str) -> None:
        """Handle face size change"""
        size = float(value)
        self.controller.config.face_size_ratio = size
        self.size_label.config(text=f"{int(size * 100)}%")
        self.controller.update_settings(self.controller.config)
    
    def _on_start(self) -> None:
        """Handle start button click"""
        success = self.controller.start()
        
        if success:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.set_status("Active", "green")
            self._start_preview_update()
        else:
            error_msg = self.controller.error_message or "Failed to start camera"
            self.show_error(error_msg)
    
    def _on_stop(self) -> None:
        """Handle stop button click"""
        self.controller.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.set_status("Inactive", "red")
        self.updating = False
        
        # Clear preview
        self.canvas.delete("all")
    
    def _start_preview_update(self) -> None:
        """Start preview update loop"""
        self.updating = True
        self._update_preview()
    
    def _update_preview(self) -> None:
        """Update preview with latest frame"""
        if not self.updating:
            return
        
        # Get frame from controller
        frame = self.controller.get_preview_frame(timeout=0.033)
        
        if frame is not None:
            # Get status for overlay
            status = self.controller.get_status()
            
            # Draw face detection box if tracking
            if status.tracking_status == TrackingStatus.TRACKING:
                # Draw green box indicator (simplified - just a corner indicator)
                cv2.rectangle(frame, (10, 10), (30, 30), (0, 255, 0), 2)
            
            # Resize for preview
            display_frame = cv2.resize(frame, (self.preview_width, self.preview_height))
            
            # Convert to PhotoImage
            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(image=img)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.current_image = photo  # Keep reference
            
            # Update FPS
            self.fps_label.config(text=f"FPS: {status.current_fps:.1f}")
        
        # Schedule next update (30fps = ~33ms)
        if self.updating:
            self.root.after(33, self._update_preview)
    
    def set_status(self, status: str, color: str) -> None:
        """
        Set status text and color
        
        Args:
            status: Status text
            color: Color name (green, red, yellow)
        """
        self.status_label.config(text=f"● {status}", foreground=color)
    
    def show_error(self, message: str) -> None:
        """
        Show error dialog
        
        Args:
            message: Error message
        """
        messagebox.showerror("Error", message)
    
    def _on_closing(self) -> None:
        """Handle window close"""
        if self.controller.running:
            self.controller.stop()
        self.root.destroy()
    
    def start(self) -> None:
        """Start the UI main loop"""
        self.root.mainloop()
