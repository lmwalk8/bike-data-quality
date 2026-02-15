"""
Circuit breaker logic: halts the pipeline when data fails the contract.
"""
import polars as pl

from pandera.errors import SchemaErrors

from contracts.citybikes_schema_laws import CityBikeSchema

def run_pipeline(df: pl.DataFrame) -> None:
    """Validate df against CityBikeSchema; exit on failure."""
    try:
        print("Validating Data Quality...")
        CityBikeSchema.validate(df, lazy=True)
        print("Quality Check Passed.")
    except SchemaErrors as err:
        print("Error in Data Quality Check!")
        failure_cases = getattr(err, "failure_cases", None)
        if failure_cases is not None:
            try:
                print(failure_cases[["column", "check", "failure_case"]].head())
            except Exception:
                print(failure_cases)
        else:
            print(err)
        raise SystemExit("Pipeline Halted: Data Integrity Violation.")
