"""
API calling logic for CityBikes. Fetches station data and returns a Polars DataFrame.
"""
import polars as pl
import requests

def fetch_citybike_data(network_id: str = "blue-bikes") -> pl.DataFrame:
    """Fetch station data from CityBikes API and return selected columns."""
    url = f"https://api.citybik.es/v2/networks/{network_id}"
    response = requests.get(url).json()
    stations = response["network"]["stations"]
    return pl.DataFrame(stations).select(
        ["name", "free_bikes", "empty_slots", "latitude", "longitude"]
    )
