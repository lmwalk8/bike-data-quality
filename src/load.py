"""
Data loading into PostgreSQL database.
"""
import polars as pl
from sqlalchemy import create_engine

def load_data_into_database(df: pl.DataFrame, database_url: str) -> None:
    """
    Load the data into the PostgreSQL database using Polars write_database.
    Expects database_url in SQLAlchemy form, e.g. postgresql://user:pass@host:port/dbname
    """
    print("Loading processed data into PostgreSQL database table...")
    try:
        engine = create_engine(database_url)
        df.write_database(
            table_name="citybikes_data",
            connection=engine,
            if_table_exists="replace",
        )
        print("Data loaded into table successfully.")
    except Exception as e:
        raise RuntimeError(f"Error loading data into database: {e}") from e
