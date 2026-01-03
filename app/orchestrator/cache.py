
from pathlib import Path

CACHE = Path("outputs/cache")
CACHE.mkdir(parents=True, exist_ok=True)


def exists(h: str) -> bool:
    return (CACHE / h).exists()


def get(h: str) -> Path:
    return CACHE / h


def store(h: str, p: Path) -> None:
    (CACHE / h).write_bytes(p.read_bytes())
