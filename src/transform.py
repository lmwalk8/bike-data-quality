"""
Data cleaning with Polars -> transformation steps (e.g. dedup, normalize).
"""
import polars as pl

def transform(df: pl.DataFrame) -> pl.DataFrame:
    """Apply cleaning/transformation steps."""
    print("Transforming the data...")

    # String cleaning for name: trim, normalize whitespace, Unicode NFC
    df = df.with_columns(
        pl.col("name")
        .str.strip_chars()
        .str.replace_all(r"\s+", " ")
        .str.normalize("NFC")
        .alias("name")
    )

    # Remove duplicates
    df = df.unique(subset=["name", "latitude", "longitude"], keep="first")

    # Fill 0 for missing free_bikes and empty_slots
    df = df.with_columns(
        pl.col("free_bikes").fill_null(0),
        pl.col("empty_slots").fill_null(0),
    )
    # Drop rows with any remaining nulls
    df = df.drop_nulls()
    # Drop rows where both free_bikes and empty_slots are 0 (invalid/unusable)
    df = df.filter(~((pl.col("free_bikes") == 0) & (pl.col("empty_slots") == 0)))

    # Round up latitude and longitude to 6 decimal places
    df = df.with_columns(
        round_up_to_decimals("latitude", 6),
        round_up_to_decimals("longitude", 6),
    )
    # Drop the original latitude and longitude columns
    df = df.drop(["latitude", "longitude"])
    # Rename the rounded latitude and longitude columns
    df = df.rename({
        "latitude_rounded": "latitude",
        "longitude_rounded": "longitude",
    })

    # Add a column for the total number of bikes
    df = df.with_columns(
        (pl.col("free_bikes") + pl.col("empty_slots")).alias("total_docks")
    )
    # Add a column for the availability percentage of bikes
    df = df.with_columns(
        ((pl.col("free_bikes") / pl.col("total_docks")) * 100).alias("availability_pct")
    )
    
    # Sorting by name
    df = df.sort("name", descending=False)

    print("Data transformed successfully.")

    return df

def round_up_to_decimals(col_name: str, decimals: int):
    """Round up a column to a specified number of decimals."""
    shift_expr = pl.col(col_name) * (10**decimals)
    rounded_shifted = shift_expr.ceil()
    result_expr = rounded_shifted / (10**decimals)
    return result_expr.alias(f"{col_name}_rounded")
