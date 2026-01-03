
import yaml
from pathlib import Path
from typing import Any


def load_script(path: str) -> dict[str, Any]:
    with open(Path(path), "r") as f:
        result = yaml.safe_load(f)
        if not isinstance(result, dict):
            raise ValueError(f"Script file {path} must contain a YAML dictionary")
        return result
