from synthetic_tiktok.make_video import generate_video
from synthetic_tiktok.upload import upload_video_to_github, text_to_speech
from synthetic_tiktok.source_material import fetch_news

import threading
import tkinter as tk
import sys
import time
import os
from dotenv import load_dotenv

load_dotenv()

SAVE_PATH = os.getenv("SAVE_PATH")

def get_next_video_number():
    existing_videos = sorted(SAVE_PATH.glob("*.mp4"), key=lambda x: x.stem)
    if not existing_videos:
        return 1
    last_video = existing_videos[-1]
    try:
        return int(last_video.stem) + 1
    except ValueError:
        return last_video.stem + "_new"
    
    
# Function to display news and start automation
def display_news():
    threading.Thread(target=automate_video_generation, daemon=True).start()
    print("Automation started. Check the console for updates.")

# Function to handle the video generation and upload process
def automate_video_generation():
    try:
        # Initial Test: Generate and upload two videos with 3 minutes interval
        for test_run in range(2):
            video_number = get_next_video_number()
            news_data_list = fetch_news()
            audio_files = text_to_speech(news_data_list)
            video_path = generate_video(news_data_list, audio_files, video_number)
            upload_video_to_github(video_path)
            print(f"Uploaded video {video_number}.mp4 to GitHub.")
            if test_run == 0:
                print("Waiting for 3 minutes before generating the next test video...")
                time.sleep(3 * 60)  # Wait for 3 minutes

        print("Initial test completed. Starting hourly video generation...")

        # Continuous Loop: Generate and upload a new video every hour
        while True:
            video_number = get_next_video_number()
            news_data_list = fetch_news()
            audio_files = text_to_speech(news_data_list)
            video_path = generate_video(news_data_list, audio_files, video_number)
            upload_video_to_github(video_path)
            print(f"Uploaded video {video_number}.mp4 to GitHub.")
            print("Waiting for 1 hour before generating the next video...")
            time.sleep(60 * 60)  # Wait for 1 hour

    except KeyboardInterrupt:
        print("Automation stopped by user.")
        sys.exit()

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit()

# Initialize the Tkinter GUI
root = tk.Tk()
root.title("Top News Video Generator")
root.geometry("300x150")

news_frame = tk.Frame(root)
news_frame.pack(fill="both", expand=True)

connect_button = tk.Button(root, text="Start Automation", command=display_news, font=("Arial", 12))
connect_button.pack(pady=50)

root.mainloop()