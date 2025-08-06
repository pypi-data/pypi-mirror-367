import matplotlib.pyplot as plt
import seaborn as sns
from scipy import sparse
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler, normalize


class kmeans_group:
    """
    This class performs k-means clustering on the genotype matrix after reducing its dimensionality using truncated SVD.

    Attributes:
        n_components (int): Number of components for Truncated SVD.
        start_k (int): Starting number of clusters for k-means.
        end_k (int): Ending number of clusters for k-means.
        random_state (int): Random state for reproducibility.
        normalize_data (bool): Flag to determine if data normalization is used.
        norm_type (str): Type of normalization ('l1', 'l2', or 'max').
        svd (TruncatedSVD): Instance of truncated SVD.
        k_values (range): Range of cluster numbers to evaluate.
        sse (list): Sum of squared errors for each K.
        silhouette_scores (list): Silhouette scores for each K.
    """

    def __init__(
        self, n_components=2, start_k=2, end_k=10, random_state=42, normalize_flag=False
    ):
        """
        Initializes the kmeans_group class with the given parameters.

        Parameters:
            n_components (int): Number of components for Truncated SVD.
            start_k (int): Starting number of clusters for K-means.
            end_k (int): Ending number of clusters for K-means.
            random_state (int): Random state for reproducibility.
            normalize_data (bool): Whether to normalize the data.
            norm_type (str): Type of normalization to apply ('l1', 'l2', or 'max').
        """
        self.n_components = n_components
        self.start_k = start_k
        self.end_k = end_k
        self.random_state = random_state
        self.normalize_flag = normalize_flag
        self.svd = TruncatedSVD(
            n_components=self.n_components, random_state=self.random_state
        )
        self.k_values = range(self.start_k, self.end_k + 1)
        self.sse = []
        self.silhouette_scores = []

    def fit_transform(self, X):
        """
        Applies normalization (if enabled) and truncated SVD to the genotype matrix and returns the transformed data.

        Parameters:
            X (array-like or CSR matrix): Genotype matrix.

        Returns:
            X_svd (array-like): Principal components from the truncated SVD.
        """
        # Check if X is a sparse CSR matrix
        if sparse.issparse(X):
            if self.normalize_flag:
                # Apply L2 normalization directly on the sparse matrix
                X_transformed = normalize(X, norm="l2", axis=1)
            else:
                # Convert sparse matrix to dense and apply standard scaling
                X_dense = X.toarray()
                X_transformed = StandardScaler().fit_transform(X_dense)
        else:
            # X is a dense array
            if self.normalize_flag:
                X_transformed = normalize(X, norm="l2", axis=1)
            else:
                X_transformed = StandardScaler().fit_transform(X)

        # Apply Truncated SVD
        X_svd = self.svd.fit_transform(X_transformed)
        return X_svd

    def evaluate_clusters(self, X_svd):
        """
        Evaluates k-means clustering for different values of k using SSE and silhouette scores.

        Parameters:
            X_svd (array-like): Principal components from the truncated SVD.
        """
        self.sse = []  # Reset SSE list
        self.silhouette_scores = []  # Reset silhouette scores list
        for k in self.k_values:
            kmeans = KMeans(n_clusters=k, random_state=self.random_state)
            kmeans.fit(X_svd)
            self.sse.append(kmeans.inertia_)
            score = silhouette_score(X_svd, kmeans.labels_)
            self.silhouette_scores.append(score)

    def plot_elbow_method(self):
        """
        Plots the SSE (Sum of Squared Errors) for different values of k
        using the Elbow Method.
        """
        plt.figure(figsize=(6, 5))
        sns.set(style="whitegrid")
        sns.lineplot(x=list(self.k_values), y=self.sse, marker="o")
        plt.xlabel("Number of Clusters")
        plt.ylabel("SSE")
        plt.title("SSE for each k")
        plt.grid(True)
        plt.show()

    def plot_silhouette_scores(self):
        """
        Plots the Silhouette Scores for different values of k.
        """
        plt.figure(figsize=(6, 5))
        sns.set(style="whitegrid")
        sns.lineplot(x=list(self.k_values), y=self.silhouette_scores, marker="o")
        plt.xlabel("Number of Clusters")
        plt.ylabel("Silhouette score")
        plt.title("Silhouette score for each k")
        plt.grid(True)
        plt.show()

    def cluster(self, X_svd, n_clusters):
        """
        Performs k-means clustering on the principal components with the specified number of clusters.

        Parameters:
            X_svd (array-like): Principal components from the truncated SVD.
            n_clusters (int): The number of clusters to form.

        Returns:
            y_kmeans (array-like): Cluster labels for each point in the dataset.
            centers (array-like): Coordinates of cluster centers.
        """
        kmeans = KMeans(n_clusters=n_clusters, random_state=self.random_state)
        y_kmeans = kmeans.fit_predict(X_svd)
        return y_kmeans, kmeans.cluster_centers_

    def plot_clusters(self, X_svd, y_kmeans, centers):
        """
        Plots the k-means clustering results including the data points and cluster centers.

        Parameters:
            X_svd (array-like): Principal components from the truncated SVD.
            y_kmeans (array-like): Cluster labels for each point in the dataset.
            centers (array-like): Coordinates of cluster centers.
        """
        plt.figure(figsize=(10, 6))
        sns.scatterplot(
            x=X_svd[:, 0],
            y=X_svd[:, 1],
            hue=y_kmeans,
            palette="Spectral",
            s=50,
            alpha=0.7,
            legend=None,
        )
        sns.scatterplot(
            x=centers[:, 0], y=centers[:, 1], color="red", s=200, marker="X"
        )
        plt.xlabel("Component 1")
        plt.ylabel("Component 2")
        plt.title(f"K-means clustering with {len(centers)} clusters")
        plt.show()
