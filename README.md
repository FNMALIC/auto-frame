# Smart Meeting Camera

Auto-framing camera for video calls and content creation using MediaPipe and OpenCV.

## Features

- 🎯 **Auto-framing**: Automatically tracks and frames your face during video calls
- 🎥 **Virtual Webcam**: Works with Zoom, Teams, Google Meet, OBS, and more
- 🔄 **Smooth Tracking**: Natural camera movements without jerkiness
- ⚙️ **Configurable**: Adjust tracking speed, zoom level, and face size
- 💻 **Lightweight**: Optimized for real-time performance

## Requirements

- Python 3.8 or higher
- Webcam
- Virtual camera driver (platform-specific)

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Virtual Camera Driver

#### Windows
- Install [OBS Studio](https://obsproject.com/) (includes OBS Virtual Camera)

#### Linux
```bash
sudo apt install v4l2loopback-dkms
sudo modprobe v4l2loopback
```

#### macOS
- Install [obs-mac-virtualcam](https://github.com/johnboiles/obs-mac-virtualcam)

### 3. Verify Installation

```bash
python setup.py
```

This will check that all dependencies are installed correctly.

## Usage

### Start the Application

```bash
python main.py
```

### Using the Interface

1. **Start**: Click the "Start" button to activate the virtual camera
2. **Preview**: Watch the auto-framing in action in the preview window
3. **Settings**: Adjust tracking speed, zoom level, and face size
4. **Stop**: Click "Stop" to deactivate

### Using with Video Conferencing Apps

1. Start Smart Meeting Camera
2. Click "Start"
3. Open your video conferencing app (Zoom, Teams, etc.)
4. Select "Smart Meeting Camera" as your camera device
5. Join your meeting!

## Settings

- **Tracking Speed**: Controls how quickly the camera follows your movements
  - Slow: Smoother, more gradual movements
  - Fast: More responsive, quicker adjustments

- **Zoom Level**: Preset framing options
  - Close: Tight framing (face is 50% of frame)
  - Medium: Balanced framing (face is 40% of frame)
  - Wide: Loose framing (face is 30% of frame)

- **Face Size**: Fine-tune how large your face appears (30-50%)

## Troubleshooting

### "No camera detected"
- Ensure your webcam is connected
- Check that no other application is using the camera
- Try a different camera index in settings

### "Virtual camera failed"
- Make sure the virtual camera driver is installed
- On Linux, verify v4l2loopback is loaded: `lsmod | grep v4l2loopback`
- On Windows, ensure OBS Studio is installed

### Low frame rate
- Close other applications using the camera
- Reduce the resolution in settings
- Check CPU usage

### Camera not appearing in video apps
- Restart the video conferencing application
- On some platforms, you may need to restart Smart Meeting Camera

## Configuration

Settings are automatically saved to `~/.smart_meeting_camera/config.json`

Logs are saved to `~/.smart_meeting_camera/logs/app.log`

## Command Line Options

```bash
python main.py --debug          # Enable debug logging
python main.py --config PATH    # Use custom config file
```

## Technical Details

- **Face Detection**: MediaPipe Face Detection
- **Video Processing**: OpenCV
- **Virtual Camera**: pyvirtualcam
- **Smoothing**: Exponential moving average with velocity limiting
- **Performance**: < 25% CPU usage, < 500MB memory

## License

MIT License

## Credits

Built with:
- [MediaPipe](https://google.github.io/mediapipe/) - Face detection
- [OpenCV](https://opencv.org/) - Video processing
- [pyvirtualcam](https://github.com/letmaik/pyvirtualcam) - Virtual camera
