"""
Application constants and enumerations.

BRANCH-8: Utilities
Author: Boris (Claude Code)
"""

# Entity types
ENTITY_TYPES = [
    "MEDICATION",
    "DOSAGE",
    "CONDITION",
    "SYMPTOM",
    "PRICE",
    "FREQUENCY",
    "FACILITY",
    "SIDE_EFFECT",
]

# Confidence levels
CONFIDENCE_LEVELS = {
    "VERY_HIGH": 0.9,
    "HIGH": 0.8,
    "MEDIUM": 0.6,
    "LOW": 0.4,
    "VERY_LOW": 0.2,
}

# HTTP Status codes
HTTP_STATUS_CODES = {
    "OK": 200,
    "CREATED": 201,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "CONFLICT": 409,
    "UNPROCESSABLE_ENTITY": 422,
    "INTERNAL_SERVER_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503,
}

# Default values
DEFAULT_BATCH_SIZE = 32
DEFAULT_MAX_TOKENS = 512
DEFAULT_CONFIDENCE_THRESHOLD = 0.6
DEFAULT_CHUNK_SIZE = 100
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_RETRIES = 3

# Telegram settings
TELEGRAM_RATE_LIMIT = 30  # requests per second
TELEGRAM_MAX_RETRIES = 3
TELEGRAM_TIMEOUT = 30
TELEGRAM_API_RETRY_DELAY = 1.0

# NLP settings
NLP_MODEL_NAME = "en_core_sci_md"
CLASSIFIER_MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
NER_BATCH_SIZE = 32
CLASSIFICATION_BATCH_SIZE = 64

# Database settings
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 40
DB_ECHO = False
DB_TIMEOUT = 30

# Cache settings
CACHE_TTL_SECONDS = 3600
CACHE_MAX_SIZE = 128

# File paths
LOGS_DIR = "logs"
DATA_DIR = "data"
MODELS_DIR = "data/nlp_models"
DOWNLOADS_DIR = "downloads"

# Medical keywords
MEDICATION_KEYWORDS = [
    "mg", "g", "ml", "tablet", "capsule", "injection", "dose",
    "treatment", "medicine", "drug", "pharmaceutical"
]

CONDITION_KEYWORDS = [
    "fever", "pain", "infection", "disease", "malaria", "cough",
    "headache", "nausea", "diarrhea", "vomiting"
]

PRICE_KEYWORDS = [
    "price", "cost", "amount", "payment", "paid", "birr", "usd", "etb",
    "shilling", "dollar", "pound"
]

# Message types
MESSAGE_TYPE_TEXT = "text"
MESSAGE_TYPE_MEDIA = "media"
MESSAGE_TYPE_LINK = "link"
MESSAGE_TYPE_DOCUMENT = "document"

# Processing status
STATUS_PENDING = "pending"
STATUS_PROCESSING = "processing"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"

# Quality score thresholds
QUALITY_THRESHOLD_HIGH = 0.8
QUALITY_THRESHOLD_MEDIUM = 0.6
QUALITY_THRESHOLD_LOW = 0.4

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 1000

# API endpoints
API_V1_PREFIX = "/api/v1"
API_TIMEOUT = 30

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "json"
LOG_MAX_BYTES = 10485760  # 10MB
LOG_BACKUP_COUNT = 10
LOG_RETENTION_DAYS = 30

# Feature flags
ENABLE_NLP = True
ENABLE_EXTRACTION = True
ENABLE_TRANSFORMATION = True
ENABLE_API = True
ENABLE_DASHBOARD = True
ENABLE_CACHING = True

# Error messages
ERROR_DATABASE_CONNECTION = "Database connection failed"
ERROR_NLP_MODEL_NOT_LOADED = "NLP model not loaded"
ERROR_INVALID_INPUT = "Invalid input data"
ERROR_PROCESSING_FAILED = "Message processing failed"
ERROR_NOT_FOUND = "Resource not found"

# Success messages
SUCCESS_PROCESSING = "Message processed successfully"
SUCCESS_SAVED = "Data saved successfully"
SUCCESS_DELETED = "Data deleted successfully"