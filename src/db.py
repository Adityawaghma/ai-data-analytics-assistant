import sqlite3
import pandas as pd

class DatabaseConnector:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
    def insert_dataframe(self, df, table):
        df.to_sql(table, self.conn, if_exists='replace', index=False)
    def query(self, sql):
        return pd.read_sql_query(sql, self.conn)
    def close(self):
        self.conn.close()