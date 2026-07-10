import os
import pandas as pd


def load_file(path: str) -> pd.DataFrame:
    """Load a supported file type into a pandas DataFrame.

    Raises:
        FileNotFoundError: if `path` does not exist on disk.
        ValueError: if the file extension is not supported.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext not in ('.csv', '.xlsx', '.xls'):
        raise ValueError(f'Unsupported file type: {ext}')

    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    if ext == '.csv':
        return pd.read_csv(path)
    else:
        return pd.read_excel(path, engine='openpyxl')