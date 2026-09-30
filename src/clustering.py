"""
src/clustering.py — P1 (Jul 27): K-Means clustering.

How to work:
    labels, centers, inertia = train_kmeans(X, k=3)
    ax = plot_clusters(X, labels)
"""

import numpy as np
from sklearn.cluster import KMeans
import matplotlib
matplotlib.use("Agg")  # safe for headless/testing; embed via FigureCanvasQTAgg in PyQt5
import matplotlib.pyplot as plt


def train_kmeans(X, k: int = 3, random_state: int = 42):
    """
    Fit K-Means on X.

    Args:
        X: array-like, shape (n_samples, n_features).
        k: number of clusters.
        random_state: for reproducibility.

    Returns:
        (labels, cluster_centers, inertia)
        labels: np.ndarray of shape (n_samples,), cluster id per row (0..k-1)
        cluster_centers: np.ndarray of shape (k, n_features)
        inertia: float, sum of squared distances to nearest centroid
    """
    X = np.asarray(X)
    model = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    model.fit(X)
    return model.labels_, model.cluster_centers_, model.inertia_


def plot_clusters(X, labels, ax=None, save_path: str = None):
    """
    Scatter-plot the first two dimensions of X, colored by cluster label.

    Args:
        X: array-like, shape (n_samples, n_features>=2). Only the first
            two columns are plotted.
        labels: cluster labels from train_kmeans().
        ax: existing matplotlib Axes to draw on; a new Figure/Axes is
            created if not given (so this also works embedded in a
            PyQt5 FigureCanvasQTAgg by passing that canvas's ax).
        save_path: if given, saves the figure to this path.

    Returns:
        The matplotlib Axes used.
    """
    X = np.asarray(X)
    if X.shape[1] < 2:
        raise ValueError("plot_clusters needs at least 2 feature columns")

    owns_fig = ax is None
    if owns_fig:
        fig, ax = plt.subplots()

    ax.clear()
    scatter = ax.scatter(X[:, 0], X[:, 1], c=labels, cmap="tab10")
    ax.set_title("K-Means Clusters")
    ax.set_xlabel("Feature 1")
    ax.set_ylabel("Feature 2")

    if owns_fig and save_path:
        fig.tight_layout()
        fig.savefig(save_path)

    return ax


def log_cluster_run(conn, table: str, k: int, inertia: float) -> None:
    """
    Log a clustering run to model_runs (reuses the table shared with
    timeseries_prep.py's ARIMA logging), so past runs are auditable.
    """
    import datetime

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS model_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_type TEXT,
            source_table TEXT,
            p INTEGER,
            d INTEGER,
            q INTEGER,
            k INTEGER,
            inertia REAL,
            created_at TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO model_runs (model_type, source_table, k, inertia, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("KMeans", table, k, inertia,
         datetime.datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()


if __name__ == "__main__":
    # Quick manual test — matches the board's "How to Work" example
    rng = np.random.default_rng(0)
    blob1 = rng.normal(loc=[0, 0], scale=0.5, size=(30, 2))
    blob2 = rng.normal(loc=[5, 5], scale=0.5, size=(30, 2))
    blob3 = rng.normal(loc=[0, 5], scale=0.5, size=(30, 2))
    X_2d = np.vstack([blob1, blob2, blob3])

    labels, centers, inertia = train_kmeans(X_2d, k=3)
    print("Unique labels:", set(labels))
    assert len(set(labels)) == 3, "Expected 3 distinct clusters"
    print("Cluster centers:\n", centers)
    print("Inertia:", inertia)

    plot_clusters(X_2d, labels, save_path="test_clusters.png")
    print("Saved test_clusters.png")
    print("\nK-Means check: PASSED")
