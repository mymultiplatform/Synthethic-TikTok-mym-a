import numpy as np
import cv2
import tkinter as tk
from tkinter import filedialog
import os

# Set up video parameters
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
fps = 24  # Frames per second
frame_size = (640, 480)  # Frame size (width, height)
letter_duration = 10  # Duration for each letter in seconds
num_frames_per_letter = fps * letter_duration  # Total number of frames per letter
num_frames = num_frames_per_letter * 3  # Total frames for A, B, and C

# Create a VideoWriter object
video_path = 'alphabet_video.mp4'
out = cv2.VideoWriter(video_path, fourcc, fps, frame_size)

# Define the letters and positions
letters = ["A", "B", "C"]
letter_positions = [(320, 240), (320, 240), (320, 240)]  # Center positions for the letters

# Generate synthetic frames
for i in range(num_frames):
    # Create a blank canvas (frame)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Calculate which letter should be displayed
    letter_index = i // num_frames_per_letter
    letter = letters[letter_index]

    # Example: Draw a moving circle (watermark)
    center_x = int(320 + 100 * np.sin(2 * np.pi * i / num_frames_per_letter))
    center_y = int(240 + 100 * np.cos(2 * np.pi * i / num_frames_per_letter))
    color = (255, 255, 255)  # White circle
    cv2.circle(frame, (center_x, center_y), 50, color, -1)

    # Add the letter to the frame
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 5
    font_thickness = 10
    text_size = cv2.getTextSize(letter, font, font_scale, font_thickness)[0]
    text_x = int((frame_size[0] - text_size[0]) / 2)
    text_y = int((frame_size[1] + text_size[1]) / 2)
    cv2.putText(frame, letter, (text_x, text_y), font, font_scale, color, font_thickness, lineType=cv2.LINE_AA)

    # Write the frame to the video
    out.write(frame)

# Release the video writer
out.release()

# Set up tkinter GUI
def download_video():
    # Ask user where to save the file
    save_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
    if save_path:
        # Copy the video to the chosen location
        os.rename(video_path, save_path)
        print("Video saved successfully.")

# Create the main window
root = tk.Tk()
root.title("Download MP4 Video")

# Create a "Download" button
download_button = tk.Button(root, text="Download", command=download_video)
download_button.pack(pady=20)

# Start the GUI event loop
root.mainloop()
