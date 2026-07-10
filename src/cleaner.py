import pandas as pd


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean a raw DataFrame: drop dupes/empty rows, fill nulls,
    normalize column names to lowercase_underscore, infer dtypes."""
    df = df.drop_duplicates()
    df = df.dropna(how='all')
    for col in df.select_dtypes(include='number').columns:
        df[col] = df[col].fillna(df[col].median())
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].fillna('Unknown')

    # Normalize column names so P3's QTableView headers are consistent
    # (lowercase, spaces -> underscores) and P2's SQL schema can match.
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]

    return df.convert_dtypes()