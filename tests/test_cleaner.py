import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
from src.cleaner import clean_dataframe


def test_drop_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": [4, 4, 5]})
    cleaned = clean_dataframe(df)
    assert len(cleaned) == 2


def test_fill_numeric_nulls_with_median():
    df = pd.DataFrame({"a": [1, None, 3], "b": ["x", "y", "z"]})
    cleaned = clean_dataframe(df)
    assert cleaned["a"].isnull().sum() == 0
    assert cleaned["a"].iloc[1] == 2  # median of 1, 3


def test_fill_object_nulls_with_unknown():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", None, "z"]})
    cleaned = clean_dataframe(df)
    assert cleaned["b"].iloc[1] == "Unknown"


def test_column_names_normalized():
    df = pd.DataFrame({"First Name": [1, 2], "Last Name": [3, 4]})
    cleaned = clean_dataframe(df)
    assert list(cleaned.columns) == ["first_name", "last_name"]