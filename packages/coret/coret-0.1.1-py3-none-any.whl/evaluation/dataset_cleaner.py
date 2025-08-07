import logging
from pathlib import Path

import dill
import numpy as np


def clean_dataset(
    embeddings: np.ndarray,
    urls: np.ndarray,
    labels: np.ndarray,
    cache_dir: Path,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    idx_file = cache_dir / f"indices_{embeddings.shape[0]}.pkl"
    size_file = cache_dir / f"size_{embeddings.shape[0]}.pkl"
    if idx_file.exists() and size_file.exists():
        saved_size = dill.load(size_file)
        if saved_size == embeddings.shape:
            logging.info("Loading cached clean indices")
            idxs = dill.load(idx_file)
            return embeddings[idxs], urls[idxs], labels[idxs]
    # otherwise compute new
    from coret_utils import clean_embeddings_v2

    emb_clean, idxs = clean_embeddings_v2(embeddings)
    dill.dump(emb_clean, idx_file)
    dill.dump(embeddings.shape, size_file)
    return emb_clean, urls[idxs], labels[idxs]
