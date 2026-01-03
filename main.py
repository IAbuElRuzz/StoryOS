#!/usr/bin/env python3
"""
StoryOS CLI Entry Point
Usage: python main.py render <script.yaml>
"""
import sys

from app.compiler.compiler import compile_script
from app.compiler.parser import load_script
from app.orchestrator.executor import execute_graph


def main() -> None:
    if len(sys.argv) < 3 or sys.argv[1] != "render":
        print("Usage: storyos render <script.yaml>")
        sys.exit(1)

    script_path = sys.argv[2]
    script = load_script(script_path)
    graph = compile_script(script)
    execute_graph(graph)


if __name__ == "__main__":
    main()
