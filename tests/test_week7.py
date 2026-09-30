"""
tests/test_week7.py — covers the Week 7 modules: clustering.py, elbow.py,
anomaly.py, dimensionality.py.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import pytest

from src.clustering import train_kmeans
from src.elbow import elbow_method, find_elbow
from src.anomaly import detect_anomalies
from src.dimensionality import apply_pca


# ---------------------------------------------------------------------
# clustering.py
# ---------------------------------------------------------------------

def _three_blobs():
    rng = np.random.default_rng(0)
    b1 = rng.normal(loc=[0, 0], scale=0.5, size=(30, 2))
    b2 = rng.normal(loc=[5, 5], scale=0.5, size=(30, 2))
    b3 = rng.normal(loc=[0, 5], scale=0.5, size=(30, 2))
    return np.vstack([b1, b2, b3])


def test_train_kmeans_finds_three_clusters():
    X = _three_blobs()
    labels, centers, inertia = train_kmeans(X, k=3)
    assert len(set(labels)) == 3
    assert centers.shape == (3, 2)
    assert inertia >= 0


# ---------------------------------------------------------------------
# elbow.py
# ---------------------------------------------------------------------

def test_elbow_method_returns_matching_length_lists():
    X = _three_blobs()
    ks, inertias = elbow_method(X, max_k=8)
    assert len(ks) == len(inertias) == 7
    assert ks == list(range(2, 9))


def test_elbow_method_rejects_small_max_k():
    X = _three_blobs()
    with pytest.raises(ValueError):
        elbow_method(X, max_k=2)


def test_find_elbow_returns_a_k_in_range():
    ks = [2, 3, 4, 5]
    inertias = [100, 40, 35, 33]  # steep drop 2->3, then flattens
    best_k = find_elbow(ks, inertias)
    assert best_k in ks
    assert best_k == 3  # steepest single-step drop is 2->3


# ---------------------------------------------------------------------
# anomaly.py
# ---------------------------------------------------------------------

def test_detect_anomalies_flags_injected_outliers():
    rng = np.random.default_rng(1)
    n = 200
    sales = rng.normal(1000, 100, n)
    price = rng.normal(50, 5, n)
    sales[:5] = [5000, 5200, 4800, 5100, 4900]
    price[:5] = [500, 480, 520, 510, 490]
    df = pd.DataFrame({"sales": sales, "price": price})

    result = detect_anomalies(df, ["sales", "price"], contamination=0.05)

    assert "is_anomaly" in result.columns
    assert "anomaly_score" in result.columns
    assert result["is_anomaly"].iloc[:5].sum() >= 3


def test_detect_anomalies_rejects_missing_column():
    df = pd.DataFrame({"a": [1, 2, 3]})
    with pytest.raises(KeyError):
        detect_anomalies(df, ["a", "does_not_exist"])


def test_detect_anomalies_rejects_empty_dataframe():
    df = pd.DataFrame({"a": []})
    with pytest.raises(ValueError):
        detect_anomalies(df, ["a"])


# ---------------------------------------------------------------------
# dimensionality.py
# ---------------------------------------------------------------------

def test_apply_pca_shapes_and_variance():
    rng = np.random.default_rng(2)
    n_rows = 100
    base = rng.normal(0, 1, n_rows)
    df = pd.DataFrame({
        "f1": base + rng.normal(0, 0.1, n_rows),
        "f2": base * 2 + rng.normal(0, 0.1, n_rows),
        "f3": rng.normal(0, 0.05, n_rows),
        "f4": rng.normal(0, 0.05, n_rows),
    })

    df_pca, explained_var = apply_pca(df, ["f1", "f2", "f3", "f4"], n=2)

    assert list(df_pca.columns) == ["PC1", "PC2"]
    assert len(df_pca) == len(df)
    assert explained_var.sum() <= 1.0
    assert explained_var.sum() > 0.7


def test_apply_pca_rejects_too_many_components():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    with pytest.raises(ValueError):
        apply_pca(df, ["a", "b"], n=5)


def test_apply_pca_rejects_empty_dataframe():
    df = pd.DataFrame({"a": []})
    with pytest.raises(ValueError):
        apply_pca(df, ["a"], n=1)
