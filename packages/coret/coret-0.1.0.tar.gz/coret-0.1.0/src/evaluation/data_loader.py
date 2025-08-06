import numpy as np
import logging
from pathlib import Path
from tqdm.auto import tqdm
from PIL import Image
import requests
from typing import Tuple, Optional, Sequence

def load_aesthetic_embeddings(
    data_path: Path,
    partial_load_size: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    files = list(data_path.glob("*.npz"))
    logging.info(f"Found {len(files)} .npz files under {data_path}")
    if partial_load_size is not None:
        files = np.random.choice(files, partial_load_size, replace=False)
    embs, labels, urls = [], [], []
    for f in tqdm(files, desc="Loading embeddings"):
        arr = np.load(f)
        e, l, u = arr["image_embeddings"], arr["labels"], arr["image_urls"]
        embs.append(e); labels.append(l); urls.append(u)
    return (
        np.concatenate(embs, axis=0),
        np.concatenate(labels, axis=0),
        np.concatenate(urls, axis=0),
    )

def fetch_image(url: str) -> Image.Image:
    try:
        resp = requests.get(url, stream=True); resp.raise_for_status()
        return Image.open(resp.raw)
    except Exception as e:
        logging.error(f"Image fetch failed for {url}: {e}")
        return Image.new("RGB", (128,128), color="white")
