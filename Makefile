# Shortcuts for building and running the bike-data-quality Docker image.
# Set DATABASE_URL (e.g. export DATABASE_URL=postgresql://...@host.docker.internal:5432/db)
# or create .env.docker with DATABASE_URL=... and run: make -f Makefile run-clean (after including it below).
#
# Optional: for Linux if host.docker.internal is missing, use:
#   make DOCKER_HOST_EXTRA="--add-host=host.docker.internal:host-gateway" run-clean

IMAGE_NAME := bike-data-quality
# Include Docker-friendly DATABASE_URL if you have .env.docker (use host.docker.internal as host)
-include .env.docker
export DATABASE_URL

DOCKER_RUN := docker run --rm -e DATABASE_URL $(DOCKER_HOST_EXTRA)
DOCKER_RUN_REPORTS := $(DOCKER_RUN) -v "$(shell pwd)/reports:/app/reports"

.PHONY: build run-clean run-clean-soda run-faulty-schema run-faulty-transform run-faulty-transform-soda help

build:
	docker build -t $(IMAGE_NAME) .

run-clean:
	$(DOCKER_RUN) $(IMAGE_NAME) --mode clean

run-clean-soda:
	$(DOCKER_RUN_REPORTS) $(IMAGE_NAME) --mode clean --soda

run-faulty-schema:
	$(DOCKER_RUN) $(IMAGE_NAME) --mode faulty --fault-type schema

run-faulty-transform:
	$(DOCKER_RUN) $(IMAGE_NAME) --mode faulty --fault-type transform

run-faulty-transform-soda:
	$(DOCKER_RUN_REPORTS) $(IMAGE_NAME) --mode faulty --fault-type transform --soda

help:
	@echo "bike-data-quality Docker shortcuts"
	@echo ""
	@echo "Set DATABASE_URL (e.g. export DATABASE_URL=postgresql://USER:PASS@host.docker.internal:5432/DBNAME)"
	@echo "or create .env.docker with: DATABASE_URL=postgresql://...@host.docker.internal:5432/..."
	@echo ""
	@echo "Targets:"
	@echo "  make build                 Build the image"
	@echo "  make run-clean             Run pipeline (clean mode)"
	@echo "  make run-clean-soda        Run pipeline (clean) + Soda, persist reports to ./reports"
	@echo "  make run-faulty-schema     Run pipeline (faulty, schema fault)"
	@echo "  make run-faulty-transform  Run pipeline (faulty, transform fault)"
	@echo "  make run-faulty-transform-soda  Run pipeline (faulty, transform) + Soda, persist reports"
	@echo "  make help                 Show this help"
