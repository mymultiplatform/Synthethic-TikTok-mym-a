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

# Function to scrape the news using Selenium and BeautifulSoup
def fetch_news():
    print("Fetching news...")  # Debugging statement
    try:
        # Set up Selenium with Firefox WebDriver
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        driver.get("https://www.bbc.com/news")
        
        # Wait for the page to load fully
        time.sleep(20)  # Increased wait time to 20 seconds
        
        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Fetching news articles based on the updated structure
        articles = soup.find_all('h2', {"data-testid": "card-headline"}, limit=3)
        news = []
        for article in articles:
            title = article.text if article else "No title available."
            description = article.find_next('p').text if article.find_next('p') else "No description available."
            image_tag = article.find_previous('img')  # Finding the image tag related to the article
            image_data = None
            if image_tag and 'src' in image_tag.attrs:
                image_url = image_tag['src']
                driver.get(image_url)  # Open the image URL directly
                image_data = driver.get_screenshot_as_png()  # Capture image data
            news.append((title, description, image_data))
            print(f"Title: {title}")  # Print fetched title for debugging
            print(f"Description: {description}")
        
        # Close the browser
        driver.quit()
        
        return news
    except Exception as e:
        print(f"Failed to fetch news: {e}")  # Debugging statement
        return [("Error", f"Failed to fetch news: {e}", None)]

# Function to convert image data to a PIL Image
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
        audio_files.append(audio_path)
    engine.runAndWait()
    return audio_files

# Function to generate the news video with images and audio
def generate_video(news, audio_files):
    # Set up video parameters
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
    fps = 24  # Frames per second
    frame_size = (640, 480)  # Frame size (width, height)
    word_duration = 14  # Duration for each paragraph in seconds
    num_frames_per_word = fps * word_duration  # Total number of frames per word
    num_frames = num_frames_per_word * len(news)  # Total frames for all news

    # Define the background colors for each news item
    background_colors = [
        (0, 0, 255),   # Red for the first news item
        (0, 255, 255), # Yellow for the second news item
        (255, 0, 0)    # Blue for the third news item
    ]

    # Create the "ReadyVideos" folder on the desktop if it doesn't exist
    desktop_path = r"C:\Users\ds1020254\Desktop"
    ready_videos_path = os.path.join(desktop_path, "ReadyVideos")
    if not os.path.exists(ready_videos_path):
        os.makedirs(ready_videos_path)

    # Find a unique filename for the output video
    video_index = 1
    video_filename = f"final_news_video_with_audio{video_index}.mp4"
    video_path = os.path.join(ready_videos_path, video_filename)
    while os.path.exists(video_path):
        video_index += 1
        video_filename = f"final_news_video_with_audio{video_index}.mp4"
        video_path = os.path.join(ready_videos_path, video_filename)

    # Create a VideoWriter object
    out = cv2.VideoWriter(video_path, fourcc, fps, frame_size)

    # Generate synthetic frames
    for i in range(num_frames):
        # Create a blank canvas (frame)
        paragraph_index = i // num_frames_per_word
        frame = np.full((480, 640, 3), background_colors[paragraph_index], dtype=np.uint8)

        # Extract the title, description, and image for the current paragraph
        title, description, image_data = news[paragraph_index]
        text = f"{title}: {description}"

        # Add the text to the frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        font_thickness = 2

        # Wrap text to fit within the frame
        max_line_width = frame_size[0] - 40  # Set a maximum line width with some padding
        wrapped_text = wrap_text(text, font, font_scale, max_line_width)

        # Start drawing text from the top, centered horizontally
        y0, dy = 50, 25  # Start position and line height
        for j, line in enumerate(wrapped_text):
            text_size = cv2.getTextSize(line, font, font_scale, font_thickness)[0]
            text_x = int((frame_size[0] - text_size[0]) / 2)
            text_y = y0 + j * dy
            cv2.putText(frame, line, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness, lineType=cv2.LINE_AA)

        # Add the image to the frame if available
        if image_data:
            img = data_to_image(image_data)
            if img:
                img.thumbnail((320, 240))  # Resize the image to fit within the frame
                img_np = np.array(img)

                # Check if the image has 4 channels (RGBA)
                if img_np.shape[2] == 4:
                    img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)  # Convert RGBA to RGB

                img_y, img_x, _ = img_np.shape
                y_offset = frame_size[1] - img_y - 10
                x_offset = int((frame_size[0] - img_x) / 2)
                frame[y_offset:y_offset+img_y, x_offset:x_offset+img_x] = img_np

        # Write the frame to the video
        out.write(frame)

    # Release the video writer
    out.release()

    # Combine the video and audio using moviepy
    video_clip = mpe.VideoFileClip(video_path)

    # Load and set the audio files to the respective portions of the video
    audio_clips = [mpe.AudioFileClip(audio) for audio in audio_files]

    # Define the start time of each paragraph's audio
    audio_start_times = [i * word_duration for i in range(len(news))]

    # Add the audio clips to the video at the correct time
    final_audio = mpe.CompositeAudioClip([
        audio_clips[i].set_start(audio_start_times[i])
        for i in range(len(news))
    ])

    # Set the audio to the video clip
    final_clip = video_clip.set_audio(final_audio)

    # Write the final output to a file
    final_clip.write_videofile(video_path, codec="libx264", fps=fps)

    # Clean up the temporary audio files
    for audio in audio_files:
        os.remove(audio)

    print("Video with synchronized audio saved successfully.")

# Function to wrap text so that it fits within a given width
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
            lines.append(current_line)
            current_line = word + ' '

    lines.append(current_line.strip())
    return lines

# Function to display the news in the GUI
def display_news():
    print("Displaying news...")  # Debugging statement
    
    # Clear any existing content in the news_frame
    for widget in news_frame.winfo_children():
        widget.destroy()
    
    # Fetch the news data
    news_data = fetch_news()
    
    # Convert news to speech
    audio_files = text_to_speech(news_data)
    
    # Generate the video with the news and audio
    generate_video(news_data, audio_files)
    
    # Display the news data in the GUI
    for i, (title, description, image_data) in enumerate(news_data):
        title_label = tk.Label(news_frame, text=title, font=("Arial", 14, "bold"))
        title_label.grid(row=i*3, column=0, sticky="w", padx=10, pady=5)
        
        desc_label = tk.Label(news_frame, text=description, wraplength=600, justify="left")
        desc_label.grid(row=i*3+1, column=0, sticky="w", padx=10, pady=5)
        
        if image_data:
            img = data_to_image(image_data)
            if img:
                img.thumbnail((300, 200))
                img_tk = ImageTk.PhotoImage(img)
                img_label = tk.Label(news_frame, image=img_tk)
                img_label.image = img_tk  # Keep a reference to avoid garbage collection
                img_label.grid(row=i*3+2, column=0, sticky="w", padx=10, pady=5)
    
    print("News displayed!")  # Debugging statement

# Set up the main window
root = tk.Tk()
root.title("Top News")
root.geometry("300x400")

# Create a frame to hold the news
news_frame = tk.Frame(root)
news_frame.pack(fill="both", expand=True)

# Add a "Connect" button to start fetching and displaying the news
connect_button = tk.Button(root, text="Connect", command=display_news, font=("Arial", 12))
connect_button.pack(pady=20)

# Start the GUI loop
root.mainloop()
