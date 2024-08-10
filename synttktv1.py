import numpy as np
import cv2
import pyttsx3
import os
import moviepy.editor as mpe

# Set up video parameters
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
fps = 24  # Frames per second
frame_size = (640, 480)  # Frame size (width, height)
word_duration = 10  # Duration for each word in seconds
num_frames_per_word = fps * word_duration  # Total number of frames per word
num_frames = num_frames_per_word * 3  # Total frames for Hello, Bye, and Love

# Create a VideoWriter object
video_path = 'alphabet_video.mp4'
out = cv2.VideoWriter(video_path, fourcc, fps, frame_size)

# Define the words and positions
words = ["Hello", "Bye", "Love"]
word_positions = [(320, 240), (320, 240), (320, 240)]  # Center positions for the words

# Initialize the TTS engine
engine = pyttsx3.init()

# Generate audio files for each word
audio_files = []
for word in words:
    audio_path = f"{word}.wav"
    audio_files.append(audio_path)
    engine.save_to_file(word, audio_path)
engine.runAndWait()

# Generate synthetic frames
for i in range(num_frames):
    # Create a blank canvas (frame)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Calculate which word should be displayed
    word_index = i // num_frames_per_word
    word = words[word_index]

    # Example: Draw a moving circle (watermark)
    center_x = int(320 + 100 * np.sin(2 * np.pi * i / num_frames_per_word))
    center_y = int(240 + 100 * np.cos(2 * np.pi * i / num_frames_per_word))
    color = (255, 255, 255)  # White circle
    cv2.circle(frame, (center_x, center_y), 50, color, -1)

    # Add the word to the frame
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 3
    font_thickness = 7
    text_size = cv2.getTextSize(word, font, font_scale, font_thickness)[0]
    text_x = int((frame_size[0] - text_size[0]) / 2)
    text_y = int((frame_size[1] + text_size[1]) / 2)
    cv2.putText(frame, word, (text_x, text_y), font, font_scale, color, font_thickness, lineType=cv2.LINE_AA)

    # Write the frame to the video
    out.write(frame)

# Release the video writer
out.release()

# Combine the video and audio using moviepy
video_clip = mpe.VideoFileClip(video_path)

# Load and set the audio files to the respective portions of the video
audio_clips = [mpe.AudioFileClip(audio) for audio in audio_files]

# Define the start time of each word's audio
audio_start_times = [i * word_duration for i in range(len(words))]

# Add the audio clips to the video at the correct time
final_audio = mpe.CompositeAudioClip([
    audio_clips[0].set_start(audio_start_times[0]),
    audio_clips[1].set_start(audio_start_times[1]),
    audio_clips[2].set_start(audio_start_times[2])
])

# Set the audio to the video clip
final_clip = video_clip.set_audio(final_audio)

# Write the final output to a file
final_clip.write_videofile("final_alphabet_video_with_audio.mp4", codec="libx264", fps=fps)

# Clean up the temporary audio files
for audio in audio_files:
    os.remove(audio)

print("Video with synchronized audio saved successfully.")
