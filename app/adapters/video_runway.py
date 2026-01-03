
"""
Real adapter placeholder.
Replace render() body with Runway or Pika API calls.
"""
from pathlib import Path
import subprocess

VERSION = "runway_v1"

def render(params, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    duration = params.get("duration", 4)

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "color=c=black:s=1280x720",
        "-t", str(duration),
        str(output)
    ], check=True)
