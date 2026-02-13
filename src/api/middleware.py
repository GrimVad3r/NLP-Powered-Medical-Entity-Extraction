"""
Custom middleware for FastAPI application.

BRANCH-6: REST API
Author: Boris (Claude Code)
"""

import time
import json
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable
import uuid

from ..core.logger import get_logger

logger = get_logger(__name__)


class RequestIdMiddleware:
    """Add unique request ID to each request."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable):
        """Add request ID to request state."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class RequestLoggingMiddleware:
    """Log all API requests and responses."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable):
        """Log request details."""
        start_time = time.time()

        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query": dict(request.query_params),
            }
        )

        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Request failed: {str(e)}", exc_info=True)
            raise

        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} ({process_time:.3f}s)",
            extra={
                "status_code": response.status_code,
                "process_time": process_time,
            }
        )

        response.headers["X-Process-Time"] = str(process_time)
        return response


class ErrorHandlingMiddleware:
    """Global error handling middleware."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable):
        """Handle exceptions globally."""
        try:
            response = await call_next(request)
            return response

        except HTTPException as exc:
            logger.warning(f"HTTP Exception: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail,
                    "status_code": exc.status_code,
                    "request_id": getattr(request.state, "request_id", None),
                },
            )

        except Exception as exc:
            logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "status_code": 500,
                    "request_id": getattr(request.state, "request_id", None),
                },
            )


class RateLimitMiddleware:
    """Simple rate limiting middleware."""

    def __init__(self, app, requests_per_minute: int = 100):
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.requests = {}

    async def __call__(self, request: Request, call_next: Callable):
        """Check rate limit."""
        client_ip = request.client.host if request.client else "unknown"
        current_minute = int(time.time() / 60)

        key = f"{client_ip}:{current_minute}"

        if key not in self.requests:
            self.requests[key] = 0

        self.requests[key] += 1

        if self.requests[key] > self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": "Too many requests"},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - self.requests[key]
        )

        return response


class CORSMiddleware:
    """Custom CORS middleware."""

    def __init__(self, app, allow_origins: list = None, allow_credentials: bool = True):
        self.app = app
        self.allow_origins = allow_origins or ["*"]
        self.allow_credentials = allow_credentials
        self.allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        self.allow_headers = ["*"]

    async def __call__(self, request: Request, call_next: Callable):
        """Handle CORS."""
        if request.method == "OPTIONS":
            return JSONResponse(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": self._get_origin(request),
                    "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
                    "Access-Control-Allow-Headers": ", ".join(self.allow_headers),
                    "Access-Control-Allow-Credentials": str(self.allow_credentials).lower(),
                },
            )

        response = await call_next(request)

        response.headers["Access-Control-Allow-Origin"] = self._get_origin(request)
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)

        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"

        return response

    def _get_origin(self, request: Request) -> str:
        """Get allowed origin."""
        origin = request.headers.get("origin")

        if "*" in self.allow_origins:
            return "*"

        if origin in self.allow_origins:
            return origin

        return self.allow_origins[0] if self.allow_origins else "*"


class ValidationMiddleware:
    """Validate request data."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable):
        """Validate content type and content length."""
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"error": "Request body too large"},
            )

        response = await call_next(request)
        return response