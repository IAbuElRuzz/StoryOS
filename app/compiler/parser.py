
import yaml
from pathlib import Path

def load_script(path: str) -> dict:
    with open(Path(path), "r") as f:
        return yaml.safe_load(f)
