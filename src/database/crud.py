"""
CRUD operations for database models.

BRANCH-4: Database Layer
Author: Boris (Claude Code)
"""

from typing import List, Optional, Any, Dict
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_,text

from src.core.logger import get_logger
from src.database.models import Message, Channel, Entity, Product, Price

logger = get_logger(__name__)


class MessageCRUD:
    """CRUD operations for Message model."""

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session

    def create(self, **kwargs) -> Message:
        """Create a new message."""
        try:
            message = Message(**kwargs)
            self.session.add(message)
            self.session.commit()
            logger.debug(f"Created message: {message.id}")
            return message
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating message: {e}")
            raise

    def get_by_id(self, message_id: int) -> Optional[Message]:
        """Get message by ID."""
        return self.session.query(Message).filter(Message.id == message_id).first()

    def get_by_telegram_id(self, telegram_id: int) -> Optional[Message]:
        """Get message by Telegram ID."""
        return self.session.query(Message).filter(Message.telegram_id == telegram_id).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> List[Message]:
        """Get all messages with pagination."""
        return self.session.query(Message).limit(limit).offset(offset).all()

    def get_by_channel(self, channel_id: int, limit: int = 100) -> List[Message]:
        """Get messages for a channel."""
        return (
            self.session.query(Message)
            .filter(Message.channel_id == channel_id)
            .order_by(desc(Message.date))
            .limit(limit)
            .all()
        )

    def get_medical_messages(self, limit: int = 100) -> List[Message]:
        """Get messages classified as medical."""
        return (
            self.session.query(Message)
            .filter(Message.is_medical == True)
            .order_by(desc(Message.quality_score))
            .limit(limit)
            .all()
        )

    def update(self, message_id: int, **kwargs) -> Optional[Message]:
        """Update a message."""
        try:
            message = self.get_by_id(message_id)
            if not message:
                return None

            for key, value in kwargs.items():
                setattr(message, key, value)

            message.updated_at = datetime.utcnow()
            self.session.commit()
            logger.debug(f"Updated message: {message_id}")
            return message

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating message: {e}")
            raise

    def delete(self, message_id: int) -> bool:
        """Soft delete a message."""
        try:
            message = self.get_by_id(message_id)
            if not message:
                return False

            message.is_deleted = True
            message.updated_at = datetime.utcnow()
            self.session.commit()
            logger.debug(f"Deleted message: {message_id}")
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting message: {e}")
            raise

    def count(self, medical_only: bool = False) -> int:
        """Count messages."""
        query = self.session.query(Message).filter(Message.is_deleted == False)
        if medical_only:
            query = query.filter(Message.is_medical == True)
        return query.count()


class EntityCRUD:
    """CRUD operations for Entity model."""

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session

    def create(self, **kwargs) -> Entity:
        """Create a new entity."""
        try:
            entity = Entity(**kwargs)
            self.session.add(entity)
            self.session.commit()
            return entity
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating entity: {e}")
            raise

    def create_batch(self, entities: List[Dict[str, Any]]) -> int:
        """Create multiple entities."""
        try:
            for entity_data in entities:
                entity = Entity(**entity_data)
                self.session.add(entity)

            self.session.commit()
            logger.debug(f"Created {len(entities)} entities")
            return len(entities)

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating entities: {e}")
            raise

    def get_by_message(self, message_id: int) -> List[Entity]:
        """Get entities for a message."""
        return self.session.query(Entity).filter(Entity.message_id == message_id).all()

    def get_by_type(self, entity_type: str, limit: int = 100) -> List[Entity]:
        """Get entities by type."""
        return (
            self.session.query(Entity)
            .filter(Entity.entity_type == entity_type)
            .limit(limit)
            .all()
        )

    def get_top_entities(self, entity_type: Optional[str] = None, limit: int = 10) -> List[tuple]:
        """Get top most mentioned entities."""
        query = self.session.query(Entity.text, Entity.entity_type)

        if entity_type:
            query = query.filter(Entity.entity_type == entity_type)

        from sqlalchemy import func
        return (
                query.group_by(Entity.text, Entity.entity_type)
                .order_by(desc(func.count(Entity.id)))
                .limit(limit)
                .all()
            )
    
    def get_analytics_top_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        FETCH from the dbt-transformed Mart table.
        This solves your 'no association' issue.
        """
        # We use a raw text query here because fct_medical_mentions 
        # is managed by dbt, not SQLAlchemy models.
        query = f"""
            SELECT entity_name, entity_type, mention_count 
            FROM public.fct_medical_mentions 
            WHERE entity_type = 'DRUG'
            ORDER BY mention_count DESC 
            LIMIT {limit}
        """
        result = self.session.execute(text(query))
        return [dict(row) for row in result]

    def count(self, entity_type: Optional[str] = None) -> int:
        """Count entities."""
        query = self.session.query(Entity)
        if entity_type:
            query = query.filter(Entity.entity_type == entity_type)
        return query.count()


class ProductCRUD:
    """CRUD operations for Product model."""

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session

    def create(self, **kwargs) -> Product:
        """Create a new product."""
        try:
            product = Product(**kwargs)
            self.session.add(product)
            self.session.commit()
            return product
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating product: {e}")
            raise

    def get_by_name(self, name: str) -> Optional[Product]:
        """Get product by name."""
        return self.session.query(Product).filter(Product.name == name).first()

    def get_top_products(self, limit: int = 10) -> List[Product]:
        """Get top products by mention count."""
        return (
            self.session.query(Product)
            .order_by(desc(Product.mention_count))
            .limit(limit)
            .all()
        )

    def get_by_category(self, category: str) -> List[Product]:
        """Get products by category."""
        return self.session.query(Product).filter(Product.category == category).all()

    def update_prices(self, product_id: int, avg_price: float, min_price: float, max_price: float) -> bool:
        """Update product prices."""
        try:
            product = self.session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return False

            product.avg_price = avg_price
            product.min_price = min_price
            product.max_price = max_price
            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating prices: {e}")
            raise

    def count(self) -> int:
        """Count products."""
        return self.session.query(Product).count()