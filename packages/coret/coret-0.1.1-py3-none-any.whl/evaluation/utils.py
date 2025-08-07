from pathlib import Path
from typing import Any

import dill


def save_checkpoint(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        dill.dump(obj, f)


def load_checkpoint(path: Path) -> Any:
    with open(path, "rb") as f:
        return dill.load(f)
