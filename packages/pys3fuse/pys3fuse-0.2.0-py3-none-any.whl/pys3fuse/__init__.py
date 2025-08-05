import os
from pathlib import Path

pys3fuse_dir = Path(os.getenv("HOME")) / ".pys3fuse"

if not pys3fuse_dir.exists():
    os.mkdir(pys3fuse_dir, mode=0o766)
