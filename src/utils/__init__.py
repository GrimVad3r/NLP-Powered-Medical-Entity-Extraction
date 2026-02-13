"""
Utilities module for helper functions and constants.

BRANCH-8: Utilities
"""

from .decorators import retry_on_error, cache_result, timing, log_errors
from .helpers import (
    chunk_list,
    flatten_list,
    safe_divide,
    merge_dicts,
    get_nested_value,
    set_nested_value,
    batch_process,
    retry_function,
    validate_keys,
    serialize_object,
    deserialize_object,
)
from .constants import (
    ENTITY_TYPES,
    CONFIDENCE_LEVELS,
    HTTP_STATUS_CODES,
    DEFAULT_BATCH_SIZE,
    DEFAULT_CONFIDENCE_THRESHOLD,
    NLP_MODEL_NAME,
    CLASSIFIER_MODEL_NAME,
)
from .text_utils import (
    normalize_text,
    clean_html,
    extract_keywords,
    remove_special_chars,
    truncate_text,
    count_sentences,
    count_words,
    extract_urls,
    extract_emails,
    extract_mentions,
    extract_hashtags,
    extract_numbers,
    similarity_score,
)

__all__ = [
    # Decorators
    "retry_on_error",
    "cache_result",
    "timing",
    "log_errors",
    # Helpers
    "chunk_list",
    "flatten_list",
    "safe_divide",
    "merge_dicts",
    "get_nested_value",
    "set_nested_value",
    "batch_process",
    "retry_function",
    "validate_keys",
    "serialize_object",
    "deserialize_object",
    # Constants
    "ENTITY_TYPES",
    "CONFIDENCE_LEVELS",
    "HTTP_STATUS_CODES",
    "DEFAULT_BATCH_SIZE",
    "DEFAULT_CONFIDENCE_THRESHOLD",
    "NLP_MODEL_NAME",
    "CLASSIFIER_MODEL_NAME",
    # Text utils
    "normalize_text",
    "clean_html",
    "extract_keywords",
    "remove_special_chars",
    "truncate_text",
    "count_sentences",
    "count_words",
    "extract_urls",
    "extract_emails",
    "extract_mentions",
    "extract_hashtags",
    "extract_numbers",
    "similarity_score",
]