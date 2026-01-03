"""
FFmpeg video concatenation adapter.
Combines multiple video files into a single continuous video.
"""
from pathlib import Path
import subprocess
import tempfile


def render(videos: list[Path], output: Path) -> None:
    """
    Concatenate multiple videos into one using ffmpeg.

    Args:
        videos: List of video file paths to concatenate (in order)
        output: Output path for the concatenated video
    """
    if not videos:
        raise ValueError("No videos provided for concatenation")

    if len(videos) == 1:
        # Single video - just copy it
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(videos[0].read_bytes())
        return

    output.parent.mkdir(parents=True, exist_ok=True)

    # Create a temporary file list for ffmpeg concat demuxer
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        concat_file = Path(f.name)
        for video in videos:
            # Use absolute paths and escape special characters
            abs_path = video.resolve()
            f.write(f"file '{abs_path}'\n")

    try:
        print(f"Concatenating {len(videos)} videos...")

        # Use concat demuxer for fast concatenation (no re-encoding)
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",  # Copy codec (no re-encoding)
            str(output)
        ], check=True, capture_output=True)

        print(f"   ✓ Concatenated video saved to: {output}")
    finally:
        # Clean up temp file
        concat_file.unlink(missing_ok=True)
