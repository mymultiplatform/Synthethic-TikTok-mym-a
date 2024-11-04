from flask import Flask, send_from_directory, render_template_string
import os

app = Flask(__name__)
video_dir = "path_to_your_video_directory"

@app.route("/")
def home():
    videos = os.listdir(video_dir)
    video_links = [f"/videos/{video}" for video in videos]
    html_template = """
    <h1>Video Library</h1>
    <ul>{% for link, name in videos %}<li><a href="{{ link }}">{{ name }}</a></li>{% endfor %}</ul>
    """
    return render_template_string(html_template, videos=zip(video_links, videos))

@app.route("/videos/<path:filename>")
def download_file(filename):
    return send_from_directory(video_dir, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
