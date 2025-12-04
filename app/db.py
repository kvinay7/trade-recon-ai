import duckdb
import pandas as pd

class InMemoryDB:
    def __init__(self):
        self.conn = duckdb.connect(database=':memory:')

    def save_df(self, df, table_name):
        self.conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")

    def run(self, query):
        return self.conn.execute(query).df()
