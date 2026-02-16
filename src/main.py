"""
Demo execution: fetch CityBikes data and run the circuit breaker.
Run from repo root: python src/main.py --mode <clean|faulty>
Or from src/: python main.py --mode <clean|faulty>
"""
import sys
from pathlib import Path
import polars as pl
import argparse

# Ensure project root is on path so other modules can be imported
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from ingest import fetch_citybike_data
from transform import transform
from pipeline_breaker import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="Run the bike data quality pipeline.")
    parser.add_argument("--mode", type=str, default="clean", choices=["clean", "faulty"], help="Run the pipeline in clean or faulty mode.")
    args = parser.parse_args()

    if args.mode == "clean":
        data = fetch_citybike_data()
        data = transform(data)
        run_pipeline(data)
    elif args.mode == "faulty":
        data = fetch_citybike_data()
        data = data.with_columns(pl.lit(39).alias("latitude").cast(pl.Float64))
        data = transform(data)
        run_pipeline(data)
    else:
        raise ValueError(f"Invalid mode: {args.mode}")

if __name__ == "__main__":
    main()
