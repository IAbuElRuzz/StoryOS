
"""ElevenLabs adapter placeholder"""
from pathlib import Path
import subprocess

VERSION = "elevenlabs_v1"

def render(params, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "sine=frequency=660:duration=2",
        str(output)
    ], check=True)
