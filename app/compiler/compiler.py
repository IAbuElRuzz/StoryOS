
from compiler.graph import Node

def compile_script(script: dict):
    nodes = []

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

    for n in nodes:
        n.compute_hash()

    return nodes
