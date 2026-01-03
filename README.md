# StoryOS v0.1

**Deterministic video compilation engine** — Treat video like software. Change one line, rebuild one asset.

StoryOS compiles human-readable YAML scripts into AI-generated videos with deterministic caching, parallel execution, and real API integration.

## Features

- 🎬 **Runway Gen-3 API Integration** - Real AI video generation (with mock mode fallback)
- 🎞️ **Multi-Shot Concatenation** - Automatically combines multiple shots into continuous videos
- 🔄 **Deterministic Caching** - Re-run scripts instantly; only changed assets rebuild
- ⚡ **Parallel Execution** - Independent nodes render simultaneously
- 🎯 **Incremental Rebuilds** - Change one shot → rebuild only that shot + final concat
- 🔒 **Type-Safe Codebase** - Full mypy strict compliance
- 📦 **Manifest Generation** - JSON build logs tracking cache hits per node

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Render a single-shot video (mock mode - no API key needed)
python main.py render scripts/demo.yaml

# Render a multi-shot video (3 shots concatenated)
python main.py render scripts/multi_shot_demo.yaml

# Output: outputs/final.mp4 + outputs/manifest.json
```

## Using Real Runway API

1. **Get API Key**: Sign up at [Runway Developer Portal](https://dev.runwayml.com/)

2. **Configure Environment**: Edit `.env`
```bash
RUNWAYML_API_SECRET=your_api_key_here
RUNWAY_MODE=api  # Change from "mock" to "api"
```

3. **Render with AI**:
```bash
python main.py render scripts/demo.yaml
```

The adapter automatically:
- ✅ Generates videos using Runway Gen-3 Alpha Turbo
- ✅ Polls for completion (max 5min timeout)
- ✅ Downloads and caches results
- ✅ Falls back to mock mode on errors

## Architecture

```
Script (YAML) → Compiler → Graph Nodes → Orchestrator → Final Video
                              ↓
                         Cache Layer (deterministic hashing)
                              ↓
                    Adapters (Runway, ElevenLabs, FFmpeg)
```

### Node Graph (Multi-Shot Example)

```
Shot 1 (video + voice) → Merge 1 ─┐
Shot 2 (video + voice) → Merge 2 ─┼→ Concat → final.mp4
Shot 3 (video + voice) → Merge 3 ─┘
```

### Script Format

**Single Shot:**
```yaml
title: simple_video
scenes:
  - id: scene1
    background: "cinematic sunrise over mountains"
    shots:
      - id: shot1
        duration: 4
        camera: "slow zoom"
        dialogue: "This is the future of storytelling."
```

**Multi-Shot (Auto-Concatenates):**
```yaml
title: multi_shot_story
scenes:
  - id: scene1
    background: "sunrise over a mountain landscape"
    shots:
      - id: shot1
        duration: 3
        camera: "wide establishing shot"
        dialogue: "Every journey begins with a single step."

      - id: shot2
        duration: 3
        camera: "slow zoom to peak"
        dialogue: "The peak calls to those brave enough to answer."

      - id: shot3
        duration: 4
        camera: "close-up of determined face"
        dialogue: "This is my moment. This is my time."
```

## Development

```bash
# Type check
mypy app/ main.py --strict

# Mock mode (no API key)
RUNWAY_MODE=mock python main.py render scripts/demo.yaml

# Real API mode
RUNWAY_MODE=api python main.py render scripts/demo.yaml
```

## Output Structure

```
outputs/
├── final.mp4              # Final rendered video (concatenated if multi-shot)
├── manifest.json          # Build metadata + cache status per node
├── cache/                 # Content-addressed assets (by hash)
│   ├── ff00c75e5b6a6257  # Video asset
│   ├── 627351ed830d77a2  # Audio asset
│   ├── 55ece2a20bf8b31c  # Merged shot
│   └── 3a945a2004688fa1  # Concatenated final
└── intermediates/         # Named intermediate files
    ├── scene1_shot1_video.mp4
    ├── scene1_shot1_voice.mp3
    ├── scene1_shot1_merge.mp4
    ├── scene1_shot2_video.mp4
    ├── scene1_shot2_voice.mp3
    ├── scene1_shot2_merge.mp4
    ├── scene1_shot3_video.mp4
    ├── scene1_shot3_voice.mp3
    ├── scene1_shot3_merge.mp4
    └── final_concat.mp4   # Multi-shot: concatenated result
```

## Incremental Rebuilds

**The Power of Deterministic Caching:**

```bash
# First render: Generate all assets
python main.py render scripts/multi_shot_demo.yaml
# → 10 nodes generated (3 shots × 3 nodes + 1 concat)

# Second render: Everything cached
python main.py render scripts/multi_shot_demo.yaml
# → 10 nodes cached, instant execution ✓

# Edit shot2 dialogue, third render: Only rebuild affected nodes
# Change: "The summit awaits..." → "The peak calls..."
python main.py render scripts/multi_shot_demo.yaml
# → 7 nodes cached, 3 nodes rebuilt:
#   - scene1_shot2_voice (changed dialogue)
#   - scene1_shot2_merge (depends on voice)
#   - final_concat (depends on shot2_merge)
```

**Manifest showing cache hits:**
```json
{
  "build_time": "2026-01-03T17:54:24.830888+00:00",
  "nodes": [
    {"id": "scene1_shot1_video", "hash": "247eb...", "cached": true},
    {"id": "scene1_shot1_voice", "hash": "020dd...", "cached": true},
    {"id": "scene1_shot2_voice", "hash": "a02cf...", "cached": false},
    {"id": "scene1_shot2_merge", "hash": "bc212...", "cached": false},
    {"id": "final_concat", "hash": "3a945...", "cached": false}
  ]
}
```

## Adapters

### Video Generation
- **Runway Gen-3 Alpha Turbo** (API mode) - Text-to-video AI generation
- **FFmpeg** (mock mode) - Placeholder solid color videos for development

### Audio Generation
- **ElevenLabs** (planned) - AI voice synthesis
- **FFmpeg** (mock mode) - Sine wave audio placeholder

### Video Processing
- **FFmpeg Merge** - Combines video + audio tracks
- **FFmpeg Concat** - Concatenates multiple shots into continuous video

## Node Types

| Node Type | Inputs | Output | Purpose |
|-----------|--------|--------|---------|
| `video` | None | `.mp4` | Generate video from prompt |
| `voice` | None | `.mp3` | Generate voice from dialogue |
| `merge` | video, voice | `.mp4` | Combine video + audio |
| `concat` | merge[] | `.mp4` | Concatenate multiple shots |

## Next Steps

- [x] Scene concatenation for multi-shot videos
- [x] Runway Gen-3 API integration
- [ ] Add subtitle generation (SRT)
- [ ] Add `--dry-run` graph visualization
- [ ] Integrate ElevenLabs API for voice
- [ ] Add transitions between shots
