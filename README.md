![CI](https://github.com/Adityawaghma/ai-data-analytics-assistant/actions/workflows/ci.yml/badge.sv) # AI Data Analytics Assistant

An AI-powered desktop application for loading, cleaning, analyzing, and visualizing data, with a PyQt5 interface and SQL-backed storage.

## Overview

AI Data Analytics Assistant helps users import raw data, clean and transform it, run SQL queries against a structured database, generate charts, and apply machine learning models — all from a single desktop application. The goal is to streamline the data analysis workflow from raw file to actionable insight, with an AI assistant layer to help interpret results and suggest next steps.

## Project Structure

```
src/            Core Python modules
  loader.py     Loads raw data files (CSV, Excel, etc.) into the system
  cleaner.py    Cleans and preprocesses data (missing values, formatting, etc.)
  db.py         Handles database connections and queries
  charts.py     Generates visualizations and charts from processed data
  ml.py         Machine learning models and predictions

data/           Raw and processed data files
sql/            SQL scripts for database setup and queries
ui/             PyQt5 interface files
tests/          Unit tests for core modules
docs/           Project documentation
notebooks/      Jupyter notebooks for exploration and prototyping
```

## Features

- Import and clean datasets from common file formats
- Store and query data using SQL
- Generate charts and visual summaries of data
- Apply machine learning models for predictions and insights
- Interact with the system through a PyQt5 desktop interface

## Setup

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd ai-data-analytics-assistant
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Mac/Linux
   venv\Scripts\activate         # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python src/main.py
   ```

## Usage

1. Launch the application.
2. Load a dataset through the UI or via `loader.py`.
3. Clean and preprocess the data using `cleaner.py`.
4. Query or store data using the SQL scripts in `sql/` and `db.py`.
5. Generate charts with `charts.py` to visualize trends and patterns.
6. Run ML models in `ml.py` for predictions or deeper insights.

## Tools & Technologies

- Python
- PyQt5 (desktop UI)
- SQL (data storage and queries)
- Git & GitHub (version control)
- Jupyter Notebooks (exploration and prototyping)

## Status

Work in progress. Core folder structure and stub files are in place; features are being built out incrementally.

## Contributing

1. Create a new branch for your feature or fix.
2. Make your changes and commit with a clear message.
3. Push your branch and open a pull request.

## License

Add your chosen license here (e.g., MIT, Apache 2.0).
