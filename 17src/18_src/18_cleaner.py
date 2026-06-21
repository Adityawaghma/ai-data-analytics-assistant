import pandas as pd
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates()
    df = df.dropna(how='all')
    for col in df.select_dtypes(include='number').columns:
      df[col] = df[col].fillna(df[col].median())
    for col in df.select_dtypes(include='object').columns:
      df[col] = df[col].fillna('Unknown')
    return df.convert_dtypes()