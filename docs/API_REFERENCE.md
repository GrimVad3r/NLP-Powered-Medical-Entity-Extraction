# API Reference - Medical Intelligence Platform v2.0

Complete REST API documentation with examples.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All requests can include an optional Bearer token:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/api/v1/products/top10
```

## Response Format

All responses are JSON:

```json
{
  "data": {},
  "status": "success",
  "timestamp": "2025-02-13T10:00:00Z"
}
```

---

## Products Endpoints

### Get Top 10 Products

```
GET /api/v1/products/top10
```

**Parameters:**
- `limit` (optional): Number of products to return (1-100, default: 10)
- `category` (optional): Filter by category

**Response:**
```json
{
  "products": [
    {
      "id": 1,
      "name": "Amoxicillin",
      "category": "Antibiotics",
      "mention_count": 234,
      "avg_price": 50.0,
      "popularity_score": 0.95
    }
  ],
  "total": 10
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/products/top10?limit=5
```

---

### Get Products by Category

```
GET /api/v1/products/by-category/{category}
```

**Parameters:**
- `category`: Product category name
- `limit` (optional): Number of results (1-1000, default: 50)

**Response:**
```json
{
  "category": "Antibiotics",
  "products": [
    {
      "id": 1,
      "name": "Amoxicillin",
      "mention_count": 234
    }
  ],
  "total": 5
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/products/by-category/Antibiotics
```

---

### Get Product Details

```
GET /api/v1/products/{product_id}
```

**Parameters:**
- `product_id`: Product ID

**Response:**
```json
{
  "id": 1,
  "name": "Amoxicillin",
  "category": "Antibiotics",
  "description": "Common antibiotic...",
  "mention_count": 234,
  "first_mentioned": "2025-01-01T00:00:00Z",
  "last_mentioned": "2025-02-13T10:00:00Z",
  "avg_price": 50.0,
  "min_price": 40.0,
  "max_price": 60.0,
  "popularity_score": 0.95
}
```

---

### Search Products

```
GET /api/v1/products/search/{query}
```

**Parameters:**
- `query`: Search term
- `limit` (optional): Number of results (1-100, default: 20)

**Response:**
```json
{
  "query": "amoxicillin",
  "products": [
    {
      "id": 1,
      "name": "Amoxicillin",
      "category": "Antibiotics",
      "mention_count": 234
    }
  ],
  "total": 1
}
```

---

### Get Price Trends

```
GET /api/v1/products/price-trends/{product_id}
```

**Parameters:**
- `product_id`: Product ID
- `days` (optional): Number of days (1-365, default: 30)

**Response:**
```json
{
  "product_id": 1,
  "product_name": "Amoxicillin",
  "period_days": 30,
  "avg_price": 50.0,
  "min_price": 40.0,
  "max_price": 60.0,
  "trend": "stable"
}
```

---

## NLP Endpoints

### Process Single Message

```
POST /api/v1/nlp/process-message
```

**Request Body:**
```json
{
  "text": "Amoxicillin 500mg for infection",
  "min_confidence": 0.6
}
```

**Response:**
```json
{
  "is_medical": true,
  "medical_confidence": 0.95,
  "entities": [
    {
      "text": "Amoxicillin",
      "entity_type": "MEDICATION",
      "confidence": 0.96,
      "normalized": "amoxicillin"
    },
    {
      "text": "500mg",
      "entity_type": "DOSAGE",
      "confidence": 0.92,
      "normalized": "500mg"
    }
  ],
  "quality_score": 0.85
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/nlp/process-message \
  -H "Content-Type: application/json" \
  -d '{"text": "Amoxicillin 500mg for infection"}'
```

---

### Batch Process Messages

```
POST /api/v1/nlp/batch-process
```

**Request Body:**
```json
{
  "messages": [
    "Amoxicillin for infection",
    "Patient has fever"
  ],
  "min_confidence": 0.6
}
```

**Response:**
```json
{
  "total_messages": 2,
  "processed": 2,
  "medical_messages": 1,
  "medical_percentage": 50.0,
  "results": [
    {
      "text": "Amoxicillin for infection",
      "is_medical": true,
      "medical_confidence": 0.95,
      "entity_count": 1,
      "quality_score": 0.85
    }
  ]
}
```

---

### Extract Entities

```
GET /api/v1/nlp/extract-entities
```

**Parameters:**
- `text`: Input text
- `min_confidence` (optional): Confidence threshold (0-1, default: 0.6)

**Response:**
```json
{
  "text": "Amoxicillin 500mg for fever",
  "total_entities": 2,
  "by_type": {
    "MEDICATION": [
      {
        "text": "Amoxicillin",
        "entity_type": "MEDICATION",
        "confidence": 0.96,
        "normalized": "amoxicillin"
      }
    ],
    "DOSAGE": [
      {
        "text": "500mg",
        "entity_type": "DOSAGE",
        "confidence": 0.92,
        "normalized": "500mg"
      }
    ]
  }
}
```

---

### Classify Text

```
GET /api/v1/nlp/classify-text
```

**Parameters:**
- `text`: Input text

**Response:**
```json
{
  "text": "Amoxicillin for infection",
  "is_medical": true,
  "medical_confidence": 0.95,
  "non_medical_confidence": 0.05
}
```

---

### Get Models Info

```
GET /api/v1/nlp/models
```

**Response:**
```json
{
  "models": [
    {
      "name": "spaCy Medical NER",
      "version": "en_core_sci_md",
      "type": "Named Entity Recognition",
      "accuracy": "94%"
    },
    {
      "name": "DistilBERT Classifier",
      "version": "distilbert-base-uncased-finetuned-sst-2-english",
      "type": "Text Classification",
      "accuracy": "92%"
    }
  ],
  "processors": {
    "medical_ner": "Enabled",
    "text_classifier": "Enabled",
    "entity_linker": "Enabled"
  }
}
```

---

## Analytics Endpoints

### Get Summary Statistics

```
GET /api/v1/analytics/summary
```

**Response:**
```json
{
  "total_messages": 5234,
  "medical_messages": 4031,
  "non_medical_messages": 1203,
  "medical_percentage": 77.0,
  "total_entities": 15420,
  "total_products": 156,
  "avg_entities_per_message": 2.95
}
```

---

### Get Daily Statistics

```
GET /api/v1/analytics/daily-stats
```

**Parameters:**
- `days` (optional): Number of days (1-365, default: 7)

**Response:**
```json
{
  "period_days": 7,
  "daily_stats": {
    "2025-02-07": {
      "count": 500,
      "medical": 385,
      "views": 15000,
      "forwards": 1200
    }
  },
  "total_messages": 3500
}
```

---

### Get Entity Distribution

```
GET /api/v1/analytics/entity-distribution
```

**Response:**
```json
{
  "total_entities": 15420,
  "distribution": {
    "MEDICATION": {
      "count": 5234,
      "percentage": 33.9
    },
    "CONDITION": {
      "count": 3856,
      "percentage": 25.0
    },
    "DOSAGE": {
      "count": 2934,
      "percentage": 19.0
    }
  }
}
```

---

### Get Top Medications

```
GET /api/v1/analytics/top-medications
```

**Parameters:**
- `limit` (optional): Number of results (1-100, default: 10)

**Response:**
```json
{
  "medications": [
    {
      "medication": "Amoxicillin",
      "mentions": 234
    }
  ],
  "total": 10
}
```

---

### Get Top Conditions

```
GET /api/v1/analytics/top-conditions
```

**Parameters:**
- `limit` (optional): Number of results (1-100, default: 10)

**Response:**
```json
{
  "conditions": [
    {
      "condition": "fever",
      "mentions": 156
    }
  ],
  "total": 10
}
```

---

### Get Quality Score Distribution

```
GET /api/v1/analytics/quality-score-distribution
```

**Response:**
```json
{
  "total_messages": 5234,
  "avg_quality_score": 0.78,
  "distribution": {
    "0.0-0.2": 234,
    "0.2-0.4": 456,
    "0.4-0.6": 1023,
    "0.6-0.8": 2045,
    "0.8-1.0": 1476
  }
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Unprocessable Entity |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Rate Limiting

- **Limit**: 100 requests per minute
- **Header**: `X-RateLimit-Limit: 100`
- **Remaining**: `X-RateLimit-Remaining: 45`

---

## Error Handling

### Error Response Format

```json
{
  "error": "Invalid input",
  "detail": "Text field is required",
  "status_code": 400,
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Examples with cURL

### Get top products
```bash
curl http://localhost:8000/api/v1/products/top10
```

### Search products
```bash
curl http://localhost:8000/api/v1/products/search/amoxicillin
```

### Process message
```bash
curl -X POST http://localhost:8000/api/v1/nlp/process-message \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Amoxicillin 500mg for infection treatment",
    "min_confidence": 0.6
  }'
```

### Get analytics summary
```bash
curl http://localhost:8000/api/v1/analytics/summary
```

---

For more information, visit the Swagger UI at `http://localhost:8000/docs`