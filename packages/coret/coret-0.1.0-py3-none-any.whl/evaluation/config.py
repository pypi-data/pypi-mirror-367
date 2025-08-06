import yaml
from pathlib import Path
from typing import Any, Dict

def load_config(path: Path) -> Dict[str, Any]:
    with open(path, 'r') as f:
        cfg = yaml.safe_load(f)
    return cfg