import tkinter as tk
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import time
import numpy as np
import cv2
import pyttsx3
import os
import moviepy.editor as mpe
from PIL import Image, ImageTk
import io
import subprocess
from pathlib import Path
import threading
import sys

# Path configurations
DESKTOP_PATH = Path("C:/Users/hola master/Desktop")
BRAINVID_PATH = DESKTOP_PATH / "brainvid"
REPO_PATH = Path("C:/Users/hola master/mp4myma")

# Ensure the brainvid directory exists
BRAINVID_PATH.mkdir(parents=True, exist_ok=True)

# Function to determine the next video number
def get_next_video_number():
    existing_videos = sorted(BRAINVID_PATH.glob("*.mp4"), key=lambda x: x.stem)
    if not existing_videos:
        return 1
    last_video = existing_videos[-1]
    try:
        return int(last_video.stem) + 1
    except ValueError:
        return last_video.stem + "_new"

# Function to upload video to GitHub
def upload_video_to_github(video_path):
    # Prepare the PowerShell command
    # Escaping quotes for PowerShell
    command = (
        f'cd "{REPO_PATH}"; '
        f'copy "{video_path}" .; '
        f'git add {video_path.name}; '
        f'git commit -m "Add {video_path.name}"; '
        f'git push origin main'
    )
    # Execute the command in PowerShell
    subprocess.run(["powershell", "-Command", command], check=True)

# Function to fetch news using Selenium and BeautifulSoup
def fetch_news():
    print("Fetching news...")
    try:
        # Initialize the Firefox driver
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        driver.get("https://www.bbc.com/news")

        # Wait for the page to load completely
        time.sleep(20)  # Consider replacing with WebDriverWait for better reliability

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find the top 3 news articles
        articles = soup.find_all('h2', {"data-testid": "card-headline"}, limit=3)
        news = []
        for article in articles:
            title = article.text.strip() if article else "No title available."
            description_tag = article.find_next('p')
            description = description_tag.text.strip() if description_tag else "No description available."

            # Attempt to find the associated image
            image_tag = article.find_previous('img')
            image_data = None
            if image_tag and 'src' in image_tag.attrs:
                image_url = image_tag['src']
                try:
                    driver.get(image_url)
                    time.sleep(2)  # Short wait to ensure image loads
                    image_data = driver.get_screenshot_as_png()
                except Exception as img_e:
                    print(f"Failed to fetch image: {img_e}")

            news.append((title, description, image_data))

        driver.quit()
        return news
    except Exception as e:
        print(f"Failed to fetch news: {e}")
        return [("Error", f"Failed to fetch news: {e}", None)]

# Function to convert image data to PIL Image
def data_to_image(image_data):
    try:
        img = Image.open(io.BytesIO(image_data))
        return img
    except Exception as e:
        print(f"Failed to convert image data: {e}")
        return None

# Function to convert text to speech and save as audio files
def text_to_speech(news):
    engine = pyttsx3.init()
    audio_files = []
    for i, (title, description, _) in enumerate(news):
        text = f"{title}. {description}"
        audio_path = f"news_{i + 1}.wav"
        engine.save_to_file(text, audio_path)
        audio_files.append(Path(audio_path))
    engine.runAndWait()
    return audio_files

# Function to wrap text for video display
def wrap_text(text, font, font_scale, max_width):
    words = text.split(' ')
    lines = []
    current_line = ''

    for word in words:
        test_line = current_line + word + ' '
        text_size = cv2.getTextSize(test_line, font, font_scale, 1)[0]
        if text_size[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + ' '

    if current_line:
        lines.append(current_line.strip())
    return lines

# Function to generate video with synchronized audio
def generate_video(news, audio_files, video_number):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 24
    frame_size = (1080, 1920)  # 9:16 aspect ratio for TikTok
    word_duration = 14  # Duration per news item in seconds
    num_frames_per_word = fps * word_duration
    num_frames = num_frames_per_word * len(news)
    video_filename = BRAINVID_PATH / f"{video_number}.mp4"
    out = cv2.VideoWriter(str(video_filename), fourcc, fps, frame_size)

    for i in range(num_frames):
        paragraph_index = i // num_frames_per_word
        frame = np.zeros((frame_size[1], frame_size[0], 3), dtype=np.uint8)  # Black background

        if paragraph_index >= len(news):
            paragraph_index = len(news) - 1  # Prevent index out of range

        title, description, image_data = news[paragraph_index]
        text = f"{title}: {description}"

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.5
        font_thickness = 3
        max_line_width = frame_size[0] - 40
        wrapped_text = wrap_text(text, font, font_scale, max_line_width)

        if image_data:
            img = data_to_image(image_data)
            if img:
                # Resize image using the updated Resampling method
                img = img.resize((800, 800), Image.Resampling.LANCZOS)  # Updated line
                img_np = np.array(img)
                if img_np.shape[2] == 4:
                    img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)

                img_y, img_x, _ = img_np.shape
                # Calculate the center position for the image
                center_x = (frame_size[0] - img_x) // 2
                center_y = (frame_size[1] - img_y) // 2
                # Ensure image fits within the frame
                if center_x < 0 or center_y < 0:
                    print("Image is too large to fit on the frame.")
                else:
                    # Place the image at the center
                    frame[center_y:center_y + img_y, center_x:center_x + img_x] = img_np

        y0, dy = 1500, 60  # Positioning text near the bottom for high-resolution
        for j, line in enumerate(wrapped_text):
            text_size = cv2.getTextSize(line, font, font_scale, font_thickness)[0]
            text_x = int((frame_size[0] - text_size[0]) / 2)
            text_y = y0 + j * dy
            cv2.putText(frame, line, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness, lineType=cv2.LINE_AA)

        out.write(frame)

    out.release()

    # Combine video with audio using MoviePy
    try:
        video_clip = mpe.VideoFileClip(str(video_filename))
        audio_clips = [mpe.AudioFileClip(str(audio)) for audio in audio_files]
        audio_start_times = [i * word_duration for i in range(len(news))]
        final_audio = mpe.CompositeAudioClip([
            audio_clips[i].set_start(audio_start_times[i])
            for i in range(len(news))
        ])
        final_clip = video_clip.set_audio(final_audio)
        final_clip.write_videofile(str(video_filename), codec="libx264", fps=fps)
    except Exception as e:
        print(f"Failed to combine video and audio: {e}")

    # Clean up temporary audio files
    for audio in audio_files:
        try:
            os.remove(audio)
        except Exception as e:
            print(f"Failed to remove audio file {audio}: {e}")

    print(f"Video {video_number} with synchronized audio saved successfully.")
    return video_filename

# Function to handle the video generation and upload process
def automate_video_generation():
    try:
        # Initial Test: Generate and upload two videos with 3 minutes interval
        for test_run in range(2):
            video_number = get_next_video_number()
            news_data = fetch_news()
            audio_files = text_to_speech(news_data)
            video_path = generate_video(news_data, audio_files, video_number)
            upload_video_to_github(video_path)
            print(f"Uploaded video {video_number}.mp4 to GitHub.")
            if test_run == 0:
                print("Waiting for 3 minutes before generating the next test video...")
                time.sleep(3 * 60)  # Wait for 3 minutes

        print("Initial test completed. Starting hourly video generation...")

        # Continuous Loop: Generate and upload a new video every hour
        while True:
            video_number = get_next_video_number()
            news_data = fetch_news()
            audio_files = text_to_speech(news_data)
            video_path = generate_video(news_data, audio_files, video_number)
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

# Function to display news and start automation
def display_news():
    threading.Thread(target=automate_video_generation, daemon=True).start()
    print("Automation started. Check the console for updates.")

# Initialize the Tkinter GUI
root = tk.Tk()
root.title("Top News Video Generator")
root.geometry("300x150")

news_frame = tk.Frame(root)
news_frame.pack(fill="both", expand=True)

connect_button = tk.Button(root, text="Start Automation", command=display_news, font=("Arial", 12))
connect_button.pack(pady=50)

root.mainloop()
