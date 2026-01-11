"""
SSI stream file to AVI converter using OpenCV
Usage: python convert_video.py
"""

import cv2
import numpy as np
import os

def convert_stream_to_avi(stream_path, output_path, fps=25.0):
    """Convert SSI stream file to AVI"""
    
    # Read the stream header file
    header_file = stream_path + ".stream"
    data_file = stream_path + ".stream~"
    
    if not os.path.exists(header_file):
        print(f"Header file not found: {header_file}")
        return False
    
    if not os.path.exists(data_file):
        print(f"Data file not found: {data_file}")
        return False
    
    # Parse header to get video dimensions
    width, height, channels = 640, 480, 3  # Default values
    
    with open(header_file, 'r') as f:
        content = f.read()
        # Extract width, height from meta tag
        if 'width="' in content:
            width = int(content.split('width="')[1].split('"')[0])
        if 'height="' in content:
            height = int(content.split('height="')[1].split('"')[0])
        if 'channels="' in content:
            channels = int(content.split('channels="')[1].split('"')[0])
    
    print(f"Video dimensions: {width}x{height}, channels: {channels}")
    
    # Calculate frame size
    frame_size = width * height * channels
    
    # Read binary data
    with open(data_file, 'rb') as f:
        data = f.read()
    
    num_frames = len(data) // frame_size
    print(f"Number of frames: {num_frames}")
    print(f"Duration: {num_frames / fps:.2f} seconds")
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        print("Failed to create video writer")
        return False
    
    # Write frames
    for i in range(num_frames):
        start = i * frame_size
        end = start + frame_size
        frame_data = data[start:end]
        
        # Convert to numpy array and reshape
        frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((height, width, channels))
        
        # SSI stores as RGB, OpenCV expects BGR
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Flip vertically (SSI stores upside down)
        frame_bgr = cv2.flip(frame_bgr, 0)
        
        out.write(frame_bgr)
        
        if (i + 1) % 25 == 0:
            print(f"Processed {i + 1}/{num_frames} frames...")
    
    out.release()
    print(f"Video saved to: {output_path}")
    return True

if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    
    # Convert User A video
    print("=== Converting User A video ===")
    convert_stream_to_avi(
        os.path.join(data_dir, "user_a_video"),
        os.path.join(data_dir, "output_video_A_cv.avi"),
        fps=25.0
    )
    
    print()
    
    # Convert User B video
    print("=== Converting User B video ===")
    convert_stream_to_avi(
        os.path.join(data_dir, "user_b_video"),
        os.path.join(data_dir, "output_video_B_cv.avi"),
        fps=25.0
    )
    
    print("\nDone!")
