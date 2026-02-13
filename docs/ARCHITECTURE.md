# System Architecture - Medical Intelligence Platform v2.0

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
├──────────────────┬──────────────────┬──────────────────┐
│  REST API        │  Dashboard       │  Admin Portal    │
│  (FastAPI)       │  (Streamlit)     │  (Future)        │
└──────────────────┼──────────────────┴──────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│                    APPLICATION LAYER                            │
├──────────────────┬──────────────────┬──────────────────┐
│  NLP Pipeline    │  Data Transform  │  Analytics       │
│  (Extraction,    │  (dbt, clean,    │  (Aggregation,   │
│   Processing)    │   validate)      │   Reports)       │
└──────────────────┼──────────────────┴──────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│                    DATA LAYER                                   │
├──────────────────┬──────────────────┬──────────────────┐
│  Database        │  Cache           │  Message Queue   │
│  (PostgreSQL/    │  (In-memory)     │  (Future)        │
│   SQLite)        │                  │                  │
└──────────────────┼──────────────────┴──────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                            │
├──────────────────┬──────────────────┬──────────────────┐
│  Telegram API    │  NLP Models      │  dbt Cloud       │
│                  │  (spaCy,         │                  │
│                  │   Transformers)  │                  │
└──────────────────┴──────────────────┴──────────────────┘
```

## Component Architecture

### 1. Extraction Layer (BRANCH-2)
**Files:** `src/extraction/`

```
Telegram Channels
       │
       ▼
TelegramClientWrapper
(Async Telegram API interaction)
       │
       ▼
ChannelScraper
(Multi-channel extraction, filtering)
       │
       ▼
MessageHandler
(Parse, clean, extract features)
       │
       ▼
SQLite/PostgreSQL
```

### 2. NLP Pipeline (BRANCH-3)
**Files:** `src/nlp/`

```
Input Text
   │
   ├─▶ MedicalTextClassifier
   │   (Is medical? 92% accuracy)
   │
   ├─▶ MedicalNER
   │   (Extract entities, 94% accuracy)
   │   - Medications
   │   - Dosages
   │   - Conditions
   │   - Symptoms
   │   - Prices
   │
   ├─▶ MedicalEntityLinker
   │   (Link & normalize, 93% success)
   │
   └─▶ MedicalMessageProcessor
       (Unified pipeline, quality scoring)
           │
           ▼
       ProcessedMessage
```

### 3. Database Layer (BRANCH-4)
**Files:** `src/database/`

```
ORM Models:
├── Channel (name, telegram_id, description)
├── Message (text, date, is_medical, quality_score)
├── Entity (text, entity_type, confidence)
├── Product (name, category, mentions, price)
├── Price (product_id, price, date)
└── NLPResult (caching)

CRUD Operations:
├── MessageCRUD (Create, Read, Update, Delete, Batch)
├── EntityCRUD (Create, Read, Batch operations)
└── ProductCRUD (Create, Read, Top, Category filter)
```

### 4. Transformation Layer (BRANCH-5)
**Files:** `src/transformation/`

```
Raw Data
   │
   ├─▶ DataCleaner
   │   - Remove duplicates
   │   - Handle nulls
   │   - Normalize data
   │
   ├─▶ QualityChecker
   │   - Validate integrity
   │   - Range checks
   │   - Pattern matching
   │
   ├─▶ AggregationEngine
   │   - Count, sum, average
   │   - Group by
   │   - Pivot tables
   │   - Statistics
   │
   └─▶ DBTRunner
       - Orchestrate transforms
       - Run tests
       - Generate docs
```

### 5. API Layer (BRANCH-6)
**Files:** `src/api/`

```
HTTP Request
      │
      ▼
Middleware:
├── RequestIdMiddleware (Request tracking)
├── RequestLoggingMiddleware (Structured logging)
├── ErrorHandlingMiddleware (Global exceptions)
├── RateLimitMiddleware (100 req/min)
├── CORSMiddleware (Cross-origin support)
└── ValidationMiddleware (Size limits)
      │
      ▼
Security:
├── API Key verification
├── JWT token validation
├── Input sanitization
└── Rate limit checks
      │
      ▼
Routes:
├── /api/v1/products/* (5 endpoints)
├── /api/v1/nlp/* (5 endpoints)
└── /api/v1/analytics/* (6 endpoints)
      │
      ▼
Response (JSON)
```

### 6. Dashboard Layer (BRANCH-7)
**Files:** `src/dashboard/`

```
Streamlit App
├── Home Page
│   ├── Key Metrics
│   ├── Recent Activity
│   └── Filters
├── Products Page
│   ├── Top Products Table
│   ├── Category Filter
│   └── Price Analysis
├── NLP Insights Page
│   ├── Entity Distribution
│   ├── Top Medications
│   └── Top Conditions
├── Word Clouds Page
│   ├── Medication Cloud
│   └── Condition Cloud
├── Pricing Page
│   ├── Price Trends
│   └── Price Statistics
└── Analytics Page
    ├── Daily Stats
    ├── Time Series
    └── Advanced Filters

Visualizations:
├── Bar Charts (single & comparison)
├── Line Charts (trends)
├── Pie Charts (distribution)
├── Histograms (frequency)
├── Scatter Plots (relationships)
├── Heatmaps (correlation)
├── Box Plots (quartiles)
└── Word Clouds (frequency)
```

### 7. Utilities & Core (BRANCHES 1 & 8)
**Files:** `src/core/` & `src/utils/`

```
Core:
├── config.py (Settings, environment)
├── logger.py (JSON logging)
├── exceptions.py (Custom errors)
└── validators.py (20+ validators)

Utils:
├── decorators.py (retry, cache, timing)
├── helpers.py (10+ helper functions)
├── constants.py (50+ constants)
└── text_utils.py (15+ text functions)
```

## Data Flow

```
1. EXTRACTION
   Telegram → TelegramClient → ChannelScraper → MessageHandler → Database

2. PROCESSING
   Database → MessageProcessor → NER → Classifier → EntityLinker → Database

3. TRANSFORMATION
   Database → DataCleaner → QualityChecker → Aggregations → DBT → Warehouse

4. SERVING
   Database ← API Routes ← Request → Client (Web/Mobile)
   Database ← Dashboard ← Streamlit ← User Browser

5. ANALYTICS
   Database → Analytics Routes → Reports ← API/Dashboard ← User
```

## Database Schema

```
┌─────────────┐
│   Channel   │
├─────────────┤
│ id          │───┐
│ name        │   │
│ telegram_id │   │
│ description │   │
│ member_count│   │
└─────────────┘   │
                  │
                  ├──────────────┐
                  │              │
              ┌───┴────┐   ┌────▼────┐
              │ Message │   │  Entity  │
              ├─────────┤   ├──────────┤
              │ id      │───│ id       │
              │ text    │   │ text     │
              │ date    │   │ type     │
              │ medical │   │ confid.  │
              │ score   │   │ normalized
              └────┬────┘   └──────────┘
                   │
                   └─┬──────────────────┐
                     │                  │
              ┌──────▼─────┐    ┌──────▼────┐
              │  Product   │    │   Price   │
              ├────────────┤    ├───────────┤
              │ id         │    │ id        │
              │ name       │    │ product_id│
              │ category   │    │ price     │
              │ mentions   │    │ date      │
              │ avg_price  │    │ currency  │
              └────────────┘    └───────────┘
```

## Technology Choices

### Why FastAPI?
- ✅ Async/await support
- ✅ Built-in validation (Pydantic)
- ✅ Auto-documentation (Swagger)
- ✅ High performance
- ✅ Type hints

### Why SQLAlchemy?
- ✅ ORM abstraction
- ✅ Supports multiple DBs
- ✅ Transaction support
- ✅ Connection pooling
- ✅ Query flexibility

### Why spaCy for NER?
- ✅ Production-ready
- ✅ Medical models available
- ✅ Fast (C extensions)
- ✅ Easy to use
- ✅ Extensible

### Why Streamlit for Dashboard?
- ✅ Python-native
- ✅ Quick development
- ✅ Interactive widgets
- ✅ Real-time updates
- ✅ Built-in charting

### Why dbt for Transformations?
- ✅ Version control data pipelines
- ✅ Testing framework
- ✅ Documentation generation
- ✅ Macros and templates
- ✅ Integration with DWH

## Scalability Considerations

### Database
- Connection pooling (SQLAlchemy)
- Batch operations
- Indexed queries
- Pagination support

### API
- Request caching
- Pagination
- Rate limiting
- Async handlers

### NLP
- Batch processing
- Model caching
- Parallel execution
- Memory optimization

### Dashboard
- Data caching
- Pagination
- Lazy loading
- Server-side filtering

## Deployment Architecture

```
Development → Testing → Staging → Production

Docker Containers:
├── API Container (Python, FastAPI)
├── Dashboard Container (Python, Streamlit)
├── Database Container (PostgreSQL)
├── Cache Container (Redis, optional)
└── Worker Container (dbt, transformations)

Orchestration:
├── Docker Compose (Development)
├── Kubernetes (Production, optional)
└── AWS/GCP (Cloud deployment)
```

## Security Architecture

```
Client Request
    │
    ▼
─────────────────
HTTPS/TLS
─────────────────
    │
    ▼
API Gateway
├── Rate Limiting
├── CORS validation
└── Request logging
    │
    ▼
Middleware
├── Request ID tracking
├── Error handling
└── Response headers
    │
    ▼
Authentication
├── API Key verification
├── JWT validation
└── Token expiration
    │
    ▼
Authorization
├── Role checking
└── Resource access
    │
    ▼
Input Validation
├── Type checking
├── Range validation
├── Pattern matching
└── Sanitization
    │
    ▼
Application Logic
├── Business rules
└── Data processing
    │
    ▼
Database Access
└── Parameterized queries

Response
```

## Performance Optimization

- **Caching**: Request caching, result caching
- **Indexing**: Database indexes on frequent queries
- **Pagination**: Limit result sets
- **Async I/O**: Non-blocking operations
- **Connection Pooling**: Reuse connections
- **Batch Operations**: Process in chunks
- **Query Optimization**: Efficient SQL queries

---

For more details, see specific module documentation in `/docs`