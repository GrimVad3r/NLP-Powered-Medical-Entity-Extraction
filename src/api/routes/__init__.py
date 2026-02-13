"""
API routes module.

BRANCH-6: REST API
"""

from . import products
from . import nlp
from . import analytics

__all__ = [
    "products",
    "nlp",
    "analytics",
]