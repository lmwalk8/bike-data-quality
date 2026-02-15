"""
Demo execution: fetch CityBikes data and run the circuit breaker.
Run from repo root: python -m src
"""

from src.ingest import fetch_citybike_data
from src.transform import transform
from src.pipeline_breaker import run_pipeline

if __name__ == "__main__":
    data = fetch_citybike_data()
    data = transform(data)
    run_pipeline(data)
