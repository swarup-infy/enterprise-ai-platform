"""
Integration tests for the PostgreSQL database.

Verifies that:
- The test database is reachable.
- Alembic-created tables exist.
- SQLAlchemy can create and query records.
"""

from uuid import uuid4

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.db.database import engine
from app.models.user import User


@pytest.fixture
def db():
    """Provide a database session for integration tests."""

    with Session(engine) as session:
        yield session
        session.rollback()


class TestDatabaseConnection:
    """Database connectivity and schema tests."""

    def test_database_connection(self):
        """Verify PostgreSQL is reachable."""

        with engine.connect() as connection:
            result = connection.exec_driver_sql("SELECT 1")
            assert result.scalar() == 1

    def test_required_tables_exist(self):
        """Verify required database tables exist."""

        inspector = inspect(engine)

        tables = set(inspector.get_table_names())

        assert "users" in tables
        assert "documents" in tables
        assert "alembic_version" in tables


class TestUserDatabaseIntegration:
    """Integration tests for User persistence."""

    def test_create_and_read_user(self, db: Session):
        """Verify a user can be persisted and retrieved."""

        user = User(
            id=uuid4(),
            full_name="Integration Test User",
            username=f"integration_{uuid4().hex[:8]}",
            email=f"{uuid4().hex[:8]}@example.com",
            password_hash="test-password-hash",
            role="user",
            is_active=True,
            is_verified=False,
            is_superuser=False,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None

        saved_user = db.scalar(
            select(User).where(User.id == user.id)
        )

        assert saved_user is not None
        assert saved_user.id == user.id
        assert saved_user.full_name == "Integration Test User"

        db.delete(saved_user)
        db.commit()