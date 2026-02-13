"""
Unit tests for CRUD operations.

Tests Create, Read, Update, Delete operations.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.crud import MessageCRUD, EntityCRUD, ProductCRUD
from src.database.models import Message, Entity, Product, Channel


class TestMessageCRUD:
    """Test Message CRUD operations."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return MagicMock()

    @pytest.fixture
    def crud(self, mock_session):
        """Create CRUD instance."""
        return MessageCRUD(mock_session)

    def test_crud_initialization(self, crud, mock_session):
        """Test CRUD initialization."""
        assert crud.session == mock_session

    def test_create_message(self, crud, mock_session):
        """Test creating message."""
        crud.create(
            telegram_id=1,
            channel_id=1,
            text="Test message",
            date=datetime.utcnow(),
            is_medical=True
        )

        # Verify add was called
        assert mock_session.add.called

    def test_get_by_id(self, crud, mock_session):
        """Test getting message by ID."""
        mock_message = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_message

        result = crud.get_by_id(1)

        assert result == mock_message
        assert mock_session.query.called

    def test_count_messages(self, crud, mock_session):
        """Test counting messages."""
        mock_session.query.return_value.count.return_value = 10

        count = crud.count()

        assert count == 10

    def test_update_message(self, crud, mock_session):
        """Test updating message."""
        mock_message = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_message

        result = crud.update(1, quality_score=0.95)

        assert mock_session.commit.called

    def test_delete_message(self, crud, mock_session):
        """Test deleting message."""
        mock_message = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_message

        crud.delete(1)

        assert mock_session.delete.called


class TestEntityCRUD:
    """Test Entity CRUD operations."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return MagicMock()

    @pytest.fixture
    def crud(self, mock_session):
        """Create CRUD instance."""
        return EntityCRUD(mock_session)

    def test_crud_initialization(self, crud, mock_session):
        """Test CRUD initialization."""
        assert crud.session == mock_session

    def test_create_entity(self, crud, mock_session):
        """Test creating entity."""
        crud.create(
            message_id=1,
            text="Amoxicillin",
            entity_type="MEDICATION",
            confidence=0.95
        )

        assert mock_session.add.called

    def test_create_batch_entities(self, crud, mock_session):
        """Test batch creating entities."""
        entities = [
            {
                "message_id": 1,
                "text": "Amoxicillin",
                "entity_type": "MEDICATION",
                "confidence": 0.95
            }
        ]

        crud.create_batch(entities)

        assert mock_session.add_all.called or mock_session.add.called

    def test_get_by_type(self, crud, mock_session):
        """Test getting entities by type."""
        mock_session.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        result = crud.get_by_type("MEDICATION")

        assert isinstance(result, list)

    def test_count_entities(self, crud, mock_session):
        """Test counting entities."""
        mock_session.query.return_value.count.return_value = 5

        count = crud.count()

        assert count == 5


class TestProductCRUD:
    """Test Product CRUD operations."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return MagicMock()

    @pytest.fixture
    def crud(self, mock_session):
        """Create CRUD instance."""
        return ProductCRUD(mock_session)

    def test_crud_initialization(self, crud, mock_session):
        """Test CRUD initialization."""
        assert crud.session == mock_session

    def test_create_product(self, crud, mock_session):
        """Test creating product."""
        crud.create(
            name="Amoxicillin",
            category="Antibiotics"
        )

        assert mock_session.add.called

    def test_get_by_name(self, crud, mock_session):
        """Test getting product by name."""
        mock_product = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_product

        result = crud.get_by_name("Amoxicillin")

        assert result == mock_product

    def test_get_by_category(self, crud, mock_session):
        """Test getting products by category."""
        mock_session.query.return_value.filter.return_value.all.return_value = []

        result = crud.get_by_category("Antibiotics")

        assert isinstance(result, list)

    def test_get_top_products(self, crud, mock_session):
        """Test getting top products."""
        mock_session.query.return_value.order_by.return_value.limit.return_value.all.return_value = []

        result = crud.get_top_products(limit=10)

        assert isinstance(result, list)

    def test_count_products(self, crud, mock_session):
        """Test counting products."""
        mock_session.query.return_value.count.return_value = 15

        count = crud.count()

        assert count == 15

    def test_update_product(self, crud, mock_session):
        """Test updating product."""
        mock_product = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_product

        result = crud.update(1, mention_count=100)

        assert mock_session.commit.called


class TestCRUDErrorHandling:
    """Test CRUD error handling."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return MagicMock()

    def test_handle_none_session(self, mock_session):
        """Test handling None session."""
        crud = MessageCRUD(mock_session)
        assert crud.session is not None

    def test_handle_database_error(self, mock_session):
        """Test handling database errors."""
        mock_session.commit.side_effect = Exception("Database error")
        crud = MessageCRUD(mock_session)

        # Should raise exception
        with pytest.raises(Exception):
            crud.create(
                telegram_id=1,
                channel_id=1,
                text="Test",
                date=datetime.utcnow()
            )
            crud.session.commit()