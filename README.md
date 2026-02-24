# Data Engineering Pipeline Breaker: Building Resilient Pipelines

This project performs thorough data quality checks on public biking data for a city. Specifically, it demonstrates a proactive approach to data quality by applying software quality engineering rigor to data pipelines. Instead of trying to catch and fix it later on in the ETL pipeline, this code identifies incorrect data during extraction/ingestion.

## Detailed Project Overview:

Instead of an ETL pipeline failing silently or bringing bad data further into the process, this project uses Python (Polars and Pandera) to implement an alert of poor data while it is being ingested from its original, raw source. Ways it fast-fails and pauses the pipeline execution:

- `Halts execution based on the data schema`: A strict set of rules is defined that the data must satisfy to proceed. This helps to prevent corrupted or illogical data from reaching further steps in the pipeline (e.g production database).
- `Intercepts schema drift`: Automatically detects when upstream APIs (or other similar data sources) change their structure.

## Technical Stack (Prerequisites to Run Project):

- Data source: CityBikes API
    - Project page: [CityBikes](https://citybik.es/#about)
    - Further documentation about API: [CityBikes API Documentation](https://api.citybik.es/v2/)
    - Example API request for Boston bikes: [Blue Bikes](https://api.citybik.es/v2/networks/blue-bikes) 
- Python 3.11+
    - Libraries Used:
        - `polars`: For data processing.
        - `pandera[polars]`: For quality gate checks.
        - `requests`: For getting API data.
        - `sqlalchemy`: For PostgreSQL interactions.
        - `soda-core`: For further data observability.
        - `soda-core-duckdb`: For DuckDB data adapter in Soda.
        - `duckdb`: For in-memory database in Soda.
        - `pyarrow`: For data interchange in Soda/DuckDB.
        - `pandas`: For Pandas DataFrame conversion in Soda.
        - `jinja2`: For displaying Soda reports in HTML files.
- PostgreSQL (database and user set up)

## Steps for Project Setup:

1. Install/create project dependencies if applicable (Python, PostgreSQL)

2. Clone this repository:
```
git clone https://github.com/lmwalk8/bike-data-quality.git
cd bike-data-quality
```

3. Create and activate a Python virutal environment:
```
python3 -m venv bike_data_quality_env
source bike_data_quality_env/bin/activate (Linux/macOS) OR bike_data_quality_env\Scripts\activate.bat (Windows)
```

4. Install all required dependencies:

Pip:
```
pip install -r requirements.txt
```

OR

Conda:
```
# Create: conda env create -f environment.yml
# Activate: conda activate bike-data-quality
# Update: conda env update -f environment.yml --prune
```

5. Set up required environment variables:

Create .env variable in project directory and add this database information:
```
DATABASE_URL=postgresql://your_user:your_password@host:port/database_name
```

6. Run different pipelines:

Healthy:
```
python src/main.py --mode clean
```

Unhealthy (inserts incorrect location for bike stations):
```
python src/main.py --mode faulty
```

Run with Soda Core checks (raw + transformed data):
```
python src/main.py --mode clean --soda
```
- **Raw checks** (`validation/soda_checks_raw.yml`): row count, missing values, non-negative counts, schema.
- **Transformed checks** (`validation/soda_checks_transformed.yml`): same plus no nulls in derived columns (`total_docks`, `availability_pct`), availability in 0–100%, no duplicate stations. Use this to confirm the data has been successfully transformed.
