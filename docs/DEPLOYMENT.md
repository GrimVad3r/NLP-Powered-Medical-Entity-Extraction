# Deployment Guide - Medical Intelligence Platform v2.0

## Production Deployment

### Prerequisites
- Docker & Docker Compose (or Kubernetes)
- PostgreSQL 12+ (or managed service)
- Python 3.9+
- Git

### Environment Setup

1. **Create .env file**
```bash
cp config/.env.example .env
```

2. **Configure environment variables**
```
# Database
DATABASE_URL=postgresql://user:password@host:5432/medical_db

# API
API_KEY=your_secret_api_key_here
SECRET_KEY=your_jwt_secret_key

# Telegram
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
TELEGRAM_PHONE_NUMBER=your_phone_number

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/medical-platform/app.log

# Feature Flags
ENABLE_NLP=true
ENABLE_EXTRACTION=true
ENABLE_API=true
```

### Docker Deployment

#### 1. Build Images
```bash
docker-compose build
```

#### 2. Start Services
```bash
docker-compose up -d
```

#### 3. Initialize Database
```bash
docker-compose exec api python scripts/setup_db.py
docker-compose exec api python scripts/download_nlp_models.py
```

#### 4. Verify Deployment
```bash
docker-compose logs -f api
curl http://localhost:8000/docs
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: medical_db
      POSTGRES_USER: medical_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    environment:
      DATABASE_URL: postgresql://medical_user:${DB_PASSWORD}@db:5432/medical_db
      API_KEY: ${API_KEY}
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data

  dashboard:
    build:
      context: .
      dockerfile: docker/Dockerfile.dashboard
    ports:
      - "8501:8501"
    environment:
      DATABASE_URL: postgresql://medical_user:${DB_PASSWORD}@db:5432/medical_db
    depends_on:
      - api

  worker:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    environment:
      DATABASE_URL: postgresql://medical_user:${DB_PASSWORD}@db:5432/medical_db
    depends_on:
      - db

volumes:
  db_data:
```

### Kubernetes Deployment

#### 1. Build and Push Images
```bash
docker build -t your-registry/medical-api:latest .
docker push your-registry/medical-api:latest
```

#### 2. Create Kubernetes Manifests
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: medical-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: medical-api
  template:
    metadata:
      labels:
        app: medical-api
    spec:
      containers:
      - name: api
        image: your-registry/medical-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: medical-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
```

#### 3. Deploy
```bash
kubectl apply -f k8s/
kubectl get pods
kubectl logs -f deployment/medical-api
```

### SSL/TLS Configuration

#### 1. Install Certbot
```bash
sudo apt-get install certbot python3-certbot-nginx
```

#### 2. Create Certificate
```bash
sudo certbot certonly --standalone -d yourdomain.com
```

#### 3. Configure Nginx
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Database Backup

#### 1. Create Backup Script
```bash
#!/bin/bash
BACKUP_DIR="/backups"
DB_NAME="medical_db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

pg_dump -U medical_user $DB_NAME > $BACKUP_DIR/medical_db_$TIMESTAMP.sql
gzip $BACKUP_DIR/medical_db_$TIMESTAMP.sql
```

#### 2. Schedule Backup
```bash
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

#### 3. Restore from Backup
```bash
gunzip < backup.sql.gz | psql -U medical_user medical_db
```

### Monitoring & Logging

#### 1. Application Logs
```bash
# View logs
docker-compose logs -f api

# Rotate logs
logrotate -f /etc/logrotate.d/medical-platform
```

#### 2. Health Checks
```bash
# API Health
curl http://localhost:8000/health

# Database Health
docker-compose exec db psql -U medical_user -d medical_db -c "SELECT 1"
```

#### 3. Metrics (Optional with Prometheus)
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'medical-api'
    static_configs:
      - targets: ['localhost:8000']
```

### Scaling Considerations

#### 1. Horizontal Scaling
```bash
docker-compose up -d --scale api=3 --scale dashboard=2
```

#### 2. Load Balancing (Nginx)
```nginx
upstream api_backend {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://api_backend;
    }
}
```

#### 3. Caching with Redis
```yaml
cache:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - cache_data:/data
```

### Performance Tuning

#### 1. Database Connection Pool
```python
# config.py
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 40
DB_POOL_RECYCLE = 3600
```

#### 2. API Concurrency
```python
# main.py
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,
    workers=4  # CPU cores * 2
)
```

#### 3. NLP Model Caching
```python
# nlp/models.py
@cache.cache_result(ttl=3600)
def load_ner_model():
    return spacy.load("en_core_sci_md")
```

### Security Hardening

#### 1. Firewall Rules
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### 2. API Rate Limiting
```python
# middleware.py
rate_limiter = RateLimiter(requests_per_minute=100)
```

#### 3. Database Encryption
```bash
# Enable PostgreSQL SSL
echo "ssl = on" >> /etc/postgresql/14/main/postgresql.conf
```

### Health Monitoring

#### 1. Create Health Check Endpoint
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": check_database(),
        "nlp_models": check_nlp_models(),
        "timestamp": datetime.utcnow().isoformat()
    }
```

#### 2. Kubernetes Probes
```yaml
livenessProbe:
    httpGet:
        path: /health
        port: 8000
    initialDelaySeconds: 10
    periodSeconds: 30

readinessProbe:
    httpGet:
        path: /health
        port: 8000
    initialDelaySeconds: 5
    periodSeconds: 10
```

### Rollback Procedure

#### 1. Git-based Rollback
```bash
git log --oneline
git revert <commit-hash>
git push origin main
docker-compose up -d --build
```

#### 2. Database Rollback
```bash
psql -U medical_user medical_db < backup.sql
```

### Troubleshooting

**Container won't start**
```bash
docker-compose logs api
docker-compose down -v
docker-compose up -d --build
```

**Database connection error**
```bash
docker-compose exec db psql -U medical_user -c "SELECT 1"
```

**Out of memory**
```bash
docker stats
# Increase memory limits in docker-compose.yml
```

---

## Post-Deployment Checklist

- [ ] All services running
- [ ] API endpoints responding
- [ ] Dashboard accessible
- [ ] Database backups configured
- [ ] Logs being collected
- [ ] SSL certificates installed
- [ ] Monitoring configured
- [ ] Alerting set up
- [ ] Documentation updated
- [ ] Team trained

---

For more details, see TROUBLESHOOTING.md