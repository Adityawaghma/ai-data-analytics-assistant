import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest
import pandas as pd
from src.loader import load_file
from src.cleaner import clean_dataframe
from src.db import DatabaseConnector


def test_full_pipeline(tmp_path):
    # ── 1. Create a temp CSV with real column names ──────────────────────
    csv = tmp_path / "data.csv"
    csv.write_text("name,score\nAlice,90\nBob,85")

    # ── 2. Load ──────────────────────────────────────────────────────────
    raw_df = load_file(str(csv))
    assert len(raw_df) == 2, "Loader should read 2 rows"

    # ── 3. Clean ─────────────────────────────────────────────────────────
    df = clean_dataframe(raw_df)
    assert len(df) == len(raw_df), "Cleaned rows should equal loaded rows"

    # ── 4. Insert into temp SQLite DB ────────────────────────────────────
    db_path = str(tmp_path / "test.db")
    db = DatabaseConnector(db_path)
    db.insert_dataframe(df, "results")

    # ── 5. Query back & assert ───────────────────────────────────────────
    result = db.query("SELECT * FROM results")
    assert len(result) == 2, "Queried rows should equal inserted rows"

    # ── 6. Cleanup ───────────────────────────────────────────────────────
    db.close()


def test_full_pipeline_with_dirty_data(tmp_path):
    """Extra: proves cleaner actually removes bad rows before inserting."""
    csv = tmp_path / "dirty.csv"
    csv.write_text("name,score\nAlice,90\nBob,85\nAlice,90\n,")  # duplicate + null

    raw_df = load_file(str(csv))
    df = clean_dataframe(raw_df)

    db = DatabaseConnector(str(tmp_path / "dirty.db"))
    db.insert_dataframe(df, "results")

    result = db.query("SELECT * FROM results")
    assert len(result) == 2  # duplicates and nulls removed
    db.close()
    