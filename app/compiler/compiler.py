
from typing import Any
from app.compiler.graph import Node


def compile_script(script: dict[str, Any]) -> list[Node]:
    nodes: list[Node] = []
    shot_outputs: list[Node] = []  # Track all merged shots for final concatenation

    for scene in script.get("scenes", []):
        for shot in scene.get("shots", []):
            video = Node(
                id=f"{scene['id']}_{shot['id']}_video",
                type="video",
                params={
                    "prompt": f"{scene.get('background')} {shot.get('camera')}",
                    "duration": shot.get("duration", 4)
                }
            )

            voice = Node(
                id=f"{scene['id']}_{shot['id']}_voice",
                type="voice",
                params={
                    "text": shot.get("dialogue"),
                    "voice": "female"
                }
            )

            merge = Node(
                id=f"{scene['id']}_{shot['id']}_merge",
                type="merge",
                params={},
                inputs=[video, voice]
            )

            nodes.extend([video, voice, merge])
            shot_outputs.append(merge)

    # If there are multiple shots, create a final concat node
    if len(shot_outputs) > 1:
        concat = Node(
            id="final_concat",
            type="concat",
            params={},
            inputs=shot_outputs
        )
        nodes.append(concat)
    elif len(shot_outputs) == 1:
        # Single shot - rename to final for consistency
        shot_outputs[0].id = "final"

    for n in nodes:
        n.compute_hash()

    return nodes
