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
    print("Fetching news...")
    try:
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        driver.get("https://www.bbc.com/news")
        time.sleep(20)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        articles = soup.find_all('h2', {"data-testid": "card-headline"}, limit=3)
        news = []
        for article in articles:
            title = article.text if article else "No title available."
            description = article.find_next('p').text if article.find_next('p') else "No description available."
            image_tag = article.find_previous('img')
            image_data = None
            if image_tag and 'src' in image_tag.attrs:
                image_url = image_tag['src']
                driver.get(image_url)
                image_data = driver.get_screenshot_as_png()
            news.append((title, description, image_data))
        driver.quit()
        return news
    except Exception as e:
        print(f"Failed to fetch news: {e}")
        return [("Error", f"Failed to fetch news: {e}", None)]

def data_to_image(image_data):
    try:
        img = Image.open(io.BytesIO(image_data))
        return img
    except Exception as e:
        print(f"Failed to convert image data: {e}")
        return None

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

def generate_video(news, audio_files):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 24
    frame_size = (1080, 1920)  # Adjusted resolution for TikTok
    word_duration = 14
    num_frames_per_word = fps * word_duration
    num_frames = num_frames_per_word * len(news)
    video_path = 'news_video.mp4'
    out = cv2.VideoWriter(video_path, fourcc, fps, frame_size)

    for i in range(num_frames):
        paragraph_index = i // num_frames_per_word
        frame = np.zeros((1920, 1080, 3), dtype=np.uint8)  # Black background by default

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
                img = img.resize((800, 800), Image.ANTIALIAS)  # Resize image to 100x100 for debugging
                img_np = np.array(img)
                if img_np.shape[2] == 4:
                    img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)
                
                img_y, img_x, _ = img_np.shape
                # Calculate the center position for the image
                center_x = (frame_size[0] - img_x) // 2
                center_y = (frame_size[1] - img_y) // 2
                # Place the image at the center
                frame[center_y:center_y + img_y, center_x:center_x + img_x] = img_np

        y0, dy = 1500, 60  # Adjusted y-position for high-resolution text overlay
        for j, line in enumerate(wrapped_text):
            text_size = cv2.getTextSize(line, font, font_scale, font_thickness)[0]
            text_x = int((frame_size[0] - text_size[0]) / 2)
            text_y = y0 + j * dy
            cv2.putText(frame, line, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness, lineType=cv2.LINE_AA)

        out.write(frame)

    out.release()

    video_clip = mpe.VideoFileClip(video_path)
    audio_clips = [mpe.AudioFileClip(audio) for audio in audio_files]
    audio_start_times = [i * word_duration for i in range(len(news))]
    final_audio = mpe.CompositeAudioClip([
        audio_clips[i].set_start(audio_start_times[i])
        for i in range(len(news))
    ])
    final_clip = video_clip.set_audio(final_audio)
    final_clip.write_videofile("final_news_video_with_audio.mp4", codec="libx264", fps=fps)

    for audio in audio_files:
        os.remove(audio)

    print("Video with synchronized audio saved successfully.")

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

def display_news():
    for widget in news_frame.winfo_children():
        widget.destroy()

    news_data = fetch_news()
    audio_files = text_to_speech(news_data)
    generate_video(news_data, audio_files)

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
                img_label.image = img_tk
                img_label.grid(row=i*3+2, column=0, sticky="w", padx=10, pady=5)

root = tk.Tk()
root.title("Top News")
root.geometry("250x100")

news_frame = tk.Frame(root)
news_frame.pack(fill="both", expand=True)

connect_button = tk.Button(root, text="Connect", command=display_news, font=("Arial", 12))
connect_button.pack(pady=20)

root.mainloop()
