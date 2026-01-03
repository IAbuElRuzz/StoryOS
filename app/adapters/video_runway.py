
"""
Runway Gen-3 Alpha Turbo video generation adapter.
Supports both real API and mock mode for development.
"""
from pathlib import Path
from typing import Any, Literal
import subprocess
import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

VERSION = "runway_gen3a_turbo_v1"

# Configuration
API_SECRET = os.getenv("RUNWAYML_API_SECRET", "")
RUNWAY_MODE = os.getenv("RUNWAY_MODE", "mock")  # "api" or "mock"


def _render_with_api(params: dict[str, Any], output: Path) -> None:
    """Use real Runway API to generate video."""
    try:
        from runwayml import RunwayML
        import runwayml
    except ImportError:
        print("Warning: runwayml package not installed. Falling back to mock mode.")
        _render_mock(params, output)
        return

    if not API_SECRET:
        print("Warning: RUNWAYML_API_SECRET not set. Falling back to mock mode.")
        _render_mock(params, output)
        return

    try:
        client = RunwayML(api_key=API_SECRET)

        # Extract parameters
        prompt = params.get("prompt", "A cinematic video")
        duration = params.get("duration", 4)
        ratio = params.get("ratio", "1280:720")

        print(f"🎬 Generating video with Runway Gen-3 Alpha Turbo...")
        print(f"   Prompt: {prompt}")
        print(f"   Duration: {duration}s")
        print(f"   Ratio: {ratio}")

        # Create image-to-video task
        # Note: Gen-3 Alpha Turbo requires a prompt_image
        # For text-to-video, we use a solid color as base
        # Valid ratios for gen3a_turbo: '768:1280' or '1280:768'
        valid_ratio: Literal["768:1280", "1280:768"] = "1280:768"
        if ratio == "768:1280":
            valid_ratio = "768:1280"

        # Valid durations for gen3a_turbo: 5 or 10
        valid_duration: Literal[5, 10] = 5 if duration <= 5 else 10

        # Create a simple solid color image URL as base
        # Using a data URL for a minimal image
        placeholder_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        task = client.image_to_video.create(
            model="gen3a_turbo",
            prompt_image=placeholder_image,
            prompt_text=prompt,
            duration=valid_duration,
            ratio=valid_ratio
        )

        task_id = task.id
        print(f"   Task ID: {task_id}")

        # Poll for completion
        max_wait = 300  # 5 minutes max
        start_time = time.time()

        # Retrieve initial status
        time.sleep(5)  # Wait a bit before first check
        status_task = client.tasks.retrieve(task_id)
        print(f"   Status: {status_task.status}")

        while status_task.status not in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            if time.time() - start_time > max_wait:
                raise TimeoutError(f"Video generation timed out after {max_wait}s")

            time.sleep(10)
            status_task = client.tasks.retrieve(task_id)
            print(f"   Status: {status_task.status} ({int(time.time() - start_time)}s elapsed)")

        if status_task.status == 'SUCCEEDED':
            # Download the generated video
            video_url = status_task.output[0] if status_task.output else None
            if not video_url:
                raise ValueError("No video URL in successful task output")

            print("Video generated successfully!")
            print(f"   Downloading from: {video_url}")

            # Download video
            response = requests.get(video_url, timeout=60)
            response.raise_for_status()
            output.write_bytes(response.content)

            print(f"   Saved to: {output}")
        else:
            error_msg = f"Video generation failed with status: {status_task.status}"
            if hasattr(status_task, 'failure'):
                error_msg += f"\n   Error: {status_task.failure}"
            raise RuntimeError(error_msg)

    except runwayml.APIConnectionError as e:
        print(f"Error: Could not connect to Runway API: {e}")
        print("Falling back to mock mode...")
        _render_mock(params, output)
    except runwayml.RateLimitError as e:
        print(f"Error: Rate limit exceeded: {e}")
        print("Falling back to mock mode...")
        _render_mock(params, output)
    except runwayml.APIStatusError as e:
        print(f"Error: API error (status {e.status_code}): {e.response}")
        print("Falling back to mock mode...")
        _render_mock(params, output)
    except Exception as e:
        print(f"Error during Runway API call: {e}")
        print("Falling back to mock mode...")
        _render_mock(params, output)


def _render_mock(params: dict[str, Any], output: Path) -> None:
    """Generate mock video using ffmpeg (for development/testing)."""
    output.parent.mkdir(parents=True, exist_ok=True)
    duration = params.get("duration", 4)

    print("Generating mock video with ffmpeg...")
    print(f"   Duration: {duration}s")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "color=c=black:s=1280x720",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        str(output)
    ], check=True, capture_output=True)

    print(f"   ✓ Mock video saved to: {output}")


def render(params: dict[str, Any], output: Path) -> None:
    """
    Render video using Runway API or mock mode.

    Mode is controlled by RUNWAY_MODE env var:
    - "api": Use real Runway API (requires RUNWAYML_API_SECRET)
    - "mock": Use ffmpeg to generate placeholder video (default)
    """
    if RUNWAY_MODE == "api":
        _render_with_api(params, output)
    else:
        _render_mock(params, output)
