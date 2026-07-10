import logging

logger = logging.getLogger(__name__)


def export_data(df, path, fmt='csv'):
    """Export a DataFrame to disk in csv/json/xlsx format.

    Raises:
        ValueError: if fmt is not one of csv/json/xlsx.
        Exception: re-raised after logging, if the underlying write fails
            (e.g. permission error, disk full, invalid path).
    """
    try:
        if fmt == 'csv':
            df.to_csv(path, index=False)
        elif fmt == 'json':
            df.to_json(path, orient='records', indent=2)
        elif fmt == 'xlsx':
            df.to_excel(path, index=False, engine='openpyxl')
        else:
            raise ValueError(f'Unknown format: {fmt}')
    except Exception as e:
        logger.error(f"Export failed ({fmt} -> {path}): {e}")
        raise