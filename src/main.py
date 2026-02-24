"""
Demo execution: fetch CityBikes data and run the circuit breaker.
Run from repo root: python src/main.py --mode <clean|faulty> --fault-type <schema|transform> --soda
Or from src/: python main.py --mode <clean|faulty> --fault-type <schema|transform> --soda
Fault type is optional and defaults to schema (will only run in faulty mode).
Soda is optional and defaults to false.
"""
import os
from dotenv import load_dotenv
import sys
from pathlib import Path
import polars as pl
import argparse

# Ensure project root is on path so other modules can be imported
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

env_path = _root / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Fallback to default behavior (current directory)
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("Database URL is not set in the .env file")

from ingest import fetch_citybike_data
from transform import transform
from schema_validator import run_schema_checks
from soda_runner import monitor_raw_data, monitor_transformed_data
from load import load_data_into_database

def main():
    parser = argparse.ArgumentParser(description="Run the bike data quality pipeline.")
    parser.add_argument("--mode", type=str, default="clean", choices=["clean", "faulty"], help="Run the pipeline in clean or faulty mode.")
    parser.add_argument("--soda", action="store_true", help="Run Soda Core checks on raw and transformed data.")
    parser.add_argument(
        "--fault-type",
        type=str,
        default="schema",
        choices=["schema", "transform"],
        help="When --mode faulty: which fault to inject — 'schema' (invalid latitude) or 'transform' (invalid availability_pct + extra row). Ignored when --mode clean.",
    )
    args = parser.parse_args()

    if args.mode == "clean":
        data = fetch_citybike_data()
        run_schema_checks(data)
        if args.soda:
            rc = monitor_raw_data(data)
            if rc != 0:
                raise SystemExit(f"Soda raw-data checks failed (exit code {rc}).")
        transformed_data = transform(data)
        if args.soda:
            rc = monitor_transformed_data(transformed_data)
            if rc != 0:
                raise SystemExit(f"Soda transformed-data checks failed (exit code {rc}).")
            print("Soda Core: raw and transformed data checks passed.")
        load_data_into_database(transformed_data, DATABASE_URL)
    elif args.mode == "faulty":
        if args.fault_type == "schema":
            data = fetch_citybike_data()
            data = data.with_columns(pl.lit(39).alias("latitude").cast(pl.Float64))
            run_schema_checks(data)
        elif args.fault_type == "transform":
            data = fetch_citybike_data()
            run_schema_checks(data)
            if args.soda:
                rc = monitor_raw_data(data)
                if rc != 0:
                    raise SystemExit(f"Soda raw-data checks failed (exit code {rc}).")
            transformed_data = transform(data)
            transformed_data = transformed_data.with_columns(
                pl.lit(39).alias("availability_pct").cast(pl.Int64)
            )
            transformed_data = transformed_data.extend(
                pl.DataFrame({
                    "name": ["699 Mt Auburn St"],
                    "free_bikes": [21],
                    "empty_slots": [4],
                    "latitude": [42.375003],
                    "longitude": [-71.148716],
                    "total_docks": [25],
                    "availability_pct": [84],
                })
            )
            if args.soda:
                rc = monitor_transformed_data(transformed_data)
                if rc != 0:
                    raise SystemExit(f"Soda transformed-data checks failed (exit code {rc}).")
        else:
            raise ValueError(f"Invalid faulty type: {args.fault_type}")
    else:
        raise ValueError(f"Invalid mode: {args.mode}")

if __name__ == "__main__":
    main()
