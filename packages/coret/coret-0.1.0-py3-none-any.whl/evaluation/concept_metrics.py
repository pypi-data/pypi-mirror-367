import numpy as np
from itertools import combinations
from sklearn.metrics.pairwise import cosine_similarity
from core_utils import cal_remove_leftover_embeddings
from scipy.stats import norm
import logging
from typing import Tuple, List

# Concept Metrics

## Relevance Score

# def compute_relevance_score_per_concept(concept_neighbors_gt_labels_bin_s: np.ndarray, gt_bin: np.ndarray) -> float:
#     """
#     Computes the relevance score for the given 3D binary matrix with respect to the ground truth.

#     Parameters:
#         concept_neighbors_gt_labels_bin (np.ndarray): A 2D binary numpy array of shape (n, d), e.g. (10, 80) 
#             where n is the number of concepts and d the total number of label options.
#         gt_bin (np.ndarray): A 1D binary numpy array of shape (d,) representing the ground truth.
#     """
#     concept_mean_labels_bin = concept_neighbors_gt_labels_bin_s.mean(axis=1) 
#     breakpoint()
#     concept_relevance_score = (concept_mean_labels_bin * gt_bin).sum(axis=1) / gt_bin.sum()
#     return concept_relevance_score
    

def compute_relevance_score_per_concept(concept_neighbors_gt_labels_bin_s: np.ndarray, gt_bin: np.ndarray) -> np.ndarray:
    """
    Computes the relevance score for each concept slice in a 3D binary matrix with respect to the ground truth.
    
    Parameters:
        concept_neighbors_gt_labels_bin_s (np.ndarray): A 3D binary numpy array of shape (c, n, d),
            where c is the number of concepts, n is the number of neighbors, and d the total number of label options.
        gt_bin (np.ndarray): A 1D binary numpy array of shape (d,) representing the ground truth.
    
    Returns:
        np.ndarray: A 1D array of shape (c,) containing the relevance score for each concept.
    """
    if concept_neighbors_gt_labels_bin_s.ndim != 3:
        raise ValueError(f"Expected a 3D input of shape (c, n, d), but got {concept_neighbors_gt_labels_bin_s.shape}")

    if gt_bin.ndim != 1:
        raise ValueError(f"Expected gt_bin to be 1D, but got shape {gt_bin.shape}")

    c, n, d = concept_neighbors_gt_labels_bin_s.shape
    if d != gt_bin.shape[0]:
        raise ValueError(f"Shape mismatch: last dimension of input ({d}) must match gt_bin shape ({gt_bin.shape[0]})")

    # Compute mean along axis=1 (neighbors)
    concept_mean_labels_bin = concept_neighbors_gt_labels_bin_s.mean(axis=1)  # Shape (c, d)

    # Compute relevance score for each concept
    concept_relevance_score = (concept_mean_labels_bin * gt_bin).sum(axis=1) / gt_bin.sum()

    return concept_relevance_score  # Shape (c,)


def compute_bin_relevance_score_per_concept_prev(concept_neighbors_gt_labels_bin_s: np.ndarray, gt_bin: np.ndarray) -> np.ndarray:
    """
    Computes a binary relevance score for each concept. For each concept, the function calculates 
    the mean over its neighbors to form a mean label vector, identifies the label with the maximum mean,
    and then returns 1 if that label is present in the ground truth (i.e. gt_bin for that label is 1), 
    otherwise returns 0.

    Parameters:
        concept_neighbors_gt_labels_bin_s (np.ndarray): A 3D binary numpy array of shape (c, n, d), 
            where c is the number of concepts, n is the number of neighbors, and d is the total number 
            of label options.
        gt_bin (np.ndarray): A 1D binary numpy array of shape (d,) representing the ground truth.

    Returns:
        np.ndarray: A binary numpy array of shape (c,), where each element is 1 if the label with the 
        highest mean value for that concept is present in gt_bin, or 0 otherwise.
    """
    # Compute the mean label vector for each concept over its neighbors (shape: (c, d))
    concept_mean_labels_bin = concept_neighbors_gt_labels_bin_s.mean(axis=1)
    
    # For each concept, get the index of the label with the maximum mean value
    max_indices = np.argmax(concept_mean_labels_bin, axis=1)
    
    # For each concept, check if the label corresponding to the maximum mean is present in gt_bin.
    # This creates a binary array: 1 if gt_bin at the max index equals 1, else 0.
    result = (gt_bin[max_indices] == 1).astype(int)
    
    return result


def compute_bin_relevance_score_per_concept(concept_neighbors_gt_labels_bin_s: np.ndarray, gt_bin: np.ndarray) -> np.ndarray:
    """
    Computes a binary relevance score for each concept. For each concept, the function calculates 
    the mean over its neighbors to form a mean label vector, identifies the label with the maximum mean,
    and then returns 1 if that label is present in the ground truth (i.e. gt_bin for that label is 1), 
    otherwise returns 0.

    Parameters:
        concept_neighbors_gt_labels_bin_s (np.ndarray): A 3D binary numpy array of shape (c, n, d), 
            where c is the number of concepts, n is the number of neighbors, and d is the total number 
            of label options.
        gt_bin (np.ndarray): A 1D binary numpy array of shape (d,) representing the ground truth.

    Returns:
        np.ndarray: A binary numpy array of shape (c,), where each element is 1 if the label with the 
        highest mean value for that concept is present in gt_bin, or 0 otherwise.
    """
    result = concept_neighbors_gt_labels_bin_s * gt_bin
    result = np.max(result, axis=2)
    result = result.mean(axis=1)


    
    return result


def weighted_paper_score(matrix: np.ndarray, weights: np.ndarray = None) -> float:
    """
    "Computes a weighted version of the paper_score.
    Instead of the simple mean per row, we compute the weighted mean per row 
    and use a weighted L2 norm.
    
    Parameters:
        matrix (np.ndarray): 2D binary array of shape (n, d).
        weights (np.ndarray): 1D array of shape (d,) with per-feature weights.
        
    Returns:
        float: Weighted consistency score.
    """
    weights = np.ones(matrix.shape[1]) if weights is None else weights
    # Compute weighted mean per row: (matrix * weights).sum(axis=1) / sum(weights)
    weighted_mean = (matrix * weights).sum(axis=1) / weights.sum()
    # Calculate the difference for each element from its row's weighted mean
    diff = matrix - weighted_mean[:, None]
    # Compute the weighted L2 norm per row
    norm_per_row = np.sqrt((diff ** 2 * weights).sum(axis=1))
    # Normalize by sqrt of total weight (analogous to sqrt(matrix.shape[1]) in the unweighted version)
    return norm_per_row.mean() / np.sqrt(weights.sum())


def weighted_jaccard_score(matrix: np.ndarray, weights: np.ndarray = None) -> float:
    """
    Computes the weighted average pairwise Jaccard similarity.
    The intersection and union are weighted by the provided weights.
    
    Parameters:
        matrix (np.ndarray): 2D binary array of shape (n, d).
        weights (np.ndarray): 1D array of shape (d,).
    
    Returns:
        float: Weighted average Jaccard similarity.
    """
    breakpoint()
    weights = np.ones(matrix.shape[1]) if weights is None else weights
    scores = []
    n = matrix.shape[0]
    for i, j in combinations(range(n), 2):
        a = matrix[i].astype(bool)
        b = matrix[j].astype(bool)
        # Weighted intersection and union
        intersection = np.sum(weights * (a & b))
        union = np.sum(weights * (a | b))
        sim = 1.0 if union == 0 else intersection / union
        scores.append(sim)
    return np.mean(scores) if scores else 0.0


def weighted_cosine_similarity_score(matrix: np.ndarray, weights: np.ndarray = None) -> float:
    """
    Computes the weighted average pairwise cosine similarity.
    The dot product and norms incorporate the weights.
    
    Parameters:
        matrix (np.ndarray): 2D binary array of shape (n, d).
        weights (np.ndarray): 1D array of shape (d,).
    
    Returns:
        float: Weighted average cosine similarity.
    """
    weights = np.ones(matrix.shape[1]) if weights is None else weights

    scores = []
    n = matrix.shape[0]
    for i, j in combinations(range(n), 2):
        a = matrix[i]
        b = matrix[j]
        # Weighted dot product: sum(weights * a * b)
        dot_product = np.dot(weights, a * b)
        norm_a = np.sqrt(np.dot(weights, a ** 2))
        norm_b = np.sqrt(np.dot(weights, b ** 2))
        sim = dot_product / (norm_a * norm_b) if norm_a and norm_b else 0.0
        scores.append(sim)
    return np.mean(scores) if scores else 0.0


def weighted_hamming_distance_score(matrix: np.ndarray, weights: np.ndarray = None) -> float:
    """
    Computes the weighted average pairwise Hamming distance.
    Each feature difference is weighted by the corresponding weight.
    
    Parameters:
        matrix (np.ndarray): 2D binary array of shape (n, d).
        weights (np.ndarray): 1D array of shape (d,).
    
    Returns:
        float: Weighted average Hamming distance.
    """
    
    weights = np.ones(matrix.shape[1]) if weights is None else weights

    scores = []
    n = matrix.shape[0]
    for i, j in combinations(range(n), 2):
        # Weight each differing feature
        distance = np.sum(weights * (matrix[i] != matrix[j]))
        scores.append(distance)
    return np.mean(scores) if scores else 0.0


def weighted_entropy_score(matrix: np.ndarray, weights: np.ndarray = None) -> float:
    """
    Computes a weighted average entropy across the columns.
    For each feature (column), the binary entropy is computed,
    and then a weighted average is taken using the provided weights.
    
    Parameters:
        matrix (np.ndarray): 2D binary array of shape (n, d).
        weights (np.ndarray): 1D array of shape (d,).
    
    Returns:
        float: Weighted average entropy.
    """
    weights = np.ones(matrix.shape[1]) if weights is None else weights
    # Fraction of ones per column
    p = np.mean(matrix, axis=0)
    eps = 1e-12  # to avoid log2(0)
    entropy = -p * np.log2(p + eps) - (1 - p) * np.log2((1 - p) + eps)
    # Set entropy to 0 for columns that are all 0 or all 1
    entropy[p < eps] = 0.0
    entropy[(1 - p) < eps] = 0.0
    # Compute the weighted average entropy
    return np.sum(weights * entropy) / np.sum(weights)




compute_consistency_score_options = ["jaccard", "cosine", "hamming", "entropy", "paper"]

## Consistency Score

# def compute_consistency_score_per_concept(concept_neighbors_gt_labels_bin_s: np.ndarray, method: str) -> np.ndarray:
    # """
    # Wrapper function that computes the consistency score using the specified method.
    
    # Parameters:
    #     concept_neighbors_gt_labels_bin (np.ndarray): A 3D binary numpy array of shape (c, n, d), e.g. (3, 10, 80). where c is the number of concepts. n is the number of neighbors and d the total number of label options.
    #     method (str): The method to use. One of "jaccard", "cosine", "hamming", "entropy".
    
    # Returns:
    #     float: The computed consistency score.
    
    # Raises:
    #     ValueError: If an unknown method is specified.
    # """
    # results = []
    # for concept_neighbors_gt_labels_bin in concept_neighbors_gt_labels_bin_s:
    #     method = method.lower()
    #     if method == "jaccard":
    #         score = weighted_jaccard_score(concept_neighbors_gt_labels_bin)
    #         score = 1 - score
    #     elif method == "cosine":
    #         score = weighted_cosine_similarity_score(concept_neighbors_gt_labels_bin)
    #         score = 1 - score
    #     elif method == "hamming":
    #         score = weighted_hamming_distance_score(concept_neighbors_gt_labels_bin)
    #         score = 1 - score
    #     elif method == "entropy":
    #         score = weighted_entropy_score(concept_neighbors_gt_labels_bin)
    #         score = 1 - score
    #     elif method == "paper":
    #         score = weighted_paper_score(concept_neighbors_gt_labels_bin)
    #         score = 1 - score
    #     else:
    #         raise ValueError(f"Unknown method: {method}. Choose from 'jaccard', 'cosine', 'hamming', or 'entropy'.")
    #     results.append(score)
    # return np.array(results)

def compute_consistency_score_per_concept(concept_neighbors_gt_labels_bin_s: np.ndarray, method: str) -> np.ndarray:
    """
    Wrapper function that computes the consistency score using the specified method.
    
    Parameters:
        concept_neighbors_gt_labels_bin_s (np.ndarray): A 3D binary numpy array of shape (c, n, d),
            where c is the number of concepts, n is the number of neighbors and d the total number of label options.
        method (str): The method to use. One of "jaccard", "cosine", "hamming", "entropy", or "paper".
    
    Returns:
        np.ndarray: Array of consistency scores, one per concept.
    
    Raises:
        ValueError: If an unknown method is specified.
    """
    results = []
    method_lower = method.lower()
    for concept_neighbors_gt_labels_bin in concept_neighbors_gt_labels_bin_s:
        if method_lower == "jaccard":
            
            score = weighted_jaccard_score(concept_neighbors_gt_labels_bin)
            score = 1 - score
        elif method_lower == "cosine":
            score = weighted_cosine_similarity_score(concept_neighbors_gt_labels_bin)
            score = 1 - score
        elif method_lower == "hamming":
            score = weighted_hamming_distance_score(concept_neighbors_gt_labels_bin)
            score = 1 - score
        elif method_lower == "entropy":
            score = weighted_entropy_score(concept_neighbors_gt_labels_bin)
            score = 1 - score
        elif method_lower == "paper":
            score = weighted_paper_score(concept_neighbors_gt_labels_bin)
            score = 1 - score
        else:
            raise ValueError(f"Unknown method: {method}. Choose from 'jaccard', 'cosine', 'hamming', 'entropy', or 'paper'.")
        
        # Clip near-zero scores to exactly zero to avoid floating-point issues.
        if abs(score) < 1e-10:
            score = 0.0
        results.append(score)
    return np.array(results)




# Inner diversity score


def compute_inner_diversity_score_per_concept(concept_neighbors_gt_labels_bin_s: np.ndarray,
                                              method: str) -> np.ndarray:
    """
    Computes the weighted inner diversity score for each concept (slice) of a 3D binary array.
    The input array has shape (c, n, d): c concepts, n neighbors, and d features.
    
    For methods 'jaccard', 'cosine', 'hamming', and 'entropy', the weighted score is computed
    using the provided functions with weights derived from 1 - (mean across concepts).
    For the 'paper' method, if all neighbor rows are identical, the inner diversity is defined as 0.
    
    Parameters:
        concept_neighbors_gt_labels_bin_s (np.ndarray): 3D binary array.
        method (str): One of "jaccard", "cosine", "hamming", "entropy", or "paper".
    
    Returns:
        np.ndarray: Array of weighted inner diversity scores, one per concept.
    """
    # Compute the mean over neighbors per concept (shape: (c, d))
    concept_mean_labels_bin = concept_neighbors_gt_labels_bin_s.mean(axis=1)
    # Compute weights based on the overall mean across concepts (shape: (d,))
    weights = 1 - concept_mean_labels_bin.mean(axis=0)
    
    results = []
    method_lower = method.lower()
    for concept_neighbors_gt_labels_bin in concept_neighbors_gt_labels_bin_s:
        if method_lower == "jaccard":
            score = weighted_jaccard_score(concept_neighbors_gt_labels_bin, weights)
        elif method_lower == "cosine":
            score = weighted_cosine_similarity_score(concept_neighbors_gt_labels_bin, weights)
        elif method_lower == "hamming":
            score = weighted_hamming_distance_score(concept_neighbors_gt_labels_bin, weights)
        elif method_lower == "entropy":
            score = weighted_entropy_score(concept_neighbors_gt_labels_bin, weights)
        elif method_lower == "paper":
            # If all neighbor rows are identical, diversity is 0.
            if np.all(concept_neighbors_gt_labels_bin == concept_neighbors_gt_labels_bin[0]):
                score = 0.0
            else:
                score = weighted_paper_score(concept_neighbors_gt_labels_bin, weights)
        else:
            raise ValueError(f"Unknown method: {method}. Choose from 'jaccard', 'cosine', 'hamming', 'entropy', or 'paper'.")
        results.append(score)
    return np.array(results)



def distinctiveness_score_per_concept(concept_neighbors_gt_labels_bin_s):
    """
    Compute the normalized distinctiveness score for each concept from a 3D numpy array 
    of binary label vectors with shape (c, n, t), where:
      - c: number of concept sets,
      - n: number of samples per concept,
      - t: length of each binary vector.

    For each concept i, the distinctiveness score is computed as follows:
      1. For every other concept j (j ≠ i):
         - For each sample in concept i, compute its Hamming distances 
           to all samples in concept j (the Hamming distance is the number 
           of differing bit positions).
         - Compute the average of these distances for that sample.
         - Then, compute the mean of these per-sample averages, which yields 
           the average Hamming distance from concept i to concept j.
      2. The distinctiveness score for concept i is defined as the minimum 
         among these average distances (i.e. the lowest average Hamming distance 
         from concept i to any other concept).
      3. Finally, the score is normalized by dividing by t, so that the score 
         always lies between 0 and 1.

    Parameters:
        concept_neighbors_gt_labels_bin_s (np.ndarray): 3D array with shape (c, n, t)

    Returns:
        concept_scores (np.ndarray): 1D array of length c, where each element is the 
                                     normalized distinctiveness score for that concept.
                                     A lower score indicates that the samples in that 
                                     concept are, on average, more similar to the samples 
                                     of at least one other concept.
    """
    c, n, t = concept_neighbors_gt_labels_bin_s.shape
    concept_scores = np.zeros(c, dtype=float)
    
    for i in range(c):
        min_distance = np.inf
        for j in range(c):
            if i == j:
                continue
            sample_mean_s = []    
            for sample in concept_neighbors_gt_labels_bin_s[i]:
                distances = np.sum(sample != concept_neighbors_gt_labels_bin_s[j], axis=1)
                sample_mean_s.append(distances.mean())
            sample_mean = np.mean(sample_mean_s)
            if sample_mean < min_distance:
                min_distance = sample_mean
        # Normalize by dividing by t so the score is in [0, 1]
        concept_scores[i] = min_distance / t
    
    return concept_scores



# Embedding based metrics


# Embedding based Relevance score 
def compute_embedding_based_relevance_score_per_concept(inputs_emb_s, concepts_emb_s):
    """
    Computes relevance scores for each input with its corresponding concepts.
    
    Args:
      inputs_emb_s: numpy array of shape (n_inputs, emb_dim)
      concepts_emb_s: numpy array of shape (n_inputs, n_concepts, emb_dim)
      
    Returns:
      fin_relevance_scores: numpy array of shape (n_inputs,)
    """
    
    # Compute cosine similarity between each input and its corresponding concepts
    # This returns an array of shape (n_inputs, n_concepts)
    relevance_scores = np.array([
        ((cosine_similarity(input_emb.reshape(1, -1), concepts_emb) + 1) / 2)[0]
        for input_emb, concepts_emb in zip(inputs_emb_s, concepts_emb_s)
    ])
    
    # Average the similarities of the first num_concept_to_use concepts per input
    
    return relevance_scores

from tqdm.auto import tqdm
def compute_normalized_embedding_based_relevance_score_per_concept(
    inputs_embs: np.ndarray, 
    concepts_embs: np.ndarray, 
    random_embs_for_normalization: np.ndarray,
    epsilon: float = 1e-8
) -> np.ndarray:
    """
    Computes normalized relevance scores for each input and its corresponding concepts.
    
    The function computes the cosine similarity between each input embedding and its associated
    concept embeddings (scaled to [0, 1]). It then uses a set of random embeddings to calculate
    a mean and standard deviation of cosine similarities, which are applied via the cumulative
    distribution function (CDF) to normalize the relevance scores.
    
    Args:
      inputs_embs (np.ndarray): Array of shape (n_inputs, emb_dim).
      concepts_embs (np.ndarray): Array of shape (n_inputs, n_concepts, emb_dim).
      random_embs_for_normalization (np.ndarray): Array of shape (n_random, emb_dim) used for normalization. (should be other concepts embeddings)
      epsilon (float): Small constant to avoid division by zero when standard deviation is zero.
      
    Returns:
      normalized_relevance_scores (np.ndarray): Array of shape (n_inputs, n_concepts) containing the normalized scores.
    """
    # Compute cosine similarity between each input and its corresponding concepts.
    # Scale similarities to the range [0, 1].
    relevance_scores = np.array([
        ((cosine_similarity(input_emb.reshape(1, -1), concept_emb) + 1) / 2)[0]
        for input_emb, concept_emb in zip(inputs_embs, concepts_embs)
    ])

    
    # Calculate mean and std of cosine similarities between each input and random embeddings.
    # random_mu_list = []
    # random_sigma_list = []
    # for input_emb in tqdm(inputs_embs, desc="Computing random relevance scores", total=len(inputs_embs)):
    #     random_scores = cosine_similarity(input_emb.reshape(1, -1), random_embs_for_normalization)
    #     mu = random_scores.mean()
    #     sigma = random_scores.std()
    #     random_mu_list.append(mu)
    #     random_sigma_list.append(sigma if sigma > 0 else epsilon)

    # # Convert to numpy arrays and reshape for broadcasting.
    # random_mu = np.array(random_mu_list).reshape(-1, 1)        # Shape: (n_inputs, 1)
    # random_sigma = np.array(random_sigma_list).reshape(-1, 1)  # Shape: (n_inputs, 1)
    

    # Compute cosine similarities between all input embeddings and random embeddings
    # Resulting shape: (n_inputs, n_random)
    random_scores_all = (cosine_similarity(inputs_embs, random_embs_for_normalization) + 1) / 2

    
    # tmp plot random scores histogram
    import matplotlib.pyplot as plt
    
    plt.hist(random_scores_all[1,:], bins=100)
    plt.title("Random scores histogram")
    plt.xlabel("Random scores")
    plt.ylabel("Frequency")
    # save the plot
    plt.savefig("tmp_random_scores_histogram.png")
    # Compute the mean and standard deviation along the random embeddings axis
    random_mu = random_scores_all.mean(axis=1, keepdims=True)      # Shape: (n_inputs, 1)
    random_sigma = random_scores_all.std(axis=1, keepdims=True)      # Shape: (n_inputs, 1)

    # Replace any zero (or negative) standard deviations with epsilon to avoid division issues
    random_sigma = np.where(random_sigma > 0, random_sigma, epsilon)

    # TODO tmp
    sigma_scale = 2.5
    # logging.warning(f"changed Random sigma: {random_sigma} to {random_sigma*2}")
    logging.warning(f"changed Random sigma by {sigma_scale}")
    random_sigma = random_sigma * sigma_scale


    # Normalize relevance scores using the CDF based on the computed mean and std.
    normalized_relevance_scores = norm.cdf(relevance_scores, loc=random_mu, scale=random_sigma)
    
    return normalized_relevance_scores


# Embedding based Consistency score

# def compute_embedding_based_consistency_score_per_concept(concepts_emb_s, concepts_retrieved_emb_s):
#     """
#     Computes consistency scores using sklearn's cosine_similarity efficiently.

#     Args:
#         concepts_emb_s: (inputs, concepts, emb_dim)
#         concepts_retrieved_emb_s: (inputs, concepts, samples, emb_dim)

#     Returns:
#         consistency_scores: (inputs, concepts)
#     """
#     inputs, concepts, samples, emb_dim = concepts_retrieved_emb_s.shape
#     consistency_scores = np.zeros((inputs, concepts))

#     for i in range(inputs):
#         for c in range(concepts):
#             reference_emb = concepts_emb_s[i, c].reshape(1, -1)        # (1, emb_dim)
#             retrieved_emb = concepts_retrieved_emb_s[i, c]              # (samples, emb_dim)
#             sim_scores = (cosine_similarity(reference_emb, retrieved_emb) + 1) / 2  # (1, samples)
#             consistency_scores[i, c] = sim_scores.mean()

#     return consistency_scores

## V2  Consistency score -> using  the normalized mean of the retrieved embeddings
def compute_embedding_based_consistency_score_per_concept(concepts_emb_s, concepts_retrieved_emb_s):
    """
    Computes consistency scores using sklearn's cosine_similarity efficiently.

    Args:
        concepts_emb_s: (inputs, concepts, emb_dim)
        concepts_retrieved_emb_s: (inputs, concepts, samples, emb_dim)

    Returns:
        consistency_scores: (inputs, concepts)
    """
    inputs, concepts, samples, emb_dim = concepts_retrieved_emb_s.shape
    consistency_scores = np.zeros((inputs, concepts))

    # norm to unit sphere
    normed_concepts_emb_s = concepts_emb_s / np.linalg.norm(concepts_emb_s, axis=-1, keepdims=True) # (inputs, concepts, emb_dim)
    normed_concepts_retrieved_emb_s = concepts_retrieved_emb_s / np.linalg.norm(concepts_retrieved_emb_s, axis=-1, keepdims=True) # (inputs, concepts, samples, emb_dim)

    for i in range(inputs):
        for c in range(concepts):
            reference_emb = normed_concepts_emb_s[i, c].reshape(1, -1)        # (1, emb_dim)
            retrieved_emb = normed_concepts_retrieved_emb_s[i, c]              # (samples, emb_dim)
            mean_retrieved_emb = retrieved_emb.mean(axis=0).reshape(1, -1)  # (1, emb_dim)
            
            # # using the cosine similarity to the reference embedding
            # sim_scores = (cosine_similarity(reference_emb, mean_retrieved_emb) + 1) / 2  # (1, samples)
            
            # # usd the dot product instead of the cosine similarity
            # sim_scores = np.dot(reference_emb, mean_retrieved_emb.T) / (np.linalg.norm(reference_emb))

            # use just the norm of the mean
            sim_scores = np.linalg.norm(mean_retrieved_emb, axis=-1).reshape(1, -1)  
            consistency_scores[i, c] = sim_scores.mean()

    return consistency_scores


# Embedding based Inner diversity score
# def compute_embedding_based_inner_diversity_score_per_concept(concepts_emb_s, concepts_retrieved_emb_s):
#     """
#     concepts_retrieved_emb_s: numpy array of shape (inputs, concepts, samples, embedding_dim)
#     Returns diversity scores of shape (inputs, concepts)
#     """
#     inputs, concepts, samples, embedding_dim = concepts_retrieved_emb_s.shape


    
#     inner_diversity_scores = np.zeros((inputs, concepts))
#     for i in range(inputs):
#         for c in range(concepts):
#             concept_emb = concepts_retrieved_emb_s[i, c]  # (samples, embedding_dim)
#             sim_matrix = (cosine_similarity(concept_emb) + 1) / 2   # (samples, samples)
#             # Exclude diagonal (self-similarity)
#             np.fill_diagonal(sim_matrix, np.nan)
#             mean_sim = np.nanmean(sim_matrix)
#             inner_diversity_scores[i, c] = 1 - mean_sim

#     return inner_diversity_scores

## V2 Embedding based Inner diversity score using leftover embeddings
def compute_embedding_based_inner_diversity_score_per_concept(concepts_emb_s, concepts_retrieved_emb_s, pca_comp_to_use=5):
    """
    concepts_retrieved_emb_s: numpy array of shape (inputs, concepts, samples, embedding_dim)
    Returns diversity scores of shape (inputs, concepts)
    """
    inputs, concepts, samples, embedding_dim = concepts_retrieved_emb_s.shape

    # remove concepts_emb_s from concepts_retrieved_emb_s

    concepts_emb_s_repeated = np.tile(concepts_emb_s[:, :, np.newaxis, :], (1, 1, concepts_retrieved_emb_s.shape[2], 1))
    left_over_concepts_retrieved_emb_s = cal_remove_leftover_embeddings(base_emb=concepts_retrieved_emb_s, emb_to_remove=concepts_emb_s_repeated)
    
    inner_diversity_scores = np.zeros((inputs, concepts))
    for i in range(inputs):
        for c in range(concepts):
            concept_leftover_emb = left_over_concepts_retrieved_emb_s[i, c]  # (samples, embedding_dim)
            # normalize to unit sphere
            concept_leftover_emb = concept_leftover_emb / np.linalg.norm(concept_leftover_emb, axis=-1, keepdims=True) # (samples, embedding_dim)
            
            # # v1
            # sim_matrix = (cosine_similarity(concept_leftover_emb) + 1) / 2   # (samples, samples)
            # # # Exclude diagonal (self-similarity)
            # # # np.fill_diagonal(sim_matrix, np.nan)
            # mean_sim = np.mean(sim_matrix[np.tril_indices(samples, k=-1)])
            
            # # v2
            # # use the dot product instead of the cosine similarity
            # sim_matrix = np.dot(concept_leftover_emb, concept_leftover_emb.T)
            # # mean on the lower triangle
            # mean_sim = np.mean(sim_matrix[np.tril_indices(samples, k=0)])
            # mean_sim = (mean_sim + 1) / 2 
            
            # # v3
            # # just return the mean l2 distance
            # # mean_sim = np.linalg.norm(concept_leftover_emb, axis=1).mean()
            # mean_sim = np.linalg.norm(concept_leftover_emb.mean(axis=0, keepdims=True), axis=-1).mean()

            # v4
            # fit pca and check the variance of the first component
            from sklearn.decomposition import PCA
            pca = PCA()
            # pca.fit(concept_leftover_emb)
            pca.fit(concepts_retrieved_emb_s[i, c])
            # opt 1: cumulative_variance 
            cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
            mean_sim = 1 - cumulative_variance[pca_comp_to_use-1]
            # mean_sim = np.mean(pca.explained_variance_ratio_)
            mean_div = 1 - mean_sim 

            # # opt 2: check for cosine similarity on the first eigen vector
            # chk_vec_pca_space = np.zeros((pca_comp_to_use, pca.n_components_))
            # # fill diagonal with 1
            # np.fill_diagonal(chk_vec_pca_space, 1)
            # chk_vec = pca.inverse_transform(chk_vec_pca_space)
            

            inner_diversity_scores[i, c] = mean_div

    if np.any(np.isnan(inner_diversity_scores)):
        logging.warning(f"inner_diversity_scores has {np.isnan(inner_diversity_scores).sum()} NaN values out of {inner_diversity_scores.size}") 
        inner_diversity_scores = np.nan_to_num(inner_diversity_scores, nan=np.nanmean(inner_diversity_scores))


    return inner_diversity_scores


    
# Embedding based Diversity score
def compute_embedding_based_diversity_score(concepts_emb_s):
    diversity_list = []
    
    for curr_concepts_emb in concepts_emb_s:
        
        # Compute cosine similarity among selected embeddings
        sim_matrix = (cosine_similarity(curr_concepts_emb, curr_concepts_emb) + 1) / 2  
        
        # (Optional: Exclude self-similarity by setting diagonal to np.nan)
        np.fill_diagonal(sim_matrix, -1)
        
        # Get the maximum similarity per row
        max_sims = sim_matrix.max(axis=1)
        # Uncomment the print if needed for debugging:
        # print(max_sims.shape)
        diversity_list.append(max_sims)
    
    # Stack to get an array of shape 
    diversity_arr = np.stack(diversity_list, axis=0)
    # Average over the concepts to obtain a per-input diversity score (shape: (n_inputs,))
    per_input_diversity = 1 - diversity_arr.mean(axis=1)
    return per_input_diversity



def prune_repeated_rows_all(
    arr_full: np.ndarray,         # (n, m, t, d)  e.g. (540, 3, 20, 1024)
    arr_condensed: np.ndarray,    # (n, m, d)     e.g. (540, 3, 1024)
    arr_inputs: np.ndarray,       # (n, d)        e.g. (540, 1024)
    *,
    atol: float = 1e-6,
    require_all_m: bool = True    # drop row only if **every** of the m lists repeats
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[int]]:
    """
    Detect rows where the t embeddings are identical (within `atol`) and
    remove those rows from all three input arrays.

    Returns
    -------
    pruned_full      : (n_keep, m, t, d)
    pruned_condensed : (n_keep, m, d)
    pruned_inputs    : (n_keep, d)
    removed_idx      : list[int]  -- axis-0 indices that were dropped
    """
    # ------------------------------------------------------------------
    # 1. Detect repetitions in the (n, m, t, d) array
    # ------------------------------------------------------------------
    identical = np.all(                          # shape  (n, m)
        np.isclose(arr_full, arr_full[:, :, :1, :], atol=atol),
        axis=(2, 3)                              # collapse t and d
    )

    rows_to_drop = np.all(identical, axis=1) if require_all_m \
                   else np.any(identical, axis=1)

    keep_mask    = ~rows_to_drop                 # shape (n,)
    removed_idx  = np.flatnonzero(rows_to_drop).tolist()

    # ------------------------------------------------------------------
    # 2. Apply the same mask to every array
    # ------------------------------------------------------------------
    return (
        arr_full[keep_mask],
        arr_condensed[keep_mask],
        arr_inputs[keep_mask],
        removed_idx
    )



# =================== 040525
def prune_repeated_and_zero_rows_all(
    arr_full: np.ndarray,         # (n, m, t, d)
    arr_condensed: np.ndarray,    # (n, m, d)
    arr_inputs: np.ndarray,       # (n, d)
    *,
    atol: float = 1e-6,
    require_all_m: bool = True
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[int]]:
    """
    1) Drop any rows where the t embeddings repeat (within `atol`),
    2) ALSO drop any rows where *any* of the m condensed embeddings is a zero-vector,
    3) ALSO drop any rows where the mean over t (i.e. arr_full.mean(axis=2)) is zero-vector.
    
    Prints counts of zero‐rows before and after pruning.
    """
    # --- detect zero‐embeddings in arr_condensed -------------------------
    is_zero_cond = np.all(np.isclose(arr_condensed, 0.0, atol=atol), axis=2)  # (n, m)
    num_zero_cond_embeddings = int(is_zero_cond.sum())
    num_zero_cond_rows       = int(np.any(is_zero_cond, axis=1).sum())
    print(f"[prune] Found {num_zero_cond_embeddings} zero embeddings across {num_zero_cond_rows} rows (condensed)")

    # --- detect zero‐embeddings in arr_full.mean(axis=2) -----------------
    mean_full = arr_full.mean(axis=2)  # shape (n, m, d)
    is_zero_mean = np.all(np.isclose(mean_full, 0.0, atol=atol), axis=2)  # (n, m)
    num_zero_mean_embeddings = int(is_zero_mean.sum())
    num_zero_mean_rows       = int(np.any(is_zero_mean, axis=1).sum())
    print(f"[prune] Found {num_zero_mean_embeddings} zero embeddings across {num_zero_mean_rows} rows (full‐mean)")

    # --- find repeated rows ---------------------------------------------
    identical = np.all(
        np.isclose(arr_full, arr_full[:, :, :1, :], atol=atol),
        axis=(2, 3)
    )  # shape (n, m)
    if require_all_m:
        repeated = np.all(identical, axis=1)
    else:
        repeated = np.any(identical, axis=1)

    # --- zero‐rows mask -------------------------------------------------
    # any zero in condensed OR any zero in full‐mean for a given row
    zero_row = np.any(is_zero_cond | is_zero_mean, axis=1)  # shape (n,)

    # --- combine into drop‐mask ----------------------------------------
    rows_to_drop = repeated | zero_row
    keep_mask    = ~rows_to_drop
    removed_idx  = np.flatnonzero(rows_to_drop).tolist()

    # --- apply mask ----------------------------------------------------
    pruned_full      = arr_full[keep_mask]
    pruned_condensed = arr_condensed[keep_mask]
    pruned_inputs    = arr_inputs[keep_mask]

    # --- verify no zero‐rows remain ------------------------------------
    rem_mean_full    = pruned_full.mean(axis=2)
    rem_zero_mean    = np.all(np.isclose(rem_mean_full, 0.0, atol=atol), axis=2)
    rem_zero_mean_cnt = int(np.any(rem_zero_mean, axis=1).sum())
    print(f"[prune] Remaining rows with zero full‐mean embeddings: {rem_zero_mean_cnt}")

    return pruned_full, pruned_condensed, pruned_inputs, removed_idx
# =================== 040525

def compute_embedding_base_scores(inputs_emb_s, concepts_emb_s, concepts_retrieved_emb_s, embedding_to_use_for_normalization=None, pca_comp_to_use=5):
    ## tmp 
    ## tmp 
    # breakpoint()
    do_prune_repeated_rows = True
    if do_prune_repeated_rows:
        pruned_3d, pruned_2d, pruned_inputs, dropped = prune_repeated_and_zero_rows_all(
            concepts_retrieved_emb_s,   # (540, 3, 20, 1024)
            concepts_emb_s,             # (540, 3, 1024)
            inputs_emb_s                # (540, 1024)
        )
        # print(pruned_3d.shape)   # → (530, 3, 20, 1024)
        # print(pruned_2d.shape)   # → (530, 3, 1024)
        # print(pruned_inputs.shape)  # -> (530, 1024)
        logging.warning(f"removed {len(dropped)} rows from the original {inputs_emb_s.shape[0]} rows")


        inputs_emb_s = pruned_inputs
        concepts_emb_s = pruned_2d
        concepts_retrieved_emb_s = pruned_3d

    ## -----
    do_recalculate_concepts_as_mean_of_retrieved = False
    if do_recalculate_concepts_as_mean_of_retrieved:
        logging.warning(f"recalculating the concepts as the mean of the retrieved embeddings")
        # recalculate the concepts as the mean of the retrieved embeddings
        concepts_emb_s = concepts_retrieved_emb_s.mean(axis=-2)
        # is_zero = np.all(concepts_emb_s == 0, axis=2)
        concepts_emb_norm_s = np.linalg.norm(concepts_emb_s, axis=-1, keepdims=True) # (inputs, concepts)
        zero_norm = (concepts_emb_norm_s == 0)
        concepts_emb_norm_s[zero_norm] = 1     
        concepts_emb_s = concepts_emb_s /  concepts_emb_norm_s # (inputs, concepts, emb_dim)
    
    ## tmp 
    ## tmp 
    if embedding_to_use_for_normalization is None:
        relevance_scores = compute_embedding_based_relevance_score_per_concept(inputs_emb_s, concepts_emb_s)
    else:
        relevance_scores = compute_normalized_embedding_based_relevance_score_per_concept(inputs_emb_s, concepts_emb_s, embedding_to_use_for_normalization)

    consistency_scores = compute_embedding_based_consistency_score_per_concept(concepts_emb_s, concepts_retrieved_emb_s)

    
    do_use_leftover = False
    if do_use_leftover:
        concepts_emb_s_repeated = np.tile(concepts_emb_s[:, :, np.newaxis, :], (1, 1, concepts_retrieved_emb_s.shape[2], 1))
        left_over_concepts_retrieved_emb_s = cal_remove_leftover_embeddings(base_emb=concepts_retrieved_emb_s, emb_to_remove=concepts_emb_s_repeated)
        do_norm_emb = False
        if do_norm_emb:
            left_over_concepts_retrieved_emb_s_norm = np.linalg.norm(left_over_concepts_retrieved_emb_s, axis=-1, keepdims=True) # (samples, embedding_dim)
            left_over_concepts_retrieved_emb_s = left_over_concepts_retrieved_emb_s / left_over_concepts_retrieved_emb_s_norm # (samples, embedding_dim)
        concepts_retrieved_emb_s = left_over_concepts_retrieved_emb_s 

    do_new_diversity_loss_from_paper = False
    new_diversity_loss_from_paper_mod = 'average' # 'average' or 'min'
    if not do_new_diversity_loss_from_paper:
        inner_diversity_scores = compute_embedding_based_inner_diversity_score_per_concept(concepts_emb_s, concepts_retrieved_emb_s, pca_comp_to_use=pca_comp_to_use)
    else:
        # New inner diversity score # ILAD and ILMD (short for Intra-List Average Distance and Intra-List Minimal Distance)
        # ----
        inner_diversity_scores = inner_diversity(concepts_retrieved_emb_s,mode=new_diversity_loss_from_paper_mod) # new # ILAD (mode='average') or ILMD (mode='min').
    

    diversity_scores = compute_embedding_based_diversity_score(concepts_emb_s)
    
    return {'relevance_scores': relevance_scores, 
            'consistency_scores': consistency_scores, 
            'inner_diversity_scores': inner_diversity_scores, 
            'diversity_scores': diversity_scores}




# New
# ====================================================================================================
# ====================================================================================================
# Result Diversification in Search and Recommendation A Survey ILAD and ILMD (short for Intra-List Average Distance and Intra-List Minimal Distance
import numpy as np
from typing import Union

# ------------------------------------------------------------------
# 1.  Cosine distance helpers (unchanged)
# ------------------------------------------------------------------
def _cosine_distance_matrix(mat: np.ndarray) -> np.ndarray:
    sim = mat @ mat.T
    return 0.5 * (1.0 - np.clip(sim, -1.0, 1.0))

# ------------------------------------------------------------------
# 2.  Inner-list diversity, now batched
# ------------------------------------------------------------------
def inner_diversity(
    embeddings: np.ndarray,
    mode: str = "average"
) -> Union[float, np.ndarray]:
    """
    ILAD (mode='average') or ILMD (mode='min').

    - If embeddings.ndim == 2 (n, m), returns a float.
    - If embeddings.ndim == 4 (t, k, n, m), returns an array of shape (t, k).
    """
    # Batch‐case: (t, k, n, m) → compute each inner_diversity( (n,m) )
    if embeddings.ndim == 4:
        t, k, n, m = embeddings.shape
        out = np.empty((t, k), dtype=float)
        for ti in range(t):
            for ki in range(k):
                # slice out one (n,m) block
                out[ti, ki] = inner_diversity(embeddings[ti, ki], mode)
        return out

    # Scalar‐case: (n, m)
    if embeddings.ndim != 2:
        raise ValueError(
            f"Expected 2D or 4D array, got embeddings.ndim = {embeddings.ndim}"
        )
    if embeddings.shape[0] < 2:
        return 0.0

    dmat = _cosine_distance_matrix(embeddings)
    triu = dmat[np.triu_indices_from(dmat, k=1)]
    return triu.mean() if mode == "average" else triu.min()


# # ------------------------------------------------------------------
# # 4.  Example usage
# # ------------------------------------------------------------------
# if __name__ == "__main__":
# single list → float
    # arr = np.random.randn(10, 512)
    # arr /= np.linalg.norm(arr, axis=1, keepdims=True)
    # print(inner_diversity(arr, mode="average"))  # e.g. 0.37

    # # batched input → (t, k) array
    # t, k, n, m = 5, 3, 10, 512
    # batch = np.random.randn(t, k, n, m)
    # batch /= np.linalg.norm(batch, axis=-1, keepdims=True)
    # scores = inner_diversity(batch)              # shape (5, 3)
    # print(scores)
# ====================================================================================================
# ====================================================================================================
# Example usage:
if __name__ == "__main__":

    # Example usage of compute_consistency_score_per_concept

    np.random.seed(42)
    # Create a sample (10, 80) binary matrix with each row having 6 ones.
    sample_matrix = np.zeros((10, 80), dtype=int)
    for i in range(10):
        ones_indices = np.random.choice(80, 6, replace=False)
        sample_matrix[i, ones_indices] = 1
    
    # compute relevance score
    c = 3
    n = 10
    d = 80
    gt_bin = np.zeros(d, dtype=int)
    gt_bin[10:20] = 1
    concept_neighbors_gt_labels_bin_s = np.zeros((c, n, d), dtype=int)
    for i in range(c):
        for j in range(n):
            ones_indices = np.random.choice(d, 6, replace=False)
            concept_neighbors_gt_labels_bin_s[i, j, ones_indices] = 1
    relevance_score = compute_relevance_score_per_concept(concept_neighbors_gt_labels_bin_s, gt_bin)
    print(f"Relevance score: {relevance_score}")
    relevance_score = compute_bin_relevance_score_per_concept(concept_neighbors_gt_labels_bin_s, gt_bin)
    print(f"Relevance score: {relevance_score}")
    
    
    
    # Compute consistency score for each concept using different methods
    for m in compute_consistency_score_options:
        score = compute_consistency_score_per_concept(sample_matrix, m)
        print(f"{m.capitalize()} score: {score}")
    
    
    # Example usage of distinctiveness_score_per_concept

    # Create a dummy dataset:
    # Let's say we have 3 concepts, 5 samples per concept, and each sample is a binary vector of length 80.
    np.random.seed(0)
    c, n, t = 3, 5, 80
    # Create sparse binary data (each sample has at most 6 ones)
    data = np.zeros((c, n, t), dtype=int)
    for i in range(c):
        for j in range(n):
            ones_idx = np.random.choice(t, size=6, replace=False)
            data[i, j, ones_idx] = 1

    per_concept = distinctiveness_score_per_concept(data)
    print("Per-Concept Scores:", per_concept)
