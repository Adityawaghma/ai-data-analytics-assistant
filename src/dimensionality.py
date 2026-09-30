"""
src/dimensionality.py — P1 (Jul 30): PCA dimensionality reduction.

How to work:
    df_pca, explained_var = apply_pca(df, ["f1", "f2", "f3", "f4"], n=2)
    # Good PCA: first 2 components explain > 80% of variance.
"""

import pandas as pd
from sklearn.decomposition import PCA


def apply_pca(df: pd.DataFrame, cols: list, n: int = 2):
    """
    Reduce the given columns of df to n principal components.

    Args:
        df: source DataFrame.
        cols: list of numeric column names to reduce.
        n: number of principal components to keep.

    Returns:
        (df_pca, explained_variance_ratio)
        df_pca: DataFrame with columns PC1..PCn, same row order as df.
        explained_variance_ratio: np.ndarray of length n, the fraction
            of total variance captured by each component (sums to
            <= 1.0 across all n; the closer to 1.0 the better).
    """
    if df.empty:
        raise ValueError("Cannot apply PCA: DataFrame is empty")
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"Column(s) not found in DataFrame: {missing}")
    if n > len(cols):
        raise ValueError(
            f"n_components ({n}) cannot exceed number of input columns ({len(cols)})"
        )

    pca = PCA(n_components=n)
    components = pca.fit_transform(df[cols])

    df_pca = pd.DataFrame(
        components,
        columns=[f"PC{i + 1}" for i in range(n)],
        index=df.index,
    )

    total_variance = pca.explained_variance_ratio_.sum()
    print(f"Variance explained by {n} component(s): {total_variance:.1%}")

    return df_pca, pca.explained_variance_ratio_


def store_pca_components(conn, df_pca: pd.DataFrame, table: str = "pca_components") -> None:
    """
    Persist PCA components to a DB table (P2 integration), keeping the
    original DataFrame's index so rows can be joined back later.
    """
    df_pca.to_sql(table, conn, if_exists="replace", index=True, index_label="row_id")


if __name__ == "__main__":
    # Quick manual test — matches the board's "How to Work" example
    import numpy as np

    rng = np.random.default_rng(2)
    n_rows = 100

    # Two genuinely informative, correlated features + two noise features,
    # so the first 2 PCs should capture most of the real variance.
    base = rng.normal(0, 1, n_rows)
    df = pd.DataFrame({
        "f1": base + rng.normal(0, 0.1, n_rows),
        "f2": base * 2 + rng.normal(0, 0.1, n_rows),
        "f3": rng.normal(0, 0.05, n_rows),
        "f4": rng.normal(0, 0.05, n_rows),
    })

    df_pca, explained_var = apply_pca(df, ["f1", "f2", "f3", "f4"], n=2)

    print("df_pca columns:", list(df_pca.columns))
    print("Explained variance ratio:", explained_var)
    print(f"Total (first 2 PCs): {explained_var.sum():.1%}")

    assert list(df_pca.columns) == ["PC1", "PC2"]
    assert len(df_pca) == len(df)
    assert explained_var.sum() <= 1.0
    # This synthetic data is built so the first 2 PCs dominate.
    assert explained_var.sum() > 0.7, "Expected first 2 PCs to explain most of the variance"

    print("\nPCA check: PASSED")
