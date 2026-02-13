"""
Helper utility functions.

BRANCH-8: Utilities
Author: Boris (Claude Code)
"""

from typing import List, Dict, Any, Union, Optional
import json

from ..core.logger import get_logger

logger = get_logger(__name__)


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Chunk a list into smaller lists.

    Args:
        lst: Input list
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(lst: List[List]) -> List:
    """
    Flatten a list of lists into a single list.

    Args:
        lst: List of lists

    Returns:
        Flattened list
    """
    return [item for sublist in lst for item in sublist]


def safe_divide(
    numerator: Union[int, float],
    denominator: Union[int, float],
    default: float = 0.0
) -> float:
    """
    Safely divide two numbers.

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Value to return if denominator is 0

    Returns:
        Division result or default
    """
    if denominator == 0:
        logger.warning("Division by zero")
        return default
    return numerator / denominator


def merge_dicts(*dicts: dict) -> dict:
    """
    Merge multiple dictionaries.

    Args:
        *dicts: Variable number of dictionaries

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def get_nested_value(
    data: Dict,
    path: str,
    default: Any = None,
    separator: str = "."
) -> Any:
    """
    Get value from nested dictionary using path.

    Args:
        data: Input dictionary
        path: Path to value (e.g., "user.profile.name")
        default: Default value if path not found
        separator: Path separator

    Returns:
        Value at path or default
    """
    keys = path.split(separator)
    current = data

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current


def set_nested_value(
    data: Dict,
    path: str,
    value: Any,
    separator: str = "."
) -> Dict:
    """
    Set value in nested dictionary using path.

    Args:
        data: Input dictionary
        path: Path to value (e.g., "user.profile.name")
        value: Value to set
        separator: Path separator

    Returns:
        Modified dictionary
    """
    keys = path.split(separator)
    current = data

    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value
    return data


def batch_process(
    items: List[Any],
    batch_size: int,
    process_fn
) -> List[Any]:
    """
    Process items in batches.

    Args:
        items: Items to process
        batch_size: Batch size
        process_fn: Function to apply to each batch

    Returns:
        List of results
    """
    results = []
    batches = chunk_list(items, batch_size)

    for batch in batches:
        result = process_fn(batch)
        results.extend(result if isinstance(result, list) else [result])

    return results


def retry_function(
    func,
    *args,
    max_retries: int = 3,
    delay: float = 1.0,
    **kwargs
) -> Any:
    """
    Retry a function multiple times.

    Args:
        func: Function to retry
        *args: Function arguments
        max_retries: Maximum retries
        delay: Delay between retries
        **kwargs: Keyword arguments

    Returns:
        Function result
    """
    import time

    last_exception = None

    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s")
                time.sleep(delay)

    raise last_exception


def validate_keys(
    data: Dict,
    required_keys: List[str]
) -> bool:
    """
    Validate dictionary has required keys.

    Args:
        data: Input dictionary
        required_keys: Required key names

    Returns:
        True if all keys present
    """
    missing = [k for k in required_keys if k not in data]

    if missing:
        logger.warning(f"Missing keys: {missing}")
        return False

    return True


def serialize_object(obj: Any) -> str:
    """
    Serialize object to JSON string.

    Args:
        obj: Object to serialize

    Returns:
        JSON string
    """
    try:
        return json.dumps(obj, default=str)
    except Exception as e:
        logger.error(f"Serialization failed: {e}")
        return "{}"


def deserialize_object(json_str: str, default: Any = None) -> Any:
    """
    Deserialize JSON string to object.

    Args:
        json_str: JSON string
        default: Default if parsing fails

    Returns:
        Deserialized object
    """
    try:
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Deserialization failed: {e}")
        return default