#!/usr/bin/env python3
"""
Embedding Evaluation Tool.

Loads checkpoint output, computes embedding‑based metrics, saves histograms,
reports, and LaTeX tables. Configurable via command‑line arguments.
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path

import dill as pickle
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import norm
from seaborn import histplot, set_style

from src.evaluation.concept_metrics import compute_embedding_base_scorets

# # make sure your src/ directory is on PYTHONPATH, or adjust as needed
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


# ------------------------------------------------------------------------------
# Constants & Defaults
# ------------------------------------------------------------------------------
DEFAULT_CFG = {
    "cuda_devices": "0",
    "num_concepts_per_image": 3,
    "number_of_samples_per_concept": 20,
    "num_hist_bins": 20,
    "pca_components": 5,
    "random_norm_samples": 5_000,
}
DEFAULT_PICKLE = Path(
    "/mnt/cgm-atlas/onrh/datasets/laion/laion2B-en-aesthetic/"
    "ablation_study_number_of_std_to_add_for_first_threshold_more/"
    "concepts_checkpoint_3_pre_image_only_concepts_100_000.pkl"
)

# ------------------------------------------------------------------------------
# Utility Functions
# ------------------------------------------------------------------------------


def escape_underscorets(s: str) -> str:
    """Escape underscorets for LaTeX/Markdown output."""
    return re.sub(r"_", r"\\_", s)


# ------------------------------------------------------------------------------
# coret Processing Functions
# ------------------------------------------------------------------------------


def load_data(pickle_path: Path) -> dict:
    """
    Load checkpoint data from a dill‑serialized pickle.

    Raises FileNotFoundError if missing.
    """
    if not pickle_path.is_file():
        raise FileNotFoundError(f"Input file not found: {pickle_path}")
    with open(pickle_path, "rb") as f:
        return pickle.load(f)


def compute_metrics(
    data: dict,
    num_hist_bins: int,
    num_concepts_per_image: int,
    number_of_samples_per_concept: int,
    normalized_relevance: bool,
    pca_comp: int,
    random_norm_samples: int,
) -> tuple[dict, dict]:
    """
    Compute embedding‑based metrics for each extraction method.

    Returns (metrics_summary, raw_base_scorets).
    """
    metrics_summary: dict = {}
    raw_scorets: dict = {}

    for method, md in data.get("extraction_results", data).items():
        try:
            inputs = np.stack(md["inputs_emb"], axis=0)
            concepts = np.stack(md["concepts_emb"], axis=0)
            retrieved = np.stack(md["concepts_retrieved_emb"], axis=0)
            pca_list = md["concepts_pca"]
        except KeyError as e:
            logging.error("Method %s missing key %s", method, e)
            continue

        # trim to desired sizes
        concepts = concepts[:, :num_concepts_per_image]
        retrieved = retrieved[:, :num_concepts_per_image]
        pca_list = [p[:num_concepts_per_image] for p in pca_list]

        # compute
        if normalized_relevance:
            # sample embeddings for normalization
            n_inputs = inputs.shape[0]
            k = min(n_inputs, random_norm_samples)
            idx1 = np.random.choice(n_inputs, k, replace=False)
            idx2 = np.random.choice(concepts.shape[1], k, replace=True)
            norm_embs = concepts[idx1, idx2, :]
            base = compute_embedding_base_scorets(
                inputs_emb_s=inputs,
                concepts_emb_s=concepts,
                concepts_retrieved_emb_s=retrieved,
                embedding_to_use_for_normalization=norm_embs,
                pca_comp_to_use=pca_comp,
            )
        else:
            base = compute_embedding_base_scorets(
                inputs_emb_s=inputs,
                concepts_emb_s=concepts,
                concepts_retrieved_emb_s=retrieved,
                pca_comp_to_use=pca_comp,
            )

        # summarize
        summary: dict = {}
        for k, v in base.items():
            arr = v.flatten()
            summary[k] = {
                "shape": v.shape,
                "mean": float(arr.mean()),
                "std": float(arr.std()),
                "min": float(arr.min()),
                "max": float(arr.max()),
                "histogram": np.histogram(arr, bins=num_hist_bins)[0].tolist(),
            }

        metrics_summary[method] = {
            "data_shapes": {
                "inputs": inputs.shape,
                "concepts": concepts.shape,
                "retrieved": retrieved.shape,
                "pca_counts": len(pca_list),
            },
            "embedding_base_scorets": summary,
        }
        raw_scorets[method] = base

    return metrics_summary, raw_scorets


def save_histograms(raw_scorets: dict, out_dir: Path, num_hist_bins: int) -> None:
    """Save flattened and per‑concept histograms for each metric."""
    set_style("whitegrid")

    for method, scorets in raw_scorets.items():
        mdir = out_dir / method
        mdir.mkdir(parents=True, exist_ok=True)

        for metric, vals in scorets.items():
            flat = vals.flatten()
            # flattened histogram
            plt.figure(figsize=(6, 4))
            histplot(flat, bins=num_hist_bins, stat="density", kde=False, alpha=0.6)
            mu, sigma = flat.mean(), flat.std()
            xs = np.linspace(flat.min(), flat.max(), 200)
            plt.plot(xs, norm.pdf(xs, mu, sigma), linewidth=2)
            plt.xlabel(f"{metric} values")
            plt.ylabel("Density")
            plt.title(f"{method}: {metric} (flattened)")
            plt.savefig(mdir / f"hist_{metric}.png", bbox_inches="tight")
            plt.close()

            # per-concept
            if vals.ndim == 2:
                n, c = vals.shape
                plt.figure(figsize=(7, 5))
                for i in range(c):
                    col = vals[:, i]
                    histplot(col, bins=num_hist_bins, stat="density", kde=False, alpha=0.4)
                    mu_i, sigma_i = col.mean(), col.std()
                    xs_i = np.linspace(col.min(), col.max(), 200)
                    plt.plot(xs_i, norm.pdf(xs_i, mu_i, sigma_i), linewidth=2)
                plt.xlabel(f"{metric} values")
                plt.ylabel("Density")
                plt.title(f"{method}: {metric} (per concept)")
                plt.savefig(mdir / f"hist_{metric}_concepts.png", bbox_inches="tight")
                plt.close()


def log_to_dataframe(raw_scorets: dict, out_dir: Path) -> pd.DataFrame:
    """Flatten raw_scorets into a single DataFrame and save CSV."""
    records = []
    for method, metrics in raw_scorets.items():
        for metric, vals in metrics.items():
            if vals.ndim == 1 or vals.shape[1] == 1:
                arr = vals.flatten()
                for x in arr:
                    records.append({"method": method, metric: x})
            else:
                for i in range(vals.shape[1]):
                    for x in vals[:, i]:
                        records.append({"method": method, f"{metric}_c{i+1}": x})

    df = pd.DataFrame(records).fillna(method="ffill")
    csv_path = out_dir / "base_scorets.csv"
    df.to_csv(csv_path, index=False)
    logging.info("Saved base‐scorets CSV to %s", csv_path)
    return df


def save_json_and_html(summary: dict, out_dir: Path, images_subdir: str = "images") -> None:
    """Write summary.json and a simple HTML report with embedded histogram images."""
    # JSON
    jpath = out_dir / "results.json"
    with open(jpath, "w") as jf:
        json.dump(summary, jf, indent=2)
    logging.info("Saved summary JSON to %s", jpath)

    # HTML
    html = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<title>Embedding Evaluation</title></head><body>"
        "<h1>Embedding Evaluation Summary</h1>"
    ]
    for method, info in summary.items():
        html.append(f"<h2>Method: {method}</h2>")
        html.append("<pre>" + json.dumps(info["data_shapes"], indent=2) + "</pre>")
        for metric in info["embedding_base_scorets"]:
            html.append(
                f"<img src='{images_subdir}/{method}/hist_{metric}.png' "
                f"alt='hist_{metric}' style='max-width:600px;'/><br>"
            )
            shape = info["embedding_base_scorets"][metric]["shape"]
            if isinstance(shape, list) or (isinstance(shape, tuple) and len(shape) == 2):
                html.append(
                    f"<img src='{images_subdir}/{method}/hist_{metric}_concepts.png' "
                    f"alt='hist_{metric}_concepts' style='max-width:600px;'/><br>"
                )
    html.append("</body></html>")

    hpath = out_dir / "summary.html"
    with open(hpath, "w") as hf:
        hf.write("\n".join(html))
    logging.info("Saved HTML report to %s", hpath)


# ------------------------------------------------------------------------------
# Main CLI
# ------------------------------------------------------------------------------


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Evaluate embeddings with embedding‑based metrics")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_PICKLE,
        help="Path to input pickle file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results"),
        help="Output directory",
    )
    parser.add_argument(
        "--hist-bins",
        type=int,
        default=DEFAULT_CFG["num_hist_bins"],
        help="Number of histogram bins",
    )
    parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="Disable normalized relevance",
    )
    args = parser.parse_args()

    # set up
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    os.environ["CUDA_VISIBLE_DEVICES"] = DEFAULT_CFG["cuda_devices"]

    out_dir = args.output
    img_dir = out_dir / "images"
    out_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(exist_ok=True)

    try:
        data = load_data(args.input)
    except FileNotFoundError as e:
        logging.error(e)
        sys.exit(1)

    metrics, raw = compute_metrics(
        data=data,
        num_hist_bins=args.hist_bins,
        num_concepts_per_image=DEFAULT_CFG["num_concepts_per_image"],
        number_of_samples_per_concept=DEFAULT_CFG["number_of_samples_per_concept"],
        normalized_relevance=not args.no_normalize,
        pca_comp=DEFAULT_CFG["pca_components"],
        random_norm_samples=DEFAULT_CFG["random_norm_samples"],
    )
    logging.info("Computed metrics for %d methods", len(metrics))

    save_histograms(raw, img_dir, args.hist_bins)
    save_json_and_html(metrics, out_dir)
    df = log_to_dataframe(raw, out_dir)

    # generate LaTeX table
    mean_df = df.groupby("method").mean()
    std_df = df.groupby("method").std()
    latex = mean_df.combine(
        std_df,
        lambda m, s: m.map("{:.3f}".format) + " $\\pm$ " + s.map("{:.3f}".format),
    )
    latex.index = latex.index.map(escape_underscorets)
    for col in latex.columns:
        latex.rename(columns={col: escape_underscorets(col)}, inplace=True)

    print(latex.to_markdown(escape=False))
    print(latex.to_latex(escape=False))

    logging.info("All done.")


if __name__ == "__main__":
    main()
