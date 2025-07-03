from pathlib import Path
from typing import Union
import os

def load_env(path: Union[str, Path] = ".env") -> None:
    """
    Read KEY=VALUE lines from `.env` into os.environ.

    • Ignores blank lines and comments that start with '#'.
    • Does NOT overwrite variables that are already set
      (so PROD environment vars win over local file).
    """
    path = Path(path)
    if not path.exists():
        return

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())
