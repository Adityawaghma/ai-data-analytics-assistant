"""
src/anomaly.py — P1 (Jul 29): Isolation Forest anomaly detection.

How to work:
    result = detect_anomalies(df, ["sales", "price"])
    flagged = result[result["is_anomaly"]]   # rows flagged as anomalous
"""

import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_anomalies(df: pd.DataFrame, cols: list, contamination: float = 0.05,
                      random_state: int = 42) -> pd.DataFrame:
    """
    Flag anomalous rows in df using Isolation Forest on the given columns.

    Args:
        df: source DataFrame. Not modified in place — a copy is returned.
        cols: list of numeric column names to fit the detector on.
        contamination: expected proportion of anomalies (0.0-0.5).
            Roughly this fraction of rows will end up flagged.
        random_state: for reproducibility.

    Returns:
        A copy of df with two new columns:
            is_anomaly: bool, True if the row was flagged as anomalous.
            anomaly_score: float, IsolationForest's raw anomaly score
                (lower/more negative = more anomalous).
    """
    if df.empty:
        raise ValueError("Cannot detect anomalies: DataFrame is empty")
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"Column(s) not found in DataFrame: {missing}")

    iso = IsolationForest(contamination=contamination, random_state=random_state)
    scores = iso.fit_predict(df[cols])

    result = df.copy()
    result["is_anomaly"] = (scores == -1)
    result["anomaly_score"] = iso.score_samples(df[cols])
    return result


def store_anomalies(conn, df_with_flags: pd.DataFrame, table: str = "anomalies") -> int:
    """
    Persist the flagged (is_anomaly == True) rows to a DB table (P2
    integration), so anomalous rows are queryable later.

    Args:
        conn: open sqlite3 connection.
        df_with_flags: output of detect_anomalies() — must have an
            is_anomaly column.
        table: destination table name.

    Returns:
        Number of anomalous rows written.
    """
    if "is_anomaly" not in df_with_flags.columns:
        raise ValueError("df_with_flags must come from detect_anomalies()")

    flagged = df_with_flags[df_with_flags["is_anomaly"]]
    if not flagged.empty:
        flagged.to_sql(table, conn, if_exists="append", index=False)
    return len(flagged)


if __name__ == "__main__":
    # Quick manual test — matches the board's "How to Work" example
    import numpy as np

    rng = np.random.default_rng(1)
    n = 200
    sales = rng.normal(1000, 100, n)
    price = rng.normal(50, 5, n)

    # Inject a handful of obvious outliers
    sales[:5] = [5000, 5200, 4800, 5100, 4900]
    price[:5] = [500, 480, 520, 510, 490]

    df = pd.DataFrame({"sales": sales, "price": price})

    result = detect_anomalies(df, ["sales", "price"], contamination=0.05)
    n_flagged = result["is_anomaly"].sum()
    expected = int(0.05 * len(df))

    print(f"Rows flagged as anomalies: {n_flagged} (expected roughly {expected})")
    print(f"Injected outliers (first 5 rows) flagged: "
          f"{result['is_anomaly'].iloc[:5].sum()} / 5")

    assert "is_anomaly" in result.columns
    assert "anomaly_score" in result.columns
    assert result["is_anomaly"].iloc[:5].sum() >= 3, (
        "Expected most of the 5 injected outliers to be flagged"
    )
    print("\nIsolation Forest check: PASSED")
