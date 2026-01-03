
from pathlib import Path
import subprocess

def render(video: Path, audio: Path, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video),
        "-i", str(audio),
        "-c:v", "copy",
        "-c:a", "aac",
        str(output)
    ], check=True)
