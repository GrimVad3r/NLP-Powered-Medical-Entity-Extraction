.PHONY: help install test lint format clean setup-db setup-nlp run-api run-dashboard run-extraction run-nlp docker-build docker-up docker-down

PYTHON := python3
PIP := pip3
VENV := venv

help:
	@echo "🏥 Medical Intelligence Platform v2.0"
	@echo ""
	@echo "Available commands:"
	@echo "  make install          Install dependencies"
	@echo "  make test             Run tests with coverage"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make test-coverage    Generate coverage report"
	@echo "  make lint             Run linting and type checks"
	@echo "  make format           Auto-format code"
	@echo "  make clean            Clean cache and build files"
	@echo "  make setup-db         Initialize database"
	@echo "  make setup-nlp        Download NLP models"
	@echo "  make run-api          Start API server"
	@echo "  make run-dashboard    Start Streamlit dashboard"
	@echo "  make run-extraction   Run Telegram extraction"
	@echo "  make run-nlp          Run NLP pipeline"
	@echo "  make docker-build     Build Docker images"
	@echo "  make docker-up        Start Docker containers"
	@echo "  make docker-down      Stop Docker containers"

venv:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip setuptools wheel

install: venv
	@echo "Installing dependencies..."
	$(VENV)/bin/pip install -r requirements.txt
	$(VENV)/bin/pip install -r requirements-dev.txt
	@echo "✅ Dependencies installed"

install-nlp:
	@echo "Installing NLP dependencies..."
	$(VENV)/bin/pip install -r requirements-nlp.txt
	@echo "Downloading NLP models..."
	$(VENV)/bin/python -m spacy download en_core_sci_md
	@echo "✅ NLP setup complete"

test:
	@echo "Running all tests..."
	$(VENV)/bin/pytest tests/ -v --tb=short

test-unit:
	@echo "Running unit tests..."
	$(VENV)/bin/pytest tests/unit/ -v --tb=short

test-integration:
	@echo "Running integration tests..."
	$(VENV)/bin/pytest tests/integration/ -v --tb=short

test-coverage:
	@echo "Running tests with coverage..."
	$(VENV)/bin/pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
	@echo "✅ Coverage report: htmlcov/index.html"

lint:
	@echo "Running linting..."
	$(VENV)/bin/flake8 src/ tests/
	$(VENV)/bin/mypy src/ --ignore-missing-imports
	$(VENV)/bin/black --check src/ tests/
	$(VENV)/bin/isort --check-only src/ tests/
	@echo "✅ Lint checks passed"

format:
	@echo "Auto-formatting code..."
	$(VENV)/bin/black src/ tests/
	$(VENV)/bin/isort src/ tests/
	@echo "✅ Code formatted"

clean:
	@echo "Cleaning cache and build files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/
	@echo "✅ Cache cleaned"

setup-db:
	@echo "Setting up database..."
	$(VENV)/bin/python scripts/setup_db.py
	@echo "✅ Database initialized"

setup-nlp:
	@echo "Downloading NLP models..."
	$(VENV)/bin/python scripts/download_nlp_models.py
	@echo "✅ NLP models ready"

run-api:
	@echo "Starting API server..."
	$(VENV)/bin/python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-dashboard:
	@echo "Starting Streamlit dashboard..."
	$(VENV)/bin/streamlit run src/dashboard/app.py

run-extraction:
	@echo "Running Telegram extraction..."
	$(VENV)/bin/python scripts/run_extraction.py --channels CheMed Lobelia Tikvah --limit 1000

run-nlp:
	@echo "Running NLP pipeline..."
	$(VENV)/bin/python scripts/run_nlp_pipeline.py --input data/raw/messages.json --output data/processed/results.json

docker-build:
	@echo "Building Docker images..."
	docker build -t medical-api:latest -f docker/Dockerfile .
	docker build -t medical-nlp:latest -f docker/Dockerfile.nlp .
	docker build -t medical-dashboard:latest -f docker/Dockerfile.dashboard .
	@echo "✅ Docker images built"

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo "✅ Services started"
	@echo "  API: http://localhost:8000"
	@echo "  Dashboard: http://localhost:8501"
	@echo "  Database: localhost:5432"

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down
	@echo "✅ Services stopped"

docker-logs:
	docker-compose logs -f

# Convenience targets
dev: install install-nlp
	@echo "✅ Development environment ready"

ci: lint test
	@echo "✅ CI checks passed"

all: clean install install-nlp test lint
	@echo "✅ All checks passed"

.DEFAULT_GOAL := help