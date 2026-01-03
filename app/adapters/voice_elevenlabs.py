
"""ElevenLabs adapter placeholder"""
from pathlib import Path
from typing import Any
import subprocess

VERSION = "elevenlabs_v1"


def render(params: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "sine=frequency=660:duration=2",
        "-t", "2",
        str(output)
    ], check=True)
