"""
Integration tests for database operations.

Tests CRUD operations with real database.
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.crud import MessageCRUD, EntityCRUD, ProductCRUD
from src.database.models import Channel, Message, Entity, Product
from src.database.connection import get_db_session


@pytest.fixture
def session():
    """Get database session."""
    return get_db_session()


@pytest.fixture
def test_channel(session):
    """Create test channel."""
    channel = Channel(
        name="test_channel",
        telegram_id=12345,
        description="Test Channel"
    )
    session.add(channel)
    session.commit()
    return channel


@pytest.fixture
def test_message(session, test_channel):
    """Create test message."""
    message = Message(
        telegram_id=1,
        channel_id=test_channel.id,
        text="Test message with Amoxicillin",
        date=datetime.utcnow(),
        is_medical=True,
        quality_score=0.85
    )
    session.add(message)
    session.commit()
    return message


class TestMessageCRUD:
    """Test message CRUD operations."""

    def test_create_message(self, session, test_channel):
        """Test creating message."""
        crud = MessageCRUD(session)

        message = crud.create(
            telegram_id=2,
            channel_id=test_channel.id,
            text="New test message",
            date=datetime.utcnow(),
            is_medical=True
        )

        assert message.id is not None
        assert message.text == "New test message"

    def test_get_message_by_id(self, session, test_message):
        """Test retrieving message by ID."""
        crud = MessageCRUD(session)

        message = crud.get_by_id(test_message.id)

        assert message is not None
        assert message.id == test_message.id
        assert message.text == test_message.text

    def test_get_message_by_telegram_id(self, session, test_message):
        """Test retrieving message by Telegram ID."""
        crud = MessageCRUD(session)

        message = crud.get_by_telegram_id(test_message.telegram_id)

        assert message is not None
        assert message.telegram_id == test_message.telegram_id

    def test_get_medical_messages(self, session, test_message):
        """Test retrieving medical messages."""
        crud = MessageCRUD(session)

        messages = crud.get_medical_messages(limit=10)

        assert len(messages) > 0
        assert all(msg.is_medical for msg in messages)

    def test_update_message(self, session, test_message):
        """Test updating message."""
        crud = MessageCRUD(session)

        updated = crud.update(test_message.id, quality_score=0.95)

        assert updated.quality_score == 0.95

    def test_count_messages(self, session, test_message):
        """Test counting messages."""
        crud = MessageCRUD(session)

        count = crud.count()

        assert count > 0

    def test_count_medical_messages(self, session, test_message):
        """Test counting medical messages."""
        crud = MessageCRUD(session)

        count = crud.count(medical_only=True)

        assert count > 0


class TestEntityCRUD:
    """Test entity CRUD operations."""

    def test_create_entity(self, session, test_message):
        """Test creating entity."""
        crud = EntityCRUD(session)

        entity = crud.create(
            message_id=test_message.id,
            text="Amoxicillin",
            entity_type="MEDICATION",
            confidence=0.95
        )

        assert entity.id is not None
        assert entity.text == "Amoxicillin"
        assert entity.entity_type == "MEDICATION"

    def test_create_batch_entities(self, session, test_message):
        """Test batch creating entities."""
        crud = EntityCRUD(session)

        entities_data = [
            {
                "message_id": test_message.id,
                "text": "Amoxicillin",
                "entity_type": "MEDICATION",
                "confidence": 0.95
            },
            {
                "message_id": test_message.id,
                "text": "500mg",
                "entity_type": "DOSAGE",
                "confidence": 0.90
            }
        ]

        count = crud.create_batch(entities_data)

        assert count == 2

    def test_get_entities_by_message(self, session, test_message):
        """Test getting entities by message."""
        crud = EntityCRUD(session)

        # Create entities first
        crud.create(
            message_id=test_message.id,
            text="Amoxicillin",
            entity_type="MEDICATION",
            confidence=0.95
        )

        entities = crud.get_by_message(test_message.id)

        assert len(entities) > 0

    def test_get_entities_by_type(self, session, test_message):
        """Test getting entities by type."""
        crud = EntityCRUD(session)

        # Create medication entity
        crud.create(
            message_id=test_message.id,
            text="Amoxicillin",
            entity_type="MEDICATION",
            confidence=0.95
        )

        entities = crud.get_by_type("MEDICATION", limit=10)

        assert len(entities) > 0
        assert all(e.entity_type == "MEDICATION" for e in entities)

    def test_count_entities(self, session, test_message):
        """Test counting entities."""
        crud = EntityCRUD(session)

        # Create entity
        crud.create(
            message_id=test_message.id,
            text="Amoxicillin",
            entity_type="MEDICATION",
            confidence=0.95
        )

        count = crud.count()

        assert count > 0


class TestProductCRUD:
    """Test product CRUD operations."""

    def test_create_product(self, session):
        """Test creating product."""
        crud = ProductCRUD(session)

        product = crud.create(
            name="Amoxicillin",
            category="Antibiotics",
            mention_count=10
        )

        assert product.id is not None
        assert product.name == "Amoxicillin"

    def test_get_product_by_name(self, session):
        """Test getting product by name."""
        crud = ProductCRUD(session)

        # Create product
        crud.create(
            name="Paracetamol",
            category="Analgesics",
            mention_count=5
        )

        product = crud.get_by_name("Paracetamol")

        assert product is not None
        assert product.name == "Paracetamol"

    def test_get_top_products(self, session):
        """Test getting top products."""
        crud = ProductCRUD(session)

        # Create products
        crud.create(name="Amoxicillin", category="Antibiotics", mention_count=100)
        crud.create(name="Paracetamol", category="Analgesics", mention_count=50)
        crud.create(name="Artemether", category="Antimalarials", mention_count=30)

        products = crud.get_top_products(limit=2)

        assert len(products) > 0
        assert products[0].mention_count >= products[-1].mention_count

    def test_get_products_by_category(self, session):
        """Test getting products by category."""
        crud = ProductCRUD(session)

        # Create products
        crud.create(name="Amoxicillin", category="Antibiotics")
        crud.create(name="Penicillin", category="Antibiotics")

        products = crud.get_by_category("Antibiotics")

        assert len(products) > 0
        assert all(p.category == "Antibiotics" for p in products)

    def test_count_products(self, session):
        """Test counting products."""
        crud = ProductCRUD(session)

        crud.create(name="Test Product", category="Test")

        count = crud.count()

        assert count > 0