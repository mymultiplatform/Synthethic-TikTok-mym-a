import cv2
import numpy as np
from PIL import Image
import io
import pyttsx3
from pathlib import Path
from dotenv import load_dotenv
import os
from typing import Tuple, List

load_dotenv()

SAVE_PATH = os.getenv("SAVE_PATH")

# Function to generate video with synchronized audio
def generate_video(news: List[dict], 
                   audio_files: List[str], 
                   video_name: str, 
                   fps: int = 24,
                   frame_size: Tuple[int, int] = (1080, 1920),
                   item_duration: float = 14.0) -> None:
    """Main entry point to generate videos

    Args:
        news (List[dict]): A list containing multiple news items, each contained in a dictionary with the keys "title", "description" and "image_data"
        audio_files (List[str]): A list of paths towards the coresponding Audio files of each item, currently unused for some reason
        video_name (str): name of the video's filename
        fps (int, optional): Frames per second (FPS) of the video. Defaults to 24.
        frame_size (Tuple[int, int], optional): The resolution of the video of the video. Defaults to (1080, 1920).
        item_duration (float, optional): How much time to cover each source material. Defaults to 14.0.
    """
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    num_frames_per_word = fps * item_duration
    num_frames = num_frames_per_word * len(news)
    video_filename = SAVE_PATH / f"{video_name}.mp4"
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

def data_to_image(image_data):
    try:
        img = Image.open(io.BytesIO(image_data))
        return img
    except Exception as e:
        print(f"Failed to convert image data: {e}")
        return None

# Use eleven labs instead

# Use Sovits based TTS instead

# Function to convert text to speech and save as audio files
def text_to_speech(news: List[dict]) -> List[str]:
    engine = pyttsx3.init()
    audio_files = []
    for i, news_data in enumerate(news):
        title = news_data["title"]
        description = news_data["description"]
        text = f"{title}. {description}"
        audio_path = f"news_{i + 1}.wav"
        engine.save_to_file(text, audio_path)
        audio_files.append(Path(audio_path))
    engine.runAndWait()
    return audio_files

# # Function to convert text to speech and save as audio files
# def text_to_speech_one(news: dict) -> str:
#     engine = pyttsx3.init()
#     for i, news_data in enumerate(news):
#         title = news_data["title"]
#         description = news_data["description"]
#         text = f"{title}. {description}"
#         audio_path = f"news_{i + 1}.wav"
#         engine.save_to_file(text, audio_path)
#     engine.runAndWait()
#     return audio_path