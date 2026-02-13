"""
Analytics endpoints for data insights.

BRANCH-6: REST API
Author: Boris (Claude Code)
"""

from fastapi import APIRouter, Query, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional

from ...database.crud import MessageCRUD, EntityCRUD, ProductCRUD
from ...database.connection import get_db_session
from ...database.models import Message, Entity
from ...core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/summary")
async def get_analytics_summary() -> dict:
    """
    Get overall analytics summary.

    Returns:
        Summary statistics
    """
    try:
        session = get_db_session()
        message_crud = MessageCRUD(session)
        entity_crud = EntityCRUD(session)
        product_crud = ProductCRUD(session)

        total_messages = message_crud.count()
        medical_messages = message_crud.count(medical_only=True)
        total_entities = entity_crud.count()
        total_products = product_crud.count()

        medical_percentage = (medical_messages / total_messages * 100) if total_messages > 0 else 0

        logger.info(f"Analytics summary: {total_messages} messages, {medical_percentage:.1f}% medical")

        return {
            "total_messages": total_messages,
            "medical_messages": medical_messages,
            "non_medical_messages": total_messages - medical_messages,
            "medical_percentage": medical_percentage,
            "total_entities": total_entities,
            "total_products": total_products,
            "avg_entities_per_message": (total_entities / total_messages) if total_messages > 0 else 0,
        }

    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        session.close()


@router.get("/daily-stats")
async def get_daily_stats(days: int = Query(7, ge=1, le=365)) -> dict:
    """
    Get daily statistics for last N days.

    Args:
        days: Number of days to retrieve

    Returns:
        Daily statistics
    """
    try:
        session = get_db_session()

        start_date = datetime.utcnow() - timedelta(days=days)
        messages = session.query(Message).filter(Message.date >= start_date).all()

        # Group by date
        daily_stats = {}
        for message in messages:
            date_key = message.date.date().isoformat()

            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    "count": 0,
                    "medical": 0,
                    "views": 0,
                    "forwards": 0,
                }

            daily_stats[date_key]["count"] += 1
            if message.is_medical:
                daily_stats[date_key]["medical"] += 1
            daily_stats[date_key]["views"] += message.views or 0
            daily_stats[date_key]["forwards"] += message.forwards or 0

        logger.info(f"Retrieved {len(daily_stats)} days of statistics")

        return {
            "period_days": days,
            "daily_stats": daily_stats,
            "total_messages": len(messages),
        }

    except Exception as e:
        logger.error(f"Error getting daily stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        session.close()


@router.get("/entity-distribution")
async def get_entity_distribution() -> dict:
    """
    Get distribution of entity types.

    Returns:
        Entity distribution statistics
    """
    try:
        session = get_db_session()
        entity_crud = EntityCRUD(session)

        entity_type_counts = {}
        entity_types = ["MEDICATION", "DOSAGE", "CONDITION", "SYMPTOM", "PRICE", "FREQUENCY"]

        for entity_type in entity_types:
            count = entity_crud.count(entity_type=entity_type)
            entity_type_counts[entity_type] = count

        total_entities = sum(entity_type_counts.values())

        distribution = {
            entity_type: {
                "count": count,
                "percentage": (count / total_entities * 100) if total_entities > 0 else 0,
            }
            for entity_type, count in entity_type_counts.items()
        }

        logger.info(f"Entity distribution retrieved: {total_entities} total")

        return {
            "total_entities": total_entities,
            "distribution": distribution,
        }

    except Exception as e:
        logger.error(f"Error getting entity distribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        session.close()


@router.get("/top-medications")
async def get_top_medications(limit: int = Query(10, ge=1, le=100)) -> dict:
    """
    Get top mentioned medications.

    Args:
        limit: Number of medications to return

    Returns:
        Top medications
    """
    try:
        session = get_db_session()
        entity_crud = EntityCRUD(session)

        top_entities = entity_crud.get_top_entities(entity_type="MEDICATION", limit=limit)

        result = [
            {"medication": text, "mentions": count}
            for text, count in top_entities
        ]

        logger.info(f"Retrieved top {len(result)} medications")

        return {
            "medications": result,
            "total": len(result),
        }

    except Exception as e:
        logger.error(f"Error getting top medications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        session.close()


@router.get("/top-conditions")
async def get_top_conditions(limit: int = Query(10, ge=1, le=100)) -> dict:
    """
    Get top mentioned conditions.

    Args:
        limit: Number of conditions to return

    Returns:
        Top conditions
    """
    try:
        session = get_db_session()
        entity_crud = EntityCRUD(session)

        top_entities = entity_crud.get_top_entities(entity_type="CONDITION", limit=limit)

        result = [
            {"condition": text, "mentions": count}
            for text, count in top_entities
        ]

        logger.info(f"Retrieved top {len(result)} conditions")

        return {
            "conditions": result,
            "total": len(result),
        }

    except Exception as e:
        logger.error(f"Error getting top conditions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        session.close()


@router.get("/quality-score-distribution")
async def get_quality_score_distribution() -> dict:
    """
    Get distribution of message quality scores.

    Returns:
        Quality score statistics
    """
    try:
        session = get_db_session()

        messages = session.query(Message).all()

        if not messages:
            return {"error": "No messages found"}

        scores = [msg.quality_score for msg in messages]

        # Group into buckets
        buckets = {
            "0.0-0.2": 0,
            "0.2-0.4": 0,
            "0.4-0.6": 0,
            "0.6-0.8": 0,
            "0.8-1.0": 0,
        }

        for score in scores:
            if score < 0.2:
                buckets["0.0-0.2"] += 1
            elif score < 0.4:
                buckets["0.2-0.4"] += 1
            elif score < 0.6:
                buckets["0.4-0.6"] += 1
            elif score < 0.8:
                buckets["0.6-0.8"] += 1
            else:
                buckets["0.8-1.0"] += 1

        return {
            "total_messages": len(messages),
            "avg_quality_score": sum(scores) / len(scores),
            "distribution": buckets,
        }

    except Exception as e:
        logger.error(f"Error getting quality score distribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        session.close()