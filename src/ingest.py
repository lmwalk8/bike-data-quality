"""
API calling logic for CityBikes. Fetches station data and returns a Polars DataFrame.
"""
import polars as pl
import requests

def fetch_citybike_data(network_id: str = "blue-bikes") -> pl.DataFrame:
    """Fetch station data from CityBikes API and return selected columns."""
    url = f"https://api.citybik.es/v2/networks/{network_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        stations = data["network"]["stations"]
        return pl.DataFrame(stations).select(
            ["name", "free_bikes", "empty_slots", "latitude", "longitude"]
        )
    except requests.exceptions.JSONDecodeError as e:
        raise Exception(f"Error decoding JSON: {e} - The raw response content was likely not valid JSON.")
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"Connection error: {e}")
    except requests.exceptions.Timeout as e:
        raise Exception(f"Timeout error: {e}")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request error: {e}")
    except Exception as e:
        raise Exception(f"General error: {e}")
