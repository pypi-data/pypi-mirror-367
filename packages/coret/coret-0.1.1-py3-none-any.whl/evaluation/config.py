from pathlib import Path
from typing import Any

import yaml


def load_config(path: Path) -> dict[str, Any]:
    with open(path) as f:
        cfg = yaml.safe_load(f)
    return cfg
