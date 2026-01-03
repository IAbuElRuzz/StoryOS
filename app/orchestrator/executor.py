
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from app.orchestrator import cache
from app.adapters import video_runway, voice_elevenlabs, ffmpeg_merge, ffmpeg_concat
from app.compiler.graph import Node
import json
from datetime import datetime, timezone
from typing import Any

OUT = Path("outputs/intermediates")
FINAL = Path("outputs/final.mp4")
MANIFEST = Path("outputs/manifest.json")


def run_node(node: Node) -> tuple[Node, bool]:
    if node.hash and cache.exists(node.hash):
        node.output_path = cache.get(node.hash)
        return node, True

    # Use appropriate file extension based on node type
    if node.type == "video":
        out = OUT / f"{node.id}.mp4"
        video_runway.render(node.params, out)
    elif node.type == "voice":
        out = OUT / f"{node.id}.mp3"
        voice_elevenlabs.render(node.params, out)
    elif node.type == "merge":
        out = OUT / f"{node.id}.mp4"
        if node.inputs[0].output_path and node.inputs[1].output_path:
            ffmpeg_merge.render(
                node.inputs[0].output_path,
                node.inputs[1].output_path,
                out
            )
        else:
            raise ValueError(f"Merge node {node.id} has missing input paths")
    elif node.type == "concat":
        out = OUT / f"{node.id}.mp4"
        # Collect all input video paths
        input_videos = []
        for input_node in node.inputs:
            if input_node.output_path:
                input_videos.append(input_node.output_path)
            else:
                raise ValueError(f"Concat node {node.id} has missing input path from {input_node.id}")
        ffmpeg_concat.render(input_videos, out)
    else:
        raise ValueError(f"Unknown node type: {node.type}")

    if node.hash:
        cache.store(node.hash, out)
        node.output_path = cache.get(node.hash)
    else:
        raise ValueError(f"Node {node.id} has no hash computed")

    return node, False


def execute_graph(nodes: list[Node]) -> None:
    manifest: dict[str, Any] = {
        "build_time": datetime.now(timezone.utc).isoformat(),
        "nodes": []
    }

    # Group nodes by whether they have dependencies
    independent_nodes = [n for n in nodes if not n.inputs]
    dependent_nodes = [n for n in nodes if n.inputs]

    # Execute independent nodes in parallel
    with ThreadPoolExecutor(max_workers=4) as ex:
        for node, cached in ex.map(run_node, independent_nodes):
            manifest["nodes"].append({
                "id": node.id,
                "hash": node.hash,
                "cached": cached
            })

    # Execute dependent nodes sequentially (they need inputs to be ready)
    for node in dependent_nodes:
        node_result, cached = run_node(node)
        manifest["nodes"].append({
            "id": node_result.id,
            "hash": node_result.hash,
            "cached": cached
        })

    FINAL.parent.mkdir(exist_ok=True)
    if nodes[-1].output_path:
        FINAL.write_bytes(nodes[-1].output_path.read_bytes())
    else:
        raise ValueError("Final node has no output path")

    MANIFEST.write_text(json.dumps(manifest, indent=2))
