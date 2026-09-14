import sys
from pathlib import Path

ROOT_DIR: Path = Path(__file__).resolve().parents[1]
SRC_DIR: Path = ROOT_DIR / "src"

src_path: str = str(SRC_DIR)

if src_path not in sys.path:
    sys.path.insert(0, src_path)