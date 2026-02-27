from pathlib import Path
import sys
import polars as pl

# Ensure project root is on path
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from src.transform import transform

def test_dataframe_transformation():
    """Test that transformation process works as expected on a sample dataframe."""
    # Create a dataframe with the test data
    df = pl.DataFrame({
        "name": ["Test Station A", "Test Station B"],
        "free_bikes": [1, 2],
        "empty_slots": [3, 4],
        "latitude": [45.2435748696, -71.4786352368],
        "longitude": [-71.4786352368, 45.2435748696],
    })
    # Transform the dataframe
    transformed_df = transform(df)
    # Assert the transformed dataframe has the correct shape
    assert transformed_df.shape == (2, 7)
    # Assert that latitude and longitude are rounded to 6 decimal places
    assert transformed_df["latitude"].to_list() == [45.243575, -71.478635]
    assert transformed_df["longitude"].to_list() == [-71.478635, 45.243575]
    # Assert that total_docks equals free_bikes + empty_slots for every row
    assert (
        transformed_df["total_docks"] == transformed_df["free_bikes"] + transformed_df["empty_slots"]
    ).all()
    # Assertions that availability percentage are calculated correctly as integers
    # (free_bikes / total_docks) * 100
    assert (
        transformed_df["availability_pct"] == ((transformed_df["free_bikes"] / transformed_df["total_docks"]) * 100).cast(pl.Int64)
    ).all()
    assert transformed_df["availability_pct"].dtype == pl.Int64
    # Assert that the dataframe is sorted by name
    assert transformed_df["name"].to_list() == ["Test Station A", "Test Station B"]

def test_no_duplicate_stations():
    """Test that duplicate (name, lat, long) rows are deduplicated; first occurrence kept."""
    df = pl.DataFrame({
        "name": ["Test Station A", "Test Station B", "Test Station A"],
        "free_bikes": [1, 2, 1],
        "empty_slots": [3, 4, 3],
        "latitude": [44.56, 74.83, 44.56],
        "longitude": [-74.83, -44.56, -74.83],
    })
    transformed_df = transform(df)
    assert len(transformed_df) == 2, "Expected 2 rows after deduplication"
    assert transformed_df["name"].to_list() == ["Test Station A", "Test Station B"]

def test_rows_with_both_free_bikes_and_empty_slots_zero_are_dropped():
    """Transform drops rows where free_bikes and empty_slots are both 0."""
    df = pl.DataFrame({
        "name": ["Station A", "Station B"],
        "free_bikes": [2, 0],
        "empty_slots": [2, 0],
        "latitude": [42.0, 42.0],
        "longitude": [-71.0, -71.0],
    })
    transformed_df = transform(df)
    assert len(transformed_df) == 1, "Expected 1 row after dropping rows with both free_bikes and empty_slots zero"
    assert transformed_df["name"].to_list() == ["Station A"]

def test_name_string_cleaning():
    """Names are trimmed and internal whitespace collapsed to a single space."""
    df = pl.DataFrame({
        "name": ["  Test   Station  "],
        "free_bikes": [1],
        "empty_slots": [1],
        "latitude": [42.0],
        "longitude": [-71.0],
    })
    transformed_df = transform(df)
    assert transformed_df["name"].to_list() == ["Test Station"], "Expected 'Test Station' after string cleaning"
