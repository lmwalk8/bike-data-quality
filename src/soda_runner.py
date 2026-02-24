"""
Run Soda Core checks on CityBikes data (raw and/or transformed).
Uses DuckDB to register in-memory DataFrames.
"""
import duckdb
import pandas as pd
import polars as pl
import sys
from pathlib import Path
from jinja2 import Template
from soda.scan import Scan

# Ensure project root is on path so other modules can be imported
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

VALIDATION_DIR = _root / "validation"
REPORT_DIR = _root / "reports"

def _pandas_for_duckdb(df: pl.DataFrame) -> pd.DataFrame:
    """Convert Polars to Pandas with dtypes DuckDB accepts (object for strings, int32 for ints)."""
    pdf = df.to_pandas()
    # DuckDB can fail on Pandas StringDtype; use object for string columns
    for col in pdf.select_dtypes(include=["string"]).columns:
        pdf[col] = pdf[col].astype(object)
    # Use INTEGER (int32) instead of BIGINT (int64) for numeric columns
    for col in pdf.select_dtypes(include=["int64"]).columns:
        pdf[col] = pdf[col].astype("int32")
    return pdf

def run_soda_scan(
    df: pl.DataFrame,
    dataset_name: str,
    sodacl_path: str | Path,
    data_source_name: str = "duckdb",
) -> int:
    """
    Run SodaCL checks from a YAML file against a Polars DataFrame.
    Registers the DataFrame in DuckDB and runs the scan.

    Returns:
        Exit code: 0 if all checks pass, non-zero if any fail.
        Scan results: dictionary containing the results of the scan.
    """
    sodacl_path = Path(sodacl_path)
    if not sodacl_path.is_file():
        raise FileNotFoundError(f"SodaCL file not found: {sodacl_path}")

    with duckdb.connect(":memory:") as con:
        con.register(dataset_name, _pandas_for_duckdb(df))
        scan = Scan()
        scan.add_duckdb_connection(con)
        scan.set_data_source_name(data_source_name)
        scan.add_sodacl_yaml_file(str(sodacl_path))
        exit_code = scan.execute()
        if exit_code != 0:
            logs = getattr(scan, "get_logs_text", None)
            if callable(logs):
                print("--- Soda Core scan output (failures / errors) ---")
                print(logs())
            else:
                print("Soda scan failed (exit code %s). Enable verbose logging for details." % exit_code)
        scan_results = scan.get_scan_results()
    return exit_code, scan_results

def display_scan_results_in_html(scan_results: dict, dataset_name: str) -> None:
    """Display Soda Core scan results in HTML.
    Args:
        scan_results: dictionary containing the results of the scan.
        dataset_name: name of the dataset.
    Returns:
        None
    """
    check_results = scan_results.get("checks", [])

    # Create HTML Template
    html_template = """
    <html>
    <body>
        <h2>Soda Scan Report</h2>
        <table border="1">
            <tr>
                <th>Table</th>
                <th>Check</th>
                <th>Status</th>
            </tr>
            {% for check in checks %}
            <tr style="background-color: {% if check.outcome == 'fail' %}#ffcccc{% elif check.outcome == 'warn' %}#ffffcc{% else %}#ccffcc{% endif %}">
                <td>{{ check.table }}</td>
                <td>{{ check.name }}</td>
                <td>{{ check.outcome }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """

    # Render and Save HTML
    template = Template(html_template)
    html_content = template.render(checks=check_results)

    with open(REPORT_DIR / f"soda_report_{dataset_name}.html", "w") as f:
        f.write(html_content)

def monitor_raw_data(df: pl.DataFrame) -> int:
    """Run Soda checks for raw (post-ingest) CityBikes data."""
    exit_code, scan_results = run_soda_scan(
        df=df,
        dataset_name="citybikes_raw",
        sodacl_path=VALIDATION_DIR / "soda_checks_raw.yml",
    )

    display_scan_results_in_html(scan_results, "raw")
    print(f"Soda Core: raw-data checks run. Results saved to {REPORT_DIR / 'soda_report_raw.html'}")

    return exit_code

def monitor_transformed_data(df: pl.DataFrame) -> int:
    """Run Soda checks for transformed CityBikes data (post-transform)."""
    exit_code, scan_results = run_soda_scan(
        df=df,
        dataset_name="citybikes_transformed",
        sodacl_path=VALIDATION_DIR / "soda_checks_transformed.yml",
    )

    display_scan_results_in_html(scan_results, "transformed")
    print(f"Soda Core: transformed-data checks run. Results saved to {REPORT_DIR / 'soda_report_transformed.html'}")

    return exit_code