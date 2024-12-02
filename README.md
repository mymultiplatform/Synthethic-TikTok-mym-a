# Synthetic TikTok - MYM-Z

## Overview

Synthetic TikTok is a Python-based project that automates the generation of TikTok-style videos by fetching the latest news, converting it into text-to-speech, creating a video with synchronized audio and text, and uploading the result to a GitHub repository. This project utilizes tools like Selenium for web scraping, OpenCV for video creation, pyttsx3 for text-to-speech, and MoviePy for video editing.

## Features

- **Fetch News**: Automatically scrapes top news articles from BBC using Selenium and BeautifulSoup.
- **Text-to-Speech**: Converts fetched news articles into speech using pyttsx3.
- **Video Creation**: Generates a TikTok-style video with the news, including text and images (if available) displayed on a black background.
- **Automatic Upload**: Uploads the generated video to a GitHub repository.
- **Automation**: Continuous video generation every hour, with a configurable 3-minute interval between test runs.

## Requirements

- Python 3.x
- Selenium
- pyttsx3
- OpenCV
- MoviePy
- PIL (Pillow)
- WebDriver Manager
- Git and PowerShell (for upload functionality)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/mymultiplatform/Synthetic-TikTok-mym-z.git
   cd Synthetic-TikTok-mym-z
   ```

2. Set up a virtual environment and install dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Usage

1. **Start Automation**:
   - Run the `main.py` file to initiate the Tkinter GUI. Press the "Start Automation" button to begin generating and uploading videos.
   
   ```bash
   python main.py
   ```

2. **Automation Process**:
   - The program will scrape the latest news, convert it to speech, create a video, and upload it to GitHub.
   - By default, it runs two test videos with a 3-minute interval and continues generating a video every hour thereafter.

## File Structure

- `brainvid/`: Folder where generated videos are saved.
- `main.py`: Main script to run the program and start the automation.
- `requirements.txt`: List of dependencies required to run the project.

## Contributing

Feel free to fork the repository and submit pull requests for improvements or bug fixes.

## License

This project is licensed under the MIT License.

## Contact

For questions, suggestions, or issues, please open an issue on the GitHub repository.
