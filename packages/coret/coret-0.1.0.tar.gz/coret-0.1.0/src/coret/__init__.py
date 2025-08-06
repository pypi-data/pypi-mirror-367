"""
Coret package for surrogate concept retrieval.

This package provides tools for extracting and analyzing concepts from large datasets
using surrogate-based methods.
"""

from .core import (
    ConceptRetrieval, 
    EmbeddingIndex, 
    cosine_similarity,
    load_pre_calculated_embeddings_from_paths,
    cosine_similarity_cpu,
    cosine_similarity_gpu,
    is_gpu_available,
    normalize_embedding,
)

__version__ = "0.1.0"
__all__ = [
    "ConceptRetrieval", 
    "EmbeddingIndex", 
    "cosine_similarity",
    "load_pre_calculated_embeddings_from_paths",
    "cosine_similarity_cpu",
    "cosine_similarity_gpu",
    "is_gpu_available",
    "normalize_embedding",
]
