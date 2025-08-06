import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import LabelEncoder, StandardScaler, normalize


def compute_pca(X, n_components=10, normalize_flag=False):
    """
    Computes the PCA (via Truncated SVD) and returns necessary components for plotting.

    Parameters:
        X (array-like or CSR matrix): Input data.
        n_components (int): Number of SVD components to compute.
        normalize_flag (bool): If True, apply L2 normalization; otherwise apply standard scaling.

    Returns:
        dict: Dictionary containing:
            - "X_scaled": The scaled data.
            - "svd": The fitted TruncatedSVD object.
            - "X_reduced": The reduced data from SVD.
            - "explained_variance": The explained variance ratio.
    """
    # Scale the data (works for both sparse and dense arrays)
    if sparse.issparse(X):
        if normalize_flag:
            X_scaled = normalize(X, norm="l2", axis=1)
        else:
            X_dense = X.toarray()
            X_scaled = StandardScaler().fit_transform(X_dense)
    else:
        if normalize_flag:
            X_scaled = normalize(X, norm="l2", axis=1)
        else:
            X_scaled = StandardScaler().fit_transform(X)

    # Perform Truncated SVD
    svd = TruncatedSVD(n_components=n_components)
    X_reduced = svd.fit_transform(X_scaled)

    return {
        "svd": svd,
        "X_reduced": X_reduced,
        "explained_variance": svd.explained_variance_ratio_,
    }


def plot_pca(pca_result, y, title="PCA Projection"):
    """
    Plots a 2D scatter plot of the first two PCA components using precomputed PCA results.

    Parameters:
        pca_result (dict): Dictionary from compute_pca() containing 'X_reduced' and 'explained_variance'.
        y (array-like): Class labels.
        title (str): Plot title.
    """
    # Encode labels for coloring
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    # Create DataFrame for plotting using the first two components
    df = pd.DataFrame(
        pca_result["X_reduced"],
        columns=[f"Component {i + 1}" for i in range(pca_result["X_reduced"].shape[1])],
    )
    df["Class"] = label_encoder.inverse_transform(y_encoded)

    # Retrieve explained variance info for the first two components
    explained_variance = pca_result["explained_variance"]
    component_1_var = explained_variance[0] * 100
    component_2_var = explained_variance[1] * 100

    plt.figure(figsize=(8, 6))
    scatter = sns.scatterplot(
        data=df,
        x="Component 1",
        y="Component 2",
        hue="Class",
        palette="Spectral",
        s=60,
        edgecolor="k",
        legend="full",
    )
    scatter.legend(loc="upper right", ncol=2, title="Class", bbox_to_anchor=(1.5, 1))
    plt.title(title)
    plt.xlabel(f"Component 1 ({component_1_var:.2f}% Variance)")
    plt.ylabel(f"Component 2 ({component_2_var:.2f}% Variance)")
    plt.grid(True)
    plt.show()


def plot_explained_variation(pca_result, title="Explained Variance"):
    """
    Plots both the explained variance per component as a bar plot and the cumulative explained variance
    using precomputed PCA results.

    Parameters:
        pca_result (dict): Dictionary from compute_pca() containing 'explained_variance'.
        title (str): Base title for the plots.
    """
    explained_variance = pca_result["explained_variance"]
    components = np.arange(1, len(explained_variance) + 1)
    cumulative_variance = np.cumsum(explained_variance) * 100

    plt.figure(figsize=(12, 5))

    # Bar plot for individual explained variance
    plt.subplot(1, 2, 1)
    plt.bar(components, explained_variance * 100)
    plt.xlabel("Component")
    plt.ylabel("Explained Variance (%)")
    plt.title(title + " per Component")
    plt.grid(True)

    # Line plot (with markers) for cumulative explained variance
    plt.subplot(1, 2, 2)
    plt.plot(components, cumulative_variance, marker="o", linestyle="-")
    plt.xlabel("Number of Components")
    plt.ylabel("Cumulative Explained Variance (%)")
    plt.title(title + " (Cumulative)")
    plt.grid(True)

    # Line plot (with markers) for cumulative explained variance
    plt.subplot(1, 2, 2)
    plt.plot(components, cumulative_variance, marker="o", linestyle="-")
    plt.xlabel("Number of Components")
    plt.ylabel("Cumulative Explained Variance (%)")

    # Add the total cumulative variance to the subplot title
    total_cum_var = cumulative_variance[-1]
    plt.title(f"{title} (Cumulative) - Total: {total_cum_var:.2f}%")
    plt.grid(True)

    plt.tight_layout()
    plt.show()
