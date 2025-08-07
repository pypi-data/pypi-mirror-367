from typing import Any

import faiss
import numpy as np
from sklearn.cluster import KMeans


class BaseExtractor:
    def extract(
        self, query: np.ndarray, embeddings: np.ndarray, params: dict[str, Any]
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        raise NotImplementedError


class DefaultExtractor(BaseExtractor):
    def extract(self, cur_emb, embeddings, params):
        """
        Extract concepts for a given embedding using the coret instance.

        Args:
            cur_emb (np.ndarray): Single embedding vector (1D or 2D).
            embeddings (np.ndarray): Full dataset embeddings.
            params (dict):
                - main: dict of coret extraction parameters
                - other: dict with extra parameters like noise_to_add_to_concepts

        Returns:
            concepts (np.ndarray): Extracted concept embeddings.
            concepts_pca (np.ndarray): PCA representation of concepts.
            concepts_retrieved_emb (np.ndarray): Retrieved neighbors per concept.
        """
        # Lazily import to avoid circular deps
        from coret import get_concept_neighbors

        # The coret instance is required as part of params
        coret_instance = params.get("coret_instance")
        if coret_instance is None:
            raise ValueError("coret_instance must be passed in params['coret_instance']")

        # Noise control
        noise_to_add_to_concepts = params.get("other", {}).get("noise_to_add_to_concepts", 0)
        if noise_to_add_to_concepts > 0:
            import logging

            logging.warning(f"Adding noise to concepts: {noise_to_add_to_concepts}")

        # Perform main coret concept search
        concepts_dict = coret_instance(query=cur_emb.reshape(1, -1), **params["main"])

        # Get neighbors for each concept
        distances, indices = get_concept_neighbors(
            concepts_dict,
            coret_instance,
            number_of_samples_per_concept=params["main"].get("number_of_samples_per_concept", 20),
            noise_std=noise_to_add_to_concepts,
        )

        # Retrieve actual neighbor embeddings
        concepts_retrieved_emb = embeddings[indices]

        # Filter out failed tests # TODO remove passed_tests
        # breakpoint()
        # passed_tests = np.array(concepts_dict["passed_tests"], dtype=np.int32)
        concepts = concepts_dict["concept_embed_s"]  # * passed_tests[:, np.newaxis]
        # TODO stopped here - > need to make concepts_retrieved_emb concept, num of samples not in one dim concept*num_of_sample
        # concepts_retrieved_emb = (
        #     concepts_retrieved_emb * passed_tests[:, np.newaxis, np.newaxis]
        # )

        # Return everything
        return (
            concepts,
            concepts_dict.get("concepts_pca", np.zeros_like(concepts)),
            concepts_retrieved_emb,
        )


class RetrievalExtractor(BaseExtractor):
    def __init__(self):
        self.index = None
        self.embedding_dim = None

    def _build_index(self, embeddings: np.ndarray):
        """
        Build a FAISS IndexFlatIP index for cosine similarity search.
        """
        # Normalize for cosine similarity = inner product
        x = np.ascontiguousarray(embeddings.astype(np.float32))
        faiss.normalize_L2(x)

        dim = x.shape[1]
        idx = faiss.IndexFlatIP(dim)
        idx.add(x)

        self.index = idx
        self.embedding_dim = dim

    def extract(self, cur_emb: np.ndarray, embeddings: np.ndarray, params: dict):
        """
        Retrieval-based extraction using FAISS cosine similarity.

        Args:
            cur_emb (np.ndarray): Query embedding vector (1D or 2D).
            embeddings (np.ndarray): Full dataset embeddings.
            params (dict):
                - main: { top_k, number_of_concepts, number_of_samples_per_concept }

        Returns:
            concepts (np.ndarray): Mean concept embedding per round
            concepts_pca (np.ndarray): Dummy PCA (zeros)
            concepts_retrieved_emb (np.ndarray): Retrieved neighbors per round
        """
        # Ensure index exists
        if self.index is None:
            self._build_index(embeddings)

        # Normalize query
        query = np.ascontiguousarray(cur_emb.reshape(1, -1).astype(np.float32))
        faiss.normalize_L2(query)

        # Parameters
        num_rounds = params["main"].get("number_of_concepts", 1)
        num_imgs_per_concept = params["main"].get("number_of_samples_per_concept", 20)

        # Compute default top_k if missing
        desired_total = num_rounds * num_imgs_per_concept
        top_k = params["main"].get("top_k", desired_total)
        if top_k < desired_total:
            top_k = desired_total

        # Search top_k neighbors
        distances, indices = self.index.search(query, top_k)
        indices = indices.flatten()

        # Divide retrieved indices into groups
        group_size = top_k // num_rounds
        concepts_list = []
        concepts_retrieved_list = []
        concepts_pca_list = []

        for r in range(num_rounds):
            start = r * group_size
            end = start + num_imgs_per_concept  # only top N for this round
            group_indices = indices[start:end]

            # Retrieve embeddings for this round
            group_embeddings = embeddings[group_indices]

            # Mean embedding is the "concept"
            concepts_list.append(group_embeddings.mean(axis=0))

            # Dummy PCA representation
            concepts_pca_list.append(np.zeros((group_embeddings.shape[0], 1)))

            # Store retrieved embeddings
            concepts_retrieved_list.append(group_embeddings)

        # Stack results
        concepts = np.stack(concepts_list, axis=0)  # (num_rounds, emb_dim)
        concepts_pca = np.stack(concepts_pca_list, axis=0)  # dummy shape
        concepts_retrieved_emb = np.stack(
            concepts_retrieved_list, axis=0
        )  # (num_rounds, num_imgs_per_concept, emb_dim)

        return concepts, concepts_pca, concepts_retrieved_emb


class KMeansExtractor(BaseExtractor):
    def __init__(self):
        self.index = None
        self.embedding_dim = None

    def _build_index(self, embeddings: np.ndarray) -> None:
        x = np.ascontiguousarray(embeddings.astype(np.float32))
        faiss.normalize_L2(x)
        self.embedding_dim = x.shape[1]
        idx = faiss.IndexFlatIP(self.embedding_dim)
        idx.add(x)
        self.index = idx

    def extract(
        self, cur_emb: np.ndarray, embeddings: np.ndarray, params: dict[str, Any]
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Build index once
        if self.index is None:
            self._build_index(embeddings)

        main = params["main"]
        num_clusters = main.get("num_clusters", embeddings.shape[0])
        num_imgs_per_concept = main.get("number_of_samples_per_concept", 20)
        top_k = min(main.get("top_k", num_clusters * num_imgs_per_concept), embeddings.shape[0])

        # --- get subset via FAISS search ---
        if top_k > 0:
            q = np.ascontiguousarray(cur_emb.reshape(1, -1).astype(np.float32))
            faiss.normalize_L2(q)
            _, indices = self.index.search(q, top_k)
            subset = embeddings[indices.flatten()]
        else:
            subset = embeddings

        # Normalize subset for clustering
        subset = np.ascontiguousarray(subset.astype(np.float32))
        faiss.normalize_L2(subset)

        # Run KMeans
        km = KMeans(n_clusters=num_clusters, random_state=0).fit(subset)
        concepts = km.cluster_centers_
        concepts_pca = concepts.copy()  # or compute real PCA if desired

        # Retrieve neighbors for each cluster center
        faiss.normalize_L2(concepts)
        _, idxs = self.index.search(concepts, num_imgs_per_concept)
        concepts_retrieved_emb = embeddings[idxs]

        return concepts, concepts_pca, concepts_retrieved_emb


class RandomExtractor(BaseExtractor):
    def __init__(self):
        self.index = None
        self.embedding_dim = None

    def _build_index(self, embeddings: np.ndarray) -> None:
        x = np.ascontiguousarray(embeddings.astype(np.float32))
        faiss.normalize_L2(x)
        self.embedding_dim = x.shape[1]
        idx = faiss.IndexFlatIP(self.embedding_dim)
        idx.add(x)
        self.index = idx

    def extract(
        self, cur_emb: np.ndarray, embeddings: np.ndarray, params: dict[str, Any]
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        main = params["main"]
        num_rounds = main.get("number_of_rounds", 3)
        num_imgs_per_concept = main.get("number_of_samples_per_concept", 20)
        top_k = main.get("top_k", num_rounds * num_imgs_per_concept)

        # Build index once
        if self.index is None:
            self._build_index(embeddings)

        # Decide pool of candidates
        if top_k == -1:
            pool = np.arange(len(embeddings))
        else:
            q = np.ascontiguousarray(cur_emb.reshape(1, -1).astype(np.float32))
            faiss.normalize_L2(q)
            _, indices = self.index.search(q, top_k)
            pool = indices.flatten()

        # Sample randomly from pool
        total_needed = num_rounds * num_imgs_per_concept
        chosen = np.random.choice(pool, total_needed, replace=False)

        # Build per‑round outputs
        concepts_list = []
        retrieved_list = []
        for r in range(num_rounds):
            start = r * num_imgs_per_concept
            end = start + num_imgs_per_concept
            grp_idx = chosen[start:end]
            grp_emb = embeddings[grp_idx]
            concepts_list.append(grp_emb.mean(axis=0))
            retrieved_list.append(grp_emb)

        concepts = np.stack(concepts_list, axis=0)
        concepts_retrieved_emb = np.stack(retrieved_list, axis=0)
        concepts_pca = np.zeros((num_rounds, 1))  # dummy

        return concepts, concepts_pca, concepts_retrieved_emb


EXTRACTOR_REGISTRY = {
    "default": DefaultExtractor(),
    "retrieval": RetrievalExtractor(),
    "kmeans": KMeansExtractor(),
    "random": RandomExtractor(),
}
