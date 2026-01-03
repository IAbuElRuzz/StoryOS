
from dataclasses import dataclass, field
from typing import Any, Optional
from pathlib import Path
import hashlib
import json


@dataclass
class Node:
    id: str
    type: str
    params: dict[str, Any]
    inputs: list["Node"] = field(default_factory=list)
    hash: Optional[str] = None
    output_path: Optional[Path] = None

    def compute_hash(self, tool_version: str = "v1") -> None:
        payload = {
            "type": self.type,
            "params": self.params,
            "inputs": [i.hash for i in self.inputs],
            "tool_version": tool_version
        }
        raw = json.dumps(payload, sort_keys=True).encode()
        self.hash = hashlib.sha256(raw).hexdigest()[:16]
