# implementing consepet retrival
import logging
from time import time

import cupy as cp
import faiss
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from sklearn.decomposition import PCA
from tqdm import tqdm


def load_pre_calculated_embeddings_from_paths(paths):
    """Load pre-calculated embeddings from the given paths.

    :param paths: List of paths to the npz files containing embeddings.
    :return: A tuple containing the concatenated embeddings, labels, and URLs.
    """
    logger = logging.getLogger(__name__)
    logger.info("Loading pre-calculated embeddings from paths...")
    start_time = time()

    embeddings_s = []
    labels_s = []
    urls_s = []

    for path in tqdm(paths, desc="Loading embeddings", leave=False):
        try:
            data = np.load(path, allow_pickle=True)
            embedding = data["embeddings"] if "embeddings" in data else data["image_embeddings"]
            if "labels" in data:
                labels = data["labels"]
            else:
                # If labels are not present, create a placeholder
                labels = [None for i in range(embedding.shape[0])]
            if (
                "urls" in data or "successful_urls" in data or "image_urls" in data
            ):  # both keys are used in different datasets
                urls = data.get(
                    "urls",
                    data.get(
                        "successful_urls",
                        data.get("image_urls", [None for i in range(len(labels))]),
                    ),
                )
            else:
                # If URLs are not present, create a placeholder
                urls = [None for i in range(len(labels))]

            if embedding.ndim != 2:
                raise ValueError(f"Embedding at {path} must be a 2D inner_product.")

            embeddings_s.append(embedding)
            labels_s.append(labels)
            urls_s.append(urls)
        except Exception as e:
            print(f"Error loading embedding from {path}: {e}")
            continue

    if len(embeddings_s) > 0:
        embeddings_s = np.concatenate(embeddings_s, axis=0)
    else:
        raise ValueError("No valid embeddings found in the provided paths.")

    labels_s = np.concatenate(labels_s)
    urls_s = np.concatenate(urls_s)
    logger.info(
        f"Loaded {embeddings_s.shape[0]} embeddings in {time() - start_time:.2f} seconds. \n  embedding memory usage: {embeddings_s.nbytes / (1024 ** 2):.2f} MB"
    )

    return embeddings_s, labels_s, urls_s


class EmbeddingIndex:
    def __init__(self, embeddings: np.array, gpu: int = 0, do_normaliztion: bool = True):
        """
        Initialize the EmbeddingIndex with pre-calculated embeddings. # This class is used to create a FAISS index for fast similarity search. and in the future it will be used to create a vector database.
        :param embeddings: Pre-calculated embeddings as a numpy array.
        :param gpu: GPU device ID to use for FAISS index, -1 for CPU.
        """
        self.embeddings = embeddings
        self.do_normaliztion = do_normaliztion
        if self.do_normaliztion:  # Normalize embeddings to unit length
            faiss.normalize_L2(self.embeddings)  # Normalize embeddings to unit length
        self.index = None
        self.gpu = gpu
        self.logger = logging.getLogger(__name__)
        self.index = self._build_index()

    def _build_index(self):
        """
        Build the FAISS index for the embeddings.
        """
        start_time = time()
        self.logger.info("Building FAISS index...")

        d = self.embeddings.shape[1]  # Dimension of the embeddings
        index_cpu = faiss.IndexFlatIP(d)  # Inner product index

        if self.gpu > 0:

            try:
                # Try to use GPU
                res = faiss.StandardGpuResources()
                device = getattr(self, "gpu", 0)  # Use self.gpu if defined, else default to 0
                index_gpu = faiss.index_cpu_to_gpu(res, device, index_cpu)
                index = index_gpu
                self.logger.info("FAISS using GPU.")
            except Exception as e:
                # Fallback to CPU
                index = index_cpu
                self.logger.warning(f"FAISS fallback to CPU due to: {e}")
        else:
            # Use CPU index if GPU is not available or not specified
            index = index_cpu
            self.logger.info("FAISS using CPU.")

        # Add embeddings to the index
        index.add(self.embeddings)
        self.logger.info(f"FAISS index built in {time() - start_time:.2f} seconds.")
        return index

    def search(self, query_embedding: np.ndarray, k: int = 10) -> tuple[np.ndarray, np.ndarray]:
        """
        Search for the k nearest neighbors of the query embedding.
        :param query_embedding: The embedding to search for.
        :param k: The number of nearest neighbors to return.
        :return: A tuple containing the distances and indices of the nearest neighbors.
        """

        if self.do_normaliztion:
            faiss.normalize_L2(query_embedding)  # Normalize the query embedding to unit length
        if self.index is None:
            raise ValueError("Index has not been built yet.")

        if not isinstance(query_embedding, np.ndarray):
            raise TypeError("Query embedding must be a numpy array.")

        distances, indices = self.index.search(query_embedding, k)
        return distances[0], indices[0]


def cosine_similarity_cpu(a, b):
    # Ensure inputs are 2D
    a = np.atleast_2d(a)
    b = np.atleast_2d(b)

    # Compute norms using vectorized sum-of-squares and sqrt
    a_norm = np.sqrt(np.sum(a * a, axis=1, keepdims=True))
    b_norm = np.sqrt(np.sum(b * b, axis=1, keepdims=True))

    # Compute dot product and normalize by the norms
    similarity = np.dot(a, b.T) / (a_norm * b_norm.T)
    return similarity


def cosine_similarity_gpu(a, b):
    # Convert to GPU arrays
    a_gpu = cp.asarray(a)
    b_gpu = cp.asarray(b)

    # Compute norms on GPU
    a_norm = cp.sqrt(cp.sum(a_gpu * a_gpu, axis=1, keepdims=True))
    b_norm = cp.sqrt(cp.sum(b_gpu * b_gpu, axis=1, keepdims=True))

    # Compute dot product and normalize
    similarity_gpu = cp.dot(a_gpu, b_gpu.T) / (a_norm * b_norm.T)

    # Convert back to NumPy array if needed
    return cp.asnumpy(similarity_gpu)


def is_gpu_available():
    try:
        count = cp.cuda.runtime.getDeviceCount()
        return count > 0
    except cp.cuda.runtime.CUDARuntimeError as e:
        if "cudaErrorNoDevice" in str(e):
            return False
        else:
            raise  # Re-raise other unexpected errors


def _cosine_sym_cpu(a):
    a = np.atleast_2d(a)
    n, d = a.shape
    norms = np.linalg.norm(a, axis=1)
    sim = np.empty((n, n), dtype=a.dtype)

    # compute only upper triangle (including diagonal)
    for i in range(n):
        # dot a[i] with a[i:], shape = (n-i,)
        dots = a[i].dot(a[i:].T)
        sim[i, i:] = dots / (norms[i] * norms[i:])
        sim[i:, i] = sim[i, i:]  # mirror into lower triangle

    # no need to fill diagonal (it's already 1)
    return sim


def _cosine_sym_gpu(a, block_size=512):
    a_gpu = cp.asarray(a)
    n, d = a_gpu.shape
    norms = cp.linalg.norm(a_gpu, axis=1)
    sim_gpu = cp.empty((n, n), dtype=a_gpu.dtype)

    # block‐wise triangular compute to reduce kernel launches
    for i in range(0, n, block_size):
        ib = slice(i, min(i + block_size, n))
        Ai = a_gpu[ib]
        ni = norms[ib]

        for j in range(i, n, block_size):
            jb = slice(j, min(j + block_size, n))
            Aj = a_gpu[jb]
            nj = norms[jb]

            # block matrix multiply
            block = Ai.dot(Aj.T)
            # normalize: shape (len(ib), len(jb))
            block /= ni[:, None] * nj[None, :]

            sim_gpu[ib, jb] = block
            sim_gpu[jb, ib] = block.T

    return cp.asnumpy(sim_gpu)


def cosine_similarity(a, b=None):
    """
    If b is None or b is a itself, we do a symmetric, triangular compute.
    Otherwise we do the full a·b^T version.
    """
    same = b is None
    use_gpu = False
    try:
        use_gpu = cp.cuda.runtime.getDeviceCount() > 0
    except Exception:
        pass

    if same:
        if use_gpu:
            return _cosine_sym_gpu(a)
        else:
            return _cosine_sym_cpu(a)
    else:
        # full asymmetric compute
        if use_gpu:
            return cosine_similarity_gpu(a, b)
        else:
            return cosine_similarity_cpu(a, b)


def vectorized_histogram_uniform(inner_products, value_range, bins):
    """
    Compute histograms for each row in a 2D inner_product assuming uniform bin spacing.

    Parameters:
        inner_products (np.ndarray): 2D inner_product of shape (n_rows, n_columns).
        value_range (tuple): (min_val, max_val) defining the data range.
        bins (int): Number of bins.

    Returns:
        hist_s (np.ndarray): 2D inner_product of shape (n_rows, bins), with histogram counts per row.
        digitized (np.ndarray): 2D inner_product of the same shape as inner_products, with the bin index for each element.
    """
    # Unpack the value range
    min_val, max_val = value_range

    # Compute the bin width
    bin_width = (max_val - min_val) / bins

    # Convert values to integer bin indices
    # scaled can go slightly beyond [0, bins] due to floating precision, so we clip
    scaled = (inner_products - min_val) / bin_width
    digitized = scaled.astype(int)
    digitized = np.clip(digitized, 0, bins - 1)

    # Allocate histogram inner_product
    n_rows = inner_products.shape[0]
    hist_s = np.zeros((n_rows, bins), dtype=int)

    # Accumulate counts
    row_indices = np.arange(n_rows)[:, None]  # shape (n_rows, 1)
    np.add.at(hist_s, (row_indices, digitized), 1)

    return hist_s, digitized


def find_peaks_in_histogram_padded(row_hist, max_len=None):
    peaks, _ = find_peaks(row_hist)
    if max_len is None:
        return peaks

    # Create a new inner_product of size `max_len` with default value -1
    result = np.full(max_len, -1, dtype=peaks.dtype)
    # Fill in the valid peak indices
    n = min(len(peaks), max_len)
    result[:n] = peaks[:n]
    return result


def truncated_pca_transform_cpu(embedding, pca_model, n_components_to_use):
    """
    CPU version: Compute the truncated forward and inverse PCA transform.

    Parameters:
        embedding (np.ndarray): Original data of shape (n_samples, n_features).
        pca_model: A fitted PCA model with attributes 'mean_' and 'components_'.
        n_components_to_use (int): The number of principal components to retain.

    Returns:
        np.ndarray: Reconstructed data using the first n_components_to_use components.
    """
    # Center the data
    X_centered = embedding - pca_model.mean_

    # Compute truncated forward transform (PCA coefficients)
    truncated_coeffs = np.dot(X_centered, pca_model.components_[:n_components_to_use].T)

    # Reconstruct using the truncated components
    reconstructed = (
        np.dot(truncated_coeffs, pca_model.components_[:n_components_to_use]) + pca_model.mean_
    )
    return reconstructed


def truncated_pca_transform_auto(embedding, pca_model, n_components_to_use):
    """
    Automatically selects the GPU version if a GPU is available, otherwise falls back to CPU.

    Parameters:
        embedding (np.ndarray): Original data of shape (n_samples, n_features).
        pca_model: A fitted PCA model with attributes 'mean_' and 'components_'.
        n_components_to_use (int): The number of principal components to retain.

    Returns:
        np.ndarray: Reconstructed data using the selected method.
    """
    try:
        # Try to import CuPy and check for GPU availability.
        import cupy as cp

        if cp.cuda.runtime.getDeviceCount() > 0:
            return truncated_pca_transform_gpu(embedding, pca_model, n_components_to_use)
    except Exception:
        # Any issue (import error or no GPU) will lead to a fallback.
        logging.warning("CuPy is not available or no GPU detected. Falling back to CPU.")

    # Default to CPU if GPU is unavailable or an error occurred.
    return truncated_pca_transform_cpu(embedding, pca_model, n_components_to_use)


def truncated_pca_transform_gpu(embedding, pca_model, n_components_to_use):
    """
    GPU version: Compute the truncated forward and inverse PCA transform using CuPy.

    Parameters:
        embedding (np.ndarray): Original data of shape (n_samples, n_features).
        pca_model: A fitted PCA model with attributes 'mean_' and 'components_'.
        n_components_to_use (int): The number of principal components to retain.

    Returns:
        np.ndarray: Reconstructed data (returned as a NumPy array) using the first n_components_to_use components.
    """
    # Transfer data and PCA parameters to GPU
    X_gpu = cp.asarray(embedding)
    mean_gpu = cp.asarray(pca_model.mean_)
    components_gpu = cp.asarray(pca_model.components_[:n_components_to_use])

    # Center the data on GPU
    X_centered_gpu = X_gpu - mean_gpu

    # Compute truncated forward transform on GPU
    truncated_coeffs_gpu = cp.dot(X_centered_gpu, components_gpu.T)

    # Reconstruct the data on GPU
    reconstructed_gpu = cp.dot(truncated_coeffs_gpu, components_gpu) + mean_gpu

    # Transfer the result back to CPU
    return cp.asnumpy(reconstructed_gpu)


def calculate_projection(base_emb, emb_to_subtract):
    projection_coefficients = np.einsum("ij,ij->i", base_emb, emb_to_subtract) / np.einsum(
        "ij,ij->i", emb_to_subtract, emb_to_subtract
    )
    return projection_coefficients[:, np.newaxis] * emb_to_subtract


def normalize_embedding(embedding):
    norm = np.sqrt(np.einsum("...i,...i", embedding, embedding))[..., np.newaxis]
    # Handle zero vectors by returning them as-is
    with np.errstate(divide="ignore", invalid="ignore"):
        normalized = embedding / norm
        # Replace NaN values (from zero vectors) with zeros
        normalized = np.nan_to_num(normalized, nan=0.0)
    return normalized


def cal_leftover_embeddings(base_emb, emb_to_subtract):
    # Ensure emb_to_subtract is at least 1-dimensional
    if len(emb_to_subtract.shape) == 1:
        emb_to_subtract = emb_to_subtract[np.newaxis, :]

    # Ensure base_emb is at least 1-dimensional
    if len(base_emb.shape) == 1:
        base_emb = base_emb[np.newaxis, :]

    # Check normalization
    assert np.isclose(
        np.linalg.norm(base_emb, axis=-1).max(), 1
    ), f"base_emb must be normalized, but got {np.linalg.norm(base_emb)}"
    assert np.isclose(
        np.linalg.norm(emb_to_subtract, axis=-1).max(), 1
    ), f"emb_to_subtract must be normalized, but got {np.linalg.norm(emb_to_subtract)}"

    # Broadcasting if emb_to_subtract has only one row, apply it to all rows of base_emb
    if emb_to_subtract.shape[0] == 1:
        emb_to_subtract = np.repeat(emb_to_subtract, base_emb.shape[0], axis=0)

    # Ensure both base_emb and emb_to_subtract have the same shape now
    assert (
        base_emb.shape == emb_to_subtract.shape
    ), f"Dimension mismatch: base_emb and emb_to_subtract must have the same shape. Got base_emb.shape = {base_emb.shape} and emb_to_subtract.shape = {emb_to_subtract.shape}"

    # Calculate the projection
    projection = calculate_projection(base_emb, emb_to_subtract)

    # Subtract the projection from base_emb
    base_emb = base_emb - projection

    # Normalize each resulting vector
    base_emb = normalize_embedding(base_emb)

    return base_emb


def cal_leftover_embeddings_pca(
    embedding,
    pca_to_subtract,
    number_of_pca_components_to_use=3,
    pca_explained_variance_to_use=None,
    change_dataset_percentage=0,
):
    if type(pca_explained_variance_to_use) is float:
        logging.info(
            f"pca_explained_variance_to_use: {pca_explained_variance_to_use}, OVERWRITING number_of_pca_components_to_use"
        )
        cum_sum_explained_variance = np.cumsum(pca_to_subtract.explained_variance_ratio_)
        # get the first index where the cum_sum_explained_variance is greater than the pca_explained_variance_to_use
        number_of_pca_components_to_use = np.argmax(
            cum_sum_explained_variance > pca_explained_variance_to_use
        )

    pca_explained_variance = pca_to_subtract.explained_variance_ratio_[
        :number_of_pca_components_to_use
    ].sum()
    logging.info(
        f"number_of_pca_components_to_use: {number_of_pca_components_to_use}, which explains {pca_explained_variance*100:.2f}% of the variance"
    )
    # Calculate which embeddings to change
    if change_dataset_percentage > 0:
        mean_concept_embedding = pca_to_subtract.mean_.reshape(1, -1)
        tmp_index = faiss.IndexFlatIP(embedding.shape[1])
        faiss.normalize_L2(embedding)
        tmp_index.add(embedding)
        num_of_embedding_to_change = int(embedding.shape[0] * change_dataset_percentage)
        logging.info(
            f"num_of_embedding_to_change: {num_of_embedding_to_change} out of {embedding.shape[0]}"
        )
        faiss.normalize_L2(mean_concept_embedding)
        tmp_dist_s, tmp_ind_s = tmp_index.search(mean_concept_embedding, num_of_embedding_to_change)
        embedding_to_change = embedding[tmp_ind_s.flatten()].copy()
    else:
        embedding_to_change = embedding.copy()

    # Calculate the leftover
    emb_to_mod_pca_inv = truncated_pca_transform_auto(
        embedding_to_change, pca_to_subtract, number_of_pca_components_to_use
    )
    emb_to_mod_pca_inv = emb_to_mod_pca_inv / np.linalg.norm(emb_to_mod_pca_inv, axis=1).reshape(
        -1, 1
    )
    emb_to_mod_left_over = cal_leftover_embeddings(embedding_to_change, emb_to_mod_pca_inv)

    # Returning to the original shape
    if change_dataset_percentage > 0:
        result_emb = embedding.copy()
        result_emb[tmp_ind_s.flatten()] = emb_to_mod_left_over
    else:
        result_emb = emb_to_mod_left_over

    return result_emb


class ConceptRetrieval:
    def __init__(self, configs=None):
        """
        Initialize the ConceptRetrieval with a list of concepts.
        """
        self.configs = configs
        self.logger = logging.getLogger(__name__)
        self.fitted = False

    def fit(self, embeddings: np.ndarray = None, paths: list[str] = None):
        """
        Fit the model with the provided embedding or paths to embeddings files (each should contain embedding nd.inner_product labels and urls).
        provide or embeddings or paths, not both.
        :param embeddings: Pre-calculated embeddings as a numpy inner_product.
        :param paths: List of paths to the npz files containing embeddings.
        """
        if embeddings is not None and paths is not None:
            raise ValueError("Provide either embeddings or paths, not both.")

        start_time = time()
        if embeddings is not None:
            if not isinstance(embeddings, np.ndarray):
                raise TypeError("Embeddings must be a numpy inner_product.")
            self.embeddings = embeddings
        elif paths is not None:
            # Load embeddings from the provided paths
            self.embeddings, self.labels, self.urls = load_pre_calculated_embeddings_from_paths(
                paths
            )
        else:
            raise ValueError("Either embeddings or paths must be provided.")

        if self.embeddings.ndim != 2:
            raise ValueError("Embeddings must be a 2D inner_product.")

        # Create the index for the embeddings
        self.index = EmbeddingIndex(
            self.embeddings, gpu=self.configs.get("gpu", 0) if self.configs else 0
        )

        self.fitted = True
        self.logger.info(
            f"ConceptRetrieval fitted with {self.embeddings.shape[0]} embeddings in {time() - start_time:.2f} seconds."
        )

    def __call__(self, *args, **kwds):
        """
        Call the retrieve method with the provided arguments.
        :param args: Positional arguments for the retrieve method.
        :param kwds: Keyword arguments for the retrieve method.
        :return: The result of the retrieve method.
        """
        return self.retrieve(*args, **kwds)

    def retrieve(
        self,
        query: np.ndarray,
        number_of_concepts: int = 5,
        number_of_samples_per_concept: int = 10,
        num_of_std_to_add_for_first_threshold: float = None,
        small_neighborhood_number_of_samples: int = None,
    ) -> list[tuple[str, list[str]]]:
        # Checks
        if self.fitted is False:
            raise RuntimeError("Model is not fitted. Call fit() before retrieve().")
        if not isinstance(query, np.ndarray):
            raise TypeError("Query must be a numpy inner_product.")
        if query.ndim != 2 and query.ndim != 1:
            raise ValueError(
                "Query must be a 2D inner_product with shape (1, d), or a 1D inner_product with shape (d,)."
            )
        # check if the query is a 1D inner_product and reshape it to 2D
        if query.ndim == 1:
            query = query.reshape(1, -1)
        if query.shape[1] != self.embeddings.shape[1]:
            raise ValueError(
                f"Query dimension {query.shape[1]} does not match embeddings dimension {self.embeddings.shape[1]}."
            )

        threshold_min_number_of_samples = (
            self.configs.get("threshold_min_number_of_samples", 50) if self.configs else 50
        )

        if num_of_std_to_add_for_first_threshold is None:
            num_of_std_to_add_for_first_threshold = (
                self.configs.get("num_of_std_to_add_for_first_threshold", None)
                if self.configs
                else None
            )
        if (
            num_of_std_to_add_for_first_threshold is not None
        ):  # Slow option better to leave it as None and set a constant for large_neighborhood_number_of_samples
            # calculate the number of samples for the large and small neighborhoods
            similarity = cosine_similarity(query, self.embeddings).squeeze()
            sim_mean = similarity.mean()
            sim_std = similarity.std()
            threshold = sim_mean + num_of_std_to_add_for_first_threshold * sim_std
            indexes_above_threshold = np.where(similarity > threshold)[-1]
            logging.info(
                f"Percentage of first stage filtered samples (mean+num_of_std_to_add_for_first_threshold*std): {(indexes_above_threshold.shape[0] / similarity.shape[0]) * 100 :.2f}%, Number of samples above threshold: {indexes_above_threshold.shape[0]}, Out of {similarity.shape[0]}, n_std: {num_of_std_to_add_for_first_threshold}, Threshold: {threshold:.3f}"
            )
            if len(indexes_above_threshold) < threshold_min_number_of_samples * 2:
                logging.info(
                    f"Too few samples above the threshold, returning the {threshold_min_number_of_samples*2} most similar samples."
                )
            large_neighborhood_number_of_samples = max(
                len(indexes_above_threshold), threshold_min_number_of_samples * 2
            )
        else:
            large_neighborhood_number_of_samples = (
                self.configs.get("large_neighborhood_number_of_samples", 10_000)
                if self.configs
                else 10_00
            )

        if small_neighborhood_number_of_samples is None:
            small_neighborhood_number_of_samples = (
                self.configs.get("small_neighborhood_number_of_samples", 750)
                if self.configs
                else 750
            )
        start_time = time()

        # create a new index so it can be changed during the retrieval
        curr_embedding_s = self.embeddings.copy()
        anchor = query.copy()  # anchor changes during the iterations while query is not
        index = EmbeddingIndex(
            curr_embedding_s, gpu=self.configs.get("gpu", 0) if self.configs else 0
        )

        concept_embed_s = []
        concept_scoret_s = []
        concept_pca_s = []
        top_k_concepts_indices_s = []
        top_k_concepts_distances_s = []
        for _concept_index in range(number_of_concepts):
            # get the large neighborhood of the query
            neighbors_distances, neighbors_indices = index.search(
                query, large_neighborhood_number_of_samples
            )
            self.logger.info(
                f"Retrieved {len(neighbors_indices)} neighbors in {time() - start_time:.2f} seconds."
            )

            # get the embeddings of the large neighborhood
            large_neighborhood_embeddings = curr_embedding_s[neighbors_indices]
            small_neighborhood_embeddings = large_neighborhood_embeddings[
                :small_neighborhood_number_of_samples
            ]

            # the query embedding as the last element in the large neighborhood
            large_neighborhood_embeddings = np.concatenate(
                (large_neighborhood_embeddings, anchor), axis=0
            )
            small_neighborhood_embeddings = np.concatenate(
                (small_neighborhood_embeddings, anchor), axis=0
            )

            # get inner product between each pair of embeddings between the smaller neighborhood and the query and the smaller neighborhood
            # NOTE: last row of inner_products is the inner product between the query and the mbeddings in the small neighborhood
            inner_products = cosine_similarity(
                large_neighborhood_embeddings, small_neighborhood_embeddings
            )

            # get per row histogram
            value_range = None
            if value_range is None:
                inner_products_flattened = inner_products.flatten()
                value_range = (inner_products_flattened.min(), inner_products_flattened.max())

            # define similar histogram bins for all rows
            bins = self.configs.get("histogram_number_of_bins", 100) if self.configs else 100
            bin_edges = np.linspace(value_range[0], value_range[1], bins + 1)
            bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

            # Calculate histogram for each row
            hist_s = np.zeros((inner_products.shape[0], bins), dtype=int)
            ind_to_bin_ind_s = np.zeros(
                (inner_products.shape), dtype=int
            )  # for each index in the row, the bin index it belongs to
            logging.info(f"Calculating histograms for {inner_products.shape[0]} rows.")
            start_time_histogram = time()

            hist_s, ind_to_bin_ind_s = vectorized_histogram_uniform(
                inner_products, value_range, bins
            )

            total_time_histogram = time() - start_time_histogram
            logging.info(f"Time taken to calculate histograms: {total_time_histogram:.2f} seconds")

            #
            smooth_sigma = self.configs.get("smooth_sigma", 0) if self.configs else 0
            if smooth_sigma > 0:
                hist_s = gaussian_filter1d(hist_s, sigma=smooth_sigma, axis=1, mode="nearest")

            start_time_peaks = time()
            peaks_s = np.apply_along_axis(
                find_peaks_in_histogram_padded, axis=1, arr=hist_s, max_len=10
            )
            total_time_peaks = time() - start_time_peaks
            logging.info(f"Time taken to find peaks in histograms: {total_time_peaks:.2f} seconds")

            separation_hight_s = np.zeros(inner_products.shape[0])
            min_peak_height_s = np.zeros(inner_products.shape[0])
            separation_hight_normalize_s = np.zeros(inner_products.shape[0])
            samples_in_largest_s = np.zeros(inner_products.shape[0], dtype=int)
            samples_inds_largest_s = {
                i: {} for i in range(inner_products.shape[0])
            }  # dict of lists to hold indices of samples in the largest gaussian
            mean_inds_of_largest_s = np.zeros(inner_products.shape[0], dtype=int)
            mean_anchor_dist_of_elem_in_largest_s = np.zeros(inner_products.shape[0])
            separation_idx_s = np.zeros(inner_products.shape[0], dtype=int)
            separation_peaks_dist_s = np.zeros(inner_products.shape[0], dtype=int)
            failed_to_find_peaks_s = np.zeros(inner_products.shape[0], dtype=bool)

            for i, (hist, peaks) in enumerate(zip(hist_s, peaks_s)):
                if (
                    sum(peaks > 0) < 2
                ):  # not enough peaks (peaks looks like [45, 69, -1, ..., -1, -1, -1], because max length is set to 10 it filles the rest of the mat with -1)
                    failed_to_find_peaks_s[i] = True
                    continue

                # import matplotlib.pyplot as plt
                # plt.clf()
                # plt.plot(hist, label=f"Row {i}")
                # plt.title(f"Histogram of Inner Products - Row {i}")
                # plt.savefig(f"tmp/tmp_histogram_row.png")
                # breakpoint()

                peaks.sort()
                rightmost_idx = peaks[
                    -1
                ]  # the largest value index in term of distance (not number of samples)
                second_rightmost_idx = peaks[-2]

                # find the min between the two largest peaks and get its the index (separation index)
                min_idx_range = np.logical_and(
                    bin_centers >= bin_centers[second_rightmost_idx],
                    bin_centers <= bin_centers[rightmost_idx],
                )
                valid_bins = np.where(min_idx_range)[0]  # absolute bin indices
                min_idx = valid_bins[np.argmin(hist[valid_bins])]  # correct global index
                separation_idx_s[i] = min_idx  # <- Original
                # TODO tmp test new - the anchor should be above the second gauss peak
                # separation_idx_s[i] = second_rightmost_idx # <- this is the test

                separation_peaks_dist_s[i] = min_idx_range.sum()

                # get the min hight between the two largest peaks
                min_between_the_two_peaks = min(hist[rightmost_idx], hist[second_rightmost_idx])
                min_peak_height_s[i] = min_between_the_two_peaks / inner_products.shape[0]

                # get normalized min height
                min_point_height = hist[min_idx]
                separation_hight_s[i] = min_point_height
                separation_hight_normalize_s[i] = (
                    min_point_height / min_between_the_two_peaks
                )  # TODO tmp test min

                # # get the number of samples in the largest gaussian
                # largest_gaussian_range = bin_centers >= bin_centers[min_idx]
                # num_samples_largest = np.sum(hist[largest_gaussian_range])
                # samples_in_largest_s[i] = num_samples_largest

                # Get indexes of samples in the largest gaussian
                samples_inds_largest_s[i] = np.where(ind_to_bin_ind_s[i] >= min_idx)[0]
                samples_in_largest_s[i] = len(samples_inds_largest_s[i])

                # TODO for the following we could add threshold to filter rows (maybe)
                mean_inds_of_largest_s[i] = np.mean(samples_inds_largest_s[i])
                mean_anchor_dist_of_elem_in_largest_s[i] = np.mean(
                    inner_products[samples_inds_largest_s[i], -1]
                )  # -1 should be the distance to the anchor (query) embedding

            # Check Conditions
            logging.info(
                f" failed_to_find_peaks_s: {failed_to_find_peaks_s.mean()*100:.2f}%, (number of peaks: {(~failed_to_find_peaks_s).sum()})"
            )
            anchor_failed_test = np.zeros(large_neighborhood_embeddings.shape[0], dtype=bool)

            min_number_of_sample_in_largest_failed_test = (
                samples_in_largest_s < threshold_min_number_of_samples
            )
            ratio_of_failed_min_samples_in_largest = (
                min_number_of_sample_in_largest_failed_test
            ).sum() / inner_products.shape[0]
            logging.info(
                f"ratio_of_failed_min_samples_in_largest: {ratio_of_failed_min_samples_in_largest * 100:.2f}%, (number of rows with less than {threshold_min_number_of_samples} samples in the largest gaussian: {(min_number_of_sample_in_largest_failed_test).sum()} out of {inner_products.shape[0]})"
            )
            do_anchor_similarity = (
                self.configs.get("do_anchor_similarity", None) if self.configs else None
            )
            if do_anchor_similarity is not None:
                # Uncomment below if doing anchor-in-largest test
                # if do_anchor_in_largest_test:
                anchor_failed_test = (inner_products[:, -1] < bin_centers[separation_idx_s]) | (
                    separation_idx_s < 0
                )
                anchor_failed_test = np.array(anchor_failed_test, dtype=bool)
                anchor_failed_test = ~failed_to_find_peaks_s & anchor_failed_test

                denominator = (~failed_to_find_peaks_s).sum()
                ratio_of_failed_anchor = (
                    anchor_failed_test.sum() / denominator if denominator > 0 else 0
                )

                logging.info(f"ratio anchor_failed_test: {ratio_of_failed_anchor * 100:.2f}%")

                if anchor_failed_test.mean() == 1:
                    logging.warning("All rows failed anchor test, CANCELLING! anchor test")
                    anchor_failed_test = np.zeros(inner_products.shape[0], dtype=bool)

                if ratio_of_failed_anchor == 1.0:
                    logging.warning(
                        "All surviving rows failed anchor test => skipping anchor check"
                    )
                    anchor_failed_test[:] = False

            passed_rows = (
                ~failed_to_find_peaks_s
                & ~anchor_failed_test
                & ~min_number_of_sample_in_largest_failed_test
            )
            if passed_rows.sum() == 0:
                logging.warning(
                    "No rows passed the tests, treating the smaller neighborhood as a single concept."
                )
                best_row_embeddings_in_largest = small_neighborhood_embeddings

            else:
                # Get the best row
                # breakpoint()
                best_row_idx = np.argmax(mean_anchor_dist_of_elem_in_largest_s[passed_rows])
                # convert to the original index
                best_row_idx_in_original = np.where(passed_rows)[0][best_row_idx]
                # Get the best samples in the largest gaussian
                best_row_samples_inds_in_largest = samples_inds_largest_s[best_row_idx_in_original]
                best_row_embeddings_in_largest = small_neighborhood_embeddings[
                    best_row_samples_inds_in_largest
                ]

            ## tmp save hist_s as an image and save TODO Debug
            do_plot_histograms = False
            if do_plot_histograms:
                from other.plot_histogram import (
                    plot_histogram,
                    plot_histograms_matrix,
                    plot_row_inds_distribution,
                )

                plot_histograms_matrix(
                    hist_s[passed_rows],
                    input_bin=ind_to_bin_ind_s[:, -1][passed_rows],
                    path="tmp/neighborhood_histograms",
                )
                plot_row_inds_distribution(
                    np.where(passed_rows)[0], path="tmp/row_inds_distribution.png"
                )

                logging.info(
                    f"Best row index: {best_row_idx_in_original}, with mean anchor distance: {mean_anchor_dist_of_elem_in_largest_s[best_row_idx_in_original]:.2f}"
                )
                # plot the best row histogram
                plot_histogram(
                    hist_s[best_row_idx_in_original],
                    input_bin=ind_to_bin_ind_s[:, -1][best_row_idx_in_original],
                    path="tmp/neighborhood_histograms",
                    title=f"best_row_histogram_row_index_{best_row_idx_in_original}",
                )

                # plot histogram of the best row TODO debug
                plot_histogram(
                    hist_s[best_row_idx_in_original],
                    input_bin=ind_to_bin_ind_s[:, -1][best_row_idx_in_original],
                    path="tmp/neighborhood_histograms",
                    title=f"best_row_histogram_row_index_{best_row_idx_in_original}",
                )

            # run pca on the embeddings in the largest gaussian in the best row
            pca_explained_variance_to_use = (
                self.configs.get("pca_explained_variance_to_use", 0.5) if self.configs else 0.5
            )

            pca = PCA()
            pca.fit(best_row_embeddings_in_largest)
            if type(pca_explained_variance_to_use) is float:
                logging.info(f"pca_explained_variance_to_use: {pca_explained_variance_to_use}")

                number_of_pca_components_to_use = np.argmax(
                    np.cumsum(pca.explained_variance_ratio_) > pca_explained_variance_to_use
                )
                logging.info(f"number_of_pca_components_to_use: {number_of_pca_components_to_use}")

            concept_embed = truncated_pca_transform_auto(
                query.reshape(1, -1), pca, number_of_pca_components_to_use
            ).flatten()

            concept_embed = concept_embed / np.linalg.norm(concept_embed)
            concept_scoret = cosine_similarity(
                query.reshape(1, -1), concept_embed.reshape(1, -1)
            ).item()
            logging.info(f"Element embedding scoret: {concept_scoret:.4f}")

            # retrieve the top k concepts based on the element embedding with the original index
            top_k_concepts_distances, top_k_concepts_indices = self.index.search(
                concept_embed.reshape(1, -1), number_of_samples_per_concept
            )

            # save the results

            concept_embed_s.append(concept_embed)
            concept_scoret_s.append(concept_scoret)
            concept_pca_s.append(pca)
            top_k_concepts_indices_s.append(top_k_concepts_indices)
            top_k_concepts_distances_s.append(top_k_concepts_distances)

            # Create the updated embedding by removing the concept from the embeddings
            logging.info("Changing dataset to remove the current concept")
            pca_explained_variance_to_use = (
                self.configs.get("pca_explained_variance_to_use", 0.5) if self.configs else 0.5
            )
            change_dataset_percentage = (
                self.configs.get("change_dataset_percentage", 0.1) if self.configs else 0.1
            )
            curr_embedding_s = cal_leftover_embeddings_pca(
                curr_embedding_s,
                pca,
                number_of_pca_components_to_use=number_of_pca_components_to_use,
                change_dataset_percentage=change_dataset_percentage,
                pca_explained_variance_to_use=pca_explained_variance_to_use,
            )
            anchor = cal_leftover_embeddings_pca(
                anchor,
                pca,
                number_of_pca_components_to_use=number_of_pca_components_to_use,
                change_dataset_percentage=0,
                pca_explained_variance_to_use=pca_explained_variance_to_use,
            )
            index = EmbeddingIndex(
                curr_embedding_s, gpu=self.configs.get("gpu", 0) if self.configs else 0
            )

        concept_embed_s = np.stack(concept_embed_s)
        concept_scoret_s = np.stack(concept_scoret_s)
        top_k_concepts_indices_s = np.stack(top_k_concepts_indices_s)
        top_k_concepts_distances_s = np.stack(top_k_concepts_distances_s)
        self.logger.info(f"Concept retrieval completed in {time() - start_time:.2f} seconds.")
        return_dict = {
            "concept_embed_s": concept_embed_s,
            "concept_scoret_s": concept_scoret_s,
            "concept_pca_s": concept_pca_s,
            "top_k_concepts_indices_s": top_k_concepts_indices_s,
            "top_k_concepts_distances_s": top_k_concepts_distances_s,
        }
        return return_dict


def get_concept_neighbors(
    concepts_dict,
    coret_instance,
    number_of_samples_per_concept,
    noise_std=0,
):
    """
    For each concept in `concepts_dict`, either:
      - if do_pca_sample=True: project to PCA space, replicate the projection,
        add Gaussian noise, back-project to the original space, then search
        for 1 nearest neighbor per noisy sample;
      - if do_pca_sample=False: search directly on the original concept
        embedding to get `number_of_samples_per_concept` neighbors.

    Args:
        concepts_dict: dict with keys
            - 'concepts':     array of shape (n_concepts, original_dim)
            - 'concepts_pca': list/array of PCA objects length n_concepts
        coret_instance:   object with .index.search(queries, k) method
        number_of_samples_per_concept: int, number of samples or neighbors per concept
        noise_std:       float, standard deviation of Gaussian noise (only if do_pca_sample)
        do_pca_sample:   bool, whether to use PCA sampling + noise or direct search

    Returns:
        distances: numpy array of shape (n_concepts * number_of_samples_per_concept, 1)
        indices:   numpy array of shape (n_concepts * number_of_samples_per_concept, 1)
    """
    distances, indices = [], []
    for concept_ind in range(concepts_dict["concept_embed_s"].shape[0]):
        cur_concept = concepts_dict["concept_embed_s"][concept_ind]

        if noise_std > 0:
            logging.warning(f"Using PCA sampling for noise std {noise_std}")
            cur_pca = concepts_dict["concept_pca_s"][concept_ind]

            # 1) Project to PCA space
            proj = cur_pca.transform(cur_concept[np.newaxis, :])  # (1, n_components)

            # 2) Repeat + add noise
            proj_rep = np.repeat(proj, number_of_samples_per_concept, axis=0)
            noisy_proj = proj_rep + np.random.normal(loc=0.0, scale=noise_std, size=proj_rep.shape)

            # normalize the noisy projection
            noisy_proj = noisy_proj / np.linalg.norm(noisy_proj, axis=1, keepdims=True)

            # 3) Back-project to original space
            queries = cur_pca.inverse_transform(noisy_proj).astype(np.float32)

            # 4) Search 1 neighbor per noisy sample
            faiss.normalize_L2(queries)
            dists, idxs = coret_instance.index.search(queries, 1)

            # transpose so that each sample contributes one row
            distances.append(dists.T)
            indices.append(idxs.T)
        else:
            # Direct search on the raw embedding: get k neighbors at once
            queries = cur_concept[np.newaxis, :].astype(np.float32)
            # normalize the query
            queries = queries / np.linalg.norm(queries, axis=1, keepdims=True)
            faiss.normalize_L2(queries)
            dists, idxs = coret_instance.index.search(queries, number_of_samples_per_concept)
            distances.append(dists)
            indices.append(idxs)

    distances = np.stack(distances, axis=0)
    indices = np.stack(indices, axis=0)
    return distances, indices
