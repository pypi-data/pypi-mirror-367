#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "dill",
#     "pillow",
#     "pyyaml",
#     "requests",
# ]
# ///
import argparse
import logging
import os
from pathlib import Path

from coret import ConceptRetrieval
from evaluation.concept_extraction import extract_concepts

# ← updated to import from your own package!
from evaluation.config import load_config
from evaluation.data_loader import load_aesthetic_embeddings
from evaluation.dataset_cleaner import clean_dataset
from evaluation.extractors import EXTRACTOR_REGISTRY
from evaluation.logging_config import setup_logging


def parse_args():
    parser = argparse.ArgumentParser(description="Run concept extraction evaluation")
    parser.add_argument(
        "--config", type=Path, default="src/evaluation/config.yaml", help="Path to YAML config file"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    cfg = load_config(args.config)
    setup_logging(cfg.get("log_level", "INFO"))

    os.environ["CUDA_VISIBLE_DEVICES"] = str(cfg["cuda_device"])

    # 1. Load the embeddings, labels, URLs
    embeddings, labels, urls = load_aesthetic_embeddings(
        Path(cfg["data_path"]), cfg.get("partial_load_size")
    )

    # 2. Optional cleaning
    if cfg.get("do_clean", False):
        embeddings, urls, labels = clean_dataset(
            embeddings, urls, labels, Path(cfg["output_dir"]) / "cache"
        )

    # 3. Fit your ConceptRetrieval model
    coret = ConceptRetrieval(**cfg["coret"])
    coret.fit(embeddings)

    # 4. Build extractors
    methods = {}
    for name, mconf in cfg["extraction_methods"].items():
        extractor_name = mconf["extractor"]
        methods[name] = {"extractor": EXTRACTOR_REGISTRY[extractor_name], "params": mconf["params"]}

    # 5. Extract concepts (with checkpointing)
    results = extract_concepts(
        embeddings=embeddings,
        coret_instance=coret,
        methods=methods,
        num_images=cfg["num_images"],
        number_of_samples_per_concept=cfg["number_of_samples_per_concept"],
        checkpoint_file=Path(cfg["output_dir"]) / "checkpoint.pkl",
        checkpoint_interval=cfg["checkpoint_interval"],
    )

    # 6. Save final results
    import dill

    out = Path(cfg["output_dir"]) / "final_concepts.pkl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as f:
        dill.dump(results, f)
    logging.info(f"Saved concepts to {out}")


if __name__ == "__main__":
    main()
