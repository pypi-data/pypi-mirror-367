from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot_histogram(hist_s, input_bin=None, path=None, title=None):
    """
    Plots a histogram for a specific row of inner products.

    Parameters:
    hist_s (numpy.ndarray): A 1D array contains the histogram of inner products for a specific vector.
    input_bin (numpy.ndarray, optional): The location of the input in each row will plot a vertical line. If None, no vertical lines will be plotted.
    path (str, optional): If provided, the plot will be saved to this path. If None, the plot will be displayed.
    title (str, optional): The title of the histogram plot. If None, a default title will be used.

    Returns:
    None
    """
    plt.figure(figsize=(10, 6))
    plt.clf()
    plt.title(f"{title}")
    plt.xlabel("Bins")
    plt.ylabel("Frequency")
    plt.plot(hist_s, label=f"{title}")

    # plot vertical line for input_bin if provided
    if input_bin is not None:
        plt.axvline(x=input_bin, color="r", linestyle="--", label="Input Bin")
    plt.legend()

    if path is not None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        plt.savefig(path / f"{title}.png")
        print(f"{title} histogram saved to {path/f'{title}.png'}")
    else:
        plt.show()


def plot_histograms_matrix(hist_s, input_bin=None, path=None, num_hist_to_plot=10):
    """
    Plots the histogram of inner products from a matrix.

    Parameters:
    hist_s (numpy.ndarray): A 2D array where each row contains the histogram of inner products for a specific vector.
    input_bin (numpy.ndarray, optional): The location of the input in each row will plot a vertical line. If None, no vertical lines will be plotted.
    path (str, optional): If provided, the plot will be saved to this path. If None, the plot will be displayed.

    Returns:
    None
    """
    plt.figure(figsize=(10, 6))

    # Plotting the histogram of inner products
    plt.clf()
    plt.title("Histogram of Inner Products")
    plt.xlabel("Bins")
    plt.ylabel("Rows")
    if path is not None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        plt.imshow(hist_s, aspect="auto", cmap="hot", interpolation="nearest")
        plt.colorbar()
        plt.savefig(path / "histogram.png")
        print(f"Histogram saved to {path/"histogram.png"}")
    else:
        plt.imshow(hist_s, aspect="auto", cmap="hot", interpolation="nearest")
        plt.colorbar()
        plt.show()

    # plot 10 random rows
    max_size = min(num_hist_to_plot, hist_s.shape[0])  # Ensure we don't exceed the number of rows
    selected_inds = np.random.choice(hist_s.shape[0], size=max_size, replace=False)
    selected_inds.sort()  # Sort the indices for better visualization
    for index, i in enumerate(selected_inds):
        plot_histogram(
            hist_s[i], input_bin=input_bin[i], path=path, title=f"place_{index}_Row_{i}_Histogram"
        )


def plot_row_inds_distribution(inds, path):
    """
    Plots the distribution of indices.

    Parameters:
    inds (numpy.ndarray): A 1D array containing the indices to be plotted.
    path (str): The path where the plot will be saved.

    Returns:
    None
    """
    plt.figure(figsize=(10, 6))
    plt.clf()
    plt.title("Distribution of Indices")
    plt.xlabel("Indices")
    plt.ylabel("Frequency")

    # Plotting the histogram of indices
    plt.hist(inds, bins=50, color="blue", alpha=0.7)

    # Save the plot if a path is provided
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    plt.savefig(path / "indices_distribution.png")
    print(f"Indices distribution saved to {path}")
    plt.close()
