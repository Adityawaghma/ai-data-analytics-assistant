"""
src/elbow.py — P1 (Jul 28): Elbow method for choosing K in K-Means.

How to work:
    ks, inertias = elbow_method(X, max_k=10)
    best_k = find_elbow(ks, inertias)
    plot_elbow(ks, inertias, save_path="elbow.png")
"""

from sklearn.cluster import KMeans
import matplotlib
matplotlib.use("Agg")  # safe for headless/testing; embed via FigureCanvasQTAgg in PyQt5
import matplotlib.pyplot as plt


def elbow_method(X, max_k: int = 10, random_state: int = 42):
    """
    Fit K-Means for k = 2..max_k and collect inertia at each k.

    Args:
        X: array-like, shape (n_samples, n_features).
        max_k: largest k to try (inclusive).
        random_state: for reproducibility.

    Returns:
        (ks, inertias) — two lists of equal length, len(ks) == max_k - 1.
        ks: [2, 3, ..., max_k]
        inertias: KMeans inertia_ for each corresponding k.
    """
    if max_k < 3:
        raise ValueError("max_k must be >= 3 to have a meaningful elbow curve")

    ks = list(range(2, max_k + 1))
    inertias = [
        KMeans(n_clusters=k, n_init=10, random_state=random_state).fit(X).inertia_
        for k in ks
    ]
    return ks, inertias


def find_elbow(ks, inertias) -> int:
    """
    Heuristically pick the "elbow" k: the point where the drop in inertia
    from the previous k is largest (i.e. where the curve bends hardest).

    Args:
        ks: list of k values, as returned by elbow_method().
        inertias: matching list of inertia values.

    Returns:
        The k value at the elbow.
    """
    if len(ks) < 2:
        raise ValueError("Need at least 2 points to find an elbow")

    diffs = [inertias[i - 1] - inertias[i] for i in range(1, len(inertias))]
    # diffs[i] is the drop going from ks[i] -> ks[i+1]; the elbow is the
    # k *after* the steepest drop.
    return ks[diffs.index(max(diffs)) + 1]


def plot_elbow(ks, inertias, save_path: str = None, ax=None):
    """
    Plot the elbow curve (k vs inertia), with the chosen elbow marked.

    Returns:
        The matplotlib Axes used.
    """
    owns_fig = ax is None
    if owns_fig:
        fig, ax = plt.subplots()

    ax.clear()
    ax.plot(ks, inertias, "bo-")
    best_k = find_elbow(ks, inertias)
    ax.axvline(best_k, color="red", linestyle="--", label=f"Elbow at k={best_k}")
    ax.set_xlabel("k (number of clusters)")
    ax.set_ylabel("Inertia")
    ax.set_title("Elbow Method")
    ax.legend()

    if owns_fig and save_path:
        fig.tight_layout()
        fig.savefig(save_path)

    return ax


def log_elbow_run(conn, table: str, chosen_k: int) -> None:
    """Log the chosen k for a clustering run to model_runs (P2 integration)."""
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
        "INSERT INTO model_runs (model_type, source_table, k, created_at) "
        "VALUES (?, ?, ?, ?)",
        ("KMeans-Elbow", table, chosen_k,
         datetime.datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()


if __name__ == "__main__":
    # Quick manual test — matches the board's "How to Work" example
    import numpy as np

    rng = np.random.default_rng(0)
    blob1 = rng.normal(loc=[0, 0], scale=0.5, size=(30, 2))
    blob2 = rng.normal(loc=[5, 5], scale=0.5, size=(30, 2))
    blob3 = rng.normal(loc=[0, 5], scale=0.5, size=(30, 2))
    X_2d = np.vstack([blob1, blob2, blob3])

    ks, inertias = elbow_method(X_2d, max_k=8)
    print("k values:   ", ks)
    print("inertias:   ", [round(i, 2) for i in inertias])

    assert len(ks) == len(inertias) == 7, "Expected 7 points for max_k=8"

    best_k = find_elbow(ks, inertias)
    print(f"Chosen elbow k: {best_k}")
    # This synthetic data has 3 real clusters, so the elbow should land
    # near k=3 (not guaranteed exactly, since it's a noisy heuristic).
    print(f"Elbow near true cluster count (3): {'yes' if abs(best_k - 3) <= 1 else 'no'}")

    plot_elbow(ks, inertias, save_path="test_elbow.png")
    print("Saved test_elbow.png")
    print("\nElbow method check: PASSED")
