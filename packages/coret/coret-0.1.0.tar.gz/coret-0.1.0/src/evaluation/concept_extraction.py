import numpy as np
from tqdm.auto import tqdm
from typing import Dict, Any
from pathlib import Path
from .utils import save_checkpoint, load_checkpoint

def extract_concepts(
    embeddings: np.ndarray,
    core_instance: Any,
    methods: Dict[str, Any],
    num_images: int,
    number_of_samples_per_concept: int,
    checkpoint_file: Path,
    checkpoint_interval: int
) -> Dict[str, Dict[str, np.ndarray]]:
    # load or init
    if checkpoint_file.exists():
        data = load_checkpoint(checkpoint_file)
        results, start_idx, indices = data["results"], data["count"], data["indices"]
    else:
        indices = np.random.choice(embeddings.shape[0], num_images, replace=False)
        results = {m: {"inputs":[], "c_emb":[], "pca":[], "retr_emb":[]} for m in methods}
        start_idx = 0

    for i in tqdm(range(start_idx, len(indices)), desc="Extracting"):
        idx = indices[i]
        emb = embeddings[idx]
        for name, cfg in methods.items():
            ext = cfg["extractor"]
            cfg["params"]["core_instance"] = core_instance  # Pass the core instance to the extractor
            cfg["params"]["main"]["number_of_samples_per_concept"] = number_of_samples_per_concept
            c, p, r = ext.extract(emb, embeddings, cfg["params"])
            results[name]["inputs"].append(emb)
            results[name]["c_emb"].append(c)
            results[name]["pca"].append(p)
            results[name]["retr_emb"].append(r)
        start_idx += 1
        if start_idx % checkpoint_interval == 0:
            save_checkpoint(
                {"results": results, "count": start_idx, "indices": indices},
                checkpoint_file
            )
    # stack into arrays
    final = {}
    for m, res in results.items():
        final[m] = {
            "inputs_emb": np.stack(res["inputs"]),
            "concepts_emb": np.stack(res["c_emb"]),
            "concepts_pca": np.stack(res["pca"]),
            "concepts_retrieved_emb": np.stack(res["retr_emb"]),
        }
    return final
