from pathlib import Path
import sys
from unittest.mock import patch, MagicMock
import polars as pl

# Ensure project root is on path
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from src.ingest import fetch_citybike_data

def test_fetch_citybike_data_returns_dataframe_with_expected_columns():
    """Ingest returns a Polars DataFrame with expected columns; uses mocked API response (no network)."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "network": {
            "stations": [
                {"name": "Station A", "free_bikes": 5, "empty_slots": 10, "latitude": 42.35, "longitude": -71.08},
                {"name": "Station B", "free_bikes": 2, "empty_slots": 8, "latitude": 42.36, "longitude": -71.09},
            ]
        }
    }

    with patch("src.ingest.requests.get", return_value=mock_response):
        df = fetch_citybike_data()

    assert isinstance(df, pl.DataFrame)
    assert df.columns == ["name", "free_bikes", "empty_slots", "latitude", "longitude"]
