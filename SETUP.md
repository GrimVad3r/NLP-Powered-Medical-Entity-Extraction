# Medical Intelligence Platform v2.0 - Setup Guide

**Production-Grade Medical Data Pipeline with NLP**

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
```bash
# Check Python version (need 3.10+)
python --version

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib build-essential python3-dev
```

### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/your-org/medical-intelligence-platform-v2.git
cd medical-intelligence-platform-v2

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 4. Download NLP models
python -m spacy download en_core_sci_md

# 5. Setup environment
cp config/.env.example .env
nano .env  # Edit with your credentials

# 6. Initialize database
python scripts/setup_db.py

# 7. Run tests
pytest tests/ -v

# 8. Start services
docker-compose up -d

# 9. Access services
# API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
# Dashboard: http://localhost:8501
```

---

## 📁 Directory Structure Setup

```bash
# Create necessary directories
mkdir -p logs
mkdir -p data/{raw,processed,nlp_models,knowledge_bases}
mkdir -p backups
mkdir -p reports

# Set permissions
chmod 755 logs data scripts
```

---

## ⚙️ Configuration (.env)

```bash
# Create .env from template
cp config/.env.example .env

# Edit .env with your settings
cat > .env << EOF
# Application
ENVIRONMENT=development
DEBUG=true
APP_VERSION=2.0.0

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=medical_db

# Telegram
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+your_phone_number

# NLP
NLP_USE_GPU=false
NLP_CONFIDENCE_THRESHOLD=0.6

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Feature Flags
ENABLE_EXTRACTION=true
ENABLE_NLP=true
ENABLE_TRANSFORMATION=true
ENABLE_API=true
ENABLE_DASHBOARD=true
EOF
```

---

## 🗄️ Database Setup

### PostgreSQL Installation

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

### Create Database

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE medical_db;
CREATE USER medical_user WITH PASSWORD 'secure_password';
ALTER ROLE medical_user SET client_encoding TO 'utf8';
ALTER ROLE medical_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE medical_user SET default_transaction_deferrable TO on;
ALTER ROLE medical_user SET default_transaction_deferrable TO off;
ALTER ROLE medical_user SET work_mem TO '256MB';
ALTER ROLE medical_user SET max_parallel_workers_per_gather TO 4;
GRANT ALL PRIVILEGES ON DATABASE medical_db TO medical_user;

# Exit
\q
```

### Initialize Schema

```bash
# Run migrations
python scripts/setup_db.py

# Or use Alembic
alembic upgrade head
```

---

## 📦 Python Package Setup

### Install Development Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Or install specific groups
pip install -r requirements-nlp.txt  # For NLP features
```

### Verify Installation

```bash
# Check main imports
python -c "from src.core.config import get_settings; print(get_settings().app_name)"

# Check NLP models
python -c "import spacy; nlp = spacy.load('en_core_sci_md'); print('NLP model loaded')"

# Check database
python -c "from src.database.connection import get_db; print('Database connection OK')"
```

---

## 🧪 Testing Setup

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_medical_ner.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Run specific test marker
pytest -m unit -v
pytest -m integration -v
```

### Test Coverage

```bash
# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html

# Open report
open htmlcov/index.html  # macOS
firefox htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

## 🐳 Docker Setup

### Build Docker Images

```bash
# Build main API image
docker build -t medical-api:latest -f docker/Dockerfile .

# Build NLP-specific image
docker build -t medical-nlp:latest -f docker/Dockerfile.nlp .

# Build dashboard image
docker build -t medical-dashboard:latest -f docker/Dockerfile.dashboard .
```

### Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f dashboard

# Stop services
docker-compose down

# Remove volumes (careful!)
docker-compose down -v
```

---

## 🚀 Running the Application

### Start API Server

```bash
# Development mode
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
python -m uvicorn src.api.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Start Dashboard

```bash
# Run Streamlit dashboard
streamlit run src/dashboard/app.py
```

### Run Extraction Pipeline

```bash
# Extract from Telegram channels
python scripts/run_extraction.py --channels "CheMed" "Lobelia" "Tikvah"
```

### Run NLP Pipeline

```bash
# Process extracted messages
python scripts/run_nlp_pipeline.py --input data/raw/messages.json
```

---

## 🔧 Development Workflow

### Set Up Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/PyCQA/flake8
    rev: 6.1.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
EOF

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/ --strict

# Lint
pylint src/

# All checks
make quality
```

---

## 📊 Monitoring & Logs

### View Logs

```bash
# API logs
tail -f logs/api.log

# NLP logs
tail -f logs/nlp.log

# Database logs
tail -f logs/database.log

# Dashboard logs
tail -f logs/dashboard.log

# JSON logs
tail -f logs/*.log | jq '.'
```

### Set Up Monitoring

```bash
# Prometheus metrics (optional)
pip install prometheus-client

# Grafana dashboards
# See docs/MONITORING.md
```

---

## 🔐 Security Setup

### Set Secure Environment Variables

```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in .env
SECRET_KEY=your_generated_key

# Rotate API keys regularly
```

### Database Security

```bash
# Update PostgreSQL password
ALTER USER medical_user WITH PASSWORD 'new_secure_password';

# Restrict connections
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Backup database
pg_dump -U medical_user medical_db > backups/medical_db_backup.sql
```

---

## 📚 Documentation

### Generate Documentation

```bash
# Build MkDocs
mkdocs build

# Serve locally
mkdocs serve

# Deploy
mkdocs gh-deploy
```

### API Documentation

```bash
# Auto-generated at:
# http://localhost:8000/api/docs  (Swagger UI)
# http://localhost:8000/api/redoc  (ReDoc)
```

---

## 🚨 Troubleshooting

### Common Issues

```bash
# ModuleNotFoundError
# Solution: Ensure virtual environment is activated
source venv/bin/activate

# Database connection error
# Solution: Check PostgreSQL is running
sudo service postgresql status

# NLP model not found
# Solution: Download spaCy model
python -m spacy download en_core_sci_md

# Port already in use
# Solution: Change port or kill process
lsof -i :8000
kill -9 <PID>

# Out of memory
# Solution: Reduce batch size
NLP_BATCH_SIZE=8
```

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=DEBUG python -m uvicorn src.api.main:app --reload

# Enable API debug
DEBUG=true python src/api/main.py

# Database debug
DB_ECHO=true python scripts/setup_db.py
```

---

## 📋 Checklist

Before deploying to production:

- [ ] All tests passing (100% coverage)
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] NLP models downloaded
- [ ] API documentation complete
- [ ] Security audit passed
- [ ] Performance benchmarks acceptable
- [ ] Logging configured
- [ ] Backups configured
- [ ] Monitoring configured
- [ ] Disaster recovery plan ready
- [ ] Team trained on deployment

---

## 🔗 Quick Links

- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Git Workflow](docs/GIT_WORKFLOW.md)
- [NLP Guide](docs/NLP_GUIDE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

---

## 📧 Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Search GitHub Issues
3. Create new issue with:
   - Python version
   - Error message
   - Steps to reproduce
   - Environment (OS, Docker version, etc.)

---

**Last Updated: 2025-02-13**
**Maintained by: Boris (Claude Code)**