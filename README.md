# Data Engineering Pipeline Breaker: Building Resilient Pipelines

This project performs thorough data quality checks on public biking data for a city. Specifically, it demonstrates a proactive approach to data quality by applying software quality engineering rigor to data pipelines. Instead of trying to catch and fix it later on in the ETL pipeline, this code identifies incorrect data during extraction/ingestion. After a clean schema check, it also confirms that any transformation steps are done correctly on the data before loading it into its final data source for storage.

## Detailed Project Overview:

Instead of an ETL pipeline failing silently or bringing bad data further into the process, this project uses Python (Polars, Pandera, Soda) to implement an alert of poor data while it is being ingested from its original, raw source. Ways it fast-fails and pauses the pipeline execution:

- `Halts execution based on the data schema`: A strict set of rules is defined that the data must satisfy to proceed. This helps to prevent corrupted or illogical data from reaching further steps in the pipeline (e.g production database).
- `Intercepts schema drift`: Automatically detects when upstream APIs (or other similar data sources) change their structure.

Along with this, it also has additional checks on transform steps done later in the pipeline (after it is confirmed the raw data fits the schema). Using Soda Core in Python, it confirms the data is now cleaned and processed in all the expected ways defined during the transformation. All checks in Soda are written into an HTML report with color-coated outcomes (green=pass, red=fail, yellow=warning). These checks help to:

- `Avoid incorrect data in production`: If data is improperly transformed, this stops it from getting loaded into its production location (e.g PostgreSQL database, etc.) that is expecting the data to be cleaned in a specific way.

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
        - `soda-core`: For further data observability.
        - `soda-core-duckdb`: For DuckDB data adapter in Soda.
        - `duckdb`: For in-memory database in Soda.
        - `pyarrow`: For data interchange in Soda/DuckDB.
        - `pandas`: For Pandas DataFrame conversion in Soda.
        - `jinja2`: For displaying Soda reports in HTML files.
        - `python-dotenv`: For fetching environment variables.
        - `sqlalchemy`: For PostgreSQL interactions.
        - `psycopg2-binary`: For driving the PostgreSQL engine.
- PostgreSQL (database and user set up)
- (Optional) Docker
    - To run all options of the application in simpler commands

## Steps for Project Setup:

1. Install/create project dependencies if applicable (Python, PostgreSQL, Docker)

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

Unhealthy (Early raw data schema failure):
```
python src/main.py --mode faulty --fault-type schema
```

Run with Soda Core checks (raw + transformed data):

Healthy:
```
python src/main.py --mode clean --soda
```

Unhealthy (Wrong data type and extra duplicate row):
```
python src/main.py --mode faulty --fault-type transform --soda
```

- **Raw checks** (`validation/soda_checks_raw.yml`): row count, missing values, non-negative counts, schema.
- **Transformed checks** (`validation/soda_checks_transformed.yml`): same plus no nulls in derived columns (`total_docks`, `availability_pct`), availability in 0–100%, no duplicate stations. Use this to confirm the data has been successfully transformed.

## Run with Docker

**Option 1: Makefile shortcuts (recommended)**

Set your database URL once, then use short commands:
```
export DATABASE_URL="postgresql://USER:PASS@host.docker.internal:5432/DBNAME"
make run-clean                  # Clean pipeline
make run-clean-soda             # Clean + Soda (reports in ./reports)
make run-faulty-schema          # Faulty, schema fault
make run-faulty-transform       # Faulty, transform fault
make run-faulty-transform-soda  # Faulty, transform + Soda (reports in ./reports)
make help                       # List all targets
```

Or create `.env.docker` with Make-compatible content (so you don’t export every time):
```
DATABASE_URL := postgresql://USER:PASS@host.docker.internal:5432/DBNAME
```

Then run `make run-clean`, `make run-clean-soda`, etc. Targets that run Soda mount `./reports` so reports persist on your machine.

**Option 2: Plain docker run**

Build the image:
```
docker build -t bike-data-quality .
```

Run (use `host.docker.internal` as host so the container can reach PostgreSQL on your machine):
```
docker run --rm -e DATABASE_URL="postgresql://USER:PASS@host.docker.internal:5432/DBNAME" bike-data-quality --mode clean
docker run --rm -e DATABASE_URL="postgresql://USER:PASS@host.docker.internal:5432/DBNAME" -v "$(pwd)/reports:/app/reports" bike-data-quality --mode clean --soda
```

On Linux, add `--add-host=host.docker.internal:host-gateway` if needed. For Make, use: `make DOCKER_HOST_EXTRA="--add-host=host.docker.internal:host-gateway" run-clean`.
