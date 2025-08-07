#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "tqdm",
#     "numpy",
#     "scikit-learn",
#     "scipy",
#     "cupy",                # or cupy-cuda11x
#     "jax[cuda12]>=0.6",
#     "cuml-cu11>=24.04",    # cuML GPU build
#     "numba",
#     "cython==3.0.2",
#  ]
# pip-args = ["--find-links", "https://storage.googleapis.com/jax-releases/jax_releases.html"]
# ///
"""
Benchmark alternative back ends for an all-pairs cosine-similarity matrix,
logging both wall-clock and CPU (process) times.  For PyTorch and JAX,
runs both CPU and GPU variants if a GPU is available.
"""

from __future__ import annotations

import importlib
import logging
import os
import sys
import time

import numpy as np

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import load_pre_calculated_embeddings_from_paths

# Dictionaries to store timings
_timings: dict[str, float] = {}
_cpu_timings: dict[str, float] = {}


def l2_normalise(mat: np.ndarray) -> None:
    """In-place L2 normalisation of rows."""
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    mat /= norms


def timeit(label: str, f, /, *args, **kw):
    """Run `f(*args, **kw)` once, record elapsed seconds and CPU time, and return the result."""
    start_wall = time.perf_counter()
    start_cpu = time.process_time()

    out = f(*args, **kw)

    dur_wall = time.perf_counter() - start_wall
    dur_cpu = time.process_time() - start_cpu

    logging.info(f"{label:<30} : {dur_wall:8.3f}s wall, {dur_cpu:8.3f}s CPU")
    _timings[label] = dur_wall
    _cpu_timings[label] = dur_cpu

    return out


def main(X: np.ndarray):
    l2_normalise(X)

    # ---------- NumPy --------------------------------------------------------
    timeit("NumPy (BLAS)", lambda A: A @ A.T, X)

    # ---------- scikit-learn -------------------------------------------------
    if importlib.util.find_spec("sklearn") is not None:
        from sklearn.metrics.pairwise import cosine_similarity

        timeit("scikit-learn (CPU)", cosine_similarity, X)
    else:
        logging.warning("scikit-learn                    : N/A")

    # ---------- PyTorch ------------------------------------------------------
    if importlib.util.find_spec("torch") is not None:
        import torch

        # CPU run
        X_cpu = torch.from_numpy(X).cpu()
        timeit("PyTorch (CPU)", lambda A: A @ A.T, X_cpu)

        # GPU run (if available)
        if torch.cuda.is_available():
            X_gpu = torch.from_numpy(X).to("cuda")
            torch.cuda.synchronize()
            timeit("PyTorch (GPU)", lambda A: A @ A.T, X_gpu)
            torch.cuda.synchronize()
        else:
            logging.info("PyTorch (GPU)                  : no CUDA device")
    else:
        logging.warning("PyTorch                         : N/A")

    # ---------- CuPy ---------------------------------------------------------
    if importlib.util.find_spec("cupy") is not None:
        import cupy as cp

        X_c = cp.asarray(X)
        cp.cuda.runtime.deviceSynchronize()
        timeit("CuPy (GPU)", cp.inner, X_c, X_c)
        cp.cuda.runtime.deviceSynchronize()
    else:
        logging.warning("CuPy                            : N/A")

    # ---------- RAPIDS cuML --------------------------------------------------
    if importlib.util.find_spec("cuml") is not None:
        import cupy as cp
        from cuml.metrics import pairwise_distances

        X_cp = cp.asarray(X)
        cp.cuda.runtime.deviceSynchronize()
        timeit(
            "cuML pairwise_dist (GPU)", lambda A: 1 - pairwise_distances(A, metric="cosine"), X_cp
        )
        cp.cuda.runtime.deviceSynchronize()
    else:
        logging.warning("cuML pairwise_dist              : N/A")

    # ---------- JAX (CPU & GPU) ---------------------------------------------
    if importlib.util.find_spec("jax") is not None:
        import jax
        import jax.numpy as jnp

        X_j = jnp.asarray(X)

        # CPU variant
        jitted_cpu = jax.jit(lambda A: A @ A.T, backend="cpu")
        res_cpu = timeit("JAX (jit CPU)", jitted_cpu, X_j)
        try:
            res_cpu.block_until_ready()
        except AttributeError:
            pass

        # GPU variant (if available)
        # on a CPU-only install this still runs on CPU
        jitted_gpu = jax.jit(lambda A: A @ A.T, backend="gpu")
        res_gpu = timeit("JAX (jit GPU)", jitted_gpu, X_j)
        try:
            res_gpu.block_until_ready()
        except AttributeError:
            pass
    else:
        logging.warning("JAX                             : N/A")

    # ---------- Numba --------------------------------------------------------
    if importlib.util.find_spec("numba") is not None:
        from numba import njit, prange

        @njit(parallel=True, fastmath=True)
        def cosine_full(mat):
            n, d = mat.shape
            out = np.empty((n, n), mat.dtype)
            norms = np.sqrt((mat * mat).sum(1))
            for i in prange(n):
                for j in range(i, n):
                    dot = (mat[i] * mat[j]).sum()
                    val = dot / (norms[i] * norms[j])
                    out[i, j] = out[j, i] = val
            return out

        timeit("Numba (compile+run) (CPU)", cosine_full, X)
    else:
        logging.warning("Numba                           : N/A")

    # ---------- SciPy --------------------------------------------------------
    if importlib.util.find_spec("scipy") is not None:
        from scipy.spatial.distance import cdist

        timeit("SciPy cdist (CPU)", cdist, X, X, "cosine")
    else:
        logging.warning("SciPy cdist                     : N/A")

    # ---------- Summary ------------------------------------------------------
    lines = [
        "Summary of timings:",
        "=" * 60,
        f"Total wall time: {sum(_timings.values()):.3f} s",
        f"Total CPU time : {sum(_cpu_timings.values()):.3f} s",
        f"Embeddings shape: {X.shape[0]} x {X.shape[1]}",
        "=" * 60,
    ]
    for label in _timings:
        lines.append(f"{label:<30}: {_timings[label]:8.3f}s wall, {_cpu_timings[label]:8.3f}s CPU")

    fastest = min(_timings, key=_timings.get)
    slowest = max(_timings, key=_timings.get)
    lines.extend(
        [
            "",
            f"Fastest: {fastest} ({_timings[fastest]:.3f}s wall, {_cpu_timings[fastest]:.3f}s CPU)",
            f"Slowest: {slowest} ({_timings[slowest]:.3f}s wall, {_cpu_timings[slowest]:.3f}s CPU)",
        ]
    )

    summary = "\n".join(lines)
    print("\n" + summary)

    with open("other/benchmark_correlation_calculation_summary.txt", "w") as f:
        f.write(summary)


if __name__ == "__main__":
    embeddings_folder_path = "/mnt/cgm-atlas/onrh/datasets/laion/laion_emb_dino/checkpoints"
    files = os.listdir(embeddings_folder_path)
    files_paths = [
        os.path.join(embeddings_folder_path, file) for file in files if file.endswith(".npz")
    ]
    X, _, _ = load_pre_calculated_embeddings_from_paths(files_paths)
    X = X[:10_000, :]
    main(X)
