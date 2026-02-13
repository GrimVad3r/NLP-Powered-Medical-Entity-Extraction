"""
Product management endpoints.

BRANCH-6: REST API
Author: Boris (Claude Code)
"""

from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta

from ...database.crud import ProductCRUD, MessageCRUD
from ...database.connection import get_db_session
from ...database.models import Product
from ...core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/products", tags=["products"])


class ProductResponse:
    """Product response schema."""
    
    def __init__(self, product: Product):
        self.id = product.id
        self.name = product.name
        self.category = product.category
        self.mention_count = product.mention_count
        self.avg_price = product.avg_price
        self.min_price = product.min_price
        self.max_price = product.max_price
        self.popularity_score = product.popularity_score


@router.get("/top10")
async def get_top_products(
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None
) -> dict:
    """
    Get top products by mention count.

    Args:
        limit: Number of products to return
        category: Optional category filter

    Returns:
        List of top products
    """
    try:
        session = get_db_session()
        crud = ProductCRUD(session)

        products = crud.get_top_products(limit=limit)

        if category:
            products = [p for p in products if p.category == category]

        result = []
        for product in products:
            result.append({
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "mention_count": product.mention_count,
                "avg_price": product.avg_price,
                "popularity_score": product.popularity_score,
            })

        logger.info(f"Retrieved {len(result)} top products")
        return {"products": result, "total": len(result)}

    except Exception as e:
        logger.error(f"Error getting top products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        session.close()


@router.get("/by-category/{category}")
async def get_products_by_category(
    category: str,
    limit: int = Query(50, ge=1, le=1000)
) -> dict:
    """
    Get products by category.

    Args:
        category: Product category
        limit: Number of products to return

    Returns:
        List of products in category
    """
    try:
        session = get_db_session()
        crud = ProductCRUD(session)

        products = crud.get_by_category(category)
        products = products[:limit]

        result = [
            {
                "id": p.id,
                "name": p.name,
                "mention_count": p.mention_count,
                "avg_price": p.avg_price,
            }
            for p in products
        ]

        logger.info(f"Retrieved {len(result)} products in category {category}")
        return {"category": category, "products": result, "total": len(result)}

    except Exception as e:
        logger.error(f"Error getting products by category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        session.close()


@router.get("/{product_id}")
async def get_product(product_id: int) -> dict:
    """
    Get detailed product information.

    Args:
        product_id: Product ID

    Returns:
        Product details
    """
    try:
        session = get_db_session()
        crud = ProductCRUD(session)

        product = session.query(Product).filter(Product.id == product_id).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        logger.info(f"Retrieved product {product_id}")
        return {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "description": product.description,
            "mention_count": product.mention_count,
            "first_mentioned": product.first_mentioned.isoformat(),
            "last_mentioned": product.last_mentioned.isoformat(),
            "avg_price": product.avg_price,
            "min_price": product.min_price,
            "max_price": product.max_price,
            "popularity_score": product.popularity_score,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        session.close()


@router.get("/search/{query}")
async def search_products(
    query: str,
    limit: int = Query(20, ge=1, le=100)
) -> dict:
    """
    Search products by name.

    Args:
        query: Search query
        limit: Number of results

    Returns:
        List of matching products
    """
    try:
        session = get_db_session()

        products = session.query(Product).filter(
            Product.name.ilike(f"%{query}%")
        ).limit(limit).all()

        result = [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "mention_count": p.mention_count,
            }
            for p in products
        ]

        logger.info(f"Found {len(result)} products matching '{query}'")
        return {"query": query, "products": result, "total": len(result)}

    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        session.close()


@router.get("/price-trends/{product_id}")
async def get_price_trends(
    product_id: int,
    days: int = Query(30, ge=1, le=365)
) -> dict:
    """
    Get price trends for product.

    Args:
        product_id: Product ID
        days: Number of days to retrieve

    Returns:
        Price trend data
    """
    try:
        session = get_db_session()

        product = session.query(Product).filter(Product.id == product_id).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        start_date = datetime.utcnow() - timedelta(days=days)

        logger.info(f"Retrieved price trends for product {product_id}")
        return {
            "product_id": product_id,
            "product_name": product.name,
            "period_days": days,
            "avg_price": product.avg_price,
            "min_price": product.min_price,
            "max_price": product.max_price,
            "trend": "stable",  # Would be calculated from actual price history
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting price trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        session.close()