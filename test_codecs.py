import cv2
import numpy as np
import os

def test_codec(codec, ext):
    filename = f"test_{codec}.{ext}"
    print(f"Testing codec: {codec} -> {filename}")
    
    width, height = 640, 480
    fps = 30
    
    try:
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        
        if not out.isOpened():
            print(f"❌ Failed to open VideoWriter for {codec}")
            return False
            
        # Write 30 frames (1 second)
        for _ in range(30):
            frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            out.write(frame)
            
        out.release()
        
        size = os.path.getsize(filename)
        print(f"✅ Successfully wrote {filename} ({size} bytes)")
        return True
        
    except Exception as e:
        print(f"❌ Error testing {codec}: {e}")
        return False

print("OpenCV Version:", cv2.__version__)

codecs_to_test = [
    ('mp4v', 'mp4'),
    ('avc1', 'mp4'),
    ('H264', 'mp4'),
    ('XVID', 'avi'),
    ('MJPG', 'avi')
]

results = {}
for codec, ext in codecs_to_test:
    results[codec] = test_codec(codec, ext)

print("\nSummary:")
for codec, success in results.items():
    print(f"{codec}: {'✅ Works' if success else '❌ Failed'}")
