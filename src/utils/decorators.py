"""
Decorators for retry logic and caching.

BRANCH-8: Utilities
Author: Boris (Claude Code)
"""

import functools
import time
from typing import Callable, Any, Optional, Dict
from datetime import datetime, timedelta

from src.core.logger import get_logger

logger = get_logger(__name__)


class RetryDecorator:
    """Retry decorator with exponential backoff."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        retryable_exceptions: tuple = (Exception,),
    ):
        """
        Initialize retry decorator.

        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            backoff_factor: Exponential backoff factor
            retryable_exceptions: Tuple of exceptions to retry on
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.retryable_exceptions = retryable_exceptions

    def __call__(self, func: Callable) -> Callable:
        """Decorator implementation."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = self.initial_delay
            last_exception = None

            for attempt in range(1, self.max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except self.retryable_exceptions as e:
                    last_exception = e

                    if attempt == self.max_attempts:
                        logger.error(
                            f"Failed after {self.max_attempts} attempts: {str(e)}"
                        )
                        raise

                    logger.warning(
                        f"Attempt {attempt}/{self.max_attempts} failed, "
                        f"retrying in {delay:.2f}s: {str(e)}"
                    )

                    time.sleep(delay)
                    delay = min(delay * self.backoff_factor, self.max_delay)

            raise last_exception

        return wrapper


def retry_on_error(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
):
    """
    Decorator for retry with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Exponential backoff factor

    Example:
        @retry_on_error(max_attempts=3, initial_delay=1.0)
        def risky_operation():
            pass
    """
    decorator = RetryDecorator(
        max_attempts=max_attempts,
        initial_delay=initial_delay,
        max_delay=max_delay,
        backoff_factor=backoff_factor,
    )
    return decorator


class CacheDecorator:
    """Cache decorator with TTL support."""

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 128):
        """
        Initialize cache decorator.

        Args:
            ttl_seconds: Time to live for cached values
            max_size: Maximum cache size
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.cache: Dict[str, tuple] = {}

    def _make_key(self, args: tuple, kwargs: dict) -> str:
        """Generate cache key from arguments."""
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return "|".join(key_parts)

    def __call__(self, func: Callable) -> Callable:
        """Decorator implementation."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            cache_key = self._make_key(args, kwargs)

            # Check if cached and not expired
            if cache_key in self.cache:
                value, timestamp = self.cache[cache_key]
                if datetime.now() - timestamp < timedelta(seconds=self.ttl_seconds):
                    logger.debug(f"Cache hit for {func.__name__}")
                    return value
                else:
                    # Expired, remove from cache
                    del self.cache[cache_key]

            # Call function and cache result
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)

            # Manage cache size
            if len(self.cache) >= self.max_size:
                # Remove oldest entry
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k][1]
                )
                del self.cache[oldest_key]

            # Store in cache
            self.cache[cache_key] = (result, datetime.now())

            return result

        # Add cache management methods
        wrapper.cache_clear = lambda: self.cache.clear()
        wrapper.cache_info = lambda: {
            "size": len(self.cache),
            "ttl": self.ttl_seconds,
            "max_size": self.max_size,
        }

        return wrapper


def cache_result(ttl_seconds: int = 3600, max_size: int = 128):
    """
    Decorator for result caching with TTL.

    Args:
        ttl_seconds: Time to live for cached values
        max_size: Maximum cache size

    Example:
        @cache_result(ttl_seconds=3600)
        def expensive_operation(param):
            return result
    """
    decorator = CacheDecorator(ttl_seconds=ttl_seconds, max_size=max_size)
    return decorator


def timing(func: Callable) -> Callable:
    """
    Decorator to measure function execution time.

    Args:
        func: Function to time

    Example:
        @timing
        def my_function():
            pass
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger.info(f"{func.__name__} took {elapsed_time:.3f} seconds")
        return result

    return wrapper


def log_errors(func: Callable) -> Callable:
    """
    Decorator to log errors.

    Args:
        func: Function to decorate

    Example:
        @log_errors
        def my_function():
            pass
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise

    return wrapper