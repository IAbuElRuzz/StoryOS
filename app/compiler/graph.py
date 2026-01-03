
from dataclasses import dataclass, field
from typing import Dict, List
import hashlib, json

@dataclass
class Node:
    id: str
    type: str
    params: Dict
    inputs: List["Node"] = field(default_factory=list)
    hash: str = None
    output_path: str = None

    def compute_hash(self, tool_version="v1"):
        payload = {
            "type": self.type,
            "params": self.params,
            "inputs": [i.hash for i in self.inputs],
            "tool_version": tool_version
        }
        raw = json.dumps(payload, sort_keys=True).encode()
        self.hash = hashlib.sha256(raw).hexdigest()[:16]
