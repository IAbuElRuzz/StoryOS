
from pathlib import Path

CACHE = Path("outputs/cache")
CACHE.mkdir(parents=True, exist_ok=True)

def exists(h): return (CACHE / h).exists()
def get(h): return CACHE / h
def store(h, p): (CACHE / h).write_bytes(p.read_bytes())
