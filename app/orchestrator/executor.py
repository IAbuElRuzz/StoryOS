
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from orchestrator import cache
from adapters import video_runway, voice_elevenlabs, ffmpeg_merge
import json
from datetime import datetime

OUT = Path("outputs/intermediates")
FINAL = Path("outputs/final.mp4")
MANIFEST = Path("outputs/manifest.json")

def run_node(node):
    if cache.exists(node.hash):
        node.output_path = cache.get(node.hash)
        return node, True

    out = OUT / f"{node.id}.bin"

    if node.type == "video":
        video_runway.render(node.params, out)
    elif node.type == "voice":
        voice_elevenlabs.render(node.params, out)
    elif node.type == "merge":
        ffmpeg_merge.render(
            node.inputs[0].output_path,
            node.inputs[1].output_path,
            out
        )

    cache.store(node.hash, out)
    node.output_path = cache.get(node.hash)
    return node, False

def execute_graph(nodes):
    manifest = {"build_time": datetime.utcnow().isoformat(), "nodes": []}

    with ThreadPoolExecutor(max_workers=4) as ex:
        for node, cached in ex.map(run_node, nodes):
            manifest["nodes"].append({
                "id": node.id,
                "hash": node.hash,
                "cached": cached
            })

    FINAL.parent.mkdir(exist_ok=True)
    FINAL.write_bytes(nodes[-1].output_path.read_bytes())
    MANIFEST.write_text(json.dumps(manifest, indent=2))
