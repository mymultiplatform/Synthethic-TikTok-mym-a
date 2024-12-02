# Function to upload video to GitHub
import subprocess


def upload_video_to_github(video_path):
    # Prepare the PowerShell command
    # Escaping quotes for PowerShell
    command = (
        f'copy "{video_path}" .; '
        f'git add {video_path.name}; '
        f'git commit -m "Add {video_path.name}"; '
        f'git push origin main'
    )
    # Execute the command in PowerShell
    subprocess.run(["powershell", "-Command", command], check=True)
    
# TODO: upload to youtube via API
def upload_to_youtube():
    pass

# TODO: upload to tiktok via API