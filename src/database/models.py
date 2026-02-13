"""
SQLAlchemy ORM models for Medical Intelligence Platform.

BRANCH-4: Database Layer
Author: Boris (Claude Code)
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Channel(Base):
    """Telegram channel model."""

    __tablename__ = "channels"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    url = Column(String(512))
    description = Column(Text)
    member_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    messages = relationship("Message", back_populates="channel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Channel(id={self.id}, name='{self.name}')>"


class Message(Base):
    """Telegram message model."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False, index=True)
    text = Column(Text)
    date = Column(DateTime, nullable=False, index=True)
    views = Column(Integer, default=0)
    forwards = Column(Integer, default=0)
    has_media = Column(Boolean, default=False)
    media_type = Column(String(50))
    media_path = Column(String(512))
    quality_score = Column(Float, default=0.0)
    is_medical = Column(Boolean, default=False)
    medical_confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    channel = relationship("Channel", back_populates="messages")
    entities = relationship("Entity", back_populates="message", cascade="all, delete-orphan")
    prices = relationship("Price", back_populates="message", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_message_channel_date", "channel_id", "date"),
        Index("ix_message_is_medical", "is_medical"),
    )

    def __repr__(self):
        return f"<Message(id={self.id}, telegram_id={self.telegram_id})>"


class Entity(Base):
    """Extracted medical entity model."""

    __tablename__ = "entities"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, index=True)
    text = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # MEDICATION, DOSAGE, CONDITION, etc.
    start_char = Column(Integer)
    end_char = Column(Integer)
    confidence = Column(Float, default=0.0)
    normalized = Column(String(255))
    is_linked = Column(Boolean, default=False)
    linked_text = Column(String(255))
    linked_category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    message = relationship("Message", back_populates="entities")

    # Indexes
    __table_args__ = (
        Index("ix_entity_message_type", "message_id", "entity_type"),
    )

    def __repr__(self):
        return f"<Entity(id={self.id}, type='{self.entity_type}', text='{self.text}')>"


class Product(Base):
    """Medical product/drug model."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    canonical_name = Column(String(255), index=True)
    category = Column(String(100), index=True)  # Antibiotics, Antimalarials, etc.
    description = Column(Text)
    mention_count = Column(Integer, default=0)
    first_mentioned = Column(DateTime, default=datetime.utcnow)
    last_mentioned = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    avg_price = Column(Float)
    min_price = Column(Float)
    max_price = Column(Float)
    popularity_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    prices = relationship("Price", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}')>"


class Price(Base):
    """Product price tracking model."""

    __tablename__ = "prices"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    price_value = Column(Float, nullable=False)
    currency = Column(String(10), default="ETB")
    date_recorded = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    message = relationship("Message", back_populates="prices")
    product = relationship("Product", back_populates="prices")
    channel = relationship("Channel")

    # Indexes
    __table_args__ = (
        Index("ix_price_product_date", "product_id", "date_recorded"),
    )

    def __repr__(self):
        return f"<Price(id={self.id}, product_id={self.product_id}, value={self.price_value})>"


class NLPResult(Base):
    """NLP processing results cache."""

    __tablename__ = "nlp_results"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, unique=True)
    is_medical = Column(Boolean, nullable=False)
    medical_confidence = Column(Float, nullable=False)
    entity_count = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)
    processing_time_ms = Column(Integer)
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<NLPResult(id={self.id}, message_id={self.message_id})>"


# Create all tables
def create_tables(engine):
    """Create all database tables."""
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    from sqlalchemy import create_engine

    # For testing
    engine = create_engine("sqlite:///:memory:")
    create_tables(engine)
    print("✅ All tables created successfully")