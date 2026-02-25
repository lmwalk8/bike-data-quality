# bike-data-quality: Data Circuit Breaker pipeline
# Python 3.11 to match project requirements
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (src + validation)
COPY src/ ./src/
COPY validation/ ./validation/

# Create reports dir (writable at runtime)
RUN mkdir -p reports

# Run from project root so imports resolve (validation, src)
# Pass DATABASE_URL at runtime: docker run -e DATABASE_URL=postgresql://... ...
ENTRYPOINT ["python", "src/main.py"]
CMD ["--mode", "clean"]
