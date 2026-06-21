import pandas as pd
import os

def load_file(path: str) -> pd.DataFrame:
  ext = os.path.splitext(path)[1].lower()
  if ext == '.csv':
    return pd.read_csv(path)
  elif ext in ['.xlsx', '.xls']:
    return pd.read_excel(path, engine='openpyxl')
  else:
    raise ValueError(f'Unsupported file type: {ext}')