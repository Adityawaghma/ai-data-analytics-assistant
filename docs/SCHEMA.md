# SQL Schema

Documents the SQLite tables used by `db.py`. Referenced from
`docs/ARCHITECTURE.md`.

## Overview

Data flows: `cleaner.py` produces a cleaned DataFrame → `db.py` inserts
it into a table → `ml_pipeline.py` and `charts.py` query it back out.

## Tables

> TODO: replace placeholders below with actual column names/types once
> `db.py` and its `insert_dataframe` calls are finalized. Each table
> should correspond to one dataset ingested through `loader.py`.

### `results`

Example table created by inserting a cleaned DataFrame.

| Column  | Type    | Notes                        |
|---------|---------|-------------------------------|
| id      | INTEGER | Primary key, autoincrement    |
| name    | TEXT    |                                |
| score   | INTEGER |                                |

**Created by:** `DatabaseConnector.insert_dataframe(df, "results")`

**Example query:**
```sql
SELECT * FROM results WHERE score > 85;
```

## Conventions

- Table names should match the dataset/domain they represent (e.g. one
  table per cleaned CSV/Excel input), not be hardcoded to `results`.
- All test/dev work should point `DatabaseConnector` at a temp file
  (e.g. `tmp_path / "test.db"` in pytest), never at a production DB file.
- Schema changes should be reflected here and, if used, in any migration
  scripts.

## Status
Work in progress. Table structure above is illustrative — update once
the real schema used by `db.py` is finalized.


