# Surrogate Concept Retrieval

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# surrogate_concept_retrieval
Implementation for the paper Concept Retrieval - What and How?

## Package Status

✅ **Added**:
- Project URLs and Documentation links
- Keywords and classifiers for PyPI
- Populated `__init__.py` for proper imports
- Documentation structure with Sphinx
- Example code
- Improved README with usage examples

🔄 **In Progress**:
- Comprehensive documentation
- Test coverage
- CI/CD setup

## Getting Started

```bash
# Install the package
pip install -e .
```

See `RECOMMENDATIONS.md` for full details on package improvements.

## Overview

This package provides tools for extracting interpretable concepts from large datasets using surrogate-based methods. It efficiently handles large embedding collections and offers various techniques for concept identification and analysis.

## Features

- Fast embedding indexing using FAISS
- GPU-accelerated similarity computation
- Automatic concept extraction from embedding spaces
- Flexible concept filtering and refinement
- Support for projection-based concept analysis

## Installation

```bash
# Install from PyPI
pip install coret

# Install with development dependencies
pip install "coret[dev]"
```

## Quick Start

```python
import numpy as np
from coret import ConceptRetrieval, EmbeddingIndex

# Load your embeddings (example uses random data)
embeddings = np.random.randn(1000, 768)
embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

# Create an embedding index
embedding_index = EmbeddingIndex(embeddings, do_normaliztion=False)

# Initialize concept retrieval
concept_retriever = ConceptRetrieval(embedding_index)

# Extract concepts
concepts = concept_retriever.extract_concepts(
    n_concepts=10,
    min_samples_per_concept=20
)

# Work with the retrieved concepts
for concept_id, concept_data in concepts.items():
    print(f"Concept {concept_id}: {len(concept_data['indices'])} samples")
```

## Requirements

- Python 3.9+
- CUDA-compatible GPU (recommended for large datasets)
- Dependencies:
  - numpy
  - faiss-gpu (or faiss-cpu)
  - scipy
  - scikit-learn
  - tqdm
  - cupy (for GPU acceleration)

## Documentation

For detailed API documentation and examples, please visit our [documentation site](https://github.com/Onr/surrogate_concept_retrieval/docs).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this library in your research, please cite:

```bibtex
@article{author2025concept,
  title={Concept Retrieval - What and How?},
  author={Author, A.},
  journal={Journal Name},
  year={2025}
}
```


