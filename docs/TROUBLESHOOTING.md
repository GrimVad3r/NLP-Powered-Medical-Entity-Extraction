# Troubleshooting Guide - Medical Intelligence Platform v2.0

## Common Issues and Solutions

### Database Issues

#### Connection Error: "could not connect to server"

**Symptoms:**
```
psycopg2.OperationalError: could not connect to server
```

**Causes:**
- Database server not running
- Incorrect connection string
- Database user permissions

**Solutions:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if stopped
sudo systemctl start postgresql

# Verify connection string in .env
echo $DATABASE_URL

# Test connection
psql -U medical_user -d medical_db -c "SELECT 1"

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql.log
```

#### "No schema has been selected"

**Symptoms:**
```
psycopg2.ProgrammingError: no schema has been selected to create in
```

**Causes:**
- Schema not created
- User permissions issue

**Solutions:**
```bash
# Create schema
python scripts/setup_db.py

# Or manually
psql -U medical_user -d medical_db -c "CREATE SCHEMA IF NOT EXISTS public;"

# Reset database
python scripts/reset_db.py
```

### API Issues

#### Port Already in Use

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python -m uvicorn src.api.main:app --port 8001
```

#### "ModuleNotFoundError: No module named 'src'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'src'
```

**Solutions:**
```bash
# Ensure you're in project root
pwd  # Should show .../medical-intelligence-platform-v2

# Install in editable mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/medical-intelligence-platform-v2"
```

#### API Response Timeout

**Symptoms:**
```
requests.exceptions.Timeout: HTTPConnectionPool timeout
```

**Solutions:**
```python
# Increase timeout
response = requests.get(url, timeout=30)

# Check API logs
docker-compose logs api

# Monitor API performance
docker stats

# Restart API
docker-compose restart api
```

### NLP Issues

#### spaCy Model Not Found

**Symptoms:**
```
OSError: [E050] Can't find model 'en_core_sci_md'
```

**Solutions:**
```bash
# Download models
python scripts/download_nlp_models.py

# Or manually
python -m spacy download en_core_sci_md

# Verify installation
python -c "import spacy; nlp = spacy.load('en_core_sci_md'); print('OK')"
```

#### Memory Error During NLP Processing

**Symptoms:**
```
MemoryError: Unable to allocate memory
```

**Solutions:**
```bash
# Process in smaller batches
texts = split_into_batches(all_texts, batch_size=32)

# Reduce model size
# Use en_core_sci_sm instead of en_core_sci_lg

# Monitor memory
watch -n 1 'free -m'

# Increase system swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### Low NER Accuracy

**Symptoms:**
- Entities not being extracted
- Wrong entity classification

**Solutions:**
```python
# Check confidence scores
result = processor.process_message(text)
for entity in result.entities:
    if entity.confidence < 0.6:
        print(f"Low confidence: {entity.text}")

# Use entity linker
linked = linker.link_entity(entity_text, entity_type)
if linked.confidence < 0.5:
    manual_review_needed(entity_text)

# Retrain or fine-tune model (advanced)
```

### Dashboard Issues

#### "streamlit-not-found"

**Symptoms:**
```
Command 'streamlit' not found
```

**Solutions:**
```bash
# Install Streamlit
pip install streamlit

# Or run with python
python -m streamlit run src/dashboard/app.py

# Verify installation
streamlit --version
```

#### Dashboard Won't Load

**Symptoms:**
- Blank page
- "Connection refused"

**Solutions:**
```bash
# Check if dashboard is running
ps aux | grep streamlit

# Restart dashboard
docker-compose restart dashboard

# Clear cache
rm -rf ~/.streamlit/cache

# Check logs
docker-compose logs dashboard

# Try different port
streamlit run src/dashboard/app.py --server.port 8502
```

#### Charts Not Displaying

**Symptoms:**
- Blank charts
- "No data available"

**Solutions:**
```python
# Check if data exists
result = analytics.get_summary()
print(len(result.data))  # Should be > 0

# Verify Plotly installation
pip install plotly

# Clear browser cache
# Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
```

### Testing Issues

#### Tests Failing

**Symptoms:**
```
FAILED tests/unit/test_api_routes.py::test_get_top_products
```

**Solutions:**
```bash
# Run with verbose output
pytest tests/ -vv -s

# Run specific test
pytest tests/unit/test_api_routes.py::test_get_top_products -vv

# Run with traceback
pytest tests/ --tb=long

# Clear pytest cache
pytest --cache-clear
```

#### "fixture 'client' not found"

**Symptoms:**
```
ERROR at setup of test_function - fixture 'client' not found
```

**Solutions:**
```python
# Add fixture to conftest.py
@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from src.api.main import app
    return TestClient(app)

# Or import from conftest
from tests.conftest import client
```

### Docker Issues

#### Container Won't Start

**Symptoms:**
```
docker-compose up
ERROR: for api  Container exited with code 1
```

**Solutions:**
```bash
# Check logs
docker-compose logs api

# Rebuild images
docker-compose down
docker-compose build --no-cache
docker-compose up

# Check docker space
docker system df

# Clean up
docker system prune
```

#### "No space left on device"

**Symptoms:**
```
no space left on device
```

**Solutions:**
```bash
# Check disk usage
df -h

# Clean up old containers
docker container prune

# Clean up old images
docker image prune

# Clean up volumes
docker volume prune

# Remove all unused resources
docker system prune -a
```

### Performance Issues

#### Slow API Response

**Causes:**
- Database slow
- NLP model taking time
- Network issue

**Solutions:**
```bash
# Check database performance
docker-compose exec db psql -U medical_user -d medical_db -c "EXPLAIN ANALYZE SELECT * FROM message LIMIT 10;"

# Add indexes
psql -U medical_user -d medical_db -c "CREATE INDEX idx_message_date ON message(date);"

# Monitor API
docker stats

# Check network
ping api
```

#### High Memory Usage

**Symptoms:**
- Memory usage > 80%
- System becomes slow

**Solutions:**
```bash
# Monitor memory
watch -n 1 'free -m'

# Check process memory
ps aux --sort=-%mem | head

# Restart services
docker-compose restart api

# Increase container limits
# In docker-compose.yml:
# memory: 512M
```

### Security Issues

#### "Unauthorized" on API Endpoint

**Symptoms:**
```
{
  "detail": "Invalid API key"
}
```

**Solutions:**
```bash
# Check API key in .env
echo $API_KEY

# Generate new key
python -c "import secrets; print(secrets.token_hex(32))"

# Add to request
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/api/v1/products/top10
```

#### "CORS error"

**Symptoms:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solutions:**
```python
# Enable CORS in main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Debug Mode

### Enable Debug Logging

```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG

# Or in .env
LOG_LEVEL=DEBUG

# View logs
docker-compose logs -f api
```

### Enable SQL Query Logging

```python
# In src/database/connection.py
engine = create_engine(
    DATABASE_URL,
    echo=True  # Print all SQL queries
)
```

### Enable Request Logging

```python
# In src/api/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Monitoring & Health Checks

### API Health Check

```bash
curl http://localhost:8000/health

# Should return:
{
  "status": "healthy",
  "database": "connected",
  "nlp_models": "loaded"
}
```

### Database Health Check

```bash
docker-compose exec db psql -U medical_user -d medical_db -c "SELECT version();"
```

### Dashboard Health Check

```bash
curl -I http://localhost:8501
```

## Recovery Procedures

### Reset Everything

```bash
# Stop all services
docker-compose down -v

# Clear data
rm -rf data/ logs/

# Rebuild
docker-compose build --no-cache

# Start fresh
docker-compose up -d

# Initialize
python scripts/setup_db.py
python scripts/download_nlp_models.py
```

### Restore from Backup

```bash
# List backups
ls -la /backups/

# Restore
gunzip < /backups/medical_db_20250213_100000.sql.gz | psql -U medical_user medical_db

# Verify
docker-compose exec db psql -U medical_user -d medical_db -c "SELECT COUNT(*) FROM message;"
```

## Getting Help

1. **Check logs first**
   ```bash
   docker-compose logs
   tail -f /var/log/syslog
   ```

2. **Search documentation**
   - README.md
   - ARCHITECTURE.md
   - API_REFERENCE.md
   - This file (TROUBLESHOOTING.md)

3. **Run diagnostics**
   ```bash
   python scripts/diagnostics.py
   ```

4. **Contact support**
   - Check GitHub issues
   - Email support team
   - Consult with team lead

---

**Still having issues?** Contact the development team or open an issue on GitHub.