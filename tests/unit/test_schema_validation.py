from pathlib import Path
import sys
import pytest
import polars as pl

# Ensure project root is on path
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from src.schema_validator import run_schema_checks

def test_schema_validation_pass():
    """Valid data passes: run_schema_checks returns without raising."""
    df = pl.DataFrame({
        "name": ["Test Station"],
        "free_bikes": [1],
        "empty_slots": [3],
        "latitude": [42.4],
        "longitude": [-71.1],
    })
    run_schema_checks(df)
    # Success = no exception; nothing to assert

def test_schema_validation_fail():
    """Invalid data (e.g. negative counts, out-of-range lat/long) raises SystemExit."""
    df = pl.DataFrame({
        "name": ["Test Station"],
        "free_bikes": [-1],
        "empty_slots": [-6],
        "latitude": [39.2],
        "longitude": [-75.4],
    })
    with pytest.raises(SystemExit):
        run_schema_checks(df)
